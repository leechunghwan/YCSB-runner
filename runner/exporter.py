class Exporter:
    """Exporter: Exports statistical data captured from YCSB output to a file."""
    def __init__(self, stats_set):
        """__init__

        :param stats_set: StatisticsSet object containing data to be exported
        """
        self.stats_set = stats_set

    def export(self, filename, *fields):
        """export

        :param filename: Filename and path for the export output
        :param *fields: Fields to be exported
        """
        raise NotImplementedError

    def export_plot(self, filename, *fields):
        """export_plot
        Automatically generates and saves a plot of the given fields

        :param filename: Filename and path for the plot output
        :param *fields: Fields to be plotted
        """
        raise NotImplementedError
