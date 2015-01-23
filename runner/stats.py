from .constants import *

class Statistics:
    """Statistics: Stores statistical data for a single run of YCSB"""
    # Map statistic names to their base Python type functions
    TRACKED_STATS = {
        'totalcash'  : float, # From YCSB output
        'countcash'  : float, # From YCSB output
        'opcount'    : float, # From YCSB output
        'runtime'    : float, # From YCSB output
        'throughput' : float, # From YCSB output
        'mpl'        : int  , # Multiprogramming level (# threads)
        'trial'      : int  , # Trial number
    }

    # The prefix for said methods, to prevent name clashes
    __FUNC_ATTRS_PREFIX = "calc_"

    # Handle importing stats from kwargs
    def __init__(self, **kwargs):
        self.__stats = {}
        # Import values from given keyword arguments
        for k, v in kwargs.items():
            if k not in self.TRACKED_STATS:
                raise AttributeError("Unexpected keyword argument: '%s'. " % k +
                    "Valid arguments are ({})".format(','.join(self.TRACKED_STATS.keys())))
            setattr(self, k, v)
        # Add default values for missing stats
        for k, v in self.TRACKED_STATS.items():
            if k not in kwargs:
                setattr(self, k, v())

    # Get from __stats dict
    def __getattr__(self, name):
        if name in self.__stats:
            return self.__stats[name]
        raise AttributeError

    # Store stats attributes in __stats dict
    def __setattr__(self, name, value):
        if name in self.TRACKED_STATS:
            if type(value) != type(self.TRACKED_STATS[name]()):
                raise TypeError("Type mismatch: '%s' should be '%s', but was '%s'" %
                    (name, type(self.TRACKED_STATS[name]()).__name__, type(value).__name__))
            self.__stats[name] = value
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        data = dict(self.__stats)
        # Add function mapped attributes
        for fa in self.__FUNC_ATTRS:
            data[fa] = getattr(self, fa)
        return str(data)

    @property
    def anomaly_score(self):
        """score
        Calculates the closed economy workload Simple Anomaly Score
        Returns None if S.A.S. can't be calculated from current data
        """
        if self.opcount > 0:
            return float(abs(self.totalcash - self.countcash) / self.opcount)
        else:
            return None

class StatisticsSet:
    """StatisticsSet: Stores a set of Statistics objects.

    Averages can be accessed by prepending a Statistics field name with avg_
        e.g. statset.avg_score
        or   statset.avg_opcount
    """
    # The type of data we're storing here
    STATS_TYPE = Statistics

    def __init__(self, *args):
        """__init__
        Instantiate this StatisticsSet with the given Statistics objects

        :param *args: Statistics instances to add to this StatisticsSet
        """
        # Mappings of magic prefixes to aggregation methods
        self.__MAGIC_ATTR_PREFIX_MAP = {
            "avg_": self.average,
            "sum_": self.sum,
            "num_": self.count,
        }
        self.__stats = []
        self.addstats(*args)

    def __getattr__(self, name):
        # Handle magic property prefixes
        for prefix, f in self.__MAGIC_ATTR_PREFIX_MAP.items():
            if name.startswith(prefix):
                name = re.sub(r'^' + prefix, "", name)
                return f(name)
        raise AttributeError

    def __len__(self):
        """__len__
        Number of Statistics instances stored
        """
        return len(self.__stats)

    def addstats(self, *args):
        """addstats
        Add the given Statistics instances to this StatisticsSet instance

        Raises ValueError if parameters are not of type Statistics

        :param *args: Statistics instances to be added
        """
        for arg in args:
            if type(arg) != self.STATS_TYPE:
                raise ValueError("Can only store instances of %s class" %
                        self.STATS_TYPE.__name__)
            else:
                self.__stats.append(arg)

    def items(self):
        """items
        A list of items stored in this StatisticsSet instance
        """
        return self.__stats

    def average(self, field):
        """average
        Average of values stored in given field

        :param field: Field to average
        """
        stats = self.getvalues(field)
        return sum(stats) / len(stats)

    def sum(self, field):
        """sum
        Sum of values stored in given field

        :param field: Field to be summed
        """
        stats = self.getvalues(field)
        return sum(stats)

    def count(self, field):
        """count
        Number of values stored in given field

        :param field: Field to count
        """
        stats = self.getvalues(field)
        return len(stats)

    def getvalues(self, field):
        """getvalues
        Get a list of all the values of the given field

        :param field: Field for which values should be retrieved
        """
        return [getattr(stat, field) for stat in self.__stats]
