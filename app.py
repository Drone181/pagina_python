from flask import Flask, request, render_template, send_file
import requests
from io import BytesIO
import logging
from urllib.parse import quote
import re

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_instagram_video_url_api(instagram_url):
    api_key = '72ea23ea89mshf6775ef3b0dde3cp1c8da5jsn0d645a94c48c'  # Replace with your actual RapidAPI key
    api_host = 'instagram-media-downloader6.p.rapidapi.com'

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host
    }

    encoded_url = quote(instagram_url, safe='')
    api_url = f'https://{api_host}/instagram/download'
    params = {'url': encoded_url}
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        video_data = response.json()
        logging.debug(f"API Response: {video_data}")
        return video_data.get('video_url')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching video via API: {e}")
        logging.error(f"Response content: {e.response.content if hasattr(e, 'response') else 'No response content'}")
        return None

def get_instagram_video_url_fallback(instagram_url):
    try:
        response = requests.get(instagram_url)
        response.raise_for_status()
        html_content = response.text
        video_url_match = re.search(r'<meta property="og:video" content="([^"]+)"', html_content)
        if video_url_match:
            return video_url_match.group(1)
        else:
            logging.warning("Fallback method: No video URL found in HTML")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Fallback method: Error fetching Instagram page: {e}")
        return None

def get_instagram_video_url(instagram_url):
    # Try API method first
    video_url = get_instagram_video_url_api(instagram_url)
    if video_url:
        return video_url
    
    # If API fails, try fallback method
    logging.info("API method failed. Attempting fallback method.")
    return get_instagram_video_url_fallback(instagram_url)

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