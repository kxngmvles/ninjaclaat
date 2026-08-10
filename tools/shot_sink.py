"""Tiny sink so a preview page can hand its rendered frame back to disk.

The browser can render the scene but can't write a file, and a full-res data
URL is too big to pull back through the tool channel. The page POSTs its JPEG
data URL here and this writes it out as _shot_<name>.jpg.
"""
import base64, http.server, os, re, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", q.get("name", ["shot"])[0])[:60]
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        data = base64.b64decode(body.split(",", 1)[-1])
        open(os.path.join(REPO, f"_shot_{name}.jpg"), "wb").write(data)
        self.send_response(200); self._cors(); self.end_headers()
        self.wfile.write(b"ok")
        print(f"_shot_{name}.jpg  {len(data)} bytes", flush=True)

    def log_message(self, *a):
        pass

http.server.HTTPServer(("127.0.0.1", 8799), H).serve_forever()
