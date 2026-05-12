import logging
import sys
import time
from flask import request, g

def setup_logger():
    """Configures the root logger to ensure a consistent output format across the app."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def attach_request_logger(app):
    """Attaches before/after request hooks to log request method, path, and latency."""
    logger = logging.getLogger("request_logger")

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        if request.path == '/favicon.ico':
            return response

        latency = time.time() - g.start_time
        status_code = response.status_code
        
        logger.info(
            f"{request.method} {request.path} - Status: {status_code} | "
            f"Latency: {latency:.4f}s | "
            f"Client: {request.remote_addr}"
        )
        return response
