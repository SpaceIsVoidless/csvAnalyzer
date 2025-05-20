import http.server
import socketserver
import json
from urllib.parse import parse_qs, urlparse
import os
from activity_analyzer import analyze_activity, format_output
from io import StringIO, BytesIO
import sys
import email.parser
import tempfile

class ActivityAnalyzerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_content().encode())
            
        elif parsed_path.path == '/analyze':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            old_stdout = sys.stdout
            result_output = StringIO()
            sys.stdout = result_output
            
            try:
                top_users, suspicious = analyze_activity('activity.csv')
                format_output(top_users, suspicious, 'json')
                analysis_result = result_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            self.wfile.write(analysis_result.encode())

    def do_POST(self):
        """Handle POST requests for file upload"""
        if self.path == '/upload':
            content_type = self.headers.get('Content-Type')
            if content_type and 'multipart/form-data' in content_type:
                # Get the boundary from content-type
                boundary = content_type.split('=')[1].encode()
                remainbytes = int(self.headers['content-length'])
                line = self.rfile.readline()
                remainbytes -= len(line)
                
                if not boundary in line:
                    self.send_error(400, "Bad Request: Content NOT begin with boundary")
                    return
                
                # Read the file content
                line = self.rfile.readline()
                remainbytes -= len(line)
                
                # Parse the Content-Disposition header
                fn = None
                if b'Content-Disposition' in line:
                    fn = line.decode()
                    if 'filename=' in fn:
                        fn = fn.split('filename=')[1].strip().strip('"\'')
                
                # Skip headers until we reach empty line
                while remainbytes > 0:
                    line = self.rfile.readline()
                    remainbytes -= len(line)
                    if line == b'\r\n':
                        break
                
                # Read the file content
                try:
                    with open('activity.csv', 'wb') as f:
                        while remainbytes > 0:
                            line = self.rfile.readline()
                            remainbytes -= len(line)
                            if boundary in line:
                                break
                            f.write(line)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                    return
                except Exception as e:
                    self.send_error(500, f"Internal error: {str(e)}")
                    return
            
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False}).encode())
    
    def get_html_content(self):
        """Return the HTML content for the web interface"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>Activity Analyzer Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #64B5F6;
            --secondary-color: #FFD54F;
            --background-color: #121212;
            --card-background: #1E1E1E;
            --text-color: #E0E0E0;
            --border-radius: 12px;
            --transition-speed: 0.3s;
        }

        body {
            font-family: 'Google Sans', 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--background-color);
            color: var(--text-color);
            transition: all var(--transition-speed) ease;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: var(--primary-color);
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            color: var(--text-color);
            opacity: 0.8;
            font-size: 1.2em;
        }

        .upload-section {
            background-color: var(--card-background);
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            margin-bottom: 40px;
            text-align: center;
            transition: transform var(--transition-speed);
        }

        .upload-section:hover {
            transform: translateY(-5px);
        }

        .file-upload {
            display: none;
        }

        .upload-btn {
            background-color: var(--primary-color);
            color: var(--text-color);
            padding: 15px 30px;
            border-radius: var(--border-radius);
            cursor: pointer;
            display: inline-block;
            transition: all var(--transition-speed);
            font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(100,181,246,0.3);
        }

        .upload-btn:hover {
            background-color: #90CAF9;
            transform: scale(1.05);
        }

        .refresh-btn {
            background-color: var(--secondary-color);
            color: #121212;
            padding: 15px 30px;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            margin: 20px 0;
            transition: all var(--transition-speed);
            font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(255,213,79,0.3);
        }

        .refresh-btn:hover {
            background-color: #FFE082;
            transform: scale(1.05);
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .card {
            background-color: var(--card-background);
            padding: 25px;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transition: all var(--transition-speed);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 25px rgba(0,0,0,0.3);
        }

        .card h2 {
            color: var(--primary-color);
            margin-top: 0;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            font-size: 1.8em;
        }

        .user-item, .suspicious-item {
            padding: 20px;
            margin: 15px 0;
            border-radius: var(--border-radius);
            transition: all var(--transition-speed);
            backdrop-filter: blur(5px);
        }

        .user-item {
            background-color: rgba(100,181,246,0.1);
            border: 1px solid rgba(100,181,246,0.2);
        }

        .suspicious-item {
            background-color: rgba(255,213,79,0.1);
            border: 1px solid rgba(255,213,79,0.2);
        }

        .user-item:hover, .suspicious-item:hover {
            transform: translateX(10px);
        }

        #uploadStatus {
            margin-top: 15px;
            padding: 15px;
            border-radius: var(--border-radius);
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .success {
            background-color: rgba(76,175,80,0.2);
            color: #81C784;
            border: 1px solid rgba(76,175,80,0.3);
        }

        .error {
            background-color: rgba(244,67,54,0.2);
            color: #E57373;
            border: 1px solid rgba(244,67,54,0.3);
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2.2em;
            }
            
            .card {
                padding: 20px;
            }
            
            .upload-btn, .refresh-btn {
                width: 100%;
                margin: 10px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Activity Analyzer Dashboard</h1>
            <p>Upload and analyze user activity data</p>
        </div>

        <div class="upload-section">
            <input type="file" id="fileUpload" class="file-upload" accept=".csv">
            <label for="fileUpload" class="upload-btn">Choose CSV File</label>
            <div id="uploadStatus"></div>
            <button class="refresh-btn" onclick="refreshData()" style="font-family: 'Google Sans', 'Segoe UI', Arial, sans-serif;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 5px; vertical-align: text-bottom;">
                    <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                    <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                </svg>
                Refresh
            </button>
        </div>

        <div class="dashboard">
            <div class="card">
                <h2>Top 5 Users by Action Count</h2>
                <div id="topUsers"></div>
            </div>
            
            <div class="card">
                <h2>Suspicious Activities</h2>
                <div id="suspiciousActivities"></div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('fileUpload').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('file', file);

                const status = document.getElementById('uploadStatus');
                status.style.display = 'block';
                status.innerHTML = 'Uploading...';
                status.className = '';

                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        status.innerHTML = 'File uploaded successfully!';
                        status.className = 'success';
                        refreshData();
                    } else {
                        status.innerHTML = 'Upload failed. Please try again.';
                        status.className = 'error';
                    }
                })
                .catch(error => {
                    status.innerHTML = 'Upload failed. Please try again.';
                    status.className = 'error';
                });
            }
        });

        function refreshData() {
            const status = document.getElementById('uploadStatus');
            status.style.display = 'block';
            status.innerHTML = 'Analyzing data...';
            status.className = '';

            fetch('/analyze')
                .then(response => response.json())
                .then(data => {
                    const topUsersHtml = data.top_users
                        .map(user => `<div class="user-item">${user.username} (${user.user_id}): ${user.count} actions</div>`)
                        .join('');
                    document.getElementById('topUsers').innerHTML = topUsersHtml;
                    
                    const suspiciousHtml = data.suspicious_activities
                        .map(activity => `
                            <div class="suspicious-item">
                                ${activity.username} (${activity.user_id}) performed '${activity.action}' 
                                suspiciously at ${new Date(activity.timestamp).toLocaleString()}
                            </div>
                        `)
                        .join('');
                    document.getElementById('suspiciousActivities').innerHTML = suspiciousHtml;

                    status.innerHTML = 'Analysis completed successfully!';
                    status.className = 'success';
                    setTimeout(() => {
                        status.style.display = 'none';
                    }, 3000);
                })
                .catch(error => {
                    status.innerHTML = 'Analysis failed. Please try again.';
                    status.className = 'error';
                });
        }
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
'''

def run_server(port=8000):
    with socketserver.TCPServer(("", port), ActivityAnalyzerHandler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()