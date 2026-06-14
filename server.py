#!/usr/bin/env python3
"""
学术雷达 — 简易 Web 服务器
"""
import http.server, json, os, sys, urllib.parse

PORT = 8081
PUBLIC_DIR = os.path.dirname(__file__)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        # Serve index.html for root
        if parsed.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def log_message(self, format, *args):
        if len(args) >= 3:
            print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")
        else:
            print(f"[{self.log_date_time_string()}] {format % args if args else format}")

if __name__ == '__main__':
    os.chdir(PUBLIC_DIR)
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Academic Radar started: http://localhost:{PORT}")
    print(f"   按 Ctrl+C 停止")
    httpd = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
