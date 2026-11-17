"""Monta o carrossel 'Brinco, anel e colar por R$ 27,50' em fila/2026-11-16_1200 (arte1..arte5)."""
import os, io, sys, math, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
import capa_reels as c

W, H = 1080, 1350
COR_S = (122, 99, 83)
OUT = "fila/2026-11-16_1200"
BRINCO, ANEL, COLAR = "fila/STORY_maxbotton2/foto1.jpg", "fila/CARR_anel/foto1.jpg", "fila/CARR_colar/foto1.jpg"
MEDALHA_URL = "https://febijus.bwimg.com.br/febijus/produtos/colar-folheado-a-ouro-18k-e-prata-escapulario-redondo-a3-1790605035.5808.jpg"


def cartao_leve(img, y0, y1, x0, x1):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([x0, y0, x1, y1], 24, fill=(244, 236, 225, 214))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def veu_topo(im):
    v = Image.new("L", (1, H))
    for y in range(H):
        v.putpixel((0, y), int(90 * max(0, 1 - y / 300)))
    im.paste(Image.new("RGB", (W, H), (40, 26, 18)), (0, 0), v.resize((W, H)))


def preco(d, y, fv_t=104, fp_t=44, fpor_t=40):
    fp, fv, fpor = c.serif(fp_t), c.serif(fv_t), c.serif(fpor_t, True)
    v = "27,50"
    lpor, lr, lv = d.textlength("por", font=fpor), d.textlength("R$", font=fp), d.textlength(v, font=fv)
    x = W / 2 - (lpor + 14 + lr + 8 + lv) / 2
    d.text((x, y + int(fv_t * .52)), "por", font=fpor, fill=c.TEXTO); x += lpor + 14
    d.text((x, y + int(fv_t * .42)), "R$", font=fp, fill=c.TEXTO); x += lr + 8
    d.text((x, y), v, font=fv, fill=c.TEXTO)


