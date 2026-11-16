"""Stand-in for the AWS instance metadata service: v1 answers anyone, v2 wants a token header."""
import http.server
import sys

PORT, MODE = int(sys.argv[1]), sys.argv[2]


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        ok = MODE == "v1" or self.headers.get("X-aws-ec2-metadata-token")
        self.send_response(200 if ok else 401)
        self.end_headers()
        self.wfile.write(b"i-0test" if ok else b"")

    def log_message(self, *args):
        pass


http.server.HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
