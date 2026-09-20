from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from cartographer.interfaces.printer import Macro, MacroParams

if TYPE_CHECKING:
    from cartographer.probe import Probe


@final
class ProbeMethodWrapperMacro(Macro):
    description = "Run a probing command using scan or touch mode."

    def __init__(self, probe: Probe) -> None:
        self._probe = probe
        self._fallback: Macro | None = None

    def set_fallback_macro(self, macro: Macro) -> None:
        self._fallback = macro

    @override
    def run(self, params: MacroParams) -> None:
        if self._fallback is None:
            msg = "Original probing command is not available"
            raise RuntimeError(msg)

        probe_method = params.get("PROBE_METHOD", "scan").lower()
        if probe_method == "scan":
            self._fallback.run(params)
            return
        if probe_method != "touch":
            msg = f"Invalid PROBE_METHOD '{probe_method}'; expected 'scan' or 'touch'"
            raise RuntimeError(msg)

        with self._probe.as_touch():
            self._fallback.run(params)
