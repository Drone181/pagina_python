from flask import Flask, request, render_template, send_file
import requests
from io import BytesIO
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_instagram_video_url(instagram_url):
    api_key = '72ea23ea89mshf6775ef3b0dde3cp1c8da5jsn0d645a94c48c'  # Replace with your actual RapidAPI key
    api_host = 'instagram-media-downloader6.p.rapidapi.com'  # Verify this host

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host
    }

    api_url = f'https://{api_host}/instagram/download'  # Updated API URL
    params = {'url': instagram_url}
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        video_data = response.json()
        logging.debug(f"API Response: {video_data}")
        return video_data.get('video_url')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching video via API: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST':
        instagram_url = request.form.get('url')
        logging.info(f"Received Instagram URL: {instagram_url}")
        video_url = get_instagram_video_url(instagram_url)
        if not video_url:
            logging.warning("Failed to fetch video URL")
            return "Failed to fetch video. Please check the URL and try again."
    return render_template('index.html', video_url=video_url)

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['video_url']
    if video_url:
        try:
            video_response = requests.get(video_url)
            video_response.raise_for_status()
            video_io = BytesIO(video_response.content)
            return send_file(video_io, as_attachment=True, download_name='Instadownloader_video.mp4', mimetype='video/mp4')
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return "Failed to download video."
    else:
        return "No video URL provided."

if __name__ == '__main__':
    app.run(debug=True)