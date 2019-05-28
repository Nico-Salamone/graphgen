import pkg_resources
import tempfile

# The path of resource files.
RESOURCE_PATH = pkg_resources.resource_filename(__name__, 'resources')

# The path of the folder containing all temporary files.
TEMP_PATH = tempfile.gettempdir()
