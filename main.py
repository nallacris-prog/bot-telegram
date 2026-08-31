import os
import threading
import requests
from flask import Flask
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Servidor Flask para manter o Render ativo no plano gratuito
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# Token do seu bot (@Assistente_nallabot)
TOKEN = '8676072226:AAH-ftvFiHyllCkAIIQg4iYIGBURRjLz2Bw'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Me envie o link de um vídeo do YouTube, TikTok ou Instagram e eu vou baixá-lo para você!")

async def baixar_e_enviar_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not url.startswith("http"):
        return

    mensagem_status = await update.message.reply_text("⏳ Processando e baixando o vídeo, aguarde...")
    nome_arquivo = f"video_{update.message.message_id}.mp4"

    try:
        # Método especial para TikTok
        if "tiktok.com" in url:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            res = requests.get(api_url).json()
            if res.get("code") == 0:
                video_url = res["data"]["play"]
                video_data = requests.get(video_url).content
                with open(nome_arquivo, "wb") as f:
                    f.write(video_data)
            else:
                raise Exception("Erro ao obter vídeo do TikTok.")

        # Método para YouTube, Instagram e outras redes
        else:
            ydl_opts = {
                'format': 'b[ext=mp4]/best[ext=mp4]/best',
                'outtmpl': nome_arquivo,
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await mensagem_status.edit_text("📤 Enviando para o Telegram...")

        with open(nome_arquivo, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

    except Exception as e:
        await update.message.reply_text("❌ Não foi possível baixar este vídeo. O link pode ser privado ou o serviço bloqueou temporariamente.")

    finally:
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, baixar_e_enviar_video))

    print("Bot online!")
    app.run_polling()
              
