from flask import Flask, request, render_template_string
import requests
import re
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Custom YouTube Player</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', sans-serif;
            padding: 20px;
        }
        .player-card {
            max-width: 1000px;
            width: 100%;
            background: rgba(0,0,0,0.85);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }
        h1 {
            text-align: center;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #ff6a00, #ee0979);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 32px;
        }
        .input-group {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .url-input {
            flex: 1;
            padding: 14px 18px;
            font-size: 16px;
            border: none;
            border-radius: 50px;
            background: #2a2a2a;
            color: white;
            outline: none;
        }
        .load-btn {
            padding: 14px 28px;
            background: #ff6a00;
            border: none;
            border-radius: 50px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        video {
            width: 100%;
            border-radius: 16px;
            margin-top: 20px;
        }
        .video-title {
            color: white;
            text-align: center;
            margin-top: 15px;
        }
        .error { color: #ff4444; text-align: center; margin-top: 20px; }
        .loading { color: #ffaa00; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="player-card">
        <h1>🎬 CUSTOM YOUTUBE PLAYER</h1>
        <div class="input-group">
            <input type="text" id="youtubeUrl" class="url-input" placeholder="Paste YouTube URL here...">
            <button class="load-btn" onclick="loadVideo()">▶ LOAD & PLAY</button>
        </div>
        <div id="loading" class="loading" style="display:none;">Loading video... Please wait ⏳</div>
        <div id="error" class="error"></div>
        <div id="videoContainer" style="display:none;">
            <video id="myPlayer" controls autoplay></video>
            <div id="videoTitle" class="video-title"></div>
        </div>
    </div>
    <script>
        async function loadVideo() {
            let url = document.getElementById('youtubeUrl').value.trim();
            if (!url) { alert('Please enter a YouTube URL!'); return; }
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').innerHTML = '';
            document.getElementById('videoContainer').style.display = 'none';
            try {
                let response = await fetch('/get_video?url=' + encodeURIComponent(url));
                let data = await response.json();
                if (data.error) {
                    document.getElementById('error').innerHTML = '❌ ' + data.error;
                } else {
                    document.getElementById('myPlayer').src = data.video_url;
                    document.getElementById('videoTitle').innerHTML = '🎵 ' + data.title;
                    document.getElementById('videoContainer').style.display = 'block';
                }
            } catch(e) {
                document.getElementById('error').innerHTML = '❌ Network error';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        document.getElementById('youtubeUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') loadVideo();
        });
    </script>
</body>
</html>
'''

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_video')
def get_video():
    url = request.args.get('url')
    if not url:
        return {'error': 'No URL provided'}, 400
    
    video_id = get_video_id(url)
    if not video_id:
        return {'error': 'Invalid YouTube URL'}, 400
    
    # Piped API se video stream URL lete hain
    try:
        # Piped ka public instance
        api_url = f'https://pipedapi.kavin.rocks/streams/{video_id}'
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if 'videoStreams' in data and len(data['videoStreams']) > 0:
            # Best quality stream lelo (usually last wala best hota hai)
            video_url = data['videoStreams'][-1]['url']
            title = data.get('title', 'Video')
            return {'video_url': video_url, 'title': title}
        else:
            return {'error': 'No video streams found'}, 500
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
