from flask import Flask, request, render_template, send_file
import instaloader
import re
import requests
from io import BytesIO

app = Flask(__name__)

def extract_shortcode(instagram_url):
    pattern = r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?'
    match = re.search(pattern, instagram_url)
    if match:
        return match.group(1)
    else:
        return None

def get_instagram_video_url(instagram_url):
    shortcode = extract_shortcode(instagram_url)
    if shortcode:
        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        video_url = post.video_url  # Get the video URL
        return video_url
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST':
        instagram_url = request.form['url']
        video_url = get_instagram_video_url(instagram_url)
        if not video_url:
            return "Failed to fetch video. Please check the URL and try again."
        return render_template('index.html', video_url=video_url, instagram_url=instagram_url)

    return render_template('index.html', video_url=video_url)

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['video_url']
    if video_url:
        # Fetch the video content from the URL
        video_response = requests.get(video_url)

        # Create a BytesIO object to store the video content
        video_io = BytesIO(video_response.content)

        # Send the video file with the custom name 'Instadownloader_video.mp4'
        return send_file(video_io, as_attachment=True, download_name='Instadownloader_video.mp4', mimetype='video/mp4')
    else:
        return "Failed to download video."
