import collections
import pandas as pd

import matplotlib
matplotlib.use('Agg')
matplotlib.rc('font', family='sans-serif')

from matplotlib import pyplot as plt
from pandas     import DataFrame, concat

from .exporter  import Exporter

class CsvExporter(Exporter):
    FILE_EXT = ".csv"

    """CsvExporter: Exports statistical data captured from YCSB output to CSV
                    format.
    """
    def export(self, filename, key, *fields):
        filename = filename + self.FILE_EXT
        # Export to CSV without indexes
        DataFrame(self.stats_set.getfields(*fields)).to_csv(filename,
                index=False)

    def export_averages(self, filename, key, *fields):
        filename = filename + self.FILE_EXT
        df = self.__dataframe(key, *fields)
        df.groupby(key).mean().to_csv(filename)

    def export_averages_plot(self, filename, title, key, *fields):
        #for field in fields:
        #filename = filename + "-" + field + self.PLOTS_FILE_EXT
        pd.options.display.mpl_style = 'default'
        filename = filename + self.PLOTS_FILE_EXT
        plt.figure()
        fig, axes = plt.subplots(nrows=len(fields), ncols=1, sharex=True)

        # axes must be iterable to satisfy later assumptions
        if not isinstance(axes, collections.Iterable):
            axes = axes,

        # Plot each list field as a separate subplot
        for i, field in enumerate(fields):
            dfs = self.__dataframe(key, field).groupby(key)
            # We want to plot the minimum, maximum, average, and standard error
            # for a more representative analysis
            dfs = concat([
                dfs.max() .rename(columns=lambda s: 'max_'+s),
                dfs.mean().rename(columns=lambda s: 'avg_'+s),
                dfs.min() .rename(columns=lambda s: 'min_'+s),
                dfs.sem() .rename(columns=lambda s: 'err_'+s),
            ], axis=1)
            # Enlarge the graph if we're plotting multiple stats
            fsz = (8,8) if i > 0 else None
            dfs.plot(ax=axes[i], figsize=fsz)

        # Set the title above the first axis
        axes[0].set_title(title)
        # Tighten the layout, ensure all elements fit in the bounding box
        plt.tight_layout()
        # Finally, save and clear
        plt.savefig(filename)
        plt.clf()

    def __dataframe(self, *fields):
        return DataFrame(self.stats_set.getfields(*fields)).sort_index(axis=1)
