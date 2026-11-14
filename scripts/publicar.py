"""Publica no Instagram as pastas da fila cujo horário já chegou.

Nome da pasta = data e hora (Brasília): AAAA-MM-DD_HHMM  ex.: 2026-12-01_1900
1 arte  -> post de foto
2 a 10  -> carrossel
"""
import os, re, sys, time, glob, shutil, datetime as dt
from zoneinfo import ZoneInfo
import requests

TZ = ZoneInfo("America/Sao_Paulo")
API = "https://graph.facebook.com/v23.0"  # token de usuario do sistema (login unificado), nao expira
TOKEN = os.environ["IG_ACCESS_TOKEN"]
USER = os.environ["IG_USER_ID"]
REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")


def url_publica(caminho):
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{caminho}"


def criar(dados):
    dados["access_token"] = TOKEN
    r = requests.post(f"{API}/{USER}/media", data=dados, timeout=60).json()
    if "id" not in r:
        raise RuntimeError(f"Erro ao criar mídia: {r}")
    return r["id"]


def aguardar(cid):
    for _ in range(24):
        s = requests.get(f"{API}/{cid}", params={"fields": "status_code", "access_token": TOKEN}, timeout=60).json()
        st = s.get("status_code")
        if st == "FINISHED":
            return
        if st == "ERROR":
            raise RuntimeError(f"Instagram recusou a mídia: {s}")
        time.sleep(5)
    raise RuntimeError("Tempo esgotado esperando o Instagram processar")


def publicar_pasta(b, artes, legenda):
    if len(artes) == 1:
        cid = criar({"image_url": url_publica(artes[0]), "caption": legenda})
    else:
        filhos = []
        for a in artes:
            f = criar({"image_url": url_publica(a), "is_carousel_item": "true"})
            aguardar(f)
            filhos.append(f)
        cid = criar({"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda})
    aguardar(cid)
    p = requests.post(f"{API}/{USER}/media_publish", data={"creation_id": cid, "access_token": TOKEN}, timeout=60).json()
    if "id" not in p:
        raise RuntimeError(f"Erro ao publicar: {p}")
    return p["id"]


def main():
    agora = dt.datetime.now(TZ)
    erros = 0
    os.makedirs("publicados", exist_ok=True)
    for pasta in sorted(os.listdir("fila")):
        b = f"fila/{pasta}"
        if not os.path.isdir(b):
            continue
        try:
            quando = dt.datetime.strptime(pasta, "%Y-%m-%d_%H%M").replace(tzinfo=TZ)
        except ValueError:
            continue  # pastas de exemplo ou com nome fora do padrão são ignoradas
        if quando > agora:
            continue
        artes = sorted(glob.glob(f"{b}/arte*.jpg"), key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
        if not artes:
            print("Ainda sem arte:", pasta)
            continue
        legenda = ""
        if os.path.exists(f"{b}/legenda.txt"):
            legenda = open(f"{b}/legenda.txt", encoding="utf-8").read().strip()
        try:
            pid = publicar_pasta(b, artes, legenda)
            print(f"Publicado: {pasta} -> post {pid}")
            shutil.move(b, f"publicados/{pasta}")
        except Exception as e:
            erros += 1
            print(f"FALHOU {pasta}: {e}")
    if erros:
        sys.exit(1)  # faz o GitHub te avisar por e-mail


if __name__ == "__main__":
    main()
