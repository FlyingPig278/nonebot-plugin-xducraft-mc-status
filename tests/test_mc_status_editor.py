from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qsl, urlsplit

import pytest

from xducraft_bot.shared.configuration import ConfigContext, ConfigurationError
from xducraft_mc_status import configuration, data_manager as dm, handlers
from xducraft_mc_status.config_coder import decompress_config


@pytest.fixture
def editor_storage(monkeypatch, tmp_path):
    path = str(tmp_path / "configuration.sqlite3")
    monkeypatch.setattr(
        dm, "_store",
        dm.ConfigDocumentStore("mc_status", dm._default_data, dm._normalize_data, database_path=path),
    )
    return path


def test_editor_address_survives_group_changes_and_storage_reopen(editor_storage):
    resource = configuration.DECLARATION.resources["global"]
    resource.write(ConfigContext(), {"editor_url": " https://editor.example/config?lang=zh#panel "})
    dm.import_group_data(42, {"servers": [{"ip": "mc.example"}], "footer": "保留页脚"})
    expected_group = dm.export_group_data(42)
    dm.configure_storage(editor_storage)

    assert resource.read(ConfigContext()).values["editor_url"] == "https://editor.example/config?lang=zh#panel"
    assert dm.export_group_data(42) == expected_group
    assert dm.list_configured_groups() == [42]


@pytest.mark.parametrize("url", ["", "/editor", "javascript:alert(1)", "ftp://editor.example", "https://", "https://editor.example:bad"])
def test_invalid_editor_address_does_not_replace_saved_value(editor_storage, url):
    resource = configuration.DECLARATION.resources["global"]
    resource.write(ConfigContext(), {"editor_url": "https://editor.example/"})

    with pytest.raises(ConfigurationError):
        resource.write(ConfigContext(), {"editor_url": url})

    assert resource.read(ConfigContext()).values["editor_url"] == "https://editor.example/"


@pytest.mark.asyncio
async def test_edit_command_uses_latest_address_and_preserves_config_payload(editor_storage, mocker, enable_plugin):
    from xducraft_bot.shared import feature_gate

    enable_plugin("mc_status", 42)
    feature_gate.set_enabled("mc_status", 42, True)
    dm.import_group_data(42, {"servers": [{"ip": "mc.example", "comment": "测试服务器"}], "footer": "测试页脚"})
    matcher = MagicMock()
    matcher.finish = AsyncMock()
    mocker.patch.object(handlers, "_matcher", return_value=matcher)
    mocker.patch.object(handlers, "notify_privately", AsyncMock(return_value=True))
    forward = mocker.patch.object(handlers, "send_private_forward", AsyncMock(return_value=True))
    mocker.patch.object(handlers, "EDITING_USERS", {})
    event = SimpleNamespace(group_id=42, user_id=123, self_id=456)
    resource = configuration.DECLARATION.resources["global"]

    for address in ["https://editor-a.example/config?lang=zh&data=old#panel", "https://editor-b.example/"]:
        resource.write(ConfigContext(), {"editor_url": address})
        await handlers._handle_edit.__wrapped__(MagicMock(), event, [])
        link = forward.call_args.args[2][0]["data"]["content"]
        parsed = urlsplit(link)
        expected = urlsplit(address)
        assert (parsed.scheme, parsed.netloc, parsed.path, parsed.fragment) == (
            expected.scheme, expected.netloc, expected.path, expected.fragment,
        )
        params = parse_qsl(parsed.query)
        assert [(key, value) for key, value in params if key != "data"] == [
            (key, value) for key, value in parse_qsl(expected.query) if key != "data"
        ]
        payloads = [value for key, value in params if key == "data"]
        assert len(payloads) == 1
        exported = decompress_config(payloads[0])
        assert exported["footer"] == "测试页脚"
        assert exported["servers"][0]["ip"] == "mc.example"
        assert exported["servers"][0]["comment"] == "测试服务器"
