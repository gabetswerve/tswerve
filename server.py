import http.server
import socketserver
import webbrowser
import sys

PORT = 8000
MAX_PORT_ATTEMPTS = 10

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Disable caching to make development edits immediately visible on refresh
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

for attempt in range(MAX_PORT_ATTEMPTS):
    current_port = PORT + attempt
    try:
        # Bind to localhost (127.0.0.1)
        httpd = socketserver.TCPServer(("127.0.0.1", current_port), NoCacheHTTPRequestHandler)
        
        print("\n" + "=" * 50)
        print(f"🚀 T Swerve Local Server successfully started!")
        print(f"🔗 Local URL: http://localhost:{current_port}")
        print("=" * 50)
        print("Press Ctrl+C to stop the server.\n")
        
        # Automatically open the browser
        webbrowser.open(f"http://localhost:{current_port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server. Goodbye!")
            httpd.server_close()
            sys.exit(0)
            
    except OSError as e:
        # Error 48 is 'Address already in use' on macOS
        if e.errno == 48:
            print(f"⚠️ Port {current_port} is already in use, trying next port...")
            continue
        else:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
else:
    print("❌ Could not find an available port to start the server.")
    sys.exit(1)
