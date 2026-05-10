from flask import Flask, request, jsonify, send_file
import yt_dlp
import re

app = Flask(__name__)

def get_video_url(youtube_url):
    """Extract video URL from YouTube"""
    ydl_opts = {
        'format': 'best',  # Best quality available
        'quiet': True,     # No output logs
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            # Get the direct video URL
            video_url = info.get('url') or info.get('direct')
            title = info.get('title', 'Video')
            return video_url, title
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom YouTube Player</title>
        <style>
            body { font-family: Arial; text-align: center; margin-top: 50px; }
            input { width: 500px; padding: 10px; margin: 10px; }
            button { padding: 10px 20px; cursor: pointer; }
            video { width: 80%; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Custom YouTube Player</h1>
        <input type="text" id="url" placeholder="Paste YouTube URL here...">
        <button onclick="loadVideo()">Play Video</button>
        <div>
            <video id="player" controls></video>
        </div>
        <p id="title"></p>
        
        <script>
        async function loadVideo() {
            let url = document.getElementById('url').value;
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            let response = await fetch('/get_video?url=' + encodeURIComponent(url));
            let data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            document.getElementById('player').src = data.video_url;
            document.getElementById('player').play();
            document.getElementById('title').innerText = data.title;
        }
        </script>
    </body>
    </html>
    '''

@app.route('/get_video')
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Validate YouTube URL
    if not ('youtube.com' in url or 'youtu.be' in url):
        return jsonify({'error': 'Only YouTube URLs are supported'}), 400
    
    video_url, title_or_error = get_video_url(url)
    
    if not video_url:
        return jsonify({'error': title_or_error}), 500
    
    return jsonify({
        'video_url': video_url,
        'title': title_or_error
    })

if __name__ == '__main__':
    print("Server starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
