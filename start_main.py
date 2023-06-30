from scraper_functions import *
from main_scraper import *

'''The run_list specifies how many RSS feeds are scraped for that particular run. For example:

run_list = [0] would scrape the first n feeds specified for range 0. So if n = 5 and source = 'media', then the first 5 media feeds would be scraped.
run_list = [0,1] would scrape the first n feeds specified for range 0-1. So if n = 5 and source = 'media', then the first 10 media feeds would be scraped.
run_list = list(range(0, 1000)) would scrape the first n feeds for range 0-1000. So if n = 5 and source = 'media', then the first 5000 media feeds would be scraped.
'''

run_list = [0]
# run_list = list(range(0, 1000))

''' Parameters for RSS_Scraper include:
source (REQUIRED): the data source to use in the data_sources folder (e.g. companies, media, jpn_media, jpn_companies)
tag (OPTIONAL): use if you want to filter the data source by its tag (e.g. energy, env, metals, shipping, local, aviation)
entity (OPTIONAL): use if you want the scraper to run for a single entity only (e.g. The New York Times). DO NOT USE in conjunction with n_feeds or random_seed, or the scraper will fail to run.
n_feeds (OPTIONAL): use if you want to specify the number of feeds to scrape for this particular run. By default this is set to 5.
random_seed (OPTIONAL): use if you want a specific seed that you can replicate for future runs (i.e. if you want to pick out n random feeds to run and then run those exact same feeds again the next time)
number (REQUIRED): leave at 'number'
'''

for number in run_list:
    philo = RSS_Scraper(source = 'media',
                        # tag = 'energy',
                        # entity = 'All About Shipping',
                        n_feeds = 3,
                        random_seed = 28,
                        number = number)
    test = philo.start()

#If a file or files fail to upload to the server, they are sent to scraped_data/need/to_upload.
