import os
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Servidor Flask para manter o Render ativo
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

    mensagem_status = await update.message.reply_text("⏳ Processando o link pela API, aguarde...")
    nome_arquivo = f"video_{update.message.message_id}.mp4"

    try:
        video_url_download = None

        # 1. TIKTOK
        if "tiktok.com" in url:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            res = requests.get(api_url, timeout=15).json()
            if res.get("code") == 0:
                video_url_download = res["data"]["play"]

        # 2. YOUTUBE / INSTAGRAM (Usa API Cobalt)
        else:
            cobalt_headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                "url": url,
                "videoQuality": "720"
            }
            # Tenta a API do Cobalt
            res = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=cobalt_headers, timeout=15)
            data = res.json()
            if "url" in data:
                video_url_download = data["url"]

        # Se encontrou o link direto do vídeo
        if video_url_download:
            await mensagem_status.edit_text("📥 Baixando arquivo do vídeo...")
            
            # Baixa os dados do vídeo
            stream = requests.get(video_url_download, stream=True, timeout=30)
            with open(nome_arquivo, "wb") as f:
                for chunk in stream.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)

            await mensagem_status.edit_text("📤 Enviando para o Telegram...")

            with open(nome_arquivo, 'rb') as video_file:
                await update.message.reply_video(video=video_file)
        else:
            await mensagem_status.edit_text("❌ Não foi possível obter o link do vídeo. O post pode ser privado ou bloqueado.")

    except Exception as e:
        await update.message.reply_text("❌ Ocorreu um erro temporário no servidor ao baixar este vídeo.")

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
