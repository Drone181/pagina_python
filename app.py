from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import instaloader
import re
import requests
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

def extract_shortcode(instagram_url):
    pattern = r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?'
    match = re.search(pattern, instagram_url)
    if match:
        return match.group(1)
    else:
        return None

def get_instagram_video_url(instagram_url):
    try:
        shortcode = extract_shortcode(instagram_url)
        if shortcode:
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            if post.is_video:  # Ensure the post is a video
                video_url = post.video_url
                return video_url
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching video URL: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST':
        instagram_url = request.form['url']
        video_url = get_instagram_video_url(instagram_url)

        if video_url:
            return render_template('index.html', video_url=video_url)
        else:
            flash("Failed to fetch video. Please check the URL and try again.")
            return redirect(url_for('index'))

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
