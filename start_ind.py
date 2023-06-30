from scraper_functions import *
from ind_scraper import *


'''The Update_Stories class loads in a source of RSS feeds, checks it for feeds that do not have any associated html elements with it, and opens up
the nth link from that feed

Parameters to load in include:
source (REQUIRED): the data source to use in the data_sources folder (e.g. companies, media, jpn_media, jpn_companies)
tag (OPTIONAL): use if you want to filter the data source by its tag (e.g. energy, env, metals, shipping, local, aviation)
feed_number (REQUIRED): the nth feed that you want to use from the source in order. In the example below we have loaded in the third feed from media with an env tag that does not have any html elements associated with it.
'''

feed_source = 'media'
ban = Update_Stories(source = feed_source,
                     tag = 'env',
                     feed_number = 14,
                     n=0)
booga = ban.start()
id = ban.get_feed_id()
feed = ban.get_feed_url()




'''The Get_HTML_Elements class takes in an element name, attribute name, and attribute content, runs it through BeautifulSoup, and produces output.
Ideally this output is equivalent to the full text of the story. If not, then try again.'''


ename = "article"
aname = "class"
acon = "post"
site = Get_HTML_Elements(source = feed_source,
                         feed = feed,
                         n = 0,
                         element_name =  ename,
                         attribute_name = aname,
                         attribute_content= acon)
site2 = site.start()





''' Check_HTML_Valid looks to see if the provided elements and attributes work for every link in the feed.'''
chec = Check_HTML_Valid(source = feed_source,
                        entity_id = id,
                        element_name = ename,
                        attribute_name = aname,
                        attribute_content = acon)
chec2 = chec.start()





'''Update_HTML updates the list of html elements for the feed that we have just checked and stores it to our database.'''
'''Updates list of html elements for each entity'''
bb = Update_HTML(source = feed_source,
                 entity_id = id,
                 element_name = ename,
                 attribute_name = aname,
                 attribute_content = acon)
bb2 = bb.start()
