'''WordCloud Generator

This class of functions loads in some text and creates a wordcloud based on the frequency of terms in that text.

'''

from wordcloud import WordCloud
from matplotlib import rcParams
import re
import json
import _datetime
import matplotlib.pyplot as plt

class TopicInterface(object):
    def __init__(self, **kwargs):
        '''
        ET_docs is currently a list of dictionaries in a json format
        '''
        self.ET_docs = kwargs.get('ET_docs')
        self.current_date = _datetime.datetime.now()
        self.file_date = str(self.current_date.year) + '_' + str(self.current_date.month) + '_' + str(
            self.current_date.day) + '-' + str(self.current_date.hour) + 'h-' + str(self.current_date.minute) + 'm'

    def open_json(self,json_file_path):
        """ opens a json in list of dictionaries ET format"""
        with open(json_file_path, 'r') as j:
            jdata = json.loads(j.read())

        return jdata

    def write_to_json(self, json_file, json_data):
        with open(json_file, 'w', encoding='utf-8') as fout:
            return json.dump(json_data, fout, ensure_ascii=False, indent=4)

    def learn(self, ETDocuments=[]):
        """ expects a list of evidence tracker objects, all with a text attribute
             returns 'ok', if ok. (or some other useful info)
        """

    def create_clouds(self):
        docs = self.open_json(self.ET_docs)
        doc_number = 1

        for document in docs:
            txt = self.regex_cleaner(document['text'])
            doc_name = document['name']
            plot = self.create_word_cloud(txt, doc_number, doc_name)
            document['wordcloud'] = plot
            doc_number += 1

    def create_word_cloud(self, text, doc_number, doc_name):
        rcParams['font.family'] = 'Oswald'

        wordcloud = WordCloud(font_path = 'Oswald.ttf', max_font_size=100, colormap = "Dark2", max_words=50, width = 600, height = 400, background_color="white").generate(text)

        """USE CODE BELOW TO EXPORT SMALLER FILE SIZE WORDCLOUDS, BUT WITHOUT DOCUMENT TITLES"""
        # s = wordcloud.to_svg()
        # filename = ('wordclouds/' + self.file_date + '_wc_' + str(doc_number) + '.svg')
        # open(filename, 'w').write(s)
        # return filename

        """USE CODE BELOW TO EXPORT LARGER FILE SIZE WORDCLOUDS, BUT WITH DOCUMENT TITLES"""
        plt.rcParams['figure.figsize'] = [7.2, 4.8]
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(str(doc_name), fontsize = 12, color = '#3fb0c3', wrap = True)
        fig = plt.gcf()  # get current figure
        filename = ('wordclouds/' + self.file_date + '_wc_' + str(doc_number) + '.svg')
        plt.savefig(filename, format ="svg")
        plt.tight_layout(pad=4)
        plt.show()

        return filename

    def regex_cleaner(self, text):
        '''cleans some text, removes html, special characters, and numbers'''
        #removes urls
        url_reg = r'[a-z]*[:.]+\S+'
        result = re.sub(url_reg, '', text)
        #removes special characters
        res = re.sub(r'\W+', ' ', result)
        #removes numbers
        rez = re.sub(r'[0-9]+', '', res)
        #removes words of <2 length
        rezz = re.sub(r'\b\w{1,2}\b', '', rez)

        return rezz
