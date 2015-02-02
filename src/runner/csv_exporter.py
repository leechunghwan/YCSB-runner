from pandas     import DataFrame
from matplotlib import pyplot as plt

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
        filename = filename + self.PLOTS_FILE_EXT
        plt.figure()
        df = self.__dataframe(key, *fields).groupby(key).mean()
        df.plot()
        plt.title(title)
        plt.savefig(filename)
        plt.clf()

    def __dataframe(self, *fields):
        return DataFrame(self.stats_set.getfields(*fields)).sort_index(axis=1)
