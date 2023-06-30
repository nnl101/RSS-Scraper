# Individual Feed Scraper
import pandas as pd
import json
import feedparser
from scraper_functions import *
from bs4 import BeautifulSoup
import html2text
import requests
import webbrowser
import operator
from collections import Counter
from pathlib import Path

'''checks list of rss feeds and returns feeds that still need html elements to scrape their websites'''
# class CheckFeeds:
#     def __init__(self, **kwargs):
#         self.source = kwargs.get('source')
#         self.pat = Path("./data_sources/" + self.source)
#
#     def start(self):
#         ''' loads a csv with rss feeds. change these columns to import other columns '''
#         feeds = pd.read_csv(str(self.pat) + '.csv')
#         feeds = feeds[feeds['rss'].notna()]
#         feeds = feeds[feeds['element_name'].isnull()]
#         feeds['ID'] = feeds['ID'].astype(float)
#
#         feed = feeds['rss'].iloc[0]
#
#         print('There are', len(feeds), 'RSS feeds without html elements. First off is\n', feed)
#         return feed
#
#     # def start(self):
#     #     feed_list = self.load_rss_feeds()
#     #     html_elements_list = open_json(str(self.pat) + '_html_elements.json')
#     #
#     #     html_elements = pd.json_normalize(html_elements_list)
#     #     df = pd.merge(feed_list, html_elements, how='left', on='ID')
#     #     is_NaN = df.isnull()
#     #
#     #     row_has_NaN = is_NaN.any(axis=1)
#     #     rows_with_NaN = df[row_has_NaN]
#     #     total_rows = rows_with_NaN.shape[0]
#     #
#     #     print('There are', total_rows, 'RSS feeds without html elements:')
#     #     print(rows_with_NaN['ID'])



class Update_Stories(object):
    def __init__(self, **kwargs):
        self.source = kwargs.get('source')
        self.tag = kwargs.get('tag')
        self.feed_number = kwargs.get('feed_number')
        self.pat = Path("./data_sources/" + self.source)
        # self.entity_id = kwargs.get('entity_id')
        self.n = kwargs.get('n')

    def get_feed_url(self):
        feeds = pd.read_csv(str(self.pat) + '.csv')
        feeds = feeds[feeds['rss'].notna()]
        feeds = feeds[feeds['element_name'].isnull()]
        feeds = feeds[feeds['tags'].str.contains(self.tag, na = False)]
        feeds['ID'] = feeds['ID'].astype(float)
        feed = feeds['rss'].iloc[self.feed_number]
        self.name = feeds['Name'].iloc[self.feed_number]
        self.feed_length = len(feeds)

        return feed

    def get_feed_id(self):
        feeds = pd.read_csv(str(self.pat) + '.csv')
        feeds = feeds[feeds['rss'].notna()]
        feeds = feeds[feeds['element_name'].isnull()]
        feeds = feeds[feeds['tags'].str.contains(self.tag, na = False)]
        feeds['ID'] = feeds['ID'].astype(float)
        feed_id = feeds['ID'].iloc[self.feed_number]

        return feed_id

    def start(self):
        feed_id = self.get_feed_id()
        rss_url = self.get_feed_url()

        # when_last_checked = open_json(str(self.pat) + '_last_checked.json')
        # feeds = self.load_rss_feeds()
        feed = feedparser.parse(rss_url)

        if 'status' not in feed:
            print("There was no feed status. Check out what's going on with ", rss_url)
            return

        elif feed.status == 200 and feed.bozo == 0:
            if len(feed.entries) == 0:
                print('ERROR! this feed', rss_url, 'has no entries.')
            else:
                url = feed.entries[self.n]['link']
            # print(rss_url)
        elif "not well-formed" in str(feed.bozo_exception):
            rss1 = requests.get(rss_url).content.decode("utf-16")
            rss1 = rss1.replace("utf-16", "unicode")
            feed = feedparser.parse(rss1)
            print(feed)
            url = feed.entries[self.n]['link']
            # print(rss_url)
        elif feed.status == 200 and feed.bozo == 3:
            print("Feed Parse Error:", feed.bozo_exception)
        else:
            print("Bad URL:", feed.status)

        if self.tag is not None:
            print('There are', self.feed_length, self.tag, 'RSS feeds without html elements. \n Getting', self.name, ':')
        else:
            print('There are', self.feed_length, 'RSS feeds without html elements. \n Getting',self.name, ':')

        self.open_feed_url(feed)

    '''opens a link from a given feed'''
    def open_feed_url(self, feed):
        url = feed.entries[self.n]['link']
        print(url)
        webbrowser.open(url)
        return url







class Get_HTML_Elements(Update_Stories):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feed = kwargs.get('feed')
        self.ename = kwargs.get('element_name')
        self.aname = kwargs.get('attribute_name')
        self.acon = kwargs.get('attribute_content')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}

    def start(self):
        parsed_feed = feedparser.parse(self.feed)
        url = parsed_feed.entries[self.n]['link']

        try:
            response = requests.get(url, timeout = 10, headers = self.headers)
            response.text
            soup = BeautifulSoup(response.text, 'html.parser')
            # print(soup)
            content = html2text.html2text(str(soup.find(self.ename, attrs={self.aname: self.acon})))
            print(content)
            return content
        except requests.exceptions.ConnectionError:
            print("CONNECT ERROR -", url)
        except requests.exceptions.ReadTimeout:
            print("READ TIMED OUT -", url)
        except requests.exceptions.RequestException as e:
            print("OTHER REQUESTS EXCEPTION -", e)
        except response.status_code == 403:
            print('ERROR! Got a 403 error code')

class Check_HTML_Valid(Get_HTML_Elements):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_id = kwargs.get('entity_id')

    def start(self):
        c = Counter()
        feeds = pd.read_csv(str(self.pat) + '.csv')
        rss_url = feeds.loc[feeds['ID'] == self.entity_id, 'rss'].values[-1]
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            entry_link = entry.get('link')

            response = requests.get(entry_link, headers = self.headers)
            content_type = response.headers.get('content-type')
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = html2text.html2text(str(soup.find(self.ename, attrs={self.aname: self.acon})))
                content = content.replace('\n', '')
                if content == 'None':
                    print("Not Working:", entry_link)
                    c['not working urls'] += 1
                    c['total'] += 1
                else:
                    print("Working:", entry_link)
                    c['working urls'] += 1
                    c['total'] += 1
            elif 'application/pdf' in content_type:
                print("This is a pdf")
                c['not html'] += 1
                c['total'] += 1
            else:
                print("This is neither a html or pdf")
                c['not html'] += 1
                c['total'] += 1

            if c['total'] == 20:
                print(c)
                print('stopping here after 20 feeds')
                break
        print(c)
        return c

class Update_HTML(Check_HTML_Valid):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = kwargs.get('source')
        self_entity_id = kwargs.get('entity_id')

    def start(self):
        feeds = pd.read_csv(str(self.pat) + '.csv')
        feeds.loc[feeds.ID == self.entity_id, ['element_name', 'attribute_name', 'attribute_content']] = self.ename, self.aname, self.acon
        # feeds.to_csv('new.csv', index = False)
        root = 'data_sources'
        feeds.to_csv(root + '/' + self.source + '.csv', index=False)

        # html_elements_dict = {}
        # html_elements_dict.update({"ID": self.entity_id, "element_name": self.ename, "attribute_name": self.aname,
        #                            "attribute_content": self.acon})
        #
        # self.e_list.append(html_elements_dict) if html_elements_dict not in self.e_list else self.e_list
        # self.e_list.sort(key=operator.itemgetter('ID'))
        print('exported to csv')



