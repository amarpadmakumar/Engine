from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper, printTop50, subdomains
import time
import GV


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        i = 0
        while True:
            i += 1
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                print(f'Max words on URL: {GV.urlMax[0]} - {GV.urlMax[1]}')
                printTop50(GV.allWords)
                print("Number of URLs:", len(GV.allURLs))
                subdomains(GV.allURLs)
 #               print(GV.allURLs)
                break
            try:
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"{i} : Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
            except:
                resp = None
                continue
            if resp != None:
                scraped_urls = scraper(tbd_url, resp)
            else:
                scraped_urls = []
            for scraped_url in scraped_urls:
##                print(scraped_url)
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
