from flask import Flask, request, jsonify, send_file, render_template
import requests
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Get the API key from environment variable
API_KEY = os.environ.get('RAPIDAPI_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download_video():
    instagram_url = request.json.get('url')
    if not instagram_url:
        return jsonify({"error": "No URL provided"}), 400

    if not API_KEY:
        logging.error("RAPIDAPI_KEY is not set")
        return jsonify({"error": "API key is not configured"}), 500

    api_url = "https://instagram-media-downloader6.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "instagram-media-downloader6.p.rapidapi.com"
    }
    payload = {"url": instagram_url}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        logging.debug(f"API Response: {data}")
        
        if 'result' in data and 'download_link' in data['result']:
            video_url = data['result']['download_link']
            video_response = requests.get(video_url)
            return send_file(
                video_response.content,
                mimetype='video/mp4',
                as_attachment=True,
                download_name='instagram_video.mp4'
            )
        else:
            logging.error(f"Unable to fetch video URL. API response: {data}")
            return jsonify({"error": "Unable to fetch video URL"}), 500
    except requests.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))