from matplotlib import pyplot as plt
from numpy      import polyfit, poly1d

# Plot given X and Y series, saving output to given file path
#   series: list of dicts in the form
#     {'x': list, 'y': list, 'series': str}
#   outputfile: path to the output file
#   xaxis and yaxis: the x and y axis labels
#   regression: boolean indicating whether to plot a linear regression line
def series(series, outputfile, xaxis=None, yaxis=None):
    # Create all plots, add to plots list
    plots = [
        plt.plot(s['x'], s['y'], label=s['series'], linestyle="-", marker="o")[0]
        for s in series
    ]
    # Add legends
    plt.legend(handles=plots)
    # Add axis labels
    if xaxis is not None:
        plt.xlabel(xaxis)
    if yaxis is not None:
        plt.ylabel(yaxis)
    plt.savefig(outputfile)

# Plot given X and Y as scatterplots, saving output to given file path
#   series: list of dicts in the form
#     {'x': list, 'y': list, 'series': str}
#   outputfile: path to the output file
#   xaxis and yaxis: the x and y axis labels
#   regression: boolean indicating whether to plot a linear regression line
def scatter(series, outputfile, xaxis=None, yaxis=None, regression=True):
    # Create all plots, add to plots list
    plots = []
    for s in series:
        plots += [plt.scatter(s['x'], s['y'], label=s['series'], marker="o")]
        # Calculate linear regression if needed
        if regression:
            fit = polyfit(s['x'], s['y'], 1)
            fit_fn = poly1d(fit)
            plt.plot(s['x'], fit_fn(s['x']), '-')
    # Add legends
    plt.legend(handles=plots)
    # Add axis labels
    if xaxis is not None:
        plt.xlabel(xaxis)
    if yaxis is not None:
        plt.ylabel(yaxis)
    plt.savefig(outputfile)

