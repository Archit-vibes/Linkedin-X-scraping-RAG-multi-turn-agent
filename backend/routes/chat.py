from flask import Blueprint, request, jsonify
from services.rag_service import get_chat_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat_with_agent():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        message = data.get('message')
        linkedin_url = data.get('linkedin_url')
        
        if not message or not linkedin_url:
            return jsonify({"status": "error", "message": "Message and linkedin_url are required to chat"}), 400
            
        # Call the RAG chain
        answer = get_chat_response(linkedin_url, message)
        
        return jsonify({
            "status": "success", 
            "reply": answer
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
