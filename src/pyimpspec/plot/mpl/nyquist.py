# pyimpspec is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 pyimpspec developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The licenses of pyimpspec's dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from inspect import signature
from pyimpspec.data import DataSet
from pyimpspec.analysis import (
    TestResult,
    FitResult,
)
from pyimpspec.analysis.drt import (
    DRTResult,
)
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from pyimpspec.typing import (
    ComplexImpedances,
    Impedances,
)
from pyimpspec.plot.colors import COLOR_RED
from pyimpspec.plot.mpl.markers import MARKER_CIRCLE
from pyimpspec.plot.mpl.utility import (
    _color_axis,
    _get_marker_color_args,
)


def plot_nyquist(
    data: Union[DataSet, TestResult, FitResult, DRTResult],
    label: Optional[str] = None,
    colors: Optional[Dict[str, str]] = None,
    markers: Optional[Dict[str, str]] = None,
    line: bool = False,
    num_per_decade: int = 100,
    figure: Optional["Figure"] = None,  # noqa: F821
    legend: bool = True,
    axes: Optional[List["Axes"]] = None,  # noqa: F821
    adjust_axes: bool = True,
    colored_axes: bool = False,
    **kwargs,
) -> Tuple["Figure", List["Axes"]]:  # noqa: F821
    """
    Plot some data as a Nyquist plot (-Im(Z) vs Re(Z)).

    Parameters
    ----------
    data: Union[DataSet, TestResult, FitResult, DRTResult]
        The data to plot.

    label: Optional[str], optional
        The optional label to use in the legend.

    colors: Optional[Dict[str, str]], optional
        The colors of the markers or lines. Valid keys: 'impedance'.

    markers: Optional[Dict[str, str]], optional
        The markers to use when not plotting lines. Valid keys: 'impedance'.

    line: bool, optional
        Whether or not a line should be used instead of markers.

    num_per_decade: int, optional
        If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).

    figure: Optional[|Figure|], optional
        The matplotlib.figure.Figure instance to use when plotting the data.

    legend: bool, optional
        Whether or not to add a legend.

    axes: Optional[List[|Axes|]], optional
        A list of matplotlib.axes.Axes instances to use when plotting the data.

    adjust_axes: bool, optional
        Whether or not to adjust the axes (label, scale, limits, etc.).

    colored_axes: bool, optional
        Color the y-axes.

    **kwargs

    Returns
    -------
    Tuple[|Figure|, List[|Axes|]]
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import EngFormatter
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    assert hasattr(data, "get_impedances") and callable(data.get_impedances)
    if colors is None:
        colors = {}
    if markers is None:
        markers = {}
    assert isinstance(colors, dict), colors
    assert isinstance(markers, dict), markers
    assert isinstance(line, bool), line
    assert isinstance(label, str) or label is None, label
    assert isinstance(legend, bool), legend
    assert isinstance(colored_axes, bool), colored_axes
    assert isinstance(figure, Figure) or figure is None, figure
    axis: Axes
    if figure is None:
        assert axes is None
        figure, axis = plt.subplots()
        axes = [axis]
    assert isinstance(axes, list)
    assert len(axes) == 1
    assert all(map(lambda _: isinstance(_, Axes), axes))
    axis = axes[0]
    assert axis is not None, axis
    if label is None:
        if hasattr(data, "get_label") and callable(data.get_label):
            label = data.get_label()
        else:
            label = ""
    color: str = colors.get("impedance", COLOR_RED)
    marker: str = markers.get("impedance", MARKER_CIRCLE)
    Z: ComplexImpedances
    if "num_per_decade" in signature(data.get_impedances).parameters:
        Z = data.get_impedances(num_per_decade=num_per_decade)
    else:
        Z = data.get_impedances()
    x: Impedances = Z.real
    y: Impedances = -Z.imag
    if line is True:
        axis.plot(
            x,
            y,
            color=color,
            linestyle="--",
            label=label if label != "" else None,
        )
    else:
        axis.scatter(
            x,
            y,
            marker=marker,
            **_get_marker_color_args(marker, color),
            label=label if label != "" else None,
        )
    if adjust_axes:
        axis.set_xlabel(r"Re($Z$) ($\Omega$)")
        axis.set_ylabel(r"$-$Im($Z$) ($\Omega$)")
        axis.xaxis.set_major_formatter(EngFormatter(unit=""))
        axis.yaxis.set_major_formatter(EngFormatter(unit=""))
        axis.set_aspect("equal", adjustable="datalim")
    if legend is True:
        axis.legend()
    if colored_axes is True:
        _color_axis(axis, color, left=True)
    return (
        figure,
        axes,
    )