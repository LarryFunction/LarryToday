"""Public read-only news server. Updates are performed through a local CLI/cron."""
import json
import os
import re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
from scripts.site_payloads import merged_sources

ROOT = Path(__file__).parent.resolve()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path.startswith('/api/') and path.endswith('.json'):
            path = path[:-5]
        routes = {'/':'public/index.html','/app.js':'public/app.js','/style.css':'public/style.css','/api/news':'data/latest.json','/api/archive':'data/archive.json','/api/sources':'srcs/sources.json','/api/status':'data/last-update.json'}
        target = routes.get(path)
        if path=='/api/sources':
            return self.send_body(json.dumps(merged_sources(ROOT),ensure_ascii=False).encode(),'application/json')
        extras={'/api/source-health':'data/source-health.json','/api/social-status':'data/social-status.json','/api/social-posts':'data/social-posts.json'}
        target=extras.get(path,target)
        match=re.fullmatch(r'/api/revisions/(\d{4}-\d{2}-\d{2})(?:/(\d+))?',path)
        if match:
            day,rev=match.groups()
            target=f'data/revisions/{day}/{rev or "index"}.json'
            if not (ROOT/target).exists() and rev is None:
                old=ROOT/f'data/editions/{day}.json'
                if old.exists(): return self.send_body(json.dumps([{'revision':1,'note':'初版（旧格式）'}]).encode(),'application/json')
                return self.send_error(404)
            if rev=='1' and not (ROOT/target).exists(): target=f'data/editions/{day}.json'
        if re.fullmatch(r'/api/editions/\d{4}-\d{2}-\d{2}',path): target = 'data/editions/'+path.rsplit('/',1)[1]+'.json'
        if path == '/health': return self.send_body(b'{"ok":true}', 'application/json')
        if not target: return self.send_error(404)
        file = ROOT/target
        if not file.exists():
            if path == '/api/news': return self.send_body(b'{"mode":"empty","articles":[]}', 'application/json')
            if path == '/api/archive': return self.send_body(b'[]','application/json')
            return self.send_error(404)
        mime = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json'}[file.suffix]
        self.send_body(file.read_bytes(),mime)

    def send_body(self, body, mime):
        self.send_response(200)
        self.send_header('Content-Type',mime+'; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    port = int(os.environ.get('PORT','8000'))
    print(f'LarryToday: http://localhost:{port}', flush=True)
    ThreadingHTTPServer((os.environ.get('HOST','127.0.0.1'),port),Handler).serve_forever()
