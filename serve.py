import http.server
import socketserver
import os
import webbrowser
import sys

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DualStackServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        """Serve the app's existing root-relative assets from benchtwin.com.

        The original page lives at /benchtwin.com/index.html but uses a few
        root-relative URLs (for example /fonts and /about).  Mapping only
        those paths keeps every original file in place and makes the local
        server behave the same way as the deployed site.
        """
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        aliases = {
            '/favicon.ico': '/benchtwin.com/favicon40db.ico',
            '/favicon.svg': '/benchtwin.com/favicon40db.svg',
            '/apple-touch-icon.png': '/benchtwin.com/apple-touch-icon40db.png',
            '/icon-192.png': '/benchtwin.com/icon-19240db.png',
        }
        clean_path = aliases.get(clean_path, clean_path)
        root_folders = ('/about/', '/privacy/', '/terms/', '/fonts/', '/img/', '/js/', '/src/', '/TeamCode/', '/.netlify/')
        root_files = ('/theme-midnight.css', '/site.webmanifest')
        if clean_path in root_files or clean_path.startswith(root_folders):
            clean_path = '/benchtwin.com' + clean_path
        return super().translate_path(clean_path)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_server(preferred_ports=(8000, 8080, 3000, 8081)):
    # Render supplies PORT and requires the service to accept public traffic.
    # Local development keeps the existing localhost-only behaviour and URL.
    render_port = os.environ.get('PORT')
    host = '0.0.0.0' if render_port else '127.0.0.1'
    httpd = None
    actual_port = None
    ports = (int(render_port),) if render_port else preferred_ports
    for port in ports:
        try:
            httpd = DualStackServer((host, port), Handler)
            actual_port = port
            break
        except OSError:
            continue

    if httpd is None:
        # Bind to any available ephemeral port
        httpd = DualStackServer((host, 0), Handler)
        actual_port = httpd.server_address[1]

    url_host = '127.0.0.1' if not render_port else host
    url = f"http://{url_host}:{actual_port}/benchtwin.com/index.html"
    print("=" * 60)
    print("  Build2Real Local Development Server")
    print("=" * 60)
    print(f"  Website URL: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)

    if not render_port:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
