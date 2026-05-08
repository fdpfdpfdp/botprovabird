import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Caricamento lista
df = pd.read_csv('specie.csv')
if 'visto' not in df.columns:
    df['visto'] = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔭 Bot Birdwatching Attivo!\nUsa /lista per vedere cosa manca oggi.")

async def mostra_lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Calcolo statistiche
    totale = len(df)
    visti = len(df[df['visto'] == True])
    mancanti_list = df[df['visto'] == False]['Nome Italiano'].tolist()
    
    percentuale = (visti / totale) * 100 if totale > 0 else 0

    if not mancanti_list:
        await update.message.reply_text(f"🏆 MISSIONE COMPIUTA! Tutte le {totale} specie sono state avvistate!")
        return

    # Creazione bottoni (mostriamo le prime 15 specie mancanti per non intasare)
    keyboard = []
    for specie in mancanti_list[:15]:
        keyboard.append([InlineKeyboardButton(f"🚩 {specie}", callback_data=specie)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Messaggio con il totale aggiornato
    testo = (
        f"📊 **PROGRESSO GIORNALIERO**\n"
        f"✅ Avvistati: {visti} / {totale} ({percentuale:.1f}%)\n"
        f"❌ Mancanti: {len(mancanti_list)}\n\n"
        f"Premi su una specie per segnarla:"
    )
    
    await update.message.reply_text(testo, reply_markup=reply_markup, parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    specie_vista = query.data
    
    # Aggiorna lo stato nel DataFrame
    df.loc[df['Nome Italiano'] == specie_vista, 'visto'] = True
    
    # Calcolo nuovi totali per il messaggio di conferma
    visti = len(df[df['visto'] == True])
    totale = len(df)
    
    await query.answer()
    
    # Modifica il messaggio per confermare l'avvistamento e mostrare il nuovo totale
    await query.edit_message_text(
        text=f"✅ **{specie_vista}** segnato correttamente!\n"
             f"Ora siamo a **{visti}/{totale}** specie.\n\n"
             f"Usa /lista per vedere le rimanenti.",
        parse_mode='Markdown'
    )

# Configurazione finale (Ricordati di mettere il tuo Token)
app = Application.builder().token("8554178904:AAG3Qw0XsKkaV-HB7PlCrFDe8GdikhFT6mA").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("lista", mostra_lista))
app.add_handler(CallbackQueryHandler(button))

print("Bot in ascolto...")
app.run_polling()
