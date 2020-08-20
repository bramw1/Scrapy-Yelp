from reviews.items import ReviewsItem
from scrapy import Spider, Request
import re


class ReviewsSpider(Spider):
    name = 'reviews_spider'
    allowed_urls = ['https://www.yelp.com/']
    start_urls = ['https://www.yelp.com/biz/levain-bakery-new-york?osq=Levains+Bakery']

    def parse(self, response):
        num_reviews = str(response.xpath('//p[@class="lemon--p__373c0__3Qnnj text__373c0__2U54h text-color--mid__373c0__27i5f text-align--left__373c0__1Uy60 text-size--large__373c0__1j9OF"]/text()').extract())
        num_reviews = int(re.search('\d+', num_reviews).group())
        
        url_list = []
        for i in range(0, num_reviews, 20):
            url_list.append('https://www.yelp.com/biz/levain-bakery-new-york?osq=Levains%20Bakery&start=' + str(i))

        for url in url_list:
            yield Request(url = url, callback = self.parse_review_page)

    def parse_review_page(self, response):
        reviews = response.xpath('//li[@class="lemon--li__373c0__1r9wz margin-b3__373c0__q1DuY padding-b3__373c0__342DA border--bottom__373c0__3qNtD border-color--default__373c0__3-ifU"]')
        
        def cleantags(raw_html):
            clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
            cleaned = re.sub(clean, '', raw_html)
            return cleaned


        for review in reviews:     
            user = review.xpath('.//a[@class="lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE"]/text()').extract_first()
            date = review.xpath('.//span[@class="lemon--span__373c0__3997G text__373c0__2Kxyz text-color--mid__373c0__jCeOG text-align--left__373c0__2XGa-"]/text()').extract_first() 
            rating = review.xpath('.//span[@class="lemon--span__373c0__3997G display--inline__373c0__3JqBP border-color--default__373c0__3-ifU"]/div//@aria-label').extract_first()
            rating = float(re.search('\d+', rating).group())
            review = review.xpath('.//p[@class="lemon--p__373c0__3Qnnj text__373c0__2Kxyz comment__373c0__3EKjH text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa-"]').extract_first()
            review = cleantags(review)

            item = ReviewsItem()
            item['user'] = user
            item['date'] = date
            item['rating'] = rating
            item['review'] = review

            yield item