from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from cartographer.probe.touch_mode import TouchBoundaries

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from cartographer.interfaces.printer import Toolhead

BOUNDS = TouchBoundaries(min_x=10.0, max_x=20.0, min_y=5.0, max_y=15.0)


@pytest.mark.parametrize(
    "x, y, expected",
    [
        # Clearly within bounds
        (15.0, 10.0, True),
        (10.0, 5.0, True),  # on lower edge
        (20.0, 15.0, True),  # on upper edge
        # Clearly outside bounds (beyond tolerance)
        (9.98, 10.0, False),
        (20.02, 10.0, False),
        (15.0, 4.98, False),
        (15.0, 15.02, False),
        # Near boundary (within 0.01 tolerance)
        (9.99, 10.0, True),
        (20.01, 10.0, True),
        (15.0, 4.99, True),
        (15.0, 15.01, True),
    ],
)
def test_is_within_bounds(x: float, y: float, expected: bool) -> None:
    assert BOUNDS.is_within(x=x, y=y) is expected


@pytest.mark.parametrize(
    "x_limits, y_limits, x_offset, y_offset, expected",
    [
        ((0.0, 302.0), (0.0, 307.0), 0.0, 21.0, TouchBoundaries(5.0, 297.0, 5.0, 281.0)),
        ((0.0, 100.0), (0.0, 100.0), -10.0, -5.0, TouchBoundaries(15.0, 95.0, 10.0, 95.0)),
        ((-5.0, 105.0), (-10.0, 110.0), 0.0, 0.0, TouchBoundaries(0.0, 100.0, -5.0, 105.0)),
    ],
)
def test_from_toolhead_bounds(
    mocker: MockerFixture,
    toolhead: Toolhead,
    x_limits: tuple[float, float],
    y_limits: tuple[float, float],
    x_offset: float,
    y_offset: float,
    expected: TouchBoundaries,
) -> None:
    toolhead.get_axis_limits = mocker.Mock(side_effect=lambda axis: x_limits if axis == "x" else y_limits)

    bounds = TouchBoundaries.from_toolhead(toolhead, x_offset=x_offset, y_offset=y_offset)

    assert bounds == expected
