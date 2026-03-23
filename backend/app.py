from flask import Flask, jsonify
from flask_cors import CORS
from routes.profile import profile_bp
from routes.chat import chat_bp

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Register Blueprints
app.register_blueprint(profile_bp)
app.register_blueprint(chat_bp)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from the Flask backend!"})

if __name__ == '__main__':
    # Run the server in debug mode on port 5000
    app.run(debug=True, port=5000)
