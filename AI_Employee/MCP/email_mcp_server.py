# Email MCP Server - Silver Tier
# Simple HTTP server for email operations

import os
import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
LOG_FILE = os.path.join(LOGS_DIR, 'email_log.txt')


class EmailHandler(BaseHTTPRequestHandler):
    """Handle email MCP requests."""
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/send_email':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                to = data.get('to', '')
                subject = data.get('subject', '')
                body_text = data.get('body', '')
                
                # Simulate send - log to console and file
                log_entry = f"[{datetime.now().isoformat()}] To: {to} | Subject: {subject} | Body: {body_text}\n"
                print(log_entry.strip())
                
                # Ensure Logs directory exists
                os.makedirs(LOGS_DIR, exist_ok=True)
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                logger.info("Email simulated successfully")
                
                # Return response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps({"status": "simulated"})
                self.wfile.write(response.encode())
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_server():
    """Run the email MCP server."""
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, EmailHandler)
    logger.info("Email MCP Server running on http://localhost:8000")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
