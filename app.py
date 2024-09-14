from flask import Flask, request, render_template, send_file
import requests
from io import BytesIO

app = Flask(__name__)

# Function to get Instagram video URL via API
def get_instagram_video_url(instagram_url):
    api_key = '72ea23ea89mshf6775ef3b0dde3cp1c8da5jsn0d645a94c48c'  # Replace with your actual RapidAPI key
    api_host = 'instagram-media-downloader6.p.rapidapi.com'  # Replace with your RapidAPI host (e.g., 'instagram-video-downloader.p.rapidapi.com')

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host
    }

    api_url = f'https://api.rapidapi.com/instagram/download?url={instagram_url}'
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            video_data = response.json()
            return video_data.get('video_url')
        else:
            print(f"Error fetching video via API: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception fetching video: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST':
        instagram_url = request.form.get('url')
        video_url = get_instagram_video_url(instagram_url)
        if not video_url:
            return "Failed to fetch video. Please check the URL and try again."
        return render_template('index.html', video_url=video_url)

    return render_template('index.html', video_url=video_url)

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['video_url']
    if video_url:
        try:
            video_response = requests.get(video_url)
            video_io = BytesIO(video_response.content)
            return send_file(video_io, as_attachment=True, download_name='Instadownloader_video.mp4', mimetype='video/mp4')
        except Exception as e:
            print(f"Error downloading video: {e}")
            return "Failed to download video."
    else:
        return "Failed to download video."

if __name__ == '__main__':
    app.run(debug=True)
