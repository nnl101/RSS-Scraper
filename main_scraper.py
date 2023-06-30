# ### Main RSS Feeds Scraper ###
''' This is a scraper that loads a list of RSS feeds and parses their contents, including the full text of each article within each feed, into a list of dictionaries.
    This list of dictionaries can then be converted into either a json or csv file and is typically sent to a tech server for further processing.
'''

import feedparser
import pandas as pd
import csv
import requests
import html2text
import json
import webbrowser
import operator
import os
import _datetime
import time
import math
from hashlib import md5
from datetime import datetime
from bs4 import BeautifulSoup
from scraper_functions import *
from pathlib import Path
from collections import Counter
from time import localtime, strftime

class ScraperInterface(object):
    """ A web scraper """
    def __init__(self, *a, **k):
        """ Initialisation.  This could include the url(s) to target,
            search terms, notification.
        """
    
    def start(self):
        """ Start the scraping operation.  
        
            Trigger notification and data export when complete """
        #### do the work ####
        # ...
        
        self.notify()
        self.export()
    
    def notify(self, status, data):
        """ notify the result of the scrape to the next step in the
            processing chain, for example using REST.
        """
    
    def export(self, data):
        """ export the result of the scrape, possibly as CSV. """

class RSS_Scraper(ScraperInterface):

    def __init__(self, **kwargs):
        '''
        source is a source of rss feeds, such as a csv of companies, their IMIDs, and their rss feeds
        use n_feeds to get a random n sample of feeds
        use random_seed to get a sample with a reproducible result
        use entity to search for a specific company or news outlet, such as Exxon Mobil or the New York Times. Do not use in conjunction with n_feeds and random_seed
        '''
        self.source = kwargs.get('source')
        self.n_feeds = kwargs.get('n_feeds')
        self.number = kwargs.get('number')
        self.random_seed = kwargs.get('random_seed')
        self.tag = kwargs.get('tag')
        self.entity = kwargs.get('entity')
        self.notify_url = kwargs.get('notify_url', 'https://tech.influencemap.org/notify/')
        self.current_date = _datetime.datetime.now()
        self.path = Path("./data_sources/" + self.source)
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


    def load_rss_feeds(self):
        ''' loads a csv with rss feeds. change these columns to import other columns '''
        col_list = ["element_name", "attribute_name", "attribute_content"]
        ent = self.entity or ''
        feeds = pd.read_csv(str(self.path) + '.csv')
        feeds = feeds.dropna(subset=col_list)
        if self.tag is not None:
            feeds = feeds[feeds['tags'].str.contains(self.tag, na = False)]
        feeds['ID'] = feeds['ID'].astype(float)

        feeds = feeds[feeds['Name'].str.match(ent)]

        if self.n_feeds and self.random_seed is not None:
            feeds = feeds.sample(n=self.n_feeds, random_state=self.random_seed)
        return feeds

    def split_df(self, df):
        '''splits a df into chunks of n. If none specified default is 5'''
        if self.entity is not None:
            n = 1
        elif self.n_feeds is not None:
            n = self.n_feeds  # chunk row size
        else:
            n = 5
        list_df = [df[i:i + n] for i in range(0, df.shape[0], n)]

        if self.entity is not None:
            print('scraping feed ' + self.entity + ' only')

        elif self.tag is not None:
            print('there are ' + str(len(df)) + ' ' + self.tag + ' rss feeds, splitting into ' + str(len(list_df))
                  + ' chunks of ' + str(n) + '\n')
        else:
            print('there are ' + str(len(df)) + ' rss feeds, splitting into ' + str(len(list_df))
                + ' chunks of ' + str(n) + '\n')
        return list_df

    #for cleaning up data - renaming keys
    def rename_key(self,list_name,old_key,new_key):
        self.list_name = list_name
        self.old_key= old_key
        self.new_key = new_key
        
        for entry in list_name:
            if old_key in entry:
                entry[new_key] = entry.pop(old_key)
        return list_name

    #for cleaning up data - getting it into InfluenceMap-ready list of dictionaries format
    def cleanup(self, list_of_dictionaries):
        self.list_of_dictionaries = list_of_dictionaries
        
        self.rename_key(list_of_dictionaries, 'link','ref')
        self.rename_key(list_of_dictionaries, 'summary','extract')
        self.rename_key(list_of_dictionaries, 'content','text')
        self.rename_key(list_of_dictionaries, 'title','name')

        for entry in list_of_dictionaries:
            entry['date_of_evidence'] = entry['updated_parsed'] if entry['updated_parsed'] != None else entry['published_parsed']
            if self.source == 'companies':
                entry['data'] = {"RSS Feed": entry["RSS Feed"], "Company Name": entry['company_name']}
                entry['source'] = 'D1'
                [entry.pop(k) for k in ['company_name', 'RSS Feed', 'published_parsed', 'updated_parsed']]
            elif self.source == 'media':
                entry['data'] = {"RSS Feed": entry["RSS Feed"],
                                 "Media_Cloud_ID": entry["Media_ID"],
                                 # "Source Tags": entry["source_tags"] if entry["source_tags"] != 'NA' else None,
                                 # "Source Region": entry["source_region"] if entry["source_region"] != 'NA' else None,
                                 "Company Name": entry['company_name']}
                entry['source'] = 'D5'
                [entry.pop(k) for k in ['Media_ID', 'company_name', 'RSS Feed', 'published_parsed', 'updated_parsed',
                                        'source_tags', 'source_region'
                                        ]]
            if entry['extract'] is None:
                entry.pop('extract')
            entry['date_of_scrape'] = datetime.today().strftime('%Y%m%d')
            entry['date_of_evidence'] = time_to_str(entry['date_of_evidence'])
            entry['date_of_evidence'] = str(entry['date_of_evidence'])
            entry['project'] = 'Climate Change'
            entry['scraper'] = 'rss' + '_' + self.source
        return list_of_dictionaries

    def start(self):
        df_number = self.number
        df_of_feeds = self.load_rss_feeds()
        splitdf = self.split_df(df_of_feeds)

        last_checked = open_json(str(self.path) + '_last_checked.json')

        parsed_data = []
        
        '''iterates through each company and accesses the rss feed url'''
        # NOTE: This returns an IndexError if only one entity is scraped - needs to be changed
        for rss_feed in splitdf[df_number].iterrows():
            rss_url = rss_feed[1]['rss']
            company_id = rss_feed[1]['ID']
            ename = rss_feed[1]['element_name']
            aname = rss_feed[1]['attribute_name']
            acon = rss_feed[1]['attribute_content']

            print("LINK TO RSS FEED:", rss_url)
            feed = feedparser.parse(rss_url)
            stored_date = ind_search(company_id, 'date', last_checked)
            current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            latest_date = stored_date
            # print('this is the stored_date:', latest_date)

            if 'status' not in feed:
                print("There was no feed status. Check out what's going on with ", rss_url)
                continue

            elif feed.status != 200:
                if "not well-formed" in str(feed.bozo_exception):
                    rss1 = requests.get(rss_url).content.decode("utf-16")
                    rss1 = rss1.replace("utf-16", "unicode")
                    feed = feedparser.parse(rss1)
                else:
                    print("Feed Parse ERROR (with 200 status code):", feed.status)

            ''' only runs the scraper if the feed url has a 200 status code'''
            if feed.status == 200 and feed.bozo == 0:
                    new_entries = []
                    new_site = 0

                    '''iterates through each story that feedparser parses from the rss feed, checks to see if it is new or not.
                       If it is new, then add to the list of stories to be scraped. If not, then move on until all links in the
                       rss feed have been checked. '''
                    for story in feed.entries:
                        entry_date = convert_to_ts(story.get('updated_parsed')) or convert_to_ts(story.get('published_parsed')) or story.get('updated') or story.get('published') or ''
                        if latest_date is None:
                            # print('this is a new rss feed')
                            new_site = 1
                            new_entries.append(story)
                            latest_date = entry_date

                        if new_site == 1:
                            # print('this is a new rss feed, looping through')
                            new_entries.append(story)

                            if entry_date > latest_date:
                                latest_date = entry_date

                        elif entry_date > stored_date and new_site == 0:
                            # print("this is the entry_date:", entry_date)
                            new_entries.append(story)

                            if entry_date > latest_date:
                                latest_date = entry_date
                            # print('this is the newest latest_date:', latest_date)

                    if not new_entries:
                        pass

                    else:
                        print(len(new_entries), "new stories from this feed, most recently at",
                              latest_date)
                        new_dict = {'ID': rss_feed[1]['ID'],
                                    'Name': rss_feed[1]['Name'],
                                    'RSS Feed': rss_feed[1]['rss'],
                                    'date': latest_date}

                        #Writes the latest story date to a json. This is separated from the csv because csv's do funky things with dates.
                        update_checked(last_checked, new_dict)
                        last_checked.sort(key=operator.itemgetter('ID'))
                        write_to_json(str(self.path) + '_last_checked.json', last_checked)

                        #Writes date of last scrape and total scraped to csv
                        feeds = pd.read_csv(str(self.path) + '.csv')
                        feeds['total_scraped'] = feeds['total_scraped'].fillna(0)
                        t_scraped = feeds.loc[feeds.ID == rss_feed[1]['ID'], ['total_scraped']]
                        feeds.loc[feeds.ID == rss_feed[1]['ID'], ['last_scraped', 'total_scraped']] = current_time, t_scraped + len(new_entries)
                        root = 'data_sources'
                        feeds.to_csv(root + '/' + self.source + '.csv', index=False)

                    '''pulls values below from each new story in the rss feed and stores it in a dictionary'''
                    for i, post in enumerate(new_entries):
                        if self.source == 'companies':
                            entry = {"IMID": int(rss_feed[1]['ID']),
                                     "company_name": rss_feed[1]['Name'],
                                     "RSS Feed": rss_url}
                        elif self.source == 'media':
                            entry = {"Media_ID": int(rss_feed[1]['ID']),
                                     "company_name": rss_feed[1]['Name'],
                                     "source_tags": rss_feed[1]['tags'] or 'NA',
                                     "source_region": rss_feed[1]['region'] or 'NA',
                                     "RSS Feed": rss_url}
                        else:
                            entry = {"ID": int(rss_feed[1]['ID']),
                                     "company_name": rss_feed[1]['Name'],
                                     "RSS Feed": rss_url}
                        # values to extract from RSS Feed
                        values = ['title', 'link', 'summary', 'published_parsed', 'updated_parsed']

                        for value in values:
                            if value in new_entries[i]:
                                entry[value] = new_entries[i][value]
                            else:
                                entry[value] = None
                        #need to do: if no link, pass
                        link = new_entries[i]['link']

                        '''opens link of story and scrapes text of the link'''
                        try:
                            response = requests.get(link, timeout = 10, headers = self.headers)
                            response.raise_for_status()
                            content_type = response.headers.get('content-type')
                            if 'text/html' in content_type:
                                soup = BeautifulSoup(response.text, 'html.parser')

                                # #searches through list of elements and attributes associated with company, then parses the web page for its text content
                                # search_list = html_elements_list

                                entry['content'] = None
                                entry['content'] = html2text.html2text(str(soup.find(ename, attrs={aname:acon})))
                                #print ("OK -", link)
                            elif 'application/pdf' in content_type:
                                #print("This is a pdf")
                                pass
                            else:
                                #print("This is neither a html or pdf")
                                pass      

                        except requests.exceptions.ConnectionError:
                            pass
                            #print("CONNECT ERROR -", link)
                        except requests.exceptions.ReadTimeout:
                            pass
                            #print("READ TIMED OUT -", link)
                        except requests.exceptions.RequestException as e:
                            pass
                            #print("OTHER REQUESTS EXCEPTION -", e)
                        con = entry.get('content', "empty")

                        #Some links do not yield any text content when scraped - this returns an error message and tells you to look into why.
                        if con != "empty":
                            ''' appends each dictionary to a list, producing a list of dictionaries where each dictionary is a link and its text'''
                            parsed_data.append(entry)
                        else:
                            print('this particular story of ' + link + ' yielded no content. Check out what happened')
                            pass

            elif feed.status == 200 and feed.bozo == 1:
                print("Feed Parse Error (with bozo):", feed.bozo_exception)

            else:
                 print("Feed Parse Error (unsure):", feed.status)

        # if the scraper returns new data, then process it, else do nothing.
        if len(parsed_data) > 0:
            data_for_export = self.cleanup(parsed_data)
            write_to_json('data_dump.json', data_for_export)

            json_file_path = 'counter.json'

            with open(json_file_path, 'rb') as inputfile:
                c = Counter(json.load(inputfile))
                
        # Splitting jsons (see below for function documentation) into steps of 5 seems to work best, but this can be changed.
            self.split_json('scraped_data/', data_for_export,5, c)

            # Enable the below line to export data to csv
            # self.export(data_for_export)
        else:
            print('\nthere was nothing new since the last scrape')

    def split_json(self,target_path, json_data, step, c):
        """ Takes a json file of n length and splits it into (n/step) lengths, and adds the total length of the
            json to a running counter c. This function is needed because json's of large file size
            tend to overwhelm the server."""
            
        amount = len(json_data) // step
        json_file_path = 'counter.json'
        failed_path = 'scraped_data/need_to_upload/'
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d") + now.strftime("-%H") + 'h' + now.strftime("-%M") + 'm' + now.strftime(
            "-%S") + 's'
        # print(c['counter'])
        c['counter'] += len(json_data)

        print('\nThere are ' + str(len(json_data)) + ' total new entries, split into chunks of '
              + str(step) + ' and a total of ' + str(math.ceil(amount) + 1) + ' chunks.\n')
        pos = 0
        for i in range(amount):
            temp_json = json_data[pos:pos + step]
            split_data = {'status': 200, 'items': temp_json}
            if len(temp_json) > 0:
                status_code = self.notify(split_data)
                if status_code == 200:
                    print('SUCCESS! chunk ' + str(i+1) + ' was sent to the InfluenceMap server.')
                    filename = dt_string + '.output{}.json'.format(i + 1)
                    with open(os.path.join(target_path, filename), 'w') as file:
                        json.dump(temp_json, file)
                else:
                    print('FAIL! chunk ' + str(i+1) + ' did not go through. Try running ff_upload.py.')
                    filename2 = 'f-' + dt_string + '.output{}.json'.format(i + 1)
                    with open(os.path.join(failed_path, filename2), 'w') as file:
                        json.dump(temp_json, file)
            pos += step
        for i in range(amount, amount + 1):
            temp_json = json_data[pos:]
            split_data = {'status': 200, 'items': temp_json}
            if len(temp_json) > 0:
                status_code = self.notify(split_data)
                if status_code == 200:
                    print('SUCCESS! last chunk ' + str(i+1) + ' was sent to the InfluenceMap server.')
                    filename = dt_string + '.output{}.json'.format(amount + 1)
                    with open(os.path.join(target_path, filename), 'w') as file:
                        json.dump(temp_json, file)
                else:
                    print('FAIL! last chunk ' + str(i+1) + ' did not go through. Try running ff_upload.py.')
                    filename2 = 'f-' + dt_string + '.output{}.json'.format(i + 1)
                    with open(os.path.join(failed_path, filename2), 'w') as file:
                        json.dump(temp_json, file)
        print(str(c['counter']) + ' pages scraped since March 21, 2021!')
        with open(json_file_path, 'w') as outputfile:
            json.dump(c, outputfile)

    def notify(self,json_data):
        """ Sends the data in json format to the server, requires a notify_url and authorization headers to properly function """

        self.json_data = json_data
        headers = {'Authorization': 'dykhPFIs^E8#ppuu'}
        response = requests.post(self.notify_url, headers=headers,
                                 data=json.JSONEncoder().encode((self.json_data)))
        # print(response.raise_for_status)
        s_code = response.status_code
        print(s_code)
        print("RESPONSE:", response.content)
        return s_code

    def export(self, export_data):
        """ Saves scraped data as a csv file """
        self.export_data = export_data

        if self.entity is not None:
            filename = str(self.current_date.year) + '_' + str(self.current_date.month) + '_' + str(self.current_date.day) + '-' + str(
                self.current_date.hour) + 'h-' + str(self.current_date.minute) + 'm' + '-' + self.entity
        else:
            filename = str(self.current_date.year) + '_' + str(self.current_date.month) + '_' + str(self.current_date.day) + '-' + str(self.current_date.hour) + 'h-' + str(self.current_date.minute) + 'm'

        df = pd.DataFrame(self.export_data)
        # print(df.head(5))
        root = 'scraped_data'
        df.to_csv(root + '/' + 'rss_feed_' + self.source + '_' + filename + '.csv', index=False, encoding='utf-8-sig')

