"""Serve a generated report.html on localhost and print the URL.

Usage: python3 serve_report.py <path_to_report.html_or_its_dir> [port]

Picks a free port if none given, serves the containing directory (so
relative assets next to report.html still load), and opens the default
browser. Runs in the foreground -- Ctrl+C to stop.
"""
import http.server
import os
import socket
import socketserver
import sys
import webbrowser


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    if len(sys.argv) < 2:
        print("usage: python3 serve_report.py <report.html_or_dir> [port]", file=sys.stderr)
        sys.exit(1)
    target = os.path.abspath(sys.argv[1])
    directory = target if os.path.isdir(target) else os.path.dirname(target)
    filename = "" if os.path.isdir(target) else os.path.basename(target)
    port = int(sys.argv[2]) if len(sys.argv) > 2 else free_port()

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=directory, **kw)
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://localhost:{port}/{filename}"
        print(f"Serving {directory} at {url}  (Ctrl+C to stop)")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
