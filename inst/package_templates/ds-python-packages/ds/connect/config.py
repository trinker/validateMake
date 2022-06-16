import re

from ds.password import Password
from ds.paths import Paths, opener
from munch import DefaultMunch
from numpy import isin
from yaml import YAMLError, safe_load


class Config:
    """Config File Parse

    Parse config file to object with the attributes named the same as the named entries.  These named attributes are dictionaries with credential key value pairs.

    Parameters:
        path: Path to the config.txt file.  Defaults to `Paths().config`.

    Attributes:
        path: The path to the user's config file (used for storing credentials); found in the user's home directory
        yaml: The raw config yaml file parsed to a dictionary/munch-bunch object
        others: All the named credentials in the config.txt can be accessed by their name from the object created by `Config()`

    Methods:
        open: Open the config.txt using the default OS tools associated with that file; use `location = True` to open the parent directory of the path

    Examples::

        from ds.connect import Config
        mc = Config()
        mc.yaml['beacon']
        mc.yaml.beacon
        mc.beacon
        mc.open()
    """

    def __init__(self, path: str = None):

        if path is None:
            path = Paths().config

        self.path = path
        with open(self.path, "r") as stream:
            try:
                self.yaml = DefaultMunch.fromDict(safe_load(stream)["default"])
            except YAMLError as exc:
                print(exc)
        for x in self.yaml:
            if isin("StoreName", list(self.yaml[x].keys())):
                self.yaml[x].SourceType = "Datalake"

            elif isin("Warehouse", list(self.yaml[x].keys())):
                self.yaml[x].SourceType = "BbSnowflake"

            elif isin("Database", list(self.yaml[x].keys())):
                self.yaml[x].SourceType = "Database"

            else:
                self.yaml[x].SourceType = "Other"

        ## Password Parser
        mpw = Password()

        pws = list(set([i["Password"] for i in self.yaml.values()]))
        pws = [
            re.sub(r"^.+\(\s*['\"]|['\"]\s*\)\s*$", "", i)
            for i in pws
            if str(i)[0:6] == "cl::pw"
        ]

        def catch(func, handle=lambda e: e, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return handle(e)

        pwl = {i: catch(lambda: mpw.get_password(i)) for i in pws}

        for x in self.yaml:
            if isin("Password", list(self.yaml[x].keys())):
                key = re.sub(r"^.+\(\s*['\"]|['\"]\s*\)\s*$", "", self.yaml[x].Password)
                if isin(key, list(pwl.keys())):
                    self.yaml[x].Password = pwl[
                        re.sub(
                            r"^.+\(\s*['\"]|['\"]\s*\)\s*$", "", self.yaml[x].Password
                        )
                    ]

        ## Available keys
        self.available = self.yaml.keys()

        for key, value in self.yaml.items():
            if key is not None and value is not None:
                setattr(self, key, value)

    def __repr__(self):
        nc = len(str(len(self.available)))
        x = [
            "{}. {}".format(str(i + 1).zfill(nc), k)
            for i, k in enumerate(self.available)
        ]
        return "\n".join(x)

    def open(self, location=False):
        opener(self.path, location=location)
