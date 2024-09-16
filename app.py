from flask import Flask, request, jsonify, render_template
import http.client
import json
import os
from urllib.parse import quote
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

API_KEY = os.environ.get('RAPIDAPI_KEY', '72ea23ea89mshf6775ef3b0dde3cp1c8da5jsn0d645a94c48c')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download_video():
    instagram_url = request.json.get('url')
    if not instagram_url:
        return jsonify({"error": "No URL provided"}), 400

    conn = http.client.HTTPSConnection("instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
    }

    encoded_url = quote(instagram_url)
    endpoint = f"/get-info-rapidapi?url={encoded_url}"

    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        logging.debug(f"API Response Status: {res.status}")
        logging.debug(f"API Response Data: {data.decode('utf-8')}")
        
        json_data = json.loads(data.decode("utf-8"))
        
        if 'video' in json_data and json_data['video']:
            video_url = json_data['video']
            return jsonify({"video_url": video_url})
        else:
            logging.error(f"Video URL not found in API response: {json_data}")
            return jsonify({"error": "Video URL not found in API response"}), 500
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error: {e}")
        return jsonify({"error": "Invalid JSON response from API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))