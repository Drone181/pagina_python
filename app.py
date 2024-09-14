from flask import Flask, request, render_template, send_file
import instaloader
import re
import requests
from io import BytesIO

app = Flask(__name__)

# Function to extract shortcode from URL
def extract_shortcode(instagram_url):
    pattern = r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?'
    match = re.search(pattern, instagram_url)
    if match:
        return match.group(1)
    else:
        return None

# Function to get Instagram video URL
def get_instagram_video_url(instagram_url):
    try:
        shortcode = extract_shortcode(instagram_url)
        if shortcode:
            print(f"Extracted shortcode: {shortcode}")  # Debugging print
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Check if the post has a video
            if post.is_video:
                video_url = post.video_url
                print(f"Fetched video URL: {video_url}")  # Debugging print
                return video_url
            else:
                print("Post does not contain a video.")  # Debugging print
                return None
        else:
            print("Failed to extract shortcode.")  # Debugging print
            return None
    except Exception as e:
        print(f"Error fetching video URL: {e}")  # Debugging print
        return None

# Route to handle the homepage and form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST':
        instagram_url = request.form.get('url')
        print(f"Instagram URL received: {instagram_url}")  # Debugging print

        video_url = get_instagram_video_url(instagram_url)

        if video_url:
            return render_template('index.html', video_url=video_url)
        else:
            print("Failed to fetch video.")  # Debugging print
            return "Failed to fetch video. Please check the URL and try again."

    return render_template('index.html', video_url=video_url)

# Route to handle downloading the video
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
