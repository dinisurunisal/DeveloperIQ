from flask import Flask, jsonify
import json
import os  # 'os' module to access environment variables
import botocore 
import botocore.session 
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig 

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Establishing the GitHub Connection"})

@app.route('/api/github/token', methods=['GET'])
def get_github_token():
    try:
        print("Received request for /api/github/token")

        client = botocore.session.get_session().create_client('secretsmanager', region_name='us-east-2')
        cache_config = SecretCacheConfig()
        cache = SecretCache( config = cache_config, client = client)
        
        secret = cache.get_secret_string('my-github-key')

        jsonForm = json.loads(secret)
        API_TOKEN = jsonForm['githubToken']
        print(API_TOKEN)

        print("Debug: Successfully reached the end of the route.")

        return jsonify(API_TOKEN)
    except Exception as e:
        error_message = f"Error in /api/github/token: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
