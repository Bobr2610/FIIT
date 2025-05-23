from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Замените 'YOUR_BOT_TOKEN' на ваш реальный токен
BOT_TOKEN = "7858818679:AAHvcbH152UCIW9jhfgXO4xZgrmvRiJRQTY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Бот пока что не доступен, он скоро будет готов.')

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()