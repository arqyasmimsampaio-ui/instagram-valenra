"""Capas de Reels da Valenra Semijoias (1080x1920) - foto real + tipografia editorial.

Regras (do brandbook):
  - a foto e sempre REAL (celular, luz natural, mao/cliente/bastidor). Sem fundo gerado.
  - tipografia: Playfair Display (titulo, com 1 palavra em italico) + Jost espacado (apoio).
  - acabamento: leve tom quente + grao fino, para parecer foto e nao arte digital.
  - tudo que importa fica na area segura do grid (y 240 a 1680).

Titulo: *palavra* = italico; "|" = quebra de linha.
Uso:  python capa_reels.py estilo foto.jpg "Titulo" "APOIO" saida.jpg
estilos: split_creme | split_chocolate | moldura | cheia
"""
import os, re, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance, ImageChops

W, H = 1080, 1920
SEG_TOPO, SEG_BASE = 240, 1680
CREME = (241, 232, 219)
CHOCOLATE = (54, 35, 26)
TEXTO = (72, 45, 31)
DOURADO = (184, 148, 88)
DOURADO_CLARO = (222, 193, 139)
CREME_TXT = (250, 244, 235)

PASTA = os.path.dirname(os.path.abspath(__file__))
FONTES = os.environ.get("VALENRA_FONTES", os.path.join(PASTA, "fonts"))


def _f(nome, tam, var):
    f = ImageFont.truetype(os.path.join(FONTES, nome), tam)
    try:
        f.set_variation_by_name(var)
    except Exception:
        pass
    return f


def serif(t, it=False):
    return _f("PlayfairItalic.ttf", t, "Italic") if it else _f("Playfair.ttf", t, "Regular")


def sans(t, peso="Regular"):
    return _f("Jost.ttf", t, peso)


# ------------------------------------------------------------ acabamento "foto real"

def grao(img, forca=7, seed=7):
    random.seed(seed)
    ruido = Image.effect_noise(img.size, forca * 6).convert("L")
    ruido = ImageOps.autocontrast(ruido).point(lambda v: 128 + (v - 128) * forca // 40)
    ruido = Image.merge("RGB", (ruido, ruido, ruido))
    return ImageChops.add(img, ruido, 1.0, -128)


def tom_quente(img, calor=0.06, contraste=1.03, sat=0.94):
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * (1 + calor))))
    b = b.point(lambda v: int(v * (1 - calor * 0.8)))
    img = Image.merge("RGB", (r, g, b))
    img = ImageEnhance.Contrast(img).enhance(contraste)
    return ImageEnhance.Color(img).enhance(sat)


