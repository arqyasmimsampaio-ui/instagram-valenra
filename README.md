# Instagram Valenra Semijoias: postagem automática

Você sobe as fotos e o GitHub cria a arte e publica no @valenrasemijoias no dia e na hora marcados.

## Como agendar um post

1. Crie uma pasta dentro de `fila/` com o nome no formato **AAAA-MM-DD_HHMM**, no horário de Brasília.
   Exemplo: `fila/2026-12-05_1900` será publicado em 05/12/2026 às 19h.
2. Coloque dentro dela:
   - `foto.jpg` para um post de 1 foto, **ou** `foto1.jpg`, `foto2.jpg`… para carrossel (até 10)
   - `titulo.txt`: texto da faixa nude com fio dourado (vai só na 1ª imagem)
   - `legenda.txt`: legenda completa, com emojis e hashtags
3. Pelo site: abra a pasta `fila` › **Add file › Upload files**, arraste a pasta inteira e clique em **Commit changes**.

Depois disso o robô **Gerar artes** cria `arte1.jpg`, `arte2.jpg`… em cerca de 1 minuto. Já o robô **Publicar no Instagram** confere a fila de hora em hora e publica o que estiver no horário. Os posts publicados vão para `publicados/`.

> A pasta `fila/EXEMPLO_…` é só um modelo. Como o nome está fora do padrão, ela nunca é publicada.

## Configuração (uma vez só)

Em **Settings › Secrets and variables › Actions › New repository secret**, cadastre:

| Nome | O que é |
|---|---|
| `IG_ACCESS_TOKEN` | Token de longa duração do Instagram (app "Valenra Automação" na Meta) |
| `IG_USER_ID` | ID da conta do Instagram |
| `GH_PAT` *(opcional)* | Token do GitHub com permissão de *Secrets: write* neste repositório. Permite que o token do Instagram seja renovado sozinho |

## Identidade visual

- Fonte: Playfair Display (licença OFL), baixada automaticamente pelo robô. Para usar outra fonte, suba o arquivo como `marca/fonte.ttf`.
- `marca/logo.png`: **coloque aqui o logo da Valenra** (PNG com fundo transparente). Ele aparece no canto superior direito.
- As cores ficam no início de `scripts/gerar_artes.py` (`NUDE`, `DOURADO`, `TEXTO`).

## Testar

Aba **Actions** › *Publicar no Instagram* › **Run workflow**. Uma pasta com data no passado é publicada na hora.

## Token

O token do Instagram vale 60 dias. O robô **Renovar token** roda nos dias 1 e 20 de cada mês. Se ele falhar, o GitHub manda um e-mail avisando.
