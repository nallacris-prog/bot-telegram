import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '8998906800:AAHsVdXbDdhcGeroRfzSEZgcWgcoetbsbBg'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Me envie o link de um vídeo e eu vou baixá-lo para você.")

async def baixar_e_enviar_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if not url.startswith("http"):
        return

    mensagem_status = await update.message.reply_text("⏳ Baixando o vídeo, aguarde...")
    nome_arquivo = f"video_{update.message.message_id}.mp4"

    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': nome_arquivo,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await mensagem_status.edit_text("📤 Enviando para o Telegram...")

        with open(nome_arquivo, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Ocorreu um erro ao processar o vídeo: {e}")

    finally:
        await mensagem_status.delete()
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, baixar_e_enviar_video))

    print("Bot online! Pode testar no Telegram.")
    app.run_polling()
