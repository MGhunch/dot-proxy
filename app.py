from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import httpx
import os

app = Flask(__name__)
CORS(app)

# Service endpoints
N8N_WEBHOOKS = {
    'todo': os.environ.get('N8N_TODO_WEBHOOK', 'https://hunch-dot.app.n8n.cloud/webhook/9e0fbfa4-00cd-4536-9231-49557ceb92db'),
    'update': os.environ.get('N8N_UPDATE_WEBHOOK', 'https://hunch-dot.app.n8n.cloud/webhook/c41beccb-b6cb-4bc8-a540-af163e5e861f'),
    'wip': os.environ.get('N8N_WIP_WEBHOOK', 'https://hunch-dot.app.n8n.cloud/webhook/7d2d86a7-d3d6-4097-a4c3-c54ecb649f82')
}

# Direct service endpoints (not via N8N)
SERVICES = {
    'incoming': os.environ.get('DOT_INCOMING_URL', 'https://dot-incoming.up.railway.app/incoming')
}


@app.route('/proxy/todo', methods=['GET', 'OPTIONS'])
def proxy_todo():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        response = httpx.get(N8N_WEBHOOKS['todo'], timeout=30.0)
        return jsonify({'status': 'sent', 'code': response.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/proxy/update', methods=['POST', 'OPTIONS'])
def proxy_update():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        response = httpx.post(
            N8N_WEBHOOKS['update'],
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30.0
        )
        return jsonify({'status': 'sent', 'code': response.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/proxy/wip', methods=['POST', 'OPTIONS'])
def proxy_wip():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        response = httpx.post(
            N8N_WEBHOOKS['wip'],
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30.0
        )
        return jsonify({'status': 'sent', 'code': response.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/proxy/incoming', methods=['POST', 'OPTIONS'])
def proxy_incoming():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        response = httpx.post(
            SERVICES['incoming'],
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30.0
        )
        # Return the full response from dot-incoming (includes jobNumber, projectName)
        return Response(
            response.content,
            status=response.status_code,
            content_type='application/json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'dot-proxy'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
