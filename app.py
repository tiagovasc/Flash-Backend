from flask import Flask, request, jsonify
from apify_client import ApifyClient
import os

app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
API_KEY = os.getenv("MY_API_KEY")  # This will be your custom API Key

@app.route('/run', methods=['POST'])
def run_actor():
    # Check for the API Key in the request headers
    if request.headers.get('X-API-Key') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Missing 'url' in request"}), 400

        client = ApifyClient(API_TOKEN)

        run_input = {
            "urls": [url],
            "maxRetries": 3,
            "proxyOptions": {"useApifyProxy": True},
        }

        run = client.actor("karamelo/test-youtube-structured-transcript-extractor").call(run_input=run_input)
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)

        return jsonify({"status": "success", "data": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
