#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

PORT = int(os.environ.get('PORT', 8080))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    os.chdir('build')
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Frontend server running on port {PORT}")
        httpd.serve_forever()
