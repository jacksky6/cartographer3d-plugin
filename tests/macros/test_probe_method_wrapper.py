from __future__ import annotations

from unittest.mock import Mock

import pytest

from cartographer.macros.probe_method_wrapper import ProbeMethodWrapperMacro
from cartographer.probe.probe import Probe
from tests.mocks.params import MockParams


def make_macro() -> tuple[ProbeMethodWrapperMacro, Probe, Mock]:
    scan = Mock()
    touch = Mock()
    probe = Probe(scan, touch)
    fallback = Mock()
    macro = ProbeMethodWrapperMacro(probe)
    macro.set_fallback_macro(fallback)
    return macro, probe, fallback


def test_scan_method_uses_default_probe() -> None:
    macro, probe, fallback = make_macro()
    params = MockParams()

    macro.run(params)

    fallback.run.assert_called_once_with(params)
    assert probe.current_mode is probe.scan


def test_touch_method_switches_probe_for_command() -> None:
    macro, probe, fallback = make_macro()
    params = MockParams()
    params.params = {"PROBE_METHOD": "touch"}

    def assert_touch_mode(_params) -> None:
        assert _params is params
        assert probe.current_mode is probe.touch

    fallback.run.side_effect = assert_touch_mode

    macro.run(params)

    fallback.run.assert_called_once_with(params)
    assert probe.current_mode is probe.scan


def test_touch_method_restores_probe_after_failure() -> None:
    macro, probe, fallback = make_macro()
    params = MockParams()
    params.params = {"PROBE_METHOD": "touch"}
    fallback.run.side_effect = RuntimeError("probe failed")

    with pytest.raises(RuntimeError, match="probe failed"):
        macro.run(params)

    assert probe.current_mode is probe.scan


def test_invalid_probe_method_is_rejected() -> None:
    macro, _, fallback = make_macro()
    params = MockParams()
    params.params = {"PROBE_METHOD": "invalid"}

    with pytest.raises(RuntimeError, match="Invalid PROBE_METHOD"):
        macro.run(params)

    fallback.run.assert_not_called()
