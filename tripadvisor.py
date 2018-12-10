#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-12-10 08:40:39
# Project: TripAdvisor

from pyspider.libs.base_handler import *
import pymongo

class Handler(BaseHandler):
    crawl_config = {
    }
    
    client = pymongo.MongoClient('localhost')
    db = client["trip"]
    
    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.tripadvisor.cn/Attractions-g186338-Activities-c47-London_England.html', callback=self.index_page,validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('div.listing_info > div.listing_title > a').items():
            self.crawl(each.attr.href, callback=self.detail_page,validate_cert=False)
        next = response.doc('a.nav.next.rndBtn.ui_button.primary.taLnk').attr.href
        self.crawl(next, callback=self.index_page,validate_cert=False)

    
    @config(priority=2)
    def detail_page(self, response):
        url = response.url
        name = response.doc(".h1").text()
        rating = response.doc("a > .reviewCount").text()
        address = response.doc(".contactInfo > .address").text()
        phone = response.doc(".contact > .is-hidden-mobile > div").text()
        duration = response.doc(".attractions-attraction-detail-about-card-AboutSection__sectionWrapper--3vxlo").text()
        introduction = response.doc("p").text()
        return {
            "name":name,
            "rating":rating,
            "address":address,
            "phone":phone,
            "duration":duration,
            "introduction":introduction,
            "url":url
        }

    def on_result(self, result):
        if result:
            self.save_to_mongo(result)
         
    def save_to_mongo(self, result):
        if self.db["london"].insert(result):
            print("save to mongo",result)