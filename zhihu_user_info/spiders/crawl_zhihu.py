# -*- coding: utf-8 -*-
import scrapy
import json
from zhihu_user_info.items import ZhihuUserInfoItem
from scrapy import Request

class CrawlZhihuSpider(scrapy.Spider):
    name = 'crawl_zhihu'
    allowed_domains = ['www.zhihu.com']

    user_url = \
        'https://www.zhihu.com/api/v4/members/{user}?include={user_include}'
    user_include = \
        'allow_message,is_followed,is_following,is_org,is_blocking,' \
        'employments,answer_count,follower_count,articles_count,' \
        'gender,badge[?(type=best_answerer)].topics'

    following_url = \
        'https://www.zhihu.com/api/v4/members/{user}/followees?' \
        'include={following_include}&offset={offset}&limit={limit}'
    following_include = \
        'data[*].answer_count,articles_count,gender,follower_count,' \
        'is_followed,is_following,badge[?(type=best_answerer)].topics'

    follower_url = \
        'https://www.zhihu.com/api/v4/members/{user}/followers?' \
        'include={follower_include}&offset={offset}&limit={limit}'
    follower_include = \
        'data[*].answer_count,articles_count,gender,follower_count,' \
        'is_followed,is_following,badge[?(type=best_answerer)].topics'

    start_user = 'chun-shu-34-60'

    def start_requests(self):
        yield Request(self.user_url
                      .format(user=self.start_user,
                              user_include=self.user_include),
                      callback=self.parse_user)
        yield Request(self.following_url
                      .format(user=self.start_user,
                              following_include=self.following_include,
                              offset=0, limit=20),
                      callback=self.parse_following)
        yield Request(self.follower_url
                      .format(user=self.start_user,
                              follower_include=self.follower_include,
                              offset=0, limit=20),
                      callback=self.parse_follower)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihuUserInfoItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
                
        yield item

        yield Request(self.following_url
                      .format(user=result.get('url_token'),
                              following_include=self.following_include,
                              offset=0, limit=20),
                      callback=self.parse_following)
        yield Request(self.follower_url
                      .format(user=result.get('url_token'),
                              follower_include=self.follower_include,
                              offset=0, limit=20),
                      callback=self.parse_following)

    def parse_following(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url
                              .format(user=result.get('url_token'),
                                      user_include=self.user_include),
                              callback=self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end')\
                == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_following)

    def parse_follower(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url
                              .format(user=result.get('url_token'),
                                      user_include=self.user_include),
                              callback=self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end')\
                == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_follower)
