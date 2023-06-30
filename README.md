

# RSS Scraper



##### Summary

This is a web scraper that takes in a list of [RSS feeds](https://en.wikipedia.org/wiki/RSS), extracts the full text for each link in the feed, and then converts that text into either a JSON or CSV file format for further processing.

To run the scraper, run **start_main.py** and specify the parameters for each particular run. 

The scraper works by parsing each feed using the *feedparser* library in Python, then using the *BeautifulSoup* library to extract the html from each link from each feed, then using the *html2text* library to extract the html of the relevant text from that link, which is usually a news story of some kind.

Each web page is formatted differently. This means that there needs to be a database stored of the html elements that will enable the scraper to successfully scrape the relevant text from a website. This database is stored in **data_sources/media.csv**. This database also stores the latest link from each feed, so that if a link has already been scraped from that feed then it will not run again.

Occasionally new RSS feeds are added to the database, which means that the proper html elements that will enable the new feed to be scraped must also be checked for and added to the database. To do this **start_ind.py** must be run.

In its current iteration, JSON files are produced for each run of the scraper and then sent to the tech server. Examples of them can be seen in the **scraped_data** folder.

**start_wc.py** creates a word cloud visualization for the text of each story in the feed.

**scraper_functions.py** are helper functions for the main and individual scrapers.



##### Example

The New York Times has a RSS feed specifically dedicated to energy, which looks like this when viewed online. For this example we will scrape a news story with the headline *'Ida is expected to gain strength as it churns towards Louisiana'*:


=======
![](https://i.imgur.com/G8SbN5j.png)


When **start_main.py** is run, with the entity parameter specified as 'New York Times (Energy)', then the scraper will go through and extract the text for each story in the New York Times energy RSS feed. It will then produce that text as well as other valuable information such as the date of scrape, the date of the story, and the URL in a handy JSON file format. We can see here that the full text of the aforementioned story has been generated:


=======
![](https://i.imgur.com/80iv4p1.png)

When **start_wc.py** is run, a word cloud of each news story is then created. Here is an example of the most frequent words from the news story about Hurricane Ida (NOTE: Formatting may be off if the Oswald font is not installed locally):


=======
![](https://i.imgur.com/2r97Qe2.png)
