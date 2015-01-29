from pandas     import DataFrame
from matplotlib import pyplot as plt

from .exporter  import Exporter

class CsvExporter(Exporter):
    """CsvExporter: Exports statistical data captured from YCSB output to CSV format."""
    def export(self, filename, *fields):
        # Export to CSV without indexes
        DataFrame(self.stats_set.getfields(*fields)).to_csv(filename,
                index=False)

    def export_averages(self, filename, key, *fields):
        df = self.__dataframe(key, *fields)
        df.groupby(key).mean().to_csv(filename)

    def export_averages_plot(self, filename, key, *fields):
        plt.figure()
        df = self.__dataframe(key, *fields).groupby(key).mean()
        df.plot()
        # Plot with matplotlib.PyPlot, save image, and clear axes
        plt.savefig(filename)
        plt.clf()

    def __dataframe(self, *fields):
        return DataFrame(self.stats_set.getfields(*fields))
