#!/usr/bin/env python3
"""
Sonar Scanner Runner - Backend Server
A simple HTTP server to handle Sonar Scanner execution requests.
"""

import os
import sys
import json
import logging
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import time

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'server.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variable to store active scans
active_scans = {}
scan_lock = threading.Lock()


class SonarScannerHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Sonar Scanner operations"""

    def _set_headers(self, content_type='text/html', status=200):
        """Set HTTP response headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._set_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/' or path == '/index.html':
            self._serve_file('../frontend/index.html', 'text/html')
        elif path.startswith('/static/'):
            self._serve_static_file(path)
        elif path == '/api/status':
            self._handle_status()
        elif path.startswith('/api/scan/'):
            scan_id = path.replace('/api/scan/', '')
            self._handle_scan_result(scan_id)
        else:
            self._set_headers(status=404)
            self.wfile.write(b'404 - Not Found')

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/scan':
            self._handle_scan()
        else:
            self._set_headers(status=404)
            self.wfile.write(b'404 - Not Found')

    def _serve_file(self, filepath, content_type):
        """Serve a file from the filesystem"""
        try:
            full_path = os.path.join(os.path.dirname(__file__), filepath)
            with open(full_path, 'rb') as f:
                content = f.read()
            self._set_headers(content_type)
            self.wfile.write(content)
        except FileNotFoundError:
            self._set_headers(status=404)
            self.wfile.write(b'404 - File Not Found')
        except Exception as e:
            logger.error(f"Error serving file {filepath}: {e}")
            self._set_headers(status=500)
            self.wfile.write(b'500 - Internal Server Error')

    def _serve_static_file(self, path):
        """Serve static files (CSS, JS)"""
        file_path = path.replace('/static/', '../frontend/static/')

        if path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        else:
            content_type = 'text/plain'

        self._serve_file(file_path, content_type)

    def _handle_status(self):
        """Handle status check requests"""
        self._set_headers('application/json')
        response = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'active_scans': len(active_scans)
        }
        self.wfile.write(json.dumps(response).encode())

    def _handle_scan_result(self, scan_id):
        """Handle scan result retrieval requests"""
        with scan_lock:
            if scan_id not in active_scans:
                self._set_headers('application/json', status=404)
                response = {
                    'status': 'error',
                    'message': f'Scan ID {scan_id} not found'
                }
                self.wfile.write(json.dumps(response).encode())
                return

            scan_data = active_scans[scan_id].copy()

        self._set_headers('application/json')
        response = {
            'status': 'success',
            'scan_id': scan_id,
            'scan_status': scan_data['status'],
            'output': scan_data['output'],
            'start_time': scan_data.get('start_time'),
            'end_time': scan_data.get('end_time'),
            'return_code': scan_data.get('return_code')
        }
        self.wfile.write(json.dumps(response).encode())

    def _handle_scan(self):
        """Handle scan execution requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            repo_name = data.get('repository_name', '').strip()
            branch_name = data.get('branch_name', '').strip()
            release_version = data.get('release_version', '').strip()

            # Validate input
            if not all([repo_name, branch_name, release_version]):
                self._send_error_response('All fields are required')
                return

            # Generate scan ID
            scan_id = f"{repo_name}_{branch_name}_{int(time.time())}"

            # Start scan in background thread
            scan_thread = threading.Thread(
                target=self._execute_scan,
                args=(scan_id, repo_name, branch_name, release_version)
            )
            scan_thread.daemon = True
            scan_thread.start()

            self._set_headers('application/json')
            response = {
                'status': 'success',
                'message': 'Scan started successfully',
                'scan_id': scan_id
            }
            self.wfile.write(json.dumps(response).encode())

        except json.JSONDecodeError:
            self._send_error_response('Invalid JSON data')
        except Exception as e:
            logger.error(f"Error handling scan request: {e}")
            self._send_error_response(f'Internal server error: {str(e)}')

    def _send_error_response(self, message):
        """Send an error response"""
        self._set_headers('application/json', status=400)
        response = {
            'status': 'error',
            'message': message
        }
        self.wfile.write(json.dumps(response).encode())

    def _execute_scan(self, scan_id, repo_name, branch_name, release_version):
        """Execute the Sonar Scanner scan"""
        with scan_lock:
            active_scans[scan_id] = {
                'status': 'running',
                'output': [],
                'start_time': datetime.now().isoformat()
            }

        try:
            logger.info(f"Starting scan {scan_id} for {repo_name}/{branch_name} v{release_version}")

            # Call the scan script
            script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'run_sonar_scan.py')

            process = subprocess.Popen(
                [sys.executable, script_path, repo_name, branch_name, release_version],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Capture output line by line
            for line in iter(process.stdout.readline, ''):
                if line:
                    with scan_lock:
                        active_scans[scan_id]['output'].append(line.strip())
                    logger.info(f"[{scan_id}] {line.strip()}")

            process.wait()

            with scan_lock:
                active_scans[scan_id]['status'] = 'completed' if process.returncode == 0 else 'failed'
                active_scans[scan_id]['return_code'] = process.returncode
                active_scans[scan_id]['end_time'] = datetime.now().isoformat()

            logger.info(f"Scan {scan_id} completed with return code {process.returncode}")

        except Exception as e:
            logger.error(f"Error executing scan {scan_id}: {e}")
            with scan_lock:
                active_scans[scan_id]['status'] = 'error'
                active_scans[scan_id]['output'].append(f"Error: {str(e)}")

    def log_message(self, format, *args):
        """Override to use custom logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")


def run_server(host='0.0.0.0', port=8080):
    """Start the HTTP server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, SonarScannerHandler)

    logger.info(f"Starting Sonar Scanner Server on http://{host}:{port}")
    logger.info(f"Access the web interface at http://localhost:{port}")
    logger.info("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        httpd.shutdown()
        logger.info("Server stopped.")


if __name__ == '__main__':
    # Get port from command line argument or use default
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    run_server(port=port)
