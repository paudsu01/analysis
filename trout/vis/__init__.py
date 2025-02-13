# Helper visualization functions

from datetime import datetime
from functools import cache
from typing import Callable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from trout.files.reference_log_file import ReferenceLogFile
from trout.internight import bands as get_bands
from trout.nights.year_nights import get_nights_in_a_year
from trout.stars import STAR_END, STAR_START, Star, get_star

# Types
StarNumberType = int
StepType = float


def field():
    """
    Plot a simple visualization of the `m23` field based on ref_revised_71
    """
    f = ReferenceLogFile.get_ref_revised_71()
    star_end = len(f.data()) + 1
    array_for_x_values = np.array([])
    array_for_y_values = np.array([])
    for star in range(1, star_end):
        xy = f.get_star_xy(star)
        array_for_x_values = np.append(array_for_x_values, [xy[0]])
        array_for_y_values = np.append(array_for_y_values, [xy[1]])
    plt.scatter(
        array_for_x_values,
        array_for_y_values,
        s=[100 / (0.1 * i) for i in range(1, star_end)],
    )
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()


@cache
def _get_valid_years():
    VALID_YEARS = []
    START_YEAR = 2003
    END_YEAR = datetime.now().year
    for y in range(START_YEAR, END_YEAR + 1):
        if len(get_nights_in_a_year(y)) > 0:
            VALID_YEARS.append(y)
    return VALID_YEARS


def attendance_plot(star_no, data_fn=Star.mean):
    """
    Displays the attendance plot of the star where yearly signal (customizable,
    defaults to mean) is used. The size of the data point co-relates to
    attendance. Helper functions
    `attendance_plot_by_mean`
    and
    `attendance_plot_by_median` are pre-defined
    """
    valid_years = _get_valid_years()
    s = get_star(star_no)
    attendances = np.array([s.attendance(y) for y in valid_years])
    signals = []
    for y in valid_years:
        s.select_year(y)
        signals.append(data_fn(s))

    fig, ax = plt.subplots()
    ax.scatter(valid_years, signals, s=attendances * 100, alpha=0.5)

    ax.set_xlabel("Year", fontsize=15)
    ax.set_ylabel(f"{data_fn.__name__}", fontsize=15)
    ax.set_title(f"Star {star_no}")

    ax.grid(True)
    fig.tight_layout()

    plt.show()


def attendance_plot_by_mean(star):
    """
    Displays the attendance plot of the star where yearly mean signal
    is used. The size of the data point co-relates to attendance
    """
    return attendance_plot(star, data_fn=Star.mean)


def attendance_plot_by_median(star):
    """
    Displays the attendance plot of the star where yearly median signal
    is used. The size of the data point co-relates to attendance
    """
    return attendance_plot(star, data_fn=Star.median)


def internight_bands(stars=range(STAR_START, STAR_END + 1)):
    """
    Draw a bar chart of stars (default to all stars) internight
    normalization band
    """
    bands = get_bands()
    plt.figure(figsize=(10, 5))

    # Creating a copy is necessary as we don't want to alter
    # dict returned by get_bands is cached
    bands_copy = {}

    for k in bands:
        bands_copy[k] = filter(lambda x: x in stars, bands[k])

    x = bands.keys()
    y = [len(list(bands_copy[i])) for i in x]

    # Crate bar plot
    plt.bar(x, y, color="maroon", width=0.4)

    plt.xlabel("Bands")
    plt.ylabel("Star count")
    plt.title("Internight normalization bands")

    plt.show()


def step_stat(start_star, end_star, from_year, to_year):
    """
    Returns a tuple of dictionary and list with the step information for the
    range of stars defined by `start_star`, `end_star`, `from_year` and
    `to_year`

    Note that the list returned only contains stars whose step ratio is
    available
    """
    star_to_step_dict = {}
    star_step_list = []

    for star_no in range(start_star, end_star + 1):
        star = get_star(star_no)
        step_ratio = star.step(from_year, to_year)
        star_to_step_dict[star_no] = step_ratio
        # Note that it's important that we don't put stars that have nan values
        # into the list if we are to use later sort that list. nan values mess
        # up sorting
        if not np.isnan(step_ratio):
            star_step_list.append((star_no, step_ratio))
    return star_to_step_dict, star_step_list


def step_stat_vis(
    stars_step_list: List[Tuple[StarNumberType, StepType]],
    get_x: Callable[[StarNumberType], float],
    x_label="X",
    title="",
):
    """
    Display plot for given `stars_step_list` with step ratio in the
    y-axis. The unary function `get_x` provides the x_value
    """

    stars = [i[0] for i in stars_step_list]
    steps = [i[1] for i in stars_step_list]
    # X-Axis is specified by user
    x = [get_x(i) for i in stars]
    # Y-Axis is step
    y = steps

    plt.plot(
        x,
        y,
        "ro",
    )
    plt.ylabel("Step")
    plt.xlabel(f"{x_label}")
    plt.title(f"{title}")

    plt.show()


def preview_step(
    start_star,
    end_star,
    from_year,
    to_year,
    get_x: Callable[[StarNumberType], float] = lambda x: 5,
    x_label="X",
    title="",
):
    """
    Show a chart for quick preview of the step for given parameters
    Note that the X-Axis is a bogus value unless specified
    """
    d = step_stat(start_star, end_star, from_year, to_year)
    step_stat_vis(d[1], get_x=get_x, x_label=x_label, title=title)
