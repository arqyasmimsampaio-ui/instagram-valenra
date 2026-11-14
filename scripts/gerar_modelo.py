"""Gera fotos com modelo IA (OpenAI) para as pastas da fila que tem pedido.txt.

Na pasta do post:
  peca.jpg      -> foto da peca real (fundo limpo de preferencia)
  pedido.txt    -> 1a linha: "modelo: 1" (ou 2, 3). Demais linhas: a cena desejada.
Gera: foto1.jpg (modelo usando a peca) e copia a peca como foto2.jpg (carrossel).
O post so e publicado depois que existir aprovado.txt na pasta.
"""
import os, io, re, glob, base64
import requests
from PIL import Image

API = "https://api.openai.com/v1/images/edits"
KEY = os.environ.get("OPENAI_API_KEY", "")
MODELO_IA = os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-1"

PROMPT_BASE = (
    "Fotografia editorial realista para catalogo de semijoias, estilo minimalista e elegante, "
    "fundo neutro bege claro, luz natural suave. "
    "A mulher deve ser exatamente a mesma pessoa das imagens de referencia da modelo "
    "(mesmo rosto, cabelo, tom de pele e tracos). Ignore as joias que ela usa nas referencias. "
    "Ela deve usar SOMENTE a peca mostrada na imagem da peca, reproduzida com fidelidade total: "
    "mesmo formato, tamanho proporcional, espessura da corrente, quantidade de elementos e cor do banho. "
    "Nao invente detalhes na joia. Cena: "
)


def ler_ref(caminho):
    im = Image.open(caminho).convert("RGB")
    im.thumbnail((1024, 1024))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return buf.getvalue()


def baixar_peca(b):
    """Se houver peca_url.txt (link da foto do fornecedor), baixa como peca.jpg."""
    if os.path.exists(f"{b}/peca_url.txt") and not glob.glob(f"{b}/peca.*"):
        url = open(f"{b}/peca_url.txt", encoding="utf-8").read().strip()
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            Image.open(io.BytesIO(r.content)).convert("RGB").save(f"{b}/peca.jpg", "JPEG", quality=95)
            print(f"{b}: foto da peca baixada do fornecedor")
        except Exception as e:
            print(f"{b}: nao consegui baixar a foto da peca: {e}")


def foto_peca(b):
    for nome in ("peca.jpg", "peca.jpeg", "peca.png"):
        if os.path.exists(f"{b}/{nome}"):
            im = Image.open(f"{b}/{nome}").convert("RGB")
            im.thumbnail((1536, 1536))
            buf = io.BytesIO()
            im.save(buf, "PNG")
            return buf.getvalue()
    return None


def gerar(b):
    baixar_peca(b)
    linhas = open(f"{b}/pedido.txt", encoding="utf-8").read().strip().splitlines()
    m = re.search(r"modelo\s*:?\s*(\d+)", linhas[0].lower()) if linhas else None
    num = m.group(1) if m else "1"
    cena = " ".join(linhas[1:] if m else linhas).strip() or "close no colo, sorriso leve"
    pasta_ref = f"marca/modelos/modelo{num}"
    refs = sorted(p for p in glob.glob(f"{pasta_ref}/*") if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))[:4]
    peca = foto_peca(b)
    if not refs or peca is None:
        print(f"{b}: falta referencia da modelo {num} ou peca.jpg")
        return False
    files = [("image[]", (f"modelo_{i}.jpg", ler_ref(r), "image/jpeg")) for i, r in enumerate(refs)]
    files.append(("image[]", ("peca.png", peca, "image/png")))
    data = {"model": MODELO_IA, "prompt": PROMPT_BASE + cena, "size": "1024x1536",
            "quality": "high", "input_fidelity": "high", "n": "1"}
    try:
        j = requests.post(API, headers={"Authorization": f"Bearer {KEY}"}, data=data, files=files, timeout=300).json()
    except Exception as e:
        print(f"{b}: falha ao chamar a OpenAI: {e}")
        return False
    if "data" not in j:
        print(f"{b}: erro da OpenAI: {j.get('error', j)}")
        return False
    img = Image.open(io.BytesIO(base64.b64decode(j["data"][0]["b64_json"]))).convert("RGB")
    img.save(f"{b}/foto1.jpg", "JPEG", quality=95)
    for nome in ("peca.jpg", "peca.jpeg", "peca.png"):
        if os.path.exists(f"{b}/{nome}"):
            Image.open(f"{b}/{nome}").convert("RGB").save(f"{b}/foto2.jpg", "JPEG", quality=95)
            break
    print(f"{b}: foto com modelo {num} gerada. Confira e crie aprovado.txt para liberar.")
    return True


def main():
    if not KEY:
        print("OPENAI_API_KEY nao configurada")
        return
    for b in sorted(glob.glob("fila/*/")):
        b = b.rstrip("/")
        if os.path.exists(f"{b}/pedido.txt") and not os.path.exists(f"{b}/foto1.jpg"):
            gerar(b)


if __name__ == "__main__":
    main()
