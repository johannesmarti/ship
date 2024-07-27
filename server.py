from http.server import BaseHTTPRequestHandler, HTTPServer
import json

import responses

response = responses.base_data()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            #response = responses.base_data()
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('client/index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/scripts/bigTable.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            with open('client/scripts/bigTable.js', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

def run(handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, handler_class)
    print(f'Starting pytrade http server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
