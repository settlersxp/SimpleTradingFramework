from flask import Flask, jsonify, request
import requests
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Global variables to control the process
process_running = False
process_thread = None
target_url = "http://100.66.179.48:3100/api/prop_firms/sync_public"  # Replace with actual URL

def api_caller():
    """Background thread function that makes API calls every 5 seconds"""
    global process_running
    while process_running:
        try:
            response = requests.post(target_url, timeout=10)
            # print(f"[{datetime.now()}] API call successful. Status: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] API call failed: {str(e)}")
        
        time.sleep(5)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/start', methods=['POST'])
def start_process():
    """Start the background process"""
    global process_running, process_thread
    
    if process_running:
        return jsonify({"message": "Process is already running"}), 400
    
    process_running = True
    process_thread = threading.Thread(target=api_caller)
    process_thread.daemon = True
    process_thread.start()
    
    return jsonify({
        "message": "Process started successfully",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stop', methods=['POST'])
def stop_process():
    """Stop the background process"""
    global process_running
    
    if not process_running:
        return jsonify({"message": "Process is not running"}), 400
    
    process_running = False
    return jsonify({
        "message": "Process stopped successfully",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Get current process status"""
    return jsonify({
        "process_running": process_running,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)