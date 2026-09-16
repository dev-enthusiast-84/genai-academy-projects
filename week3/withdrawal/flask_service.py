"""Flask service app for withdrawal demo."""
import json
import logging
import sys
import os
from pathlib import Path

# Ensure Flask is available
try:
    from flask import Flask, jsonify, request
except ImportError:
    print("Flask not found. Install with: pip install flask")
    sys.exit(1)

# Suppress Flask and Werkzeug startup messages
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask.cli').setLevel(logging.ERROR)

# Service data
SERVICE_DATA = {
    'documents': {
        'port': 8101,
        'name': 'documents',
        'records': {
            'D1': {'id': 'D1', 'service': 'documents', 'title': 'Fitness Questionnaire', 'version': 1},
            'D2': {'id': 'D2', 'service': 'documents', 'title': 'Membership Form', 'version': 1},
        }
    },
    'search': {
        'port': 8102,
        'name': 'search',
        'records': {
            'T1': {'id': 'T1', 'service': 'search', 'title': 'Class Preferences', 'version': 1},
            'T2': {'id': 'T2', 'service': 'search', 'title': 'Search History', 'version': 1},
        }
    },
    'personalization': {
        'port': 8103,
        'name': 'personalization',
        'records': {
            'V1': {'id': 'V1', 'service': 'personalization', 'title': 'Personalized Offers', 'version': 3},
            'V3': {'id': 'V3', 'service': 'personalization', 'title': 'Explore Interests', 'version': 1},
        }
    }
}

def get_consent_state():
    """Read consent state from the Engine."""
    try:
        data_dir = os.environ.get('RECALL_DATA_DIR', '.runtime/fitness-local')
        consent_file = Path(data_dir) / 'recall' / 'consent.json'
        if consent_file.exists():
            with open(consent_file) as f:
                return json.load(f).get('state', 'not_granted')
    except Exception:
        pass
    return 'not_granted'


def get_engine_catalog():
    """Get actual catalog from Engine."""
    try:
        data_dir = os.environ.get('RECALL_DATA_DIR', '.runtime/fitness-local')
        catalog_file = Path(data_dir) / 'recall' / 'catalog.json'
        if catalog_file.exists():
            with open(catalog_file) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def get_records_for_service(service_name, user_id='U1'):
    """Get records from catalog for a specific service."""
    catalog = get_engine_catalog()
    records = {}
    for rec_id, rec in catalog.items():
        if rec.get('user_id') == user_id and rec.get('service') == service_name:
            records[rec_id] = rec
    return records


