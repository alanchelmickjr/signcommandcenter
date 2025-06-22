#!/usr/bin/env python3
"""
HTTPS server for ASL Command Center
Enables camera permissions and PWA installation
"""

import http.server
import ssl
import socketserver
import os
import sys
import argparse

# Default port
DEFAULT_PORT = 8443
Handler = http.server.SimpleHTTPRequestHandler

class CustomHTTPRequestHandler(Handler):
    def end_headers(self):
        # Add security headers for PWA
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Permissions-Policy', 'camera=*, microphone=*, geolocation=*')
        super().end_headers()

def run_https_server(port=DEFAULT_PORT):
    print(f"🔒 Starting HTTPS server on port {port}")
    print(f"📱 App will be available at: https://localhost:{port}")
    print("⚠️  You'll need to accept the self-signed certificate")
    
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('cert.pem', 'key.pem')
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"✅ HTTPS Server started at https://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start HTTPS server for ASL Command Center')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to run server on (default: {DEFAULT_PORT})')
    args = parser.parse_args()
    
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("❌ SSL certificates not found. Generating self-signed certificates...")
        os.system('openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=CA/L=Berkeley/O=ASL Command Center/OU=Cal Hacks 2025/CN=localhost"')
        if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
            print("❌ Failed to generate certificates. Please install OpenSSL or create certificates manually.")
            sys.exit(1)
        print("✅ Self-signed certificates generated")
    
    run_https_server(args.port)
