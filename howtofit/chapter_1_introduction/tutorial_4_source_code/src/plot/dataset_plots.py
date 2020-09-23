from howtofit.chapter_1_introduction.tutorial_4_source_code.src.plot import (
    line_plots,
)

"""
These functions are simple matplotlib calls that plot components of our Line class, specifically its data and
noise-map.

Storing simple functions like this for plotting components of our _Dataset_ will prove beneficial in later tutorials,
when it comes to inspecting the results of a model-fit after they have been completed.
"""


def data(dataset):
    """Plot the data values of a Line _Dataset_.

    Parameters
    -----------
    Line : _Dataset_.Line
        The observed Line _Dataset_ whose data is plotted.
    """
    line_plots.line(xvalues=dataset.xvalues, line=dataset.data, ylabel="Data Values")


def noise_map(dataset):
    """Plot the noise-map of a Line _Dataset_.

    Parameters
    -----------
    Line : _Dataset_.Line
        The observed Line _Dataset_ whose data is plotted.
    """
    line_plots.line(xvalues=dataset.xvalues, line=dataset.noise_map, ylabel="Noise-Map")