def create_app(service_name: str):
    """Create Flask app for a service.

    Args:
        service_name: Name of service (documents, search, personalization)

    Returns:
        Flask app instance
    """
    if service_name not in SERVICE_DATA:
        raise ValueError(f"Unknown service: {service_name}")

    app = Flask(__name__)
    service_info = SERVICE_DATA[service_name]
    records = service_info['records']

    @app.route('/', methods=['GET'])
    def index():
        """Serve UI for the service."""
        service_titles = {
            'documents': 'Start Your Journey',
            'search': 'Class Booking',
            'personalization': 'Member Offers'
        }
        service_descriptions = {
            'documents': 'Fitness questionnaire and membership information',
            'search': 'Search class preferences and booking history',
            'personalization': 'Personalized offers and recommendations'
        }

        title = service_titles.get(service_name, service_name.title())
        description = service_descriptions.get(service_name, '')

        # Check if consent is active and get actual records from catalog
        consent_state = get_consent_state()
        is_sharing = consent_state == "active"

        # Get actual records from Engine catalog
        catalog_records = get_records_for_service(service_name)

        # Filter records based on consent state
        visible_records = {}
        for rec_id, rec in catalog_records.items():
            consent_root = rec.get('consent_root')
            # Show records that:
            # 1. Don't have a consent_root (always visible)
            # 2. Have consent_root=D1 and consent is active (sharing enabled)
            if consent_root is None or (consent_root == 'D1' and is_sharing):
                visible_records[rec_id] = rec

        # Data flow descriptions based on service
        data_flow_html = ""
        if service_name == 'documents' and is_sharing:
            data_flow_html = '''
            <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong style="color: #2e7d32;">🔗 Data Sharing Active</strong>
                <p style="color: #558b2f; margin: 8px 0; font-size: 14px;">Your questionnaire is being shared with Class Booking & Member Offers for personalization.</p>
            </div>
            '''
        elif (service_name == 'search' or service_name == 'personalization') and is_sharing:
            data_flow_html = f'''
            <div style="background: #fff3e0; border-left: 4px solid #f57f17; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong style="color: #e65100;">📥 Using Shared Data from Start Your Journey</strong>
                <p style="color: #bf360c; margin: 8px 0; font-size: 14px;">This app is receiving and using your preferences to personalize recommendations.</p>
            </div>
            '''
        elif (service_name == 'search' or service_name == 'personalization') and not is_sharing:
            data_flow_html = f'''
            <div style="background: #f5f5f5; border-left: 4px solid #999; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong style="color: #666;">⏸️ Data Sharing Paused</strong>
                <p style="color: #777; margin: 8px 0; font-size: 14px;">Enable consent in Recall Dashboard to see personalized data.</p>
            </div>
            '''

        # Build records HTML with content and derivation info
        records_html = ""
        for rec_id, rec in visible_records.items():
            rec_type = rec.get('type', 'unknown')
            content = rec.get('content', '')
            derived = '📥 Derived from preferences' if rec.get('consent_root') == 'D1' else '📋 Primary record'
            records_html += f'''
            <div style="background: #f9f9f9; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div style="font-weight: bold; color: #333;">{rec.get("title", "Untitled")}</div>
                        <div style="color: #666; font-size: 0.9em; margin: 5px 0;">ID: {rec_id}</div>
                        <div style="color: #666; font-size: 0.85em; margin: 5px 0;">{content[:70]}{'...' if len(content) > 70 else ''}</div>
                    </div>
                    <span style="background: #e3f2fd; color: #0066cc; padding: 4px 8px; border-radius: 3px; font-size: 11px; white-space: nowrap;">{derived}</span>
                </div>
            </div>
            '''

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }}
                h1 {{ color: #333; }}
                .service-info {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .records {{ margin-top: 30px; }}
                .record {{ background: #f9f9f9; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; }}
                .record-title {{ font-weight: bold; color: #333; }}
                .record-id {{ color: #666; font-size: 0.9em; }}
                .consent-badge {{ display: inline-block; background: #4caf50; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏋️ {title}</h1>
                <div class="service-info">
                    <p>{description}</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    {f'<span class="consent-badge">✓ SHARING</span>' if is_sharing else ''}
                </div>

                {data_flow_html}

                <div class="records">
                    <h2>📋 Records ({len(visible_records)})</h2>
                    {records_html if records_html else '<p style="color: #999;">No records available. Enable consent in Recall Dashboard to see shared data.</p>'}
                </div>

                <div style="margin-top: 40px; padding: 15px; background: #f0f0f0; border-radius: 5px; font-size: 12px; color: #666;">
                    <strong>💡 Workflow:</strong> Go to <strong>Recall Dashboard</strong> (http://127.0.0.1:8501) → Click "Give Consent to Share" → Return here to see data flow → Records will appear showing how your preferences are being used.
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': service_name
        }), 200

    @app.route('/api/reset', methods=['POST'])
    def api_reset():
        """Reset service - stub for Engine integration."""
        return jsonify({'success': True}), 200

    @app.route('/api/read', methods=['POST'])
    def api_read():
        """Read record endpoint."""
        data = request.get_json() or {}
        record_id = data.get('id', '')
        if record_id not in records:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'record': records[record_id]}), 200

    @app.route('/api/delete', methods=['POST'])
    def api_delete():
        """Delete record endpoint."""
        data = request.get_json() or {}
        record_id = data.get('id', '')
        if record_id not in records:
            return jsonify({'error': 'Not found'}), 404
        del records[record_id]
        return jsonify({'changed': True}), 200

    @app.route('/api/block', methods=['POST'])
    def api_block():
        """Block records endpoint."""
        return jsonify({'success': True}), 200

    @app.route('/api/behavior', methods=['POST'])
    def api_behavior():
        """Get behavior endpoint."""
        return jsonify({'behavior': 'normal'}), 200

    @app.route('/api/replay', methods=['POST'])
    def api_replay():
        """Replay endpoint."""
        return jsonify({'replayed': True}), 200

    @app.route('/catalog', methods=['GET'])
    def catalog():
        """List all records for a user."""
        user_id = request.args.get('user_id', '')
        if not user_id:
            return jsonify([]), 200

        # Return all records for this service
        return jsonify(list(records.values())), 200

    @app.route('/record/<record_id>', methods=['GET'])
    def get_record(record_id):
        """Get a specific record."""
        user_id = request.args.get('user_id', '')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400

        if record_id not in records:
            return jsonify({'error': 'Not found'}), 404

        return jsonify(records[record_id]), 200

    @app.route('/record/<record_id>', methods=['DELETE'])
    def delete_record(record_id):
        """Delete a record."""
        user_id = request.args.get('user_id', '')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400

        if record_id not in records:
            return jsonify({'error': 'Not found'}), 404

        # Remove the record
        del records[record_id]
        return jsonify({'success': True}), 200

    return app


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m withdrawal.flask_service <service_name>")
        sys.exit(1)

    service_name = sys.argv[1]
    app = create_app(service_name)
    port = SERVICE_DATA[service_name]['port']

    print(f"Starting {service_name} service on port {port}...")
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
