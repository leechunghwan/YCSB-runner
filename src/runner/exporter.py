class Exporter:
    """Exporter: Exports statistical data captured from YCSB output to a file."""
    def __init__(self, stats_set):
        """__init__

        :param stats_set: StatisticsSet object containing data to be exported
        """
        self.stats_set = stats_set

    def export(self, filename, key, *fields):
        """export
        Exports the given fields to the given CSV file.

        :param filename: Filename and path for the export output
        :param key: Key to use as index column
        :param *fields: Fields to be exported
        """
        raise NotImplementedError

    def export_averages(self, filename, key, *fields):
        """export_averages
        Exports the averages of the given fields, grouped by the given key, to
          the given CSV file.

        :param filename: Filename and path for export output
        :param key: Key to group by
        :param *fields: Fields to average
        """
        raise NotImplementedError

    def export_averages_plot(self, filename, key, *fields):
        """export_plot
        Automatically generates and saves a plot of the given fields

        :param filename: Filename and path for the plot output
        :param *fields: Fields to be plotted
        """
        raise NotImplementedError
