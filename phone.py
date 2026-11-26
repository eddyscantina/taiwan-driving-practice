"""Serve the Taiwan Driving Practice web app on your local Wi-Fi so you can study on your phone."""
import argparse
import functools
import socket
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import IPv4Address
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
STANDALONE = ROOT / 'Taiwan Driving Practice.html'


def detect_lan_ip():
    """Find this PC's private LAN/Wi-Fi IPv4 address without sending external traffic."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        candidate = IPv4Address(sock.getsockname()[0])
        if candidate.is_private and not candidate.is_loopback:
            return candidate
    except OSError:
        pass
    finally:
        sock.close()
    return None


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    'address',
    nargs='?',
    type=IPv4Address,
    help='Optional: this PC’s Wi-Fi IPv4 address (auto-detected if omitted)',
)
parser.add_argument('--port', type=int, default=8765, help='Local port to listen on (default: 8765)')
options = parser.parse_args()

bind_ip = options.address or detect_lan_ip()
if bind_ip is None:
    parser.error('Could not auto-detect your Wi-Fi IPv4 address. Run ipconfig and pass it explicitly, e.g. python phone.py 192.168.1.23')
if not bind_ip.is_private or bind_ip.is_unspecified:
    parser.error('Use your PC’s private Wi-Fi/LAN IPv4 address (e.g. 192.168.x.x).')

if (DIST / 'index.html').exists():
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(DIST))
    mode_label = 'fast web/PWA bundle (dist/)'
else:
    body = STANDALONE.read_bytes()

    class StandaloneHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/favicon.ico':
                self.send_response(204)
                self.end_headers()
                return
            if self.path not in ('/', '/index.html'):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(body)

    handler = StandaloneHandler
    mode_label = 'standalone HTML'

with ThreadingHTTPServer((str(bind_ip), options.port), handler) as server:
    print(f'Serving {mode_label} at http://{bind_ip}:{options.port}/', flush=True)
    print('Open that link on your phone (same Wi-Fi). Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
