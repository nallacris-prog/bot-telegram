import os
import threading
import requests
from flask import Flask
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

TOKEN = '8676072226:AAH-ftvFiHyllCkAIIQg4iYIGBURRjLz2Bw'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Me envie o link de um vídeo do YouTube, TikTok ou Instagram e eu vou baixá-lo para você!")

async def baixar_e_enviar_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not url.startswith("http"):
        return

    mensagem_status = await update.message.reply_text("⏳ Baixando o vídeo na nuvem, aguarde...")
    nome_arquivo = f"video_{update.message.message_id}.mp4"

    try:
        # Método TikTok via API TikWM (sempre funciona na nuvem)
        if "tiktok.com" in url:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            res = requests.get(api_url, timeout=20).json()
            if res.get("code") == 0:
                video_url = res["data"]["play"]
                video_data = requests.get(video_url, timeout=30).content
                with open(nome_arquivo, "wb") as f:
                    f.write(video_data)
            else:
                raise Exception("Falha no TikTok TikWM")

        # Método Geral (Instagram / YouTube) com bypass de IP
        else:
            ydl_opts = {
                'format': 'b[ext=mp4]/best[ext=mp4]/best',
                'outtmpl': nome_arquivo,
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'source_address': '0.0.0.0',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Sec-Fetch-Mode': 'navigate',
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await mensagem_status.edit_text("📤 Enviando para o Telegram...")

        with open(nome_arquivo, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

    except Exception as e:
        await mensagem_status.edit_text("❌ Não foi possível baixar. O vídeo pode ser privado ou a rede bloqueou o acesso temporariamente.")

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
