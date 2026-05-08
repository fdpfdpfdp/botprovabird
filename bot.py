import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Caricamento lista
df = pd.read_csv('specie.csv')
if 'visto' not in df.columns:
    df['visto'] = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Birdwatching Attivo! Usa /lista per vedere le specie mancanti.")

async def mostra_lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Filtra solo le specie NON viste
    mancanti = df[df['visto'] == False]['Nome Italiano'].tolist()
    
    if not mancanti:
        await update.message.reply_text("Tutte le specie sono state avvistate! 🎉")
        return

    # Crea bottoni per le prime 10 specie mancanti (per non intasare la chat)
    keyboard = []
    for specie in mancanti[:10]:
        keyboard.append([InlineKeyboardButton(specie, callback_data=specie)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    testo = f"Specie da avvistare oggi ({len(mancanti)} rimanenti):\n" + "\n".join(mancanti[:10])
    await update.message.reply_text(testo, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    specie_vista = query.data
    
    # Aggiorna il DataFrame
    df.loc[df['Nome Italiano'] == specie_vista, 'visto'] = True
    
    await query.answer(f"Segnato: {specie_vista}!")
    await query.edit_message_text(text=f"✅ {specie_vista} AVVISTATO! \nUsa /lista per aggiornare.")

# Configurazione finale (Inserisci il tuo Token qui)
app = Application.builder().token("8554178904:AAG3Qw0XsKkaV-HB7PlCrFDe8GdikhFT6mA").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("lista", mostra_lista))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
