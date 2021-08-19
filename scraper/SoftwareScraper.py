from time import sleep
from selenium.webdriver.common.by import By
from seleniumwire import webdriver


class SoftwareScraper:
    def __init__(self, gecko_driver, download_folder, ublock_addon):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList', 2)
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream,application/x-msdownload,application/x-ms-installer,application/vnd.microsoft.portable-executable,application/zip,application/vnd.rar,application/x-7z-compressed')
        self.profile.set_preference('browser.download.dir', download_folder)
        self.driver = webdriver.Firefox(firefox_profile=self.profile, executable_path=gecko_driver)
        self.driver.install_addon(ublock_addon, temporary=True)


    def start_cnet(self):
        for page_num in range(1, 4099):
            site = f'https://download.cnet.com/windows/{page_num}/?sort=newReleases&price=free'
            print(f'Visiting {site}')
            self.driver.get(site)
            self.driver.implicitly_wait(10) # Wait for page to load.
            product_cards = self.driver.find_elements(By.CLASS_NAME, 'c-productCard_link')
            links = []
            # Get all download links.
            for card in product_cards:
                link = card.get_attribute('href')
                links.append(link)
            # Visit each download link.
            for link in links:
                self.driver.get(link)
                self.driver.implicitly_wait(10) # Wait for page to load.
                try:
                    # Only click button if it is a direct download link.
                    if self.driver.find_element_by_class_name('c-productActionButton_text').text == 'DOWNLOAD NOW':
                        self.driver.find_element_by_class_name('c-globalButton-standard').click()
                        print(f'Downloading {link}')
                except:
                    pass
                finally:
                    sleep(15) # Wait for download to start.
                    self.driver.implicitly_wait(45) # Wait longer if necessary.
        sleep(12) # Wait for last download.
        self.driver.close()
        print('Done')


    def start_portable_freeware(self):
        for i in range(0, 2974):
            site = f'https://www.portablefreeware.com/index.php?id={i}'
            print(f'Getting {site}')
            self.driver.get(site)
            self.driver.implicitly_wait(10) # Wait for site to load.
            try:
                download_div = driver.find_element_by_class_name('download')
                external = download_div.find_element_by_class_name('external')
                driver.execute_script("arguments[0].target='_self';", external) # Prevent opening new tabs/windows
                external.click()
            except:
                print('Warning: Could not find ^')
            finally:
                sleep(5)
        sleep(120) # Wait for last download to complete.
        self.driver.close()
        print('Done')


    def start_softpedia(self):
        for page_num in range(25, 31):
            site = f'https://win.softpedia.com/index{page_num}.free.shtml?scroll_flt'
            print(f'Visiting {site}')
            self.driver.get(site)
            self.driver.implicitly_wait(10) # Wait for page to load.
            items = self.driver.find_elements(By.CLASS_NAME, 'dlcls')
            links = []
            # Get all download links
            for item in items:
                h4 = item.find_element_by_tag_name('h4')
                a = h4.find_element_by_tag_name('a')
                link = a.get_attribute('href') + '#download'
                links.append(link)
            # Visit each downlaod link.
            for link in links:
                print(f'Downloading {link}')
                self.driver.get(link)
                self.driver.implicitly_wait(10) # Wait for page to load.
                try:
                    dl_linkbox = driver.find_element_by_class_name('dllinkbox2')
                    dl_linkbox.click()
                    driver.implicitly_wait(10)
                    manstart = driver.find_element_by_id('manstart')
                    a = manstart.find_element_by_tag_name('a')
                    dl_link = a.get_attribute('href')
                    driver.get(dl_link)
                except:
                    pass
                finally:
                    sleep(15)
                    self.driver.implicitly_wait(45) # Wait longer if necessary for download to start.
        sleep(120) # Wait for last download
        self.driver.close()
        print('Done')
