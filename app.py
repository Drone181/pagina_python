from flask import Flask, request, jsonify, send_file, render_template
import requests
import os

app = Flask(__name__)

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

    api_url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
    querystring = {"url": instagram_url}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        if 'media' in data and data['media']:
            video_url = data['media']
            video_response = requests.get(video_url)
            return send_file(
                video_response.content,
                mimetype='video/mp4',
                as_attachment=True,
                download_name='instagram_video.mp4'
            )
        else:
            return jsonify({"error": "Unable to fetch video URL"}), 500
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))