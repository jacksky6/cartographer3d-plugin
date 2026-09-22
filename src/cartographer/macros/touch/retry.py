from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cartographer.probe.touch_mode import TouchError

if TYPE_CHECKING:
    from collections.abc import Callable

    from cartographer.interfaces.printer import GCodeDispatch

logger = logging.getLogger(__name__)


def run_with_retries(
    operation: Callable[[], None],
    *,
    gcode: GCodeDispatch | None,
    wipe_extension: str,
    retry: int,
    operation_name: str,
) -> None:
    """Run a Touch operation again after noisy samples, optionally wiping first."""
    for attempt in range(retry):
        try:
            operation()
            return
        except TouchError:
            if attempt + 1 >= retry:
                raise
            if gcode is None or not wipe_extension:
                msg = f"{operation_name} retry requested, but no wipe_extension is configured"
                raise RuntimeError(msg) from None

            logger.warning(
                "%s attempt %d/%d failed; running wipe extension '%s' before retry",
                operation_name,
                attempt + 1,
                retry,
                wipe_extension,
            )
            gcode.run_gcode(wipe_extension)
