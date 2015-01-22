class DbSystem:
    # A list of required configuration fields
    REQUIRED_FIELDS = [
        'trials' , 'min_mpl' , 'max_mpl',
        'inc_mpl', 'workload'
    ]

    def __init__(self, dbname, config, label=""):
        self.label = label
        self.config = config

    # Gets attributes from the configuration dict
    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        else:
            raise AttributeError("Attribute {} not found".format(name))

    # Sets attributes in the configuration dict
    def __setattr(self, name, value):
        if name in self.config and type(value) == type(self.config[name]):
            self.config[name] = value
        else:
            object.__setattr__(self, name, value)

    # Ensures self.config contains all required configuration keys
    def __validate_config(self, config):
        for k in config:
            if k not in REQUIRED_FIELDS:
                raise AttributeError("Key %s is not a configuration parameter" % k)
        for k in REQUIRED_FIELDS:
            if k not in self.config:
                raise AttributeError("Missing required configuration parameter: %s" % k)
        return true # presumably nothing was raised and all is well
