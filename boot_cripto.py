import logging
import requests
import feedparser
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token já no código, só cola e roda
TOKEN = "7553238358:AAGxJh2vS18tBx009-m2pyHPTN6ddraXDuU"

CARTEIRA = {
    'solana': {'qtde': 7, 'preco_medio': 717.0},
    'xrp': {'qtde': 440, 'preco_medio': 12.25}
}

KEYWORDS = ['xrp', 'ripple', 'solana', 'sec', 'crypto', 'blockchain', 'investment', 'price', 'market']

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://cryptobriefing.com/feed/",
    "https://decrypt.co/feed",
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml"
]

def pegar_precos():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ripple&vs_currencies=brl&include_24hr_change=true"
    try:
        resp = requests.get(url)
        dados = resp.json()
        sol = dados['solana']['brl']
        sol_var = dados['solana']['brl_24h_change']
        sol_24h = sol / (1 + sol_var / 100)

        xrp = dados['ripple']['brl']
        xrp_var = dados['ripple']['brl_24h_change']
        xrp_24h = xrp / (1 + xrp_var / 100)

        return {
            'solana': {'preco_atual': sol, 'preco_24h_atras': sol_24h, 'var_24h': sol_var},
            'xrp': {'preco_atual': xrp, 'preco_24h_atras': xrp_24h, 'var_24h': xrp_var}
        }
    except Exception as e:
        logging.error(f"Erro ao pegar preços: {e}")
        return None

def buscar_noticias(periodo_horas=24):
    agora = datetime.utcnow()
    limite = agora - timedelta(hours=periodo_horas)
    noticias = []

    for feed in RSS_FEEDS:
        try:
            d = feedparser.parse(feed)
            for entry in d.entries:
                if not entry.get('published_parsed'):
                    continue
                dt_pub = datetime(*entry.published_parsed[:6])
                if dt_pub < limite:
                    continue
                texto = (entry.title + entry.get('summary', '')).lower()
                if any(k in texto for k in KEYWORDS):
                    if entry.link not in [n['link'] for n in noticias]:
                        noticias.append({'titulo': entry.title, 'link': entry.link})
        except Exception as e:
            logging.error(f"Erro ao buscar notícias: {e}")
            continue
    return noticias[:10]

def formatar_resumo(carteira, precos):
    sol = carteira['solana']
    xrp = carteira['xrp']

    sol_atual = precos['solana']['preco_atual']
    xrp_atual = precos['xrp']['preco_atual']

    sol_invest = sol['qtde'] * sol['preco_medio']
    sol_valor = sol['qtde'] * sol_atual
    sol_lucro = sol_valor - sol_invest
    sol_pct = (sol_lucro / sol_invest) * 100 if sol_invest else 0

    xrp_invest = xrp['qtde'] * xrp['preco_medio']
    xrp_valor = xrp['qtde'] * xrp_atual
    xrp_lucro = xrp_valor - xrp_invest
    xrp_pct = (xrp_lucro / xrp_invest) * 100 if xrp_invest else 0

    total_invest = sol_invest + xrp_invest
    total_valor = sol_valor + xrp_valor
    total_lucro = total_valor - total_invest
    total_pct = (total_lucro / total_invest) * 100 if total_invest else 0

    return (
        f"📊 *Resumo da Carteira*\n\n"
        f"• SOLANA: R${sol_atual:.2f} (Qtd: {sol['qtde']})\n"
        f"  Investido: R${sol_invest:.2f} → Atual: R${sol_valor:.2f}\n"
        f"  Lucro/Prejuízo: R${sol_lucro:.2f} ({sol_pct:+.2f}%)\n\n"
        f"• XRP: R${xrp_atual:.2f} (Qtd: {xrp['qtde']})\n"
        f"  Investido: R${xrp_invest:.2f} → Atual: R${xrp_valor:.2f}\n"
        f"  Lucro/Prejuízo: R${xrp_lucro:.2f} ({xrp_pct:+.2f}%)\n\n"
        f"• Total Investido: R${total_invest:.2f}\n"
        f"• Valor Atual: R${total_valor:.2f}\n"
        f"• Lucro/Prejuízo Total: R${total_lucro:.2f} ({total_pct:+.2f}%)"
    )

def formatar_analise(moeda, dados, carteira):
    preco = dados[moeda]['preco_atual']
    preco_24h = dados[moeda]['preco_24h_atras']
    var = dados[moeda]['var_24h']
    return (
        f"📈 *Análise de Preço - {moeda.upper()}*\n\n"
        f"24h atrás: R${preco_24h:.2f}\n"
        f"Atual: R${preco:.2f}\n"
        f"Variação: {var:+.2f}%\n"
        f"Na sua carteira: {carteira[moeda]['qtde']} (PM R${carteira[moeda]['preco_medio']:.2f})"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botoes = [
        [InlineKeyboardButton("Resumo da Carteira", callback_data='resumo')],
        [InlineKeyboardButton("Análise de Preço", callback_data='analise')],
        [InlineKeyboardButton("Últimas Notícias", callback_data='noticias')]
    ]
    await update.message.reply_text("Escolha uma opção:", reply_markup=InlineKeyboardMarkup(botoes))

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'resumo':
        precos = pegar_precos()
        texto = formatar_resumo(CARTEIRA, precos) if precos else "Erro ao buscar preços."
        await query.edit_message_text(texto, parse_mode='Markdown')

    elif query.data == 'analise':
        botoes = [
            [InlineKeyboardButton("SOLANA", callback_data='analise_solana')],
            [InlineKeyboardButton("XRP", callback_data='analise_xrp')],
            [InlineKeyboardButton("Voltar", callback_data='voltar')]
        ]
        await query.edit_message_text("Escolha a moeda:", reply_markup=InlineKeyboardMarkup(botoes))

    elif query.data == 'noticias':
        botoes = [
            [InlineKeyboardButton("Últimas 24h", callback_data='noticias_24h')],
            [InlineKeyboardButton("Últimos 7 dias", callback_data='noticias_7d')],
            [InlineKeyboardButton("Voltar", callback_data='voltar')]
        ]
        await query.edit_message_text("Escolha o período:", reply_markup=InlineKeyboardMarkup(botoes))

    elif query.data == 'voltar':
        await start(update, context)

    elif query.data.startswith("analise_"):
        moeda = query.data.split("_")[1]
        precos = pegar_precos()
        texto = formatar_analise(moeda, precos, CARTEIRA) if precos else "Erro ao buscar preço."
        await query.edit_message_text(texto, parse_mode='Markdown')

    elif query.data.startswith("noticias_"):
        horas = 24 if '24h' in query.data else 168
        noticias = buscar_noticias(horas)
        if noticias:
            texto = "\n\n".join([f"• [{n['titulo']}]({n['link']})" for n in noticias])
            await query.edit_message_text(f"📰 *Notícias Relevantes*\n\n{texto}", parse_mode='Markdown')
        else:
            await query.edit_message_text("Nenhuma notícia relevante encontrada.")

def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback))
    print("🤖 Bot cripto rodando...")
    app.run_polling()

if __name__ == "__main__":
    start_bot()