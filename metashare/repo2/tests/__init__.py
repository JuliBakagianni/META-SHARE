# Get all individual unit tests together.
# Do it by hand for now;
# should we need something automatic, see here: http://djangosnippets.org/snippets/1972/

# Yes, pylint, we want wildcard imports here.
# pylint: disable-msg=W0401
from metashare.repo2.tests.test_editor import *
from metashare.repo2.tests.test_view import *
from metashare.repo2.tests.test_search import *
from metashare.repo2.tests.test_email import *
from metashare.repo2.tests.test_model import *
from metashare.repo2.tests.test_import import *
from metashare.repo2.tests.test_status_workflow import *