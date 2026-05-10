from flask import Flask, request, render_template_string
import yt_dlp as youtube_dl
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Custom YouTube Player</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }

        .player-card {
            max-width: 1000px;
            width: 100%;
            background: rgba(0,0,0,0.85);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
            transition: transform 0.3s;
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #ff6a00, #ee0979);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 32px;
            letter-spacing: 1px;
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
            transition: 0.2s;
        }

        .url-input:focus {
            background: #3a3a3a;
            box-shadow: 0 0 0 2px #ff6a00;
        }

        .load-btn {
            padding: 14px 28px;
            background: #ff6a00;
            border: none;
            border-radius: 50px;
            color: white;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .load-btn:hover {
            background: #ee0979;
            transform: scale(1.02);
        }

        .video-container {
            margin-top: 20px;
        }

        video {
            width: 100%;
            border-radius: 16px;
            background: black;
            outline: none;
        }

        .video-title {
            color: white;
            text-align: center;
            margin-top: 15px;
            font-size: 18px;
            word-break: break-word;
        }

        .loading, .error {
            text-align: center;
            margin-top: 20px;
            font-size: 16px;
        }

        .loading {
            color: #ffaa00;
        }

        .error {
            color: #ff4444;
        }
    </style>
</head>
<body>
    <div class="player-card">
        <h1>🎬 CUSTOM YOUTUBE PLAYER</h1>
        
        <div class="input-group">
            <input type="text" id="youtubeUrl" class="url-input" placeholder="Paste YouTube URL here... (e.g., https://youtu.be/... or https://youtube.com/...)">
            <button class="load-btn" onclick="loadVideo()">▶ LOAD & PLAY</button>
        </div>
        
        <div id="loading" class="loading" style="display:none;">Fetching video... Please wait ⏳</div>
        <div id="error" class="error"></div>
        
        <div id="videoContainer" style="display:none;">
            <div class="video-container">
                <video id="myPlayer" controls autoplay></video>
            </div>
            <div id="videoTitle" class="video-title"></div>
        </div>
    </div>

    <script>
        async function loadVideo() {
            let url = document.getElementById('youtubeUrl').value.trim();
            if (!url) {
                alert('Please enter a YouTube URL first!');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').innerHTML = '';
            document.getElementById('videoContainer').style.display = 'none';
            
            try {
                let response = await fetch('/get_video?url=' + encodeURIComponent(url));
                let data = await response.json();
                
                if (data.error) {
                    document.getElementById('error').innerHTML = '❌ ' + data.error;
                } else {
                    let video = document.getElementById('myPlayer');
                    video.src = data.video_url;
                    document.getElementById('videoTitle').innerHTML = '🎵 ' + data.title;
                    document.getElementById('videoContainer').style.display = 'block';
                }
            } catch(e) {
                document.getElementById('error').innerHTML = '❌ Network error: ' + e.message;
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        // Enter key support
        document.getElementById('youtubeUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') loadVideo();
        });
    </script>
</body>
</html>
'''
def get_video_info(youtube_url):
    """Extract video URL and title from YouTube"""
    ydl_opts = {
        'format': 'best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sleep_interval': 3,  # Har request ke beech 3 second ka gap
        'max_sleep_interval': 5,
        'sleep_interval_requests': 2,
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info.get('url'), info.get('title')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_video')
def get_video():
    url = request.args.get('url')
    if not url:
        return {'error': 'No URL provided'}, 400
    
    # Simple YouTube URL validation
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return {'error': 'Only YouTube URLs are supported'}, 400
    
    try:
        video_url, title = get_video_info(url)
        if not video_url:
            return {'error': 'Could not extract video URL'}, 500
        return {
            'video_url': video_url,
            'title': title
        }
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
