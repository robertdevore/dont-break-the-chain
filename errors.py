from flask import Blueprint, render_template, jsonify, request

# Create a blueprint for error handling
errors_blueprint = Blueprint('errors', __name__)

# Utility function to determine if the request is for JSON
def is_json_request():
    return request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']

# 404 Error Handler
@errors_blueprint.app_errorhandler(404)
def page_not_found(e):
    if is_json_request():
        return jsonify({"error": "Resource not found", "code": 404}), 404
    return render_template('errors/404.html', error=e), 404

# 500 Error Handler
@errors_blueprint.app_errorhandler(500)
def internal_server_error(e):
    if is_json_request():
        return jsonify({"error": "Internal server error", "code": 500}), 500
    return render_template('errors/500.html', error=e), 500

# 403 Error Handler
@errors_blueprint.app_errorhandler(403)
def forbidden(e):
    if is_json_request():
        return jsonify({"error": "Forbidden", "code": 403}), 403
    return render_template('errors/403.html', error=e), 403

# 400 Error Handler
@errors_blueprint.app_errorhandler(400)
def bad_request(e):
    if is_json_request():
        return jsonify({"error": "Bad request", "code": 400}), 400
    return render_template('errors/400.html', error=e), 400

# Generic Error Handler for other HTTP status codes
@errors_blueprint.app_errorhandler(Exception)
def handle_generic_error(e):
    code = getattr(e, 'code', 500)  # Default to 500 if no specific code
    if is_json_request():
        return jsonify({"error": "An unexpected error occurred", "code": code}), code
    return render_template('errors/generic.html', error=e, code=code), code

# Initialization function for the blueprint
def init_error_handlers(app):
    app.register_blueprint(errors_blueprint)
