"""Gera as artes da Valenra Semijoias (1080x1350) para cada pasta em fila/.

Em cada pasta da fila:
  foto.jpg  OU  foto1.jpg, foto2.jpg ... (carrossel, até 10)
  titulo.txt   -> texto da faixa (só na 1ª imagem)
  legenda.txt  -> legenda do post
Gera: arte1.jpg, arte2.jpg ...
"""
import os, re, io, glob, base64
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
NUDE = (245, 238, 230, 235)
DOURADO = (191, 155, 90)
TEXTO = (60, 45, 35)
FONTE = "marca/fonte.ttf"
LOGO = "marca/logo.png"
ARTE_VERSAO = "2"  # mude este numero para refazer todas as artes da fila
LOGO_MASCARA = "marca/logo_mascara.b64"  # logo da Valenra em texto (usado se nao houver logo.png)


def fotos_da_pasta(b):
    fotos = glob.glob(f"{b}/foto*.jpg") + glob.glob(f"{b}/foto*.jpeg") + glob.glob(f"{b}/foto*.png")
    def ordem(p):
        n = re.findall(r"\d+", os.path.basename(p))
        return int(n[0]) if n else 0
    return sorted(fotos, key=ordem)[:10]


def fonte(tam):
    try:
        f = ImageFont.truetype(FONTE, tam)
        try:
            f.set_variation_by_name("SemiBold")
        except Exception:
            pass
        return f
    except Exception:
        return ImageFont.load_default(tam)


def quebrar(d, texto, f, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if d.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def carregar_logo():
    if os.path.exists(LOGO):
        return Image.open(LOGO).convert("RGBA")
    if os.path.exists(LOGO_MASCARA):
        mascara = Image.open(io.BytesIO(base64.b64decode(open(LOGO_MASCARA).read()))).convert("L")
        lg = Image.new("RGBA", mascara.size, DOURADO + (255,))
        lg.putalpha(mascara)
        return lg
    return None


def logo_canto(img):
    lg = carregar_logo()
    if lg is None:
        return
    lg.thumbnail((200, 200))
    img.paste(lg, (W - lg.width - 40, 40), lg)


def arte(caminho, titulo=None, centro_y=0.5):
    img = ImageOps.fit(ImageOps.exif_transpose(Image.open(caminho)).convert("RGB"), (W, H), centering=(0.5, centro_y))
    if titulo:
        d = ImageDraw.Draw(img, "RGBA")
        tam = 64
        f = fonte(tam)
        linhas = quebrar(d, titulo, f, W - 120)
        while len(linhas) > 2 and tam > 40:
            tam -= 4
            f = fonte(tam)
            linhas = quebrar(d, titulo, f, W - 120)
        altura_faixa = 90 + len(linhas) * int(tam * 1.3)
        topo = H - altura_faixa
        d.rectangle([0, topo, W, H], fill=NUDE)
        d.line([(60, topo), (W - 60, topo)], fill=DOURADO, width=3)
        y = topo + 45
        for linha in linhas:
            d.text((60, y), linha, font=f, fill=TEXTO)
            y += int(tam * 1.3)
    logo_canto(img)
    return img


def main():
    if not os.path.isdir("fila"):
        return
    for pasta in sorted(os.listdir("fila")):
        b = f"fila/{pasta}"
        if not os.path.isdir(b):
            continue
        marca_v = f"{b}/arte_versao.txt"
        if glob.glob(f"{b}/arte*.jpg") and os.path.exists(marca_v) and open(marca_v).read().strip() == ARTE_VERSAO:
            continue
        fotos = fotos_da_pasta(b)
        if not fotos:
            print("Sem fotos:", pasta)
            continue
        titulo = ""
        if os.path.exists(f"{b}/titulo.txt"):
            titulo = open(f"{b}/titulo.txt", encoding="utf-8").read().strip()
        for velha in glob.glob(f"{b}/arte*.jpg"):
            os.remove(velha)
        ia = os.path.exists(f"{b}/pedido.txt")
        for i, foto in enumerate(fotos, start=1):
            # foto da modelo IA: enquadra mais para baixo para o pingente nao ficar atras da faixa
            centro = 0.95 if (ia and i == 1) else 0.5
            arte(foto, titulo if i == 1 else None, centro).save(f"{b}/arte{i}.jpg", "JPEG", quality=92)
        open(marca_v, "w").write(ARTE_VERSAO)
        print(f"Artes geradas: {pasta} ({len(fotos)} imagem(ns))")


if __name__ == "__main__":
    main()
