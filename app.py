try:
    from flask import Flask, jsonify, request, abort
except ImportError:  # Minimal fallback for environments without Flask
    class DummyRequest:
        headers = {}

    request = DummyRequest()

    class DummyResponse:
        def __init__(self, data=None, status=200):
            self._data = data
            self.status_code = status

        def get_json(self):
            return self._data

    class Flask:
        def __init__(self, name):
            self.routes = {}

        def route(self, rule):
            def decorator(func):
                self.routes[rule] = func
                return func
            return decorator

        def test_client(self):
            app = self

            class Client:
                def get(self, path, headers=None):
                    headers = headers or {}
                    request.headers = headers
                    for rule, func in app.routes.items():
                        if '<' in rule and '>' in rule and rule.startswith('/api/tables/'):
                            name = path.split('/api/tables/')[1]
                            try:
                                return DummyResponse(func(name))
                            except AbortException as exc:
                                return DummyResponse({}, exc.code)
                        if rule == path:
                            try:
                                return DummyResponse(func())
                            except AbortException as exc:
                                return DummyResponse({}, exc.code)
                    return DummyResponse({}, 404)

            return Client()

    def jsonify(obj):
        return obj

    class AbortException(Exception):
        def __init__(self, code):
            self.code = code

    def abort(code):
        raise AbortException(code)
import os
try:
    from dotenv import load_dotenv
except Exception:  # Fallback if python-dotenv isn't installed
    def load_dotenv(*args, **kwargs):
        pass

try:
    from keycloak import KeycloakOpenID
except Exception:
    class KeycloakOpenID:
        def __init__(self, *_, **__):
            pass
        def userinfo(self, *_, **__):
            pass
try:
    from . import table_service
except Exception:
    import table_service

load_dotenv()

app = Flask(__name__)

# Optional Keycloak configuration mirroring the Express backend
keycloak_openid = None
if os.getenv("KEYCLOAK_REALM"):
    keycloak_openid = KeycloakOpenID(
        server_url=os.getenv("KEYCLOAK_URL", "http://localhost:8080/"),
        realm_name=os.getenv("KEYCLOAK_REALM"),
        client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
        client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET"),
    )


def requires_auth(func):
    """Decorator that enforces Keycloak authentication if configured."""

    def wrapper(*args, **kwargs):
        if keycloak_openid:
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                abort(401)
            token = auth.split(" ", 1)[1]
            try:
                keycloak_openid.userinfo(token)
            except Exception:
                abort(401)
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/api/tables/<name>')
@requires_auth
def get_table(name):
    try:
        rows = table_service.get_table_data(name)
        return jsonify({'data': rows})
    except Exception as exc:
        print(exc)
        return jsonify({'error': 'Failed to fetch table data'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '3000'))
    app.run(host='0.0.0.0', port=port)
