#Feedseeker
import feed_seeker as fs
import pandas as pd
from collections import Counter
from scraper_functions import *
import requests




def convert_to_ts(time_struct_object):
    if type(time_struct_object) == time.struct_time:
        time_string = time.strftime('%Y-%m-%d %H:%M:%S', time_struct_object)
        return time_string


from time import localtime, strftime
current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
import datetime, pytz
from dateutil.tz.tz import tzoffset

loc = datetime.datetime(2010, 1, 1, 0, 0, tzinfo=tzoffset(None, -7200))

mock_time = loc.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")











amount = 6
for i in range(amount,amount+1):
    print(i)


run_list = [1,4]

n = 10  #chunk row size

list_df = [test_split[i:i+n] for i in range(0,test_split.shape[0],n)]

[i.shape for i in list_df]

for i in run_list:
    print(list_df[i])





from feed_seeker import find_feed_url
find_feed_url('http://chicagotribune.com')

for url in fs.generate_feed_urls('http://chicagotribune.com'):
    print(url)

find_feed_url('http://www.washingtonpost.com')

for url in ('https://httpstat.us/200?sleep=5000',
            'https://github.com/mitmedialab/feed_seeker'):
    try:
        print('found feed:\t{}'.format(find_feed_url(url, max_time=3)))
    except TimeoutError:
        print('skipping {}'.format(url))







df = pd.read_csv('media2.csv')

cols = ['url', 'rss_link']
lst = []

for url in df['url']:
    add_http = 'http://' + url
    rss_link = fs.find_feed_url(add_http)
    try:
        print('found feed:\t{}'.format(fs.find_feed_url(add_http, max_time=3)))
        # rss_link = fs.find_feed_url(add_http, max_time=3)
    except TimeoutError:
        print('skipping {}'.format(add_http))
        # rss_link = None
    lst.append([add_http,rss_link])


stuff = 'companies'
p = Path("./data_sources/" + stuff)
l = open_json(str(p) + '_last_checked.json')
h = open_json(str(p) + '_html_elements.json')
d = open_json('data_dump.json')

for d in l:
    d['date'] = '2010-01-01 00:00:00'


data = feedparser.parse('https://feeds.mcclatchy.com/miamiherald/sections/news/local/environment/stories')




x = limit_files(d,2)

x[1]

def Extract(lst):
    for item in lst:
        return item[0]['ref']
    return [item[0]['ref'] for item in lst]

print(Extract(x))

Extract(x)

for item in x:
    print(item[0]['ref'])


import feedparser

feed = 'https://ceres.org/rss.xml'
f= feedparser.parse(feed)

if "not well-formed" in str(nonfeed.bozo_exception):
    print(True)
else:
    print(False)



def notify(json_data):
    notify_data = {'status': 200, 'items': json_data}
    headers = {'Authorization': 'dykhPFIs^E8#ppuu'}
    response = requests.post('https://imd.crimmond-associates.co.uk/notify/', headers = headers, data=json.JSONEncoder().encode((notify_data)))
    print(response.raise_for_status)
    print(response.content)

import glob
path = "scraped_data/*.json"
for fname in glob.glob(path):
    temp_json = open_json(fname)
    notify(temp_json)




def split_json(self,target_path, json_data, step, c):
    amount = len(json_data) // step
    json_file_path = 'counter.json'
    failed_path = 'scraped_data/need_to_upload/'
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d") + now.strftime("-%H") + 'h' + now.strftime("-%M") + 'm' + now.strftime(
        "-%S") + 's'
    print(c['counter'])
    c['counter'] += len(json_data)

    print('there are ' + str(len(json_data)) + ' entries, splitting into chunks of '
          + str(step) + ' for a total of ' + str(math.ceil(amount) + 1) + ' lists')
    pos = 0
    for i in range(amount):
        temp_json = json_data[pos:pos + step]
        split_data = {'status': 200, 'items': temp_json}
        if len(temp_json) > 0:
            status_code = self.notify(split_data)
            if status_code == 200:
                print('chunk ' + str(i+1) + ' was sent to notify')
                filename = dt_string + '.output{}.json'.format(i + 1)
                with open(os.path.join(target_path, filename), 'w') as file:
                    json.dump(temp_json, file)
            else:
                print('chunk ' + str(i+1) + ' FAILED! Try running ff_upload.py')
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
                print('last chunk ' + str(i+1) + ' was sent to notify')
                filename = dt_string + '.output{}.json'.format(amount + 1)
                with open(os.path.join(target_path, filename), 'w') as file:
                    json.dump(temp_json, file)
            else:
                print('last chunk ' + str(i+1) + ' FAILED! Try running ff_upload.py')
                filename2 = 'f-' + dt_string + '.output{}.json'.format(i + 1)
                with open(os.path.join(failed_path, filename2), 'w') as file:
                    json.dump(temp_json, file)
    print(str(c['counter']) + ' pages scraped since March 21, 2021!')
    with open(json_file_path, 'w') as outputfile:
        json.dump(c, outputfile)


feeds = pd.read_csv('data_sources/media.csv')
t_scraped = feeds.loc[feeds.ID == 1.0, ['total_scraped']].fillna(0)

feeds.loc[feeds.ID == 1.0, ['total_scraped']] = t_scraped + 13

open_json("bs.json")