def papel(cor, w=W, h=H):
    """Fundo liso com textura de papel bem sutil (nada de degrade digital)."""
    base = Image.new("RGB", (w, h), cor)
    t = Image.effect_noise((w // 2, h // 2), 5).convert("L").resize((w, h), Image.BICUBIC)
    t = t.filter(ImageFilter.GaussianBlur(1.5))
    t = Image.merge("RGB", (t, t, t))
    return ImageChops.add(base, t, 1.0, -128)


def preparar(foto, w, h, cx=0.5, cy=0.5):
    im = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(cx, cy))
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    return tom_quente(im)


# ------------------------------------------------------------ texto

def tokens(l):
    return [(p.strip("*"), p.startswith("*")) for p in re.split(r"(\*[^*]+\*)", l) if p]


def espacado(d, cx, y, txt, f, cor, esp):
    larg = sum(d.textlength(c, font=f) for c in txt) + esp * (len(txt) - 1)
    x = cx - larg / 2
    for c in txt:
        d.text((x, y), c, font=f, fill=cor)
        x += d.textlength(c, font=f) + esp
    return larg


def titulo(d, txt, y, tam, cor, largura=W - 170, cx=W / 2, entrelinha=1.06):
    linhas = [l.strip() for l in txt.split("|")]
    while True:
        fr, fi = serif(tam), serif(tam, True)
        m = max(sum(d.textlength(t, font=fi if i else fr) for t, i in tokens(l)) for l in linhas)
        if m <= largura or tam <= 56:
            break
        tam -= 4
    for l in linhas:
        tk = tokens(l)
        x = cx - sum(d.textlength(t, font=fi if i else fr) for t, i in tk) / 2
        for t, i in tk:
            f = fi if i else fr
            d.text((x, y), t, font=f, fill=cor)
            x += d.textlength(t, font=f)
        y += int(tam * entrelinha)
    return y


def apoio(d, txt, y, cor, fio, cx=W / 2):
    f = sans(28)
    larg = espacado(d, cx, y, txt.upper(), f, cor, 6)
    m = y + 19
    d.line([(cx - larg / 2 - 80, m), (cx - larg / 2 - 28, m)], fill=fio, width=2)
    d.line([(cx + larg / 2 + 28, m), (cx + larg / 2 + 80, m)], fill=fio, width=2)
    return y + 60


def assinatura(d, y, cor):
    espacado(d, W / 2, y, "VALENRA", sans(34), cor, 15)


# ------------------------------------------------------------ estilos

def split_creme(foto, txt, sub="", cx=0.5, cy=0.5, altura_texto=700):
    """Topo creme com titulo; foto real ocupando o resto (como 'Brilho de pertinho')."""
    img = papel(CREME)
    img.paste(preparar(foto, W, H - altura_texto, cx, cy), (0, altura_texto))
    d = ImageDraw.Draw(img)
    assinatura(d, SEG_TOPO + 20, TEXTO)
    y = titulo(d, txt, SEG_TOPO + 110, 118, TEXTO)
    if sub:
        apoio(d, sub, y + 22, TEXTO, DOURADO)
    return grao(img, 5)


def split_chocolate(foto, txt, sub="", preco="", cx=0.5, cy=0.5, altura_foto=1080):
    """Foto real em cima, base chocolate com chamada/preco (promo, live, VIP)."""
    img = papel(CHOCOLATE)
    img.paste(preparar(foto, W, altura_foto, cx, cy), (0, 0))
    d = ImageDraw.Draw(img)
    d.line([(90, altura_foto + 1), (W - 90, altura_foto + 1)], fill=DOURADO, width=2)
    y = titulo(d, txt, altura_foto + 60, 96, CREME_TXT)
    if preco:
        fp, fv = serif(64), serif(170)
        v = preco.replace("R$", "").strip()
        lv, lp = d.textlength(v, font=fv), d.textlength("R$", font=fp)
        x = (W - lv - lp - 12) / 2
        d.text((x, y + 52), "R$", font=fp, fill=DOURADO_CLARO)
        d.text((x + lp + 12, y - 8), v, font=fv, fill=DOURADO_CLARO)
        y += 200
    if sub:
        apoio(d, sub, y + 10, CREME_TXT, DOURADO)
    espacado(d, W / 2, 1830, "VALENRA", sans(26), DOURADO_CLARO, 12)
    return grao(img, 5)


def moldura(foto, txt, sub="", cx=0.5, cy=0.5, legenda="", fw=720, fh=860, topo_min=820):
    """Foto real 'impressa' (borda branca + sombra) sobre papel creme - para cliente/depoimento."""
    img = papel(CREME)
    d = ImageDraw.Draw(img)
    assinatura(d, SEG_TOPO + 20, TEXTO)
    y = titulo(d, txt, SEG_TOPO + 110, 104, TEXTO)
    if sub:
        y = apoio(d, sub, y + 20, TEXTO, DOURADO)
    foto_im = preparar(foto, fw, fh, cx, cy)
    borda = 26
    cartao = Image.new("RGB", (fw + 2 * borda, fh + 2 * borda + (70 if legenda else 0)), (252, 250, 246))
    cartao.paste(foto_im, (borda, borda))
    if legenda:
        dc = ImageDraw.Draw(cartao)
        fl = serif(36, True)
        dc.text(((cartao.width - dc.textlength(legenda, font=fl)) / 2, fh + borda + 14), legenda, font=fl, fill=TEXTO)
    topo = max(y + 40, topo_min)
    x = (W - cartao.width) // 2
    sombra = Image.new("L", img.size, 0)
    ImageDraw.Draw(sombra).rectangle([x + 10, topo + 18, x + cartao.width + 10, topo + cartao.height + 18], fill=120)
    sombra = sombra.filter(ImageFilter.GaussianBlur(22))
    img.paste(Image.new("RGB", img.size, (90, 70, 55)), (0, 0), sombra)
    img.paste(cartao, (x, topo))
    return grao(img, 5)


def cheia(foto, txt, sub="", cx=0.5, cy=0.5):
    """Foto real em tela cheia, titulo claro no topo com sombra suave (sem caixas)."""
    img = preparar(foto, W, H, cx, cy)
    veu = Image.new("L", (1, H))
    for y in range(H):
        veu.putpixel((0, y), int(185 * max(0.0, 1 - max(0, y - 260) / 820)))
    img.paste(Image.new("RGB", (W, H), (30, 20, 14)), (0, 0), veu.resize((W, H)))
    d = ImageDraw.Draw(img)
    assinatura(d, SEG_TOPO + 20, CREME_TXT)
    y = titulo(d, txt, SEG_TOPO + 110, 116, CREME_TXT)
    if sub:
        apoio(d, sub, y + 22, CREME_TXT, DOURADO_CLARO)
    return grao(img, 6)


ESTILOS = {"split_creme": split_creme, "split_chocolate": split_chocolate, "moldura": moldura, "cheia": cheia}


def processar_fila(raiz="fila"):
    """Para cada pasta com video (*.mp4) + capa.txt e sem capa.jpg: tira um quadro do video e gera a capa.

    capa.txt (uma chave por linha):
        estilo: moldura | split_creme | split_chocolate | cheia
        titulo: Ta na *hora*|de escolher o seu
        apoio: Relogio de brincos
        segundo: 4.5                      (quadro do video usado na capa)
        recorte: 10,450,1070,1490         (opcional: x1,y1,x2,y2 do quadro)
        preco: R$ 45                      (opcional, so split_chocolate)
        opcoes: fw=840,fh=840,topo_min=740 (opcional, numeros extras do estilo)
    """
    import glob, subprocess
    if not os.path.isdir(raiz):
        return
    for pasta in sorted(os.listdir(raiz)):
        b = os.path.join(raiz, pasta)
        videos = glob.glob(os.path.join(b, "*.mp4"))
        if not videos or not os.path.exists(os.path.join(b, "capa.txt")) or os.path.exists(os.path.join(b, "capa.jpg")):
            continue
        cfg = {}
        for linha in open(os.path.join(b, "capa.txt"), encoding="utf-8"):
            if ":" in linha:
                k, v = linha.split(":", 1)
                cfg[k.strip().lower()] = v.strip()
        quadro = os.path.join(b, "_quadro.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", cfg.get("segundo", "1"), "-i", videos[0],
                        "-frames:v", "1", "-q:v", "1", quadro], check=True)
        if cfg.get("recorte"):
            x1, y1, x2, y2 = [int(n) for n in cfg["recorte"].split(",")]
            Image.open(quadro).crop((x1, y1, x2, y2)).save(quadro, quality=95)
        extras = {}
        for par in filter(None, cfg.get("opcoes", "").split(",")):
            k, v = par.split("=")
            extras[k.strip()] = float(v) if "." in v else int(v)
        estilo = cfg.get("estilo", "split_creme")
        args = dict(sub=cfg.get("apoio", ""), **extras)
        if estilo == "split_chocolate" and cfg.get("preco"):
            args["preco"] = cfg["preco"]
        ESTILOS[estilo](quadro, cfg.get("titulo", ""), **args).save(os.path.join(b, "capa.jpg"), "JPEG", quality=93)
        os.remove(quadro)
        print("Capa de reels gerada:", pasta)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fila":
        processar_fila()
        sys.exit(0)
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(0)
    est, foto, txt, sub, saida = sys.argv[1:6]
    ESTILOS[est](foto, txt, sub).save(saida, "JPEG", quality=93)
