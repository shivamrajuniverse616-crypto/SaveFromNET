import os
import time
from flask import Flask, request, jsonify, send_file, render_template, after_this_request
from flask_cors import CORS
from yt_dlp import YoutubeDL

# Initialize the Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow requests from different origins
CORS(app)

# Define the folder where downloads will be stored
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
# Create the download directory if it doesn't already exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Define the route for the home page
@app.route('/')
def index():
    # Render and return the index.html template
    return render_template('index.html')

# Define the route to get video information, accepting POST requests
@app.route('/get_info', methods=['POST'])
def get_info():
    # Parse the JSON data from the request
    data = request.get_json()
    # Extract the 'url' from the data
    url = data.get('url')
    
    # If URL is missing, return an error with 400 Bad Request status
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Configuration options for yt-dlp
        ydl_opts = {
            'quiet': True,              # Suppress stdout output
            'no_warnings': True,        # Suppress warnings
            'skip_download': True,      # Do not download the video, just fetch info
            'force_ipv4': True,         # Force IPv4 to avoid IPv6 connection issues
            'proxy': '',                # Force no proxy to avoid local environment issues
            # Use a mobile user agent to mimic the app/mobile site which often has looser restrictions
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            # Allow unplayable formats to be listed so we can filter them out later if needed, 
            # though usually we want to avoid them. 
            # 'ignoreerrors': True, 
        }
        
        # Use YoutubeDL as a context manager
        with YoutubeDL(ydl_opts) as ydl:
            # Extract video information without downloading. Throws exception if fails.
            info = ydl.extract_info(url, download=False)
            
            formats = []
            seen_resolutions = set()
            # Iterate over available formats
            for f in info.get('formats', []):
                res = f.get('height')
                # Check if resolution exists (filter for video formats)
                if res:
                    res_str = f"{res}p"
                    # Add unique resolutions to the list
                    if res_str not in seen_resolutions:
                        formats.append({
                            'format_id': f['format_id'],
                            'resolution': res_str,
                            'ext': f.get('ext', 'mp4')
                        })
                        seen_resolutions.add(res_str)
            
            # Sort formats by resolution (descending) for better UX
            formats.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'][:-1].isdigit() else 0, reverse=True)

            # Construct the response dictionary
            video_details = {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration'),
                'formats': formats,
                'webpage_url': info.get('webpage_url', url) 
            }
            # Return the video details as JSON
            return jsonify(video_details)
            
    except Exception as e:
        # Log the error to the console
        print(f"Error fetching info: {e}") 
        import traceback
        traceback.print_exc()
        # Return the error message with 500 Internal Server Error status
        return jsonify({'error': str(e)}), 500

# Define the route using POST to handle video downloads
@app.route('/download', methods=['POST'])
def download_video():
    # Get JSON payload
    data = request.get_json()
    url = data.get('url')
    # quality can be a format_id or 'best', default to 'best'
    quality = data.get('quality', 'best') 
    
    # Validation
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Generate a unique filename prefix using current timestamp to avoid collisions
        timestamp = int(time.time())
        filename_tmpl = f"{timestamp}_%(title)s.%(ext)s"
        
        # yt-dlp configuration for downloading
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, filename_tmpl), # Output template
            'quiet': True,
            'no_warnings': True,
            'force_ipv4': True,
            'proxy': '', # Force no proxy
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        # Logic for handling quality selection
        if quality == 'best':
            # Download best video and best audio and merge them
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            # If user selected a specific format_id
            # Try to download that video format and merge with best audio
            ydl_opts['format'] = f"{quality}+bestaudio/best"
            ydl_opts['merge_output_format'] = 'mp4'

        # Execute download
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Determine the final filename
            filename = ydl.prepare_filename(info)
            
            # Check if using 'requested_downloads' gives a more accurate path (common with merges)
            if 'requested_downloads' in info:
                filepath = info['requested_downloads'][0]['filepath']
            else:
                filepath = filename
            
            # Additional check to ensure correct extension if merged to mp4
            # because sometimes the file extension changes after merge
            base, _ = os.path.splitext(filepath)
            if ydl_opts.get('merge_output_format') == 'mp4' and not filepath.endswith('.mp4'):
                 possible_path = base + '.mp4'
                 if os.path.exists(possible_path):
                     filepath = possible_path
 
            filename_only = os.path.basename(filepath)
            
            # Return success status and the local download URL
            return jsonify({
                'status': 'success',
                'download_url': f"/downloads/{filename_only}"
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to serve the downloaded file to the user
@app.route('/downloads/<filename>')
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Register a function to run after the request is complete
    @after_this_request
    def remove_file(response):
        try:
            # Delete the file from the server to save space and maintain privacy
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            app.logger.error(f"Error removing file: {e}")
        return response

    # Send the file to the client as an attachment (triggers download)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, port=5000)
