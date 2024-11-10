from flask import Flask, request, jsonify
from flask_cors import CORS
from apify_client import ApifyClient
import os
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS

logging.basicConfig(level=logging.DEBUG)

API_TOKEN = os.getenv("API_TOKEN")
API_KEY = os.getenv("MY_API_KEY")

@app.route('/run', methods=['POST'])
def run_actor():
    app.logger.debug("Received headers: %s", request.headers)

    received_api_key = request.headers.get('Authorization')
    if received_api_key != f'Bearer {API_KEY}':
        app.logger.warning("Unauthorized access attempt with key: %s", received_api_key)
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        app.logger.debug("Received data: %s", data)
        
        urls = data.get("urls")
        clean_output = request.args.get('clean_output', 'False').lower() == 'true'

        if not urls or not isinstance(urls, list):
            app.logger.error("Missing 'urls' in request or 'urls' is not a list")
            return jsonify({"error": "Missing 'urls' in request or 'urls' is not a list"}), 400

        client = ApifyClient(API_TOKEN)
        app.logger.debug("Apify Client initialized with token: %s", API_TOKEN)

        run_input = {
            "urls": urls,
            "maxRetries": 3,
            "proxyOptions": {"useApifyProxy": True},
        }
        app.logger.debug("Actor input: %s", run_input)

        run = client.actor("karamelo/test-youtube-structured-transcript-extractor").call(run_input=run_input)
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item['captions'])

        app.logger.debug("Actor results: %s", results)

        # Check if clean_output is set to True and format accordingly
        if clean_output:
            # Flatten the list of lists and join into a single string
            flat_list = ' '.join([caption for sublist in results for caption in sublist])
            return flat_list

        return jsonify({"status": "success", "data": results})

    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
