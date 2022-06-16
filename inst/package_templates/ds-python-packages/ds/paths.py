import os
import re
import sys
import subprocess
import warnings


class Paths:
    """Create a Data Science Paths Object

    Create an object with user path attributes.  If the attribute is a path (all except 'home') it will inherit path action methods.

    Attributes:
        sys_drive: The primary hard drive in a computer, which contains the machine's operating system and other the software
        home: The path to the user's home directory
        user: The username associated with the home directory; the only non-path attribute
        desktop: The path to the user's desktop
        config: The path to the user's config file (used for storing credentials); found in the user's home directory
        onedrive: The path to the user's OneDrive folder
        downloads: The path to the user's downloads folder
        sharepoint: The path to the user's data science SharePoint projects folder
        admin: The path to the administration folder named '`Data_Science' in the data science SharePoint projects folder
        templates: The path to the data science templates folder in the data science SharePoint projects folder
        workflow: The path to the data science workflow folder in the data science SharePoint projects folder
        sprint: The path to the data science sprint folder in the data science SharePoint projects folder
        library: The path to the data science library folder in the data science SharePoint projects folder

    Inherited Path Methods:
        open: Open the path (file or folder) using the default OS tools associated with that file or folder; use `location = True` to open the parent directory of the path
        exists: Logical; if True then the path exists on the operating system
        type: One of 'file', 'directory', or None

    Examples::

        from ds import Paths
        mp = Paths()
        mp.home
        mp.home.type()
        mp.class_attrs()
        mp.config
        mp.config.exists()
        mp.sys_drive
        mp.onedrive
        mp.desktop
        mp.downloads
        mp.sharepoint

    """

    def __init__(self):

        atts = {
            "home": [],
            "sys_drive": [],
            "config": [],
            "onedrive": [],
            "desktop": [],
            "downloads": [],
            "sharepoint": [],
            "admin": [],
            "templates": [],
            "workflow": [],
            "sprint": [],
            "library": [],
        }

        if sys.platform == "darwin":
            atts["home"].append(os.path.join("/Users", os.environ["USER"]))
            atts["sys_drive"].append("/")
            atts["onedrive"].append(
                os.path.join(
                    atts["home"][0], "Library/CloudStorage/OneDrive-AnthologyInc"
                )
            )
            atts["sharepoint"].append(
                os.path.join(
                    atts["home"][0],
                    "Library/CloudStorage/OneDrive-SharedLibraries-AnthologyInc/DataScienceProjects (CL) - General",
                )
            )
        elif sys.platform.startswith("win") == True:
            atts["home"].append(os.environ["USERPROFILE"].replace(os.sep, "/"))
            atts["sys_drive"].append(re.sub("/.*$", "", atts["home"][0]) + "/")
            atts["onedrive"].append(
                os.path.join(atts["home"][0], "OneDrive - Anthology Inc")
            )
            atts["sharepoint"].append(
                os.path.join(
                    atts["home"][0], "Anthology Inc/DataScienceProjects (CL) - General"
                )
            )
        else:
            atts["home"].append(os.environ["USER"])

        atts["config"].append(os.path.join(atts["home"][0], ".clconfig.txt"))

        if sys.platform == "darwin":
            atts["desktop"].append(os.path.join(atts["home"][0], "Desktop"))
        else:
            atts["desktop"].append(os.path.join(atts["onedrive"][0], "Desktop"))

        atts["downloads"].append(os.path.join(atts["home"][0], "Downloads"))
        atts["admin"].append(os.path.join(atts["sharepoint"][0], "`Data_Science"))
        atts["templates"].append(
            os.path.join(atts["admin"][0], "`Tools_Maintenance/`Templates")
        )
        atts["workflow"].append(os.path.join(atts["admin"][0], "`Workflow"))
        atts["sprint"].append(os.path.join(atts["workflow"][0], "`Sprint_Planning"))
        atts["library"].append(os.path.join(atts["admin"][0], "`The_Library"))

        for key, value in atts.items():
            if key is not None and value is not None:
                setattr(
                    self,
                    key,
                    _PathActions(_if_not_exists_warn(value[0].replace(os.sep, "/"))),
                )
        self.user = os.path.basename(atts["home"][0])

        if sys.platform == "darwin":
            self.os = "Mac"
        elif sys.platform.startswith("win") == True:
            self.os = "Windows"
        else:
            self.os = "Linux"

    def class_attrs(self):
        return vars(self)

    def norm(self):
        return win_fix(self)

    def __repr__(self):
        available = vars(self)
        nc = len(str(len(available)))
        x = ["{}. {}".format(str(i + 1).zfill(nc), k) for i, k in enumerate(available)]
        return "\n".join(x)


# Function to normalize paths
def win_fix(x):
    """Normalize Paths

    Parameters:
        x: A path to a file or directory.

    Returns:
        str: A normalized path with forward slashes.

    """
    x = os.path.abspath(x).replace(os.sep, "/")

    return x


# Function to open files and folders independent of OS
def opener(x, location=False):
    """Open Files and Directories

    Parameters:
        x: A path to a file or directory.
        location: Logical; if True, the parent directory is opened

    Returns:
        str: While the function is used mainly for its side effects, it returns the input path or parent directory if `location = True`

    """
    x = os.path.abspath(x)

    if location:
        x = os.path.dirname(x)

    if not os.path.exists(x):
        raise Exception("Path for `x` does not exist")

    if sys.platform.startswith("win") == True:
        os.startfile(x)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, x])

    return x


# Helper class to give paths associated methods
class _PathActions(str):
    def __init__(self, path=False):
        self.path = path

    # Open the path's file or folder
    def open(self, location=False):
        return opener(self.path, location=location)

    # Logical detection idf the path exists
    def exists(self):
        return os.path.exists(self.path)

    ##
    def join(self, x):
        val = os.path.join(self.path, x)
        return _PathActions(_if_not_exists_warn(val.replace(os.sep, "/")))

    # Return if the path is a file, folder, or None
    def type(self):
        if os.path.isfile(self.path):
            return "file"
        elif os.path.isdir(self.path):
            return "directory"
        else:
            return None


# Helper function to warn about non-existent paths
def _if_not_exists_warn(x):
    if not os.path.exists(x):
        warnings.warn("'{}' does not exist as a real path".format(x))

    return x
