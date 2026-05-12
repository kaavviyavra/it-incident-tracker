import os
from flask import Flask
from dotenv import load_dotenv
from services.logger_setup import setup_logger, attach_request_logger

# 1. Load all configurations and blueprints
from routes.incidents import incidents_bp
from routes.batch import batch_bp
from routes.insights import insights_bp
from routes.ai import ai_bp
from routes.sop import sop_bp

# Config runtime environment
load_dotenv()

def create_app():
    # Initialize Global Logging Format
    setup_logger()
    
    # Create standard Flask Application instance
    app = Flask(__name__)

    # Attach lifecycle-aware latency logging middleware
    attach_request_logger(app)
    
    # Register distinct microservices modules (Blueprints)
    app.register_blueprint(incidents_bp, url_prefix='/')
    app.register_blueprint(batch_bp, url_prefix='/')
    app.register_blueprint(insights_bp, url_prefix='/')
    app.register_blueprint(ai_bp, url_prefix='/')
    app.register_blueprint(sop_bp, url_prefix='/')
    
    # Diagnostic checkpoint
    print("🚀 Incident Tracker Server Modules Ready.")
    print("Registered Blueprint Routes:")
    for rule in app.url_map.iter_rules():
        print(f" -> {rule}")
        
    return app

app = create_app()

if __name__ == "__main__":
    # Execute the Gateway on local interface, port 5000 matching Vite proxies.
    app.run(host='127.0.0.1', port=5000, debug=True)
