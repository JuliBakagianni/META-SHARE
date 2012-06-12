'''
Created on 29.05.2012

@author: steffen
'''
from django.core.management import call_command
from django.test.testcases import TestCase
from metashare import settings, test_utils
from metashare.repository.models import resourceInfoType_model
from metashare.settings import ROOT_PATH, LOG_LEVEL, LOG_HANDLER
from metashare.storage.models import StorageObject, restore_from_folder, \
MASTER, INGESTED, INTERNAL, update_digests
# pylint: disable-msg=E0611
from hashlib import md5
import os.path
import zipfile
from xml.etree.ElementTree import ParseError
import shutil
import time
import logging

TESTFIXTURE_XML = '{}/repository/fixtures/ILSP10.xml'.format(ROOT_PATH)


# Setup logging support.
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger('metashare.repository.tests')
LOGGER.addHandler(LOG_HANDLER)

def copy_fixtures():
    """
    Copies the test fixtures to the storage folder.
    """
    _fixture_folder = '{0}/storage/test_fixtures'.format(settings.ROOT_PATH)
    for fixture_name in os.listdir(_fixture_folder):
        shutil.copytree(
          os.path.join(_fixture_folder, fixture_name),
          os.path.join(settings.STORAGE_PATH, fixture_name))
          
def cleanup_storage():
    """
    Deletes the content of the storage folder.
    """
    for _folder in os.listdir(settings.STORAGE_PATH):
        for _file in os.listdir(os.path.join(settings.STORAGE_PATH, _folder)):
            os.remove(os.path.join(settings.STORAGE_PATH, _folder, _file))
        os.rmdir(os.path.join(settings.STORAGE_PATH, _folder))


class PersistenceTest(TestCase):
    """
    Tests persistence methods for saving data to the storage folder.
    """
    
    @classmethod
    def setUpClass(cls):
        test_utils.setup_test_storage()
        # copy fixtures to storage folder
        copy_fixtures()
        
    @classmethod
    def tearDownClass(cls):
        # delete content of storage folder
        cleanup_storage()
    
    def setUp(self):
        # make sure the index does not contain any stale entries
        call_command('rebuild_index', interactive=False, using=settings.TEST_MODE_NAME)
        # make sure all resources and storage objects are deleted
        resourceInfoType_model.objects.all().delete()
        StorageObject.objects.all().delete()
        
    def tearDown(self):
        resourceInfoType_model.objects.all().delete()
        StorageObject.objects.all().delete()

    def test_save_metadata(self):
        """
        Tests that the metadata XML is not written to the storage folder for internal
        resources but only when the resource is ingested
        """
        # load test fixture; its initial status is 'internal'
        _result = test_utils.import_xml(TESTFIXTURE_XML)
        resource = resourceInfoType_model.objects.get(pk=_result[0].id)
        _storage_object = resource.storage_object
        _storage_object.update_storage()
        # initial status is 'internal'
        self.assertTrue(_storage_object.publication_status == INTERNAL)
        # internal resource has no metadata XML stored in storage folder
        self.assertFalse(
          os.path.isfile('{0}/metadata-{1:04d}.xml'.format(
                  _storage_object._storage_folder(), _storage_object.revision)))
        # set status to ingested
        _storage_object.publication_status = INGESTED
        _storage_object.update_storage()
        # ingested resource has metadata XML stored in storage folder
        self.assertTrue(
          os.path.isfile('{0}/metadata-{1:04d}.xml'.format(
            _storage_object._storage_folder(), _storage_object.revision)))
        # ingested resource has global part of storage object in storage folder
        self.assertTrue(
          os.path.isfile('{0}/storage-global.json'.format(
            _storage_object._storage_folder())))
        # ingested resource has local part of storage object in storage folder
        self.assertTrue(
          os.path.isfile('{0}/storage-local.json'.format(
            _storage_object._storage_folder())))
        # ingested resource has digest zip in storage folder
        self.assertTrue(
          os.path.isfile('{0}/resource.zip'.format(
            _storage_object._storage_folder())))
        # digest zip contains metadata.xml and storage-global.json
        _zf_name = '{0}/resource.zip'.format( _storage_object._storage_folder())
        _zf = zipfile.ZipFile(_zf_name, mode='r')
        self.assertTrue('metadata.xml' in _zf.namelist())
        self.assertTrue('storage-global.json' in _zf.namelist())
        # md5 of digest zip is stored in storage object
        _checksum = md5()
        with open(_zf_name, 'rb') as _zf_reader:
            _checksum.update(_zf_reader.read())
        self.assertEqual(_checksum.hexdigest(), _storage_object.digest_checksum)


