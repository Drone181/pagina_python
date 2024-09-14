from flask import Flask, request, render_template, redirect
import logging
from urllib.parse import quote

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_downloader_link(instagram_url):
    # Using a reliable third-party Instagram downloader
    base_url = "https://www.instagramsave.com/download-instagram-videos.php"
    encoded_url = quote(instagram_url)
    return f"{base_url}?url={encoded_url}"

@app.route('/', methods=['GET', 'POST'])
def index():
    downloader_link = None
    if request.method == 'POST':
        instagram_url = request.form.get('url')
        logging.info(f"Received Instagram URL: {instagram_url}")
        if instagram_url:
            downloader_link = get_downloader_link(instagram_url)
            logging.info(f"Generated downloader link: {downloader_link}")
        else:
            logging.warning("No Instagram URL provided")
            return "Please provide an Instagram URL."
    return render_template('index.html', downloader_link=downloader_link)

if __name__ == '__main__':
    app.run(debug=True)