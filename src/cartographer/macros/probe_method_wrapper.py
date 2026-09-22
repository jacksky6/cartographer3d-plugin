from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from cartographer.interfaces.printer import Macro, MacroParams
from cartographer.macros.touch.retry import run_with_retries

if TYPE_CHECKING:
    from cartographer.interfaces.printer import GCodeDispatch
    from cartographer.probe import Probe


@final
class ProbeMethodWrapperMacro(Macro):
    description = "Run a probing command using scan or touch mode."

    def __init__(
        self,
        probe: Probe,
        *,
        gcode: GCodeDispatch | None = None,
        wipe_extension: str = "",
        retry: int = 1,
    ) -> None:
        self._probe = probe
        self._fallback: Macro | None = None
        self._gcode = gcode
        self._wipe_extension = wipe_extension.strip()
        self._retry = retry

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

        def run_probe() -> None:
            with self._probe.as_touch():
                self._fallback.run(params)

        run_with_retries(
            run_probe,
            gcode=self._gcode,
            wipe_extension=self._wipe_extension,
            retry=self._retry,
            operation_name="Touch probing command",
        )
