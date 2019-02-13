# -*- coding: utf-8 -*-

import scrapy
import os
import re
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor


# This spider is similar to the previous one, in that it scrapes a forum, but it is much less directed.
# It clicks every link and we define rules for how to handle different types of link.
# This is handy if, for example, you want to scrape an entire forum.
# It's a bit rough and ready, and there will be some errors. 
# Scrapers often need to be resilient to errors as they will happen often.
# Thankfully scrapy handles most of this for us.
class FlatEarthSpider(CrawlSpider):
    name='flatearth'
    allowed_domains=['tfes.org']
    start_urls = ['https://forum.tfes.org']

    # We can define different rules for how to handle different links
    rules = (
        Rule(LinkExtractor(allow=(r'\/?index\.php\?.*topic=\d+\.?\d*',)), 
        follow=True,   callback='parse_topic'),

        Rule(LinkExtractor(allow=(r'\/?index\.php\?.*board=\d+\.?\d*',), deny=r'.*;sort.*'), 
        follow=True,   callback='parse_board'),

        Rule(LinkExtractor(allow=(r'\/?index\.php\?.*action=profile;u=\d+',)), 
        follow=False,   callback='parse_user'),

        Rule(LinkExtractor(allow=(r'wiki\.tfes\.org\/index.*', r'wiki\.tfes\.org\/Special.*', r'wiki\.tfes\.org\/Talk.*',)), 
        follow=False),

        Rule(LinkExtractor(allow=(r'wiki\.tfes\.org\/.*',), deny=(r'wiki\.tfes\.org\/index.*', r'wiki\.tfes\.org\/Special.*', r'wiki\.tfes\.org\/Talk.*',)), 
        follow=True,   callback='parse_wiki'),

        Rule(LinkExtractor(allow=())),
    )

    def __init__(self, *a, **kw):
        super(FlatEarthSpider, self).__init__(*a, **kw)
        self.folder = "tfes"
        self.check_folder(self.folder)
        self.check_folder("{0}/users".format(self.folder))
        self.check_folder("{0}/wiki".format(self.folder))

    def check_folder(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)

    # method for parsing the discussions.
    def parse_topic(self, response):
        # Get the part of the code containing the board and extract the board number using regex.
        breadcrumb = response.css('ol').extract_first()
        curr_board = re.findall(r'board=\d+\.?\d*', breadcrumb)[0]
        print("Curr board = {}".format(curr_board))

        # If there was no board, stick it in the unidentified folder.
        if not curr_board:
            curr_board = "unidentified"

        self.check_folder("{0}/{1}".format(self.folder, curr_board))
        regex = 'topic=\d+\.?\d*'
        curr_page = re.findall(regex, response.url)[0]
        print("Parsing Topic - {}".format(curr_page))
        filename = 'tfes/{0}/{1}.html'.format(curr_board, curr_page)
        with open(filename, 'wb') as f:
            f.write(response.body)

    # Method for parsing a board (list of discussions)
    def parse_board(self, response):
        regex = 'board=\d+\.?\d*'
        curr_page = re.findall(regex, response.url)[0]
        print("Parsing Board - {}".format(curr_page))
        self.check_folder("{0}/{1}".format(self.folder, curr_page))
        filename = 'tfes/{0}/{0}.html'.format(curr_page)
        with open(filename, 'wb') as f:
            f.write(response.body)

    # method for parsing a user page
    def parse_user(self, response):
        regex = r'u=\d+'
        curr_page = re.findall(regex, response.url)[0]
        print("Parsing User - {}".format(curr_page))
        filename = '{0}/users/{1}.html'.format(self.folder, curr_page)
        with open(filename, 'wb') as f:
            f.write(response.body)

    # method for parsing a wiki page
    def parse_wiki(self, response):
        curr_page = response.url.split('.org/')[-1]
        print("Parsing Wiki - {}".format(curr_page))
        filename = '{0}/wiki/{1}.html'.format(self.folder, curr_page)
        with open(filename, 'wb') as f:
            f.write(response.body)

    def detail(self, response):
        print('parsed detail!')
