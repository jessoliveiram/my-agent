from unittest.mock import Mock

import pytest

from src import oauth_flow


class FakeCredentials:
    def __init__(self, valid=False, expired=False, refresh_token=None):
        self.valid = valid
        self.expired = expired
        self.refresh_token = refresh_token
        self.refresh_called = False

    def refresh(self, request):
        self.refresh_called = True
        self.valid = True

    def to_json(self):
        return '{"access_token":"redacted"}'


def test_run_oauth_flow_rejects_missing_client_secrets(tmp_path):
    with pytest.raises(FileNotFoundError):
        oauth_flow.run_oauth_flow(
            str(tmp_path / "missing-client.json"), str(tmp_path / "token.json")
        )


def test_run_oauth_flow_returns_existing_valid_credentials(monkeypatch, tmp_path):
    client_file = tmp_path / "client.json"
    token_file = tmp_path / "token.json"
    client_file.write_text("client", encoding="utf-8")
    token_file.write_text("token", encoding="utf-8")
    credentials = FakeCredentials(valid=True)
    loader = Mock(return_value=credentials)
    monkeypatch.setattr(
        oauth_flow.Credentials, "from_authorized_user_file", loader
    )

    result = oauth_flow.run_oauth_flow(str(client_file), str(token_file))

    assert result is credentials
    loader.assert_called_once_with(str(token_file), oauth_flow.SCOPES)
    assert token_file.read_text(encoding="utf-8") == "token"


def test_run_oauth_flow_refreshes_and_persists_credentials(monkeypatch, tmp_path):
    client_file = tmp_path / "client.json"
    token_file = tmp_path / "token.json"
    client_file.write_text("client", encoding="utf-8")
    token_file.write_text("token", encoding="utf-8")
    credentials = FakeCredentials(
        valid=False, expired=True, refresh_token="refresh-token"
    )
    monkeypatch.setattr(
        oauth_flow.Credentials,
        "from_authorized_user_file",
        Mock(return_value=credentials),
    )
    request = Mock()
    monkeypatch.setattr(oauth_flow, "Request", lambda: request)

    result = oauth_flow.run_oauth_flow(str(client_file), str(token_file))

    assert result is credentials
    assert credentials.refresh_called is True
    assert token_file.read_text(encoding="utf-8") == '{"access_token":"redacted"}'


def test_run_oauth_flow_runs_installed_app_when_no_token(
    monkeypatch, tmp_path
):
    client_file = tmp_path / "client.json"
    token_file = tmp_path / "nested" / "token.json"
    client_file.write_text("client", encoding="utf-8")
    credentials = FakeCredentials(valid=True)
    flow = Mock()
    flow.run_local_server.return_value = credentials
    factory = Mock(return_value=flow)
    monkeypatch.setattr(
        oauth_flow.InstalledAppFlow,
        "from_client_secrets_file",
        factory,
    )

    result = oauth_flow.run_oauth_flow(str(client_file), str(token_file))

    assert result is credentials
    factory.assert_called_once_with(str(client_file), oauth_flow.SCOPES)
    flow.run_local_server.assert_called_once_with(port=0)
    assert token_file.exists()
