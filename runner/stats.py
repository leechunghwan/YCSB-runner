from .constants import *

class Statistics:
    # Map statistic names to their base Python type functions
    TRACKED_STATS = {
        'totalcash'  : float, # From YCSB output
        'countcash'  : float, # From YCSB output
        'opcount'    : float, # From YCSB output
        'runtime'    : float, # From YCSB output
        'throughput' : float, # From YCSB output
        'mpl'        : int  , # Multiprogramming level (# threads)
        'trial'      : int  , # Trial number
        'score'      : float, # Simple anomaly score (SAS)
    }

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

    def calc_sas(self):
        """calc_sas
        Calculates the closed economy workload Simple Anomaly Score
        Returns None if S.A.S. can't be calculated from current data
        """
        if self.opcount > 0:
            return float(abs(self.totalcash - self.countcash) / self.opcount)
        else:
            return None
