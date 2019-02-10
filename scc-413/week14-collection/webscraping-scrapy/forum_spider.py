import scrapy
import re
import os


class ForumSpider(scrapy.Spider):
    # A unique (within the project) name for the spider.
    name = "forumspider"

    # These are some regular expressions to identify urls that point to boards and topics.
    # Do not worry too much about this, you'll cover regular expressions in a future lab.
    reg_topic = re.compile(r'.*\/?index\.php\?.*topic=(\d+\.?\d*)')
    reg_board = re.compile(r'.*\/?index\.php\?.*board=(\d+\.?\d*)')

    # This method tells the scraper how to start. It must return an iterable of Requests. 
    def start_requests(self):
        # The URLS the scraper will go through
        urls = ['http://tropicalfruitforum.com/index.php?board=16.0']      # INSERT YOUR BOARD URL HERE
        self.folder = "forum-dump"                  # YOU CAN ALTER THIS TOO IF YOU WISH
        self.check_folder(self.folder)
        for url in urls:
            # yield the request. define the callback function.
            # The callback function will be called to handle the response of this request.
            yield scrapy.Request(url=url, callback=self.board_parse)

    # The method that handles the response (instance of TextResponse)
    # Usually this method will take information from the current page and then create new Requests.
    def board_parse(self, response):
        # Gets the board number from the url with a regular expression.
        board_num = self.reg_board.match(response.url).group(1)

        # loops through all links on the page
        # specifically, we are looking for "a" html elements, which contain links, and getting the "href" attributes.
        for link in response.css('a::attr(href)').getall():
            if self.reg_topic.fullmatch(link):         # Makes a request for the url if it's a topic.
                yield response.follow(link, callback=self.topic_parse)

        # Dump the board to a file.
        filename = '{0}/board-{1}.html'.format(self.folder, board_num)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file {}'.format(filename))

    # Parses topic pages, dumps the contents into an html file.
    def topic_parse(self, response):
        # Gets the topic number.
        topic_num = self.reg_topic.match(response.url).group(1)

        # Dumps the page to a file.
        filename = '{0}/topic-{1}.html'.format(self.folder, topic_num)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file {}'.format(filename))

    # This just makes a folder if you don't have one.
    def check_folder(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)