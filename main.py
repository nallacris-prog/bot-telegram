import os
import yt_dlp
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Pegamos o Token diretamente das variáveis de ambiente da Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route('/', methods=['GET'])
def health_check():
    # Rota simples para manter o servidor ativo na Render
    return "Servidor rodando!", 200

@app.route('/download', methods=['POST'])
def process_download():
    data = request.get_json()
    chat_id = data.get("chat_id")
    video_url = data.get("url")

    if not chat_id or not video_url:
        return jsonify({"error": "Dados inválidos"}), 400

    output_filename = f"video_{chat_id}.mp4"

    # Configuração do yt_dlp para baixar o vídeo localmente no servidor
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024 # Limite de 50MB para não travar
    }

    try:
        # 1. Baixa o vídeo na Render
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # 2. Envia o vídeo baixado de volta para o chat do Telegram via API HTTP
        telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        
        with open(output_filename, 'rb') as video_file:
            payload = {'chat_id': chat_id}
            files = {'video': video_file}
            requests.post(telegram_api_url, data=payload, files=files)

        # 3. Apaga o arquivo temporário do servidor para economizar espaço
        if os.path.exists(output_filename):
            os.remove(output_filename)

        return jsonify({"status": "sucesso"}), 200

    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        # Avisa o usuário se der algum erro no download
        msg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(msg_url, json={'chat_id': chat_id, 'text': f"Não foi possível baixar este vídeo: {str(e)}"})
        
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