def capa():
    im = c.papel(c.CREME, W, H); d = ImageDraw.Draw(im)
    c.espacado(d, W / 2, 110, "VALENRA", c.sans(30), c.TEXTO, 14)
    y = c.titulo(d, "Brinco, anel e colar|por *R$ 27,50*", 200, 94, c.TEXTO, largura=920)
    y = c.apoio(d, "escolha o seu brilho", y + 18, c.TEXTO, c.DOURADO)
    fotos = [(BRINCO, 0.42), (ANEL, 0.45), (COLAR, 0.42)]
    fw, fh, b, gap = 292, 400, 14, 22
    total = 3 * (fw + 2 * b) + 2 * gap; x0 = (W - total) // 2; top = y + 70; x = x0
    for i, (f, cy) in enumerate(fotos):
        p = c.preparar(f, fw, fh, 0.5, cy)
        card = Image.new("RGB", (fw + 2 * b, fh + 2 * b), (252, 250, 246)); card.paste(p, (b, b))
        card = card.convert("RGBA").rotate([-2.5, 0, 2.5][i], Image.BICUBIC, expand=True)
        yy = top + (0 if i == 1 else 14)
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rectangle([x + 8, yy + 14, x + card.width + 4, yy + card.height + 10], fill=90)
        im.paste(Image.new("RGB", im.size, (90, 70, 55)), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
        im.paste(card, (x, yy), card); x += fw + 2 * b + gap
    d = ImageDraw.Draw(im); x = x0
    for lab in ["brinco", "anel", "colar"]:
        c.espacado(d, x + (fw + 2 * b) / 2, top + fh + 2 * b + 46, lab.upper(), c.sans(22), COR_S, 6); x += fw + 2 * b + gap
    c.espacado(d, W / 2, H - 90, "ARRASTA PRO LADO", c.sans(22), COR_S, 5)
    return c.grao(im, 4)


def peca(foto, nome, sub, cy, n):
    im = c.preparar(foto, W, H, 0.5, cy); veu_topo(im)
    y0 = 990
    im = cartao_leve(im, y0, 1300, 150, W - 150); d = ImageDraw.Draw(im)
    c.espacado(d, W / 2, 70, "VALENRA", c.sans(28), c.CREME_TXT, 13)
    c.espacado(d, W - 90, 70, n, c.sans(24), c.CREME_TXT, 4)
    y = c.titulo(d, nome, y0 + 30, 62, c.TEXTO, largura=700)
    c.espacado(d, W / 2, y + 6, sub.upper(), c.sans(22), COR_S, 5)
    preco(d, y + 44)
    return c.grao(im, 5)


def colar():
    src = Image.open(io.BytesIO(requests.get(MEDALHA_URL, timeout=60).content)).convert("RGB")
    lupa = src.crop((160, 790, 374, 1004)).resize((330, 330), Image.LANCZOS); D = 330
    im = c.preparar(COLAR, W, H, 0.5, 1.0); veu_topo(im)
    px, py, cx, cy = 593, 943, 835, 610
    d = ImageDraw.Draw(im); ang = math.atan2(cy - py, cx - px); r = D / 2 + 14
    d.line([(px + 16 * math.cos(ang), py + 16 * math.sin(ang)), (cx - r * math.cos(ang), cy - r * math.sin(ang))], fill=c.DOURADO_CLARO, width=3)
    d.ellipse([px - 16, py - 16, px + 16, py + 16], outline=c.DOURADO_CLARO, width=3)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse([cx - D / 2 - 8, cy - D / 2 - 2, cx + D / 2 + 20, cy + D / 2 + 26], fill=110)
    im.paste(Image.new("RGB", (W, H), (60, 40, 28)), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.ellipse([cx - D / 2 - 14, cy - D / 2 - 14, cx + D / 2 + 14, cy + D / 2 + 14], fill=(250, 246, 239))
    m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse([0, 0, D - 1, D - 1], fill=255)
    im.paste(lupa, (int(cx - D / 2), int(cy - D / 2)), m)
    d.ellipse([cx - D / 2 - 14, cy - D / 2 - 14, cx + D / 2 + 14, cy + D / 2 + 14], outline=c.DOURADO, width=2)
    lab = "MEDALHA DE SÃO BENTO"; f = c.sans(20, "Medium")
    lw = sum(d.textlength(ch, font=f) for ch in lab) + 4 * (len(lab) - 1)
    d.rounded_rectangle([cx - lw / 2 - 22, cy + D / 2 + 30, cx + lw / 2 + 22, cy + D / 2 + 74], 22, fill=(250, 246, 239))
    c.espacado(d, cx, cy + D / 2 + 40, lab, f, c.TEXTO, 4)
    y0 = 1062
    im = cartao_leve(im, y0, 1318, 180, W - 180); d = ImageDraw.Draw(im)
    c.espacado(d, W / 2, 70, "VALENRA", c.sans(28), c.CREME_TXT, 13)
    c.espacado(d, W - 90, 70, "4/5", c.sans(24), c.CREME_TXT, 4)
    y = c.titulo(d, "Escapulário *São Bento*", y0 + 24, 56, c.TEXTO, largura=640)
    c.espacado(d, W / 2, y + 12, "MEDALHA FRENTE E VERSO", c.sans(20), COR_S, 5)
    preco(d, y + 40, 88, 38, 34)
    return c.grao(im, 5)


def final():
    im = c.papel(c.CHOCOLATE, W, H); d = ImageDraw.Draw(im)
    c.espacado(d, W / 2, 90, "VALENRA", c.sans(30), c.DOURADO_CLARO, 14)
    y = c.titulo(d, "Qual vai ser|o seu *favorito*?", 380, 96, c.CREME_TXT, largura=880)
    y = c.apoio(d, "cada peça por R$ 27,50", y + 30, c.CREME_TXT, c.DOURADO)
    f = c.sans(34, "Medium"); t = "me chama no direct"; lt = d.textlength(t, font=f)
    d.rounded_rectangle([(W - lt) / 2 - 46, y + 60, (W + lt) / 2 + 46, y + 138], 39, outline=c.DOURADO_CLARO, width=2)
    d.text(((W - lt) / 2, y + 76), t, font=f, fill=c.CREME_TXT)
    c.espacado(d, W / 2, H - 120, "ENVIAMOS PARA TODO O BRASIL", c.sans(22), c.DOURADO_CLARO, 5)
    c.espacado(d, W / 2, H - 70, "IMAGENS ILUSTRATIVAS", c.sans(16), (170, 140, 110), 4)
    return c.grao(im, 4)


if __name__ == "__main__":
    if os.path.exists(f"{OUT}/arte1.jpg") or os.path.isdir("publicados/2026-11-16_1200"):
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    slides = [capa(), peca(BRINCO, "Brinco *Max Botton*", "dourado liso", 0.38, "2/5"),
              peca(ANEL, "Anel *Círculos*", "regulável", 0.55, "3/5"), colar(), final()]
    for i, s in enumerate(slides, 1):
        s.save(f"{OUT}/arte{i}.jpg", "JPEG", quality=92)
    print("Carrossel montado:", OUT)
