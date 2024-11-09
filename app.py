from flask import Flask, request, jsonify
from apify_client import ApifyClient

app = Flask(__name__)

# Replace with your Apify API token
API_TOKEN = "YOUR_API_TOKEN"

@app.route('/run', methods=['POST'])
def run_actor():
    try:
        # Parse the URL from the request JSON
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "Missing 'url' in request"}), 400

        # Initialize the ApifyClient
        client = ApifyClient(API_TOKEN)

        # Prepare the Actor input
        run_input = {
            "urls": [url],
            "maxRetries": 3,
            "proxyOptions": {"useApifyProxy": True},
        }

        # Run the Actor and wait for it to finish
        run = client.actor("karamelo/test-youtube-structured-transcript-extractor").call(run_input=run_input)

        # Fetch results from the run's dataset
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)

        return jsonify({"status": "success", "data": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
