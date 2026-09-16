"""Flask service app for withdrawal demo."""
import json
import sys
from pathlib import Path

# Ensure Flask is available
try:
    from flask import Flask, jsonify, request
except ImportError:
    print("Flask not found. Install with: pip install flask")
    sys.exit(1)

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

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': service_name
        }), 200

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
    app.run(host='127.0.0.1', port=port, debug=False)
