"""Publica no Instagram as pastas da fila cujo horário já chegou.

Nome da pasta = data e hora (Brasília): AAAA-MM-DD_HHMM  ex.: 2026-12-01_1900
1 arte  -> post de foto
2 a 10  -> carrossel
video.mp4 -> reels (capa.jpg vira a capa, se existir)
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


def aguardar(cid, tentativas=24):
    for _ in range(tentativas):
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


def publicar_reels(b, video, legenda):
    base = {"media_type": "REELS", "caption": legenda, "share_to_feed": "true"}
    if os.path.exists(f"{b}/capa.jpg"):
        base["cover_url"] = url_publica(f"{b}/capa.jpg")
    try:
        # envio direto do arquivo (nao depende do link do GitHub)
        cid = criar(dict(base, upload_type="resumable"))
        tam = os.path.getsize(video)
        with open(video, "rb") as fh:
            r = requests.post(
                f"https://rupload.facebook.com/ig-api-upload/v23.0/{cid}",
                headers={"Authorization": f"OAuth {TOKEN}", "offset": "0", "file_size": str(tam)},
                data=fh, timeout=600,
            )
        if not r.ok or not r.json().get("success"):
            raise RuntimeError(f"upload do video falhou: {r.status_code} {r.text[:300]}")
    except Exception as e:
        print("Envio direto falhou, tentando pelo link publico:", e)
        cid = criar(dict(base, video_url=url_publica(video)))
    aguardar(cid, tentativas=72)
    p = requests.post(f"{API}/{USER}/media_publish", data={"creation_id": cid, "access_token": TOKEN}, timeout=60).json()
    if "id" not in p:
        raise RuntimeError(f"Erro ao publicar reels: {p}")
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
        videos = sorted(glob.glob(f"{b}/*.mp4"))
        if videos:
            legenda = open(f"{b}/legenda.txt", encoding="utf-8").read().strip() if os.path.exists(f"{b}/legenda.txt") else ""
            try:
                pid = publicar_reels(b, videos[0], legenda)
                print(f"Reels publicado: {pasta} -> {pid}")
                shutil.move(b, f"publicados/{pasta}")
            except Exception as e:
                erros += 1
                print(f"FALHOU {pasta}: {e}")
            continue
        artes = sorted(glob.glob(f"{b}/arte*.jpg"), key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
        if not artes:
            print("Ainda sem arte:", pasta)
            continue
        ia = os.path.exists(f"{b}/pedido.txt")
        if ia and not os.path.exists(f"{b}/aprovado.txt"):
            print("Aguardando aprovacao (foto com modelo IA):", pasta)
            continue
        legenda = ""
        if os.path.exists(f"{b}/legenda.txt"):
            legenda = open(f"{b}/legenda.txt", encoding="utf-8").read().strip()
        if ia:
            legenda += "\n\nImagem ilustrativa criada com IA. A peca real aparece na foto seguinte."
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
