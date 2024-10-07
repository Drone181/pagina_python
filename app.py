from flask import Flask, request, jsonify, render_template, send_file
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
            video_url = json_data.get('src_url')
            if not video_url:
                return jsonify({"error": "No valid download URL found"}), 404

            thumbnail_url = json_data.get('picture', '')
            title = json_data.get('title', '')
            
            logging.debug(f"Video URL: {video_url}")
            logging.debug(f"Thumbnail URL: {thumbnail_url}")
            logging.debug(f"Title: {title}")
            
            return jsonify({
                "video_url": video_url, 
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
        logging.info(f"Attempting to download video from URL: {video_url}")
        
        # Stream the video content
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get the content type from the response headers
        content_type = response.headers.get('content-type', 'video/mp4')
        logging.info(f"Content-Type of the video: {content_type}")
        
        # Determine the appropriate file extension
        file_extension = 'mp4' if 'mp4' in content_type else 'mov'
        
        # Create a generator to stream the content
        def generate():
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    yield chunk
            except Exception as e:
                logging.error(f"Error while streaming video content: {str(e)}")
                raise

        # Return a streaming response
        return Response(
            generate(),
            headers={
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename=instagram_video.{file_extension}'
            }
        )
    except requests.RequestException as e:
        logging.error(f"Request exception while downloading video: {str(e)}")
        return jsonify({"error": "Failed to download video", "details": str(e)}), 500
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))