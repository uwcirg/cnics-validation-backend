import app as app_mod
from unittest.mock import patch

@patch('table_service.get_table_data')
def test_get_table_route(mock_service):
    mock_service.return_value = [{'id': 1}]
    client = app_mod.app.test_client()
    res = client.get('/api/tables/events')
    assert res.status_code == 200
    assert res.get_json() == {'data': [{'id': 1}]}


@patch("table_service.get_table_data")
def test_auth_required(mock_service):
    mock_service.return_value = []
    app_mod.keycloak_openid = object()
    client = app_mod.app.test_client()
    res = client.get('/api/tables/events')
    assert res.status_code == 401
