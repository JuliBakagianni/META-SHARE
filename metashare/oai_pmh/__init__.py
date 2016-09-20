# coding=utf-8
# pylint:
from collections import OrderedDict

from oaipmh.server import Server
from oaipmh.metadata import MetadataRegistry

from metashare.oai_pmh.oaipmh_server import OaiPmhServer
from metashare.settings import DJANGO_URL, ADMINS, METASHARE_VERSION, OAIPMH_URL
from metashare.oai_pmh.metadata_handlers import MetashareWriter, OlacWriter, \
    CmdiWriter
from metashare.oai_pmh._utils import *
from metashare.oai_pmh.oaipmh_verbs import *

def metadata_registry():
    registry = MetadataRegistry()
    registry.registerWriter('metashare', MetashareWriter())
    registry.registerWriter('olac', OlacWriter())
    registry.registerWriter('cmdi', CmdiWriter())
    return registry

# META-SHARE OAI-PMH server instantiation
__env_dict = {
    "repositoryName": u"META-SHARE {}".format(METASHARE_VERSION),
    "baseURL": OAIPMH_URL,
    "adminEmails": [admin[1] for admin in ADMINS],
}
oaipmh_server = Server(server=OaiPmhServer(__env_dict),
                       metadata_registry=metadata_registry(),
                       resumption_batch_size=1000)

#==========================
# Supported commands
#==========================
key_list_ids_for_import = u"List Identifiers (use for import)"
key_import = u"Import Resource(s)"
key_list_metadata_format = u"List Metadata Formats"

supported_commands = OrderedDict()
supported_commands[key_import] = harvest_from_GUI
supported_commands[key_list_ids_for_import] = ListIdentifiers

# available as separate buttons
supported_commands.update({
    u"List Records": ListRecords,
    u"Identify Server": Identify,
    u"List Sets": ListSets,
    key_list_metadata_format: ListMetadataFormats,
})
