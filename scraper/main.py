from SoftwareScraper import SoftwareScraper

GECKO_DRIVER = '/Users/brandonlou/Projects/MLSEC_2021/scraper/geckodriver'
DOWNLOAD_DIR = '/Users/brandonlou/Projects/MLSEC_2021/scraper/cnet_downloads'
UBLOCK_ADDON = '/Users/brandonlou/Projects/MLSEC_2021/scraper/uBlock0_1.37.2.firefox.xpi'


def main():
    software_scraper = SoftwareScraper(GECKO_DRIVER, DOWNLOAD_DIR, UBLOCK_ADDON)
    software_scraper.start_cnet()


if __name__ == '__main__':
    main()
