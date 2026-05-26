from importlib import import_module, reload


def load_app_module():
    module = import_module("app")
    return reload(module)


def test_windows_tauri_http_origin_is_allowed():
    app_module = load_app_module()
    client = app_module.app.test_client()

    resp = client.get("/api/status", headers={"Origin": "http://tauri.localhost"})

    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "http://tauri.localhost"
    assert resp.get_json() == {"ready": False}


def test_windows_tauri_http_origin_preflight_is_allowed():
    app_module = load_app_module()
    client = app_module.app.test_client()

    resp = client.options("/api/status", headers={"Origin": "http://tauri.localhost"})

    assert resp.status_code == 204
    assert resp.headers.get("Access-Control-Allow-Origin") == "http://tauri.localhost"
