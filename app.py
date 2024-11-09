from flask import Flask, request, jsonify
from apify_client import ApifyClient
import os
import logging

app = Flask(__name__)

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)

API_TOKEN = os.getenv("API_TOKEN")
API_KEY = os.getenv("MY_API_KEY")

@app.route('/run', methods=['POST'])
def run_actor():
    # Log all headers for debugging
    app.logger.debug("Received headers: %s", request.headers)

    # Check and log the specific header we expect
    received_api_key = request.headers.get('Authorization')
    app.logger.debug("Received API Key: %s", received_api_key)

    if received_api_key != API_KEY:
        app.logger.warning("Unauthorized access attempt with key: %s", received_api_key)
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        app.logger.debug("Received data: %s", data)

        url = data.get("url")
        if not url:
            app.logger.error("Missing 'url' in request")
            return jsonify({"error": "Missing 'url' in request"}), 400

        client = ApifyClient(API_TOKEN)
        app.logger.debug("Apify Client initialized with token: %s", API_TOKEN)

        run_input = {
            "urls": [url],
            "maxRetries": 3,
            "proxyOptions": {"useApifyProxy": True},
        }
        app.logger.debug("Actor input: %s", run_input)

        run = client.actor("karamelo/test-youtube-structured-transcript-extractor").call(run_input=run_input)
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        app.logger.debug("Actor results: %s", results)
        return jsonify({"status": "success", "data": results})

    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
