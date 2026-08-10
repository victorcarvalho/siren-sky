from frontend.streamlit.utils import (
    format_coordinate,
    is_garbage,
    update_alert_status,
    get_alert_records,
    is_alert_record,
    get_marker_color,
    get_display_classification,
    get_status_badge_html,
    is_email_authorized,
)


def test_format_coordinate():
    assert format_coordinate(None) is None
    assert format_coordinate(12.3456789) == 12.345679
    assert format_coordinate(-45.123) == -45.123
    assert format_coordinate(0.0) == 0.0


def test_is_garbage():
    assert is_garbage("Yes") is True
    assert is_garbage("yes ") is True
    assert is_garbage("YES, there is garbage") is True
    assert is_garbage("No") is False
    assert is_garbage("no") is False
    assert is_garbage(None) is False
    assert is_garbage("") is False


def test_update_alert_status():
    # 1. Classification is None -> Pendente
    r1 = {"classification": None, "latitude": 1.0, "longitude": 2.0}
    update_alert_status(r1)
    assert r1["alert_status"] == "Pendente"

    # 2. Classification starts with "Error:" or "Erro:" -> Erro
    r2 = {"classification": "Error: Timeout", "latitude": 1.0, "longitude": 2.0}
    update_alert_status(r2)
    assert r2["alert_status"] == "Erro"

    r2_pt = {"classification": "Erro: Timeout", "latitude": 1.0, "longitude": 2.0}
    update_alert_status(r2_pt)
    assert r2_pt["alert_status"] == "Erro"

    # 3. Classification is Yes, GPS present -> Novo
    r3 = {"classification": "Yes, litter detected", "latitude": -23.123, "longitude": -45.456}
    update_alert_status(r3)
    assert r3["alert_status"] == "Novo"

    # 4. Classification is Yes, GPS missing -> GPS ausente
    r4 = {"classification": "Yes", "latitude": None, "longitude": -45.456}
    update_alert_status(r4)
    assert r4["alert_status"] == "GPS ausente"

    r4_2 = {"classification": "Yes", "latitude": 12.0, "longitude": None}
    update_alert_status(r4_2)
    assert r4_2["alert_status"] == "GPS ausente"

    # 5. Classification is No -> Sem alerta
    r5 = {"classification": "No litter", "latitude": 1.0, "longitude": 2.0}
    update_alert_status(r5)
    assert r5["alert_status"] == "Sem alerta"


def test_is_alert_record():
    assert is_alert_record({"alert_status": "Novo"}) is True
    assert is_alert_record({"alert_status": "Revisado"}) is True
    assert is_alert_record({"alert_status": "Resolvido"}) is True
    assert is_alert_record({"alert_status": "GPS ausente"}) is True
    assert is_alert_record({"alert_status": "Pendente"}) is False
    assert is_alert_record({"alert_status": "Sem alerta"}) is False
    assert is_alert_record({"alert_status": "Erro"}) is False


def test_get_alert_records():
    records = [
        {"alert_status": "Novo"},
        {"alert_status": "Pendente"},
        {"alert_status": "Resolvido"},
        {"alert_status": "Sem alerta"},
    ]
    alerts = get_alert_records(records)
    assert len(alerts) == 2
    assert alerts[0]["alert_status"] == "Novo"
    assert alerts[1]["alert_status"] == "Resolvido"


def test_get_marker_color():
    assert get_marker_color({"alert_status": "Resolvido", "review_status": ""}) == [25, 135, 84, 190]
    assert get_marker_color({"alert_status": "Novo", "review_status": "Revisado"}) == [255, 193, 7, 190]
    assert get_marker_color({"alert_status": "Novo", "review_status": "Não revisado"}) == [220, 53, 69, 210]
    assert get_marker_color({"alert_status": "GPS ausente", "review_status": ""}) == [108, 117, 125, 190]
    assert get_marker_color({"alert_status": "Pendente", "review_status": ""}) == [13, 110, 253, 160]


def test_get_display_classification():
    assert get_display_classification(None) == "-"
    assert get_display_classification("") == "-"
    assert get_display_classification("Error: API limit reached") == "Error: API limit reached"
    assert get_display_classification("Erro: Conexao falhou") == "Erro: Conexao falhou"
    assert get_display_classification("Yes, trash detected") == "Com lixo"
    assert get_display_classification("No trash") == "Sem lixo"


def test_get_status_badge_html():
    assert get_status_badge_html(None) == ""
    assert get_status_badge_html("") == ""
    assert "status-badge-pendente" in get_status_badge_html("Pendente")
    assert "status-badge-novo" in get_status_badge_html("Novo")
    assert "status-badge-revisado" in get_status_badge_html("Revisado")
    assert "status-badge-resolvido" in get_status_badge_html("Resolvido")
    assert "status-badge-gps-ausente" in get_status_badge_html("GPS ausente")
    assert "status-badge-erro" in get_status_badge_html("Erro: API error")
    assert "status-badge-sem-alerta" in get_status_badge_html("Sem alerta")


def test_is_email_authorized():
    # 1. Whitelist bypass is True -> Everyone is authorized
    assert is_email_authorized("test@example.com", "user@example.com", True) is True
    assert is_email_authorized(None, "user@example.com", True) is True
    assert is_email_authorized("", "", True) is True

    # 2. Whitelist bypass is False, whitelist is empty -> No one is authorized (Fail-Closed)
    assert is_email_authorized("test@example.com", "", False) is False
    assert is_email_authorized("test@example.com", "   ", False) is False
    assert is_email_authorized(None, "", False) is False

    # 3. Whitelist has matching email -> Authorized
    assert is_email_authorized("user@example.com", "user@example.com", False) is True
    assert is_email_authorized("USER@EXAMPLE.COM", "user@example.com", False) is True
    assert is_email_authorized("user@example.com", "USER@EXAMPLE.COM", False) is True
    assert is_email_authorized("user@example.com", "other@example.com, user@example.com", False) is True

    # 4. Whitelist doesn't have matching email -> Unauthorized
    assert is_email_authorized("test@example.com", "user@example.com", False) is False
    assert is_email_authorized("test@example.com", "other@example.com, another@example.com", False) is False
    assert is_email_authorized(None, "user@example.com", False) is False

