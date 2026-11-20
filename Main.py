import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("9170374112:AAHm88GkJmJ0_HAyRxuC9T9RMUv6Rj0Lav4")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===== SEUS PRODUTOS INFO CC - VITALÍCIO =====
# Aqui você coloca BANDEIRA e LEVEL de cada BIN
PRODUTOS = {
    "550209": {"nome": "INFO CC - Vitalício", "preco": "R$ 50,00", "bandeira": "MASTERCARD", "level": "PLATINUM", "banco": "Banco do Brasil"},
    "411111": {"nome": "INFO CC - Vitalício", "preco": "R$ 50,00", "bandeira": "VISA", "level": "GOLD", "banco": "Nubank"},
    "378282": {"nome": "INFO CC - Vitalício", "preco": "R$ 70,00", "bandeira": "AMEX", "level": "BLACK", "banco": "Bradesco"},
    "601111": {"nome": "INFO CC - Vitalício", "preco": "R$ 40,00", "bandeira": "DISCOVER", "level": "CLASSIC", "banco": "Itaú"},
}


def teclado_comprar(bin_code):
    teclado = InlineKeyboardMarkup()
    teclado.add(InlineKeyboardButton("🛒 COMPRAR", callback_data=f"comprar_{bin_code}"))
    return teclado

def formata_produto(bin_code, p):
    return f"💳 *BIN:* `{bin_code}`\n🏦 *Banco:* {p['banco']}\n💎 *Bandeira:* {p['bandeira']}\n🏷️ *Level:* {p['level']}\n📦 *Produto:* {p['nome']}\n💰 *Preço:* {p['preco']}\n"

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Bot INFO CC online! ✅\n\nComandos:\n/bin 550209 - pesquisar por BIN\n/bandeira visa - pesquisar por bandeira\n/level platinum - pesquisar por level")

@dp.message_handler(commands=['bin'])
async def check_bin(message: types.Message):
    args = message.get_args()
    if not args or not args.isdigit() or len(args) < 6:
        await message.reply("Uso: /bin 550209")
        return
    bin_code = args[:6]
    # Busca dados na internet
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_code}", headers={"Accept-Version": "3"}, timeout=10)
        d = r.json() if r.status_code == 200 else {}
    except:
        d = {}
    banco = d.get('bank', {}).get('name', 'Desconhecido')
    bandeira = d.get('scheme', 'Desconhecido').upper()
    pais = d.get('country', {}).get('name', 'Desconhecido')
    emoji = d.get('country', {}).get('emoji', '')
    tipo = d.get('type', 'Desconhecido')
    texto = f"💳 *BIN:* `{bin_code}`\n🏦 *Banco:* {banco}\n💎 *Bandeira:* {bandeira}\n🌍 *País:* {pais} {emoji}\n🏷️ *Tipo:* {tipo}\n"
    produto = PRODUTOS.get(bin_code)
    if produto:
        texto += f"\n📦 *Produto:* {produto['nome']}\n💰 *Preço:* {produto['preco']}\n🏷️ *Level:* {produto['level']}"
        await message.reply(texto, parse_mode="Markdown", reply_markup=teclado_comprar(bin_code))
    else:
        texto += "\n❌ Nenhum INFO CC com esse BIN."
        await message.reply(texto, parse_mode="Markdown")

@dp.message_handler(commands=['bandeira'])
async def por_bandeira(message: types.Message):
    busca = message.get_args().upper()
    if not busca:
        await message.reply("Uso: /bandeira visa\nExemplo: /bandeira mastercard, /bandeira visa, /bandeira amex")
        return
    achados = [(b, p) for b, p in PRODUTOS.items() if busca in p['bandeira']]
    if not achados:
        await message.reply(f"❌ Nenhum INFO CC com bandeira {busca}")
        return
    await message.reply(f"💎 *Achados com bandeira {busca}:* {len(achados)}", parse_mode="Markdown")
    for b, p in achados:
        await message.reply(formata_produto(b, p), parse_mode="Markdown", reply_markup=teclado_comprar(b))

@dp.message_handler(commands=['level'])
async def por_level(message: types.Message):
    busca = message.get_args().upper()
    if not busca:
        await message.reply("Uso: /level platinum\nExemplo: /level gold, /level platinum, /level black, /level classic")
        return
    achados = [(b, p) for b, p in PRODUTOS.items() if busca in p['level']]
    if not achados:
        await message.reply(f"❌ Nenhum INFO CC com level {busca}")
        return
    await message.reply(f"🏷️ *Achados com level {busca}:* {len(achados)}", parse_mode="Markdown")
    for b, p in achados:
        await message.reply(formata_produto(b, p), parse_mode="Markdown", reply_markup=teclado_comprar(b))

@dp.callback_query_handler(lambda c: c.data.startswith('comprar_'))
async def comprar(callback: types.CallbackQuery):
    bin_code = callback.data.split('_')[1]
    produto = PRODUTOS.get(bin_code)
    await callback.answer()
    await callback.message.reply(f"Você escolheu:\n📦 {produto['nome']}\n💰 {produto['preco']}\n\nPara comprar, chama o suporte @SEU_USUARIO")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
