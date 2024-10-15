""" from flask import Flask, request, jsonify, render_template, send_file, redirect
import http.client
import json
import os
from urllib.parse import quote, unquote
import logging
import requests
from io import BytesIO
import re
import traceback
from flask import Response, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

API_KEY = os.environ.get('RAPIDAPI_KEY', '72ea23ea89mshf6775ef3b0dde3cp1c8da5jsn0d645a94c48c')

def is_instagram_url(url):
    # Regular expression to match Instagram URLs
    instagram_regex = r'^https?:\/\/(www\.)?instagram\.com\/(p|reel|tv)\/[\w-]+\/?'
    return re.match(instagram_regex, url) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_video():
    instagram_url = request.json.get('url')
    if not instagram_url:
        return jsonify({"error": "No URL provided"}), 400

    if not is_instagram_url(instagram_url):
        return jsonify({"error": "Invalid Instagram URL"}), 400

    url = "https://social-media-video-downloader.p.rapidapi.com/smvd/get/instagram"

    querystring = {"url": instagram_url}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "social-media-video-downloader.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
        json_data = response.json()
        
        logging.debug(f"API Response Status: {response.status_code}")
        logging.debug(f"API Response Data: {json_data}")
        
        if json_data.get('success') == True:
            # Extract the correct download URL from the 'links' array
            download_url = None
            for link in json_data.get('links', []):
                if link.get('quality') == 'video_0':
                    download_url = link.get('link')
                    break
            
            if not download_url:
                return jsonify({"error": "No valid download URL found"}), 404

            thumbnail_url = json_data.get('picture', '')
            title = json_data.get('title', '')
            
            logging.debug(f"Download URL: {download_url}")
            logging.debug(f"Thumbnail URL: {thumbnail_url}")
            logging.debug(f"Title: {title}")
            
            return jsonify({
                "video_url": download_url, 
                "thumbnail_url": thumbnail_url,
                "title": title
            })
        elif 'error' in json_data:
            logging.error(f"API returned an error: {json_data['error']}")
            return jsonify({"error": "API returned an error"}), 500
        else:
            logging.error(f"Unexpected API response structure: {json_data}")
            return jsonify({"error": "Unexpected API response structure"}), 500
    except requests.RequestException as e:
        logging.error(f"Error communicating with API: {e}")
        return jsonify({"error": str(e)}), 500
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error: {e}")
        return jsonify({"error": "Invalid JSON response from API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Redirect to the correct download URL
        return redirect(video_url)
    except Exception as e:
        logging.error(f"Unexpected error in download_video: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route('/api/thumbnail')
def get_thumbnail():
    thumbnail_url = request.args.get('url')
    if not thumbnail_url:
        return jsonify({"error": "No thumbnail URL provided"}), 400

    try:
        # Decode the URL if it's encoded
        decoded_url = unquote(thumbnail_url)
        response = requests.get(decoded_url)
        response.raise_for_status()
        
        return send_file(
            BytesIO(response.content),
            mimetype='image/jpeg'
        )
    except requests.RequestException as e:
        logging.error(f"Error fetching thumbnail: {e}")
        return jsonify({"error": "Failed to fetch thumbnail"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) """

from flask import Flask, request, jsonify, render_template, send_file, redirect
import requests
import logging
import os
from urllib.parse import unquote
import re
from io import BytesIO

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

API_KEY = os.environ.get('RAPIDAPI_KEY', '72ea23ea89mshf6775ef3b0dde3cp1c8da5jsn0d645a94c48c')

def is_instagram_url(url):
    instagram_regex = r'^https?:\/\/(www\.)?instagram\.com\/(p|reel|tv)\/[\w-]+\/?'
    return re.match(instagram_regex, url) is not None

def is_video_link(link):
    video_indicators = ['video', '.mp4', 'dashvideo']
    return any(indicator in link.lower() for indicator in video_indicators)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_video():
    instagram_url = request.json.get('url')
    if not instagram_url or not is_instagram_url(instagram_url):
        return jsonify({"error": "Invalid or missing Instagram URL"}), 400

    url = "https://social-media-video-downloader.p.rapidapi.com/smvd/get/instagram"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "social-media-video-downloader.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params={"url": instagram_url})
        response.raise_for_status()
        json_data = response.json()

        logging.debug(f"API Response: {json_data}")

        if json_data.get('success') == True:
            download_url = None
            for link in json_data.get('links', []):
                logging.debug(f"Link: {link}")
                if 'link' in link and link['link'].startswith('http') and is_video_link(link['link']):
                    download_url = link['link']
                    break
            
            if not download_url:
                logging.error("No valid video download URL found in API response")
                return jsonify({"error": "No valid video download URL found in API response"}), 404

            return jsonify({
                "video_url": download_url, 
                "thumbnail_url": json_data.get('picture', ''),
                "title": json_data.get('title', '')
            })
        else:
            error_message = json_data.get('error', 'Unknown error')
            logging.error(f"API Error: {error_message}")
            return jsonify({"error": f"API returned an error: {error_message}"}), 500
    except requests.RequestException as e:
        logging.error(f"Request Error: {str(e)}")
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unexpected Error: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Redirect to the download URL
    return redirect(video_url)

@app.route('/api/thumbnail')
def get_thumbnail():
    thumbnail_url = request.args.get('url')
    if not thumbnail_url:
        return jsonify({"error": "No thumbnail URL provided"}), 400

    try:
        response = requests.get(unquote(thumbnail_url))
        response.raise_for_status()
        return send_file(
            BytesIO(response.content),
            mimetype='image/jpeg'
        )
    except requests.RequestException as e:
        logging.error(f"Error fetching thumbnail: {str(e)}")
        return jsonify({"error": "Failed to fetch thumbnail"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))