class RestoreTest(TestCase):
    """
    Tests method for restoring resource and storage object from storage folder.
    """
    
    @classmethod
    def setUpClass(cls):
        test_utils.setup_test_storage()
        # copy fixtures to storage folder
        copy_fixtures()
        
    @classmethod
    def tearDownClass(cls):
        # delete content of storage folder
        cleanup_storage()
    
    def setUp(self):
        # make sure the index does not contain any stale entries
        call_command('rebuild_index', interactive=False, using=settings.TEST_MODE_NAME)
        # make sure all resources and storage objects are deleted
        resourceInfoType_model.objects.all().delete()
        StorageObject.objects.all().delete()
        
    def tearDown(self):
        resourceInfoType_model.objects.all().delete()
        StorageObject.objects.all().delete()

    def test_valid_restore(self):
        """
        Tests restoring from storage folder with valid content.
        """
        resource = restore_from_folder(
          '2e6ed4b0af2d11e192dc005056c00008ce474a763e0e4b618e01d15170593630')
        # check that there is 1 storage object and 1 resource in the database
        self.assertEqual(len(StorageObject.objects.all()), 1)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 1)
        # check identifier
        self.assertEqual(resource.storage_object.identifier, 
          '2e6ed4b0af2d11e192dc005056c00008ce474a763e0e4b618e01d15170593630')
        # check copy status
        self.assertEqual(resource.storage_object.copy_status, MASTER)
        
        # restore the same resource again, check that duplicate detection works
        resource = restore_from_folder(
          '2e6ed4b0af2d11e192dc005056c00008ce474a763e0e4b618e01d15170593630', MASTER)
        # check that there is still 1 storage object and 1 resource in the database
        self.assertEqual(len(StorageObject.objects.all()), 1)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 1)
        # check copy status
        self.assertEqual(resource.storage_object.copy_status, MASTER)
        
        # delete storage object; this also deletes the resource
        resource.storage_object.delete()
        self.assertEqual(len(StorageObject.objects.all()), 0)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 0)

    def test_invalid_restore(self):
        """
        Tests restoring from storage folder with invalid XML.
        """
        self.assertRaises(ParseError, 
          restore_from_folder,
          '3b305b40af4311e18673005056c0000826bc07611017478d87046dca78d3c603'
          )
        # make sure there is nothing in the db
        self.assertEqual(len(StorageObject.objects.all()), 0)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 0)
    
    def test_missing_metadata(self):
        """
        Tests restoring from storage folder with missing metadata XML.
        """
        self.assertRaises(Exception, 
          restore_from_folder,
          '4e1da1deaf4311e19ca7005056c00008cf98a6721df14cd5b52a307e57ec2b7a'
          )
        # make sure there is nothing in the db
        self.assertEqual(len(StorageObject.objects.all()), 0)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 0)
        
    def test_missing_global(self):
        """
        Tests restoring from storage folder with missing storage-global.json.
        """
        # keep copy of old storage-local.json as it will be overwritten 
        # during the test
        storage_folder = os.path.join(
          settings.STORAGE_PATH,
          '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
        with open('{0}/storage-local.json'.format(storage_folder), 'rb') as _in:
            json_string = _in.read()
        
        resource = restore_from_folder(
          '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
          )
        # importing successful, but is imported as new
        self.assertEquals(resource.storage_object.copy_status, MASTER)
        self.assertEquals(resource.storage_object.publication_status, INTERNAL)
        # revision is only increased when the resource is ingested
        self.assertEquals(resource.storage_object.revision, 0)
        # ingest resource
        resource.storage_object.publication_status = INGESTED
        resource.storage_object.save()
        resource.storage_object.update_storage()
        # delete newly created storage-local.json and resource.zip
        # and restore storage-local.json
        os.remove('{0}/storage-global.json'.format(storage_folder))
        os.remove('{0}/resource.zip'.format(storage_folder))
        with open('{0}/storage-local.json'.format(storage_folder), 'wb') as _out:
            _out.write(json_string)

        self.assertEquals(resource.storage_object.publication_status, INGESTED)
        self.assertEquals(resource.storage_object.revision, 1)
        self.assertEqual(len(StorageObject.objects.all()), 1)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 1)
        
        # delete storage object; this also deletes the resource
        resource.storage_object.delete()
        self.assertEqual(len(StorageObject.objects.all()), 0)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 0)

    def test_missing_local(self):
        """
        Tests restoring from storage folder with missing storage-local.json.
        """
        resource = restore_from_folder(
          '6c28ac1eaf4311e1b3d3005056c000083e35d6e955534994aac84d959266465a'
          )
        # delete newly created storage-local.json
        os.remove('{0}/{1}/storage-local.json'.format(
          settings.STORAGE_PATH, resource.storage_object.identifier))

        # default copy status MASTER is used
        self.assertEqual(resource.storage_object.copy_status, MASTER)
        
        # delete storage object; this also deletes the resource
        resource.storage_object.delete()
        self.assertEqual(len(StorageObject.objects.all()), 0)
        self.assertEqual(len(resourceInfoType_model.objects.all()), 0)
   
     
