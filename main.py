import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from groq import Groq

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 **Metin Çeviri Botu**\n\n"
        "İngilizce mesaj yazarsan Türkçe'ye çeviririm.\n"
        "Türkçe yazarsan dokunmam.\n\n"
        "Hadi dene! ✨",
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text.strip()

    if len(text) < 3:
        return

    try:
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""
Aşağıdaki mesaj İngilizce ise akıcı ve doğal Türkçe'ye çevir.
Eğer zaten Türkçe ise aynı bırak.

Mesaj: {text}

Sadece çeviriyi ver, ekstra açıklama yazma.
"""
            }],
            temperature=0.3,
            max_tokens=700
        )

        sonuc = response.choices[0].message.content.strip()

        if sonuc != text and len(sonuc) > 5:
            await message.reply_text(f"**🇹🇷 Türkçe Çeviri:**\n{sonuc}")

    except Exception as e:
        logger.error(e)
        await message.reply_text("❌ Çeviri sırasında hata oluştu.")

def main():
    if not TOKEN or not GROQ_API_KEY:
        logger.error("❌ TOKEN veya GROQ_API_KEY eksik!")
        return

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ Metin Çeviri Botu aktif!")
    app.run_polling()


if __name__ == "__main__":
    main()
