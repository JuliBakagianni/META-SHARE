from django_selenium.testcases import SeleniumTestCase
from metashare import settings, test_utils
from metashare.repository.seltests.test_utils import setup_screenshots_folder, import_dir
from metashare.settings import DJANGO_BASE, ROOT_PATH
from selenium import webdriver
import time
from django.core.management import call_command
from metashare.repository.models import resourceInfoType_model


TESTFIXTURE_XML = '{}/repository/test_fixtures/ELRA/'.format(ROOT_PATH)

class FilterTest(SeleniumTestCase):

    def setUp(self):
        # make sure the index does not contain any stale entries
        call_command('rebuild_index', interactive=False, using=settings.TEST_MODE_NAME)
        # load test fixture; status will be set 'published'
        test_utils.setup_test_storage()
        import_dir(TESTFIXTURE_XML)
        
        # init Selenium
        driver = getattr(webdriver, settings.SELENIUM_DRIVER, None)
        assert driver, "settings.SELENIUM_DRIVER contains non-existing driver"
        self.driver = driver()
        self.driver.implicitly_wait(30)
        host = getattr(settings, 'SELENIUM_TESTSERVER_HOST', 'localhost')
        port = getattr(settings, 'SELENIUM_TESTSERVER_PORT', 8000)
        self.base_url = 'http://{0}:{1}/{2}'.format(host, port, DJANGO_BASE)
        self.verification_errors = []


    def tearDown(self):
        resourceInfoType_model.objects.all().delete()
        
        # clean up Selenium
        self.driver.quit()
        self.assertEqual([], self.verification_errors)
        

    def test_filter(self):
        ss_path = setup_screenshots_folder(
          "PNG-metashare.repository.seltests.test_editor.FilterTest",
          "test_filter")

        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_id("browse").click()
        driver.get_screenshot_as_file('{0}/{1}.png'.format(ss_path, time.time()))
        self.assertEqual("17 Language Resources", driver.find_element_by_css_selector("h3").text)
        # make sure all filters are available
        self.assertEqual("Availability", driver.find_element_by_link_text("Availability").text)
        self.assertEqual("Language", driver.find_element_by_link_text("Language").text)
        self.assertEqual("Licence", driver.find_element_by_link_text("Licence").text)
        self.assertEqual("Linguality Type", driver.find_element_by_link_text("Linguality Type").text)
        self.assertEqual("Media Type", driver.find_element_by_link_text("Media Type").text)
        self.assertEqual("MIME Type", driver.find_element_by_link_text("MIME Type").text)
        self.assertEqual("Resource Type", driver.find_element_by_link_text("Resource Type").text)
        self.assertEqual("Restrictions of Use", driver.find_element_by_link_text("Restrictions of Use").text)
        # check Availability filter
        driver.find_element_by_link_text("Availability").click()
        self.assertEqual("available-restrictedUse (17)", driver.find_element_by_css_selector("dd").text)
        driver.find_element_by_link_text("Availability").click()
        # check Language filter
        driver.find_element_by_link_text("Language").click()
        self.assertEqual("English (8)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[2]").text)
        self.assertEqual("Spanish (6)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[3]").text)
        self.assertEqual("French (3)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[4]").text)
        self.assertEqual("Italian (3)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[5]").text)
        self.assertEqual("German (2)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[6]").text)
        self.assertEqual("Portuguese (2)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[7]").text)
        self.assertEqual("Arabic (1)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[8]").text)
        self.assertEqual("Chinese (1)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[9]").text)
        self.assertEqual("Estonian (1)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[10]").text)
        self.assertEqual("Thai (1)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[11]").text)
        self.assertEqual("Turkish (1)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[12]").text)
        self.assertEqual("more", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[13]").text)
        # check language filter more/less 
        driver.find_element_by_link_text("more").click()
        self.assertEqual("less", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[13]").text)
        driver.find_element_by_link_text("less").click()
        self.assertEqual("more", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[13]").text)
        driver.find_element_by_link_text("Language").click()
        # check Licence filter
        driver.find_element_by_link_text("Licence").click()
        self.assertEqual("ELRA_VAR (14)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[14]").text)
        self.assertEqual("ELRA_END_USER (13)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[15]").text)
        self.assertEqual("ELRA_EVALUATION (3)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[16]").text)
        driver.find_element_by_link_text("Licence").click()
        # check Linguality Type filter        
        driver.find_element_by_link_text("Linguality Type").click()
        self.assertEqual("monolingual (17)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[17]").text)
        driver.find_element_by_link_text("Linguality Type").click()
        # check Media Type filter        
        driver.find_element_by_link_text("Media Type").click()
        self.assertEqual("text (11)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[18]").text)
        self.assertEqual("audio (6)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[19]").text)
        driver.find_element_by_link_text("Media Type").click()
        # check MIME Type filter        
        driver.find_element_by_link_text("MIME Type").click()
        self.assertEqual("Plain text (2)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[20]").text)
        driver.find_element_by_link_text("MIME Type").click()
        # check Resource Type filter        
        driver.find_element_by_link_text("Resource Type").click()
        self.assertEqual("lexicalConceptualResource (9)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[21]").text)
        self.assertEqual("corpus (8)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[22]").text)
        driver.find_element_by_link_text("Resource Type").click()
        # check Restrictions of Use filter        
        driver.find_element_by_link_text("Restrictions of Use").click()
        self.assertEqual("commercialUse (14)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[23]").text)
        self.assertEqual("academic-nonCommercialUse (13)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[24]").text)
        self.assertEqual("evaluationUse (3)", driver.find_element_by_xpath(
          "//dl[@id='searchFilters']/dd[25]").text)
        driver.find_element_by_link_text("Restrictions of Use").click()
        
        # test sorting:
        # default sorting is by resource name, ascending
        self.assertEqual("sortDesc", driver.find_element_by_xpath(
          "//a[contains(text(),'Resource Name')]").get_attribute("class"))
        self.assertEqual("AURORA-5", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/th/a").text)
        # now sort by Resource name descending
        driver.find_element_by_link_text("Resource Name").click()
        self.assertEqual("sortAsc", driver.find_element_by_xpath(
          "//a[contains(text(),'Resource Name')]").get_attribute("class"))
        self.assertEqual("VERBA Polytechnic and Plurilingual Terminological Database - S-AA Anatomy", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/th/a").text)
        # now sort by resource type ascending
        driver.find_element_by_xpath("(//a[contains(text(),'Resource Type')])[2]").click()
        self.assertEqual("sortDesc", driver.find_element_by_xpath(
          "(//a[contains(text(),'Resource Type')])[2]").get_attribute("class"))
        self.assertEqual("Corpus", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/td/img/title").text)
        # now sort by resource type descending
        driver.find_element_by_xpath("(//a[contains(text(),'Resource Type')])[2]").click() 
        self.assertEqual("sortAsc", driver.find_element_by_xpath(
          "(//a[contains(text(),'Resource Type')])[2]").get_attribute("class"))
        self.assertEqual("Lexical/Conceptual", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/td/img").text)
        # now sort by media type ascending
        driver.find_element_by_link_text("Media Type(s)").click()
        self.assertEqual("sortDesc", driver.find_element_by_link_text(
          "Media Type(s)").get_attribute("class"))
        self.assertEqual("audio", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/td[2]/img").get_attribute("title"))
        # now sort by media type descending
        driver.find_element_by_link_text("Media Type(s)").click()
        self.assertEqual("sortAsc", driver.find_element_by_link_text(
          "Media Type(s)").get_attribute("class"))
        self.assertEqual("text", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/td[2]/img").get_attribute("title"))
        # now sort by language ascending
        driver.find_element_by_link_text("Language(s)").click()
        self.assertEqual("sortDesc", driver.find_element_by_link_text(
          "Language(s)").get_attribute("class"))
        self.assertEqual("Arabic, English, French", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/td[3]").text)
        # now sort by language descending
        driver.find_element_by_link_text("Language(s)").click()
        self.assertEqual("sortAsc", driver.find_element_by_link_text(
          "Language(s)").get_attribute("class"))
        self.assertEqual("Turkish", driver.find_element_by_xpath(
          "//table[@class='result_table']/tbody/tr[2]/td[3]").text)
        driver.get_screenshot_as_file('{0}/{1}.png'.format(ss_path, time.time()))

        # test filter application:
        # filter by language English
        driver.find_element_by_link_text("Language").click()
        driver.find_element_by_link_text("English").click()
        self.assertEqual("8 Language Resources", driver.find_element_by_css_selector("h3").text)
        # additionally filter by license
        driver.find_element_by_link_text("Licence").click()
        driver.find_element_by_link_text("ELRA_VAR").click()
        self.assertEqual("5 Language Resources", driver.find_element_by_css_selector("h3").text)
        # addtionally filter by media type
        driver.find_element_by_link_text("Media Type").click()
        driver.find_element_by_link_text("text").click()
        self.assertEqual("4 Language Resources", driver.find_element_by_css_selector("h3").text)
        # additionally filter by restriction of use
        driver.find_element_by_link_text("Restrictions of Use").click()
        driver.find_element_by_link_text("commercialUse").click()
        self.assertEqual("4 Language Resources", driver.find_element_by_css_selector("h3").text)
        driver.get_screenshot_as_file('{0}/{1}.png'.format(ss_path, time.time()))
        # remove language filter
        driver.find_element_by_link_text("English").click()
        self.assertEqual("9 Language Resources", driver.find_element_by_css_selector("h3").text)
        # remove license filter
        driver.find_element_by_link_text("ELRA_VAR").click()
        self.assertEqual("9 Language Resources", driver.find_element_by_css_selector("h3").text)
        # remove media type filter
        driver.find_element_by_link_text("text").click()
        self.assertEqual("14 Language Resources", driver.find_element_by_css_selector("h3").text)
        # remove restiriction of use filter
        driver.find_element_by_link_text("commercialUse").click()
        self.assertEqual("17 Language Resources", driver.find_element_by_css_selector("h3").text)
        driver.get_screenshot_as_file('{0}/{1}.png'.format(ss_path, time.time()))
        
        