class UpdateTest(TestCase):
    """
    Tests updating of metadata XML and storage object serialization
    """
    
    @classmethod
    def setUpClass(cls):
        test_utils.setup_test_storage()

    @classmethod
    def tearDownClass(cls):
        # delete content of storage folder
        cleanup_storage()
    
    def setUp(self):
        # make sure the index does not contain any stale entries
        call_command('rebuild_index', interactive=False, using=settings.TEST_MODE_NAME)
        # make sure all resources and storage objects are deleted
        resourceInfoType_model.objects.all().delete()
        StorageObject.objects.all().delete()
        
    def tearDown(self):
        resourceInfoType_model.objects.all().delete()
        StorageObject.objects.all().delete()
        
    def test_update(self):
        # define maximum age of 4 seconds; this means that every 2 seconds an
        # update check is done
        settings.MAX_DIGEST_AGE = 4
        # import resource
        _result = test_utils.import_xml(TESTFIXTURE_XML)
        _so = resourceInfoType_model.objects.get(pk=_result[0].id).storage_object
        self.assertIsNone(_so.digest_last_checked)
        # set status to ingested
        _so.publication_status = INGESTED
        _so.update_storage()
        _so = resourceInfoType_model.objects.get(pk=_result[0].id).storage_object
        self.assertIsNotNone(_so.digest_last_checked)
        _last_checked = _so.digest_last_checked
        _modified = _so.digest_modified
        # check if update is required
        update_digests()
        _so = resourceInfoType_model.objects.get(pk=_result[0].id).storage_object
        # check that digest was not updated
        self.assertEquals(_modified, _so.digest_modified)
        self.assertEquals(_last_checked, _so.digest_last_checked)
        # wait 3 seconds and check again
        time.sleep(3)
        LOGGER.info('1------- {}'.format(_so.digest_last_checked))
        update_digests()
        _so = resourceInfoType_model.objects.get(pk=_result[0].id).storage_object
        LOGGER.info('2------- {}'.format(_so.digest_last_checked))
        # now an update should have happened, but the underlying data has not 
        # changed, so digest_modified is not changed
        self.assertEquals(_modified, _so.digest_modified)
        self.assertNotEqual(_last_checked, _so.digest_last_checked)
