from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# N8N webhook URLs
N8N_WEBHOOKS = {
    'todo': 'https://hunch-dot.app.n8n.cloud/webhook/9e0fbfa4-00cd-4536-9231-49557ceb92db',
    'update': 'https://hunch-dot.app.n8n.cloud/webhook/c41beccb-b6cb-4bc8-a540-af163e5e861f',
    'wip': 'https://hunch-dot.app.n8n.cloud/webhook/7d2d86a7-d3d6-4097-a4c3-c54ecb649f82'
}


@app.route('/proxy/<action>', methods=['GET', 'POST', 'OPTIONS'])
def proxy(action):
    """Proxy requests to N8N webhooks"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    if action not in N8N_WEBHOOKS:
        return jsonify({'error': f'Unknown action: {action}'}), 400
    
    webhook_url = N8N_WEBHOOKS[action]
    
    try:
        if request.method == 'GET':
            # Forward GET request
            response = httpx.get(webhook_url, timeout=30.0)
        else:
            # Forward POST request with JSON body
            response = httpx.post(
                webhook_url,
                json=request.get_json() or {},
                headers={'Content-Type': 'application/json'},
                timeout=30.0
            )
        
        # Return N8N's response
        return jsonify({
            'success': True,
            'status': response.status_code,
            'data': response.json() if response.text else None
        })
        
    except httpx.TimeoutException:
        return jsonify({'error': 'Request timed out'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Dot Proxy',
        'endpoints': ['/proxy/todo', '/proxy/update', '/proxy/wip', '/health']
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
