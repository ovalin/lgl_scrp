import scrapy
import string

class LoginSpider(scrapy.Spider):
    name = 'example.com'
    #Start command = scrapy crawl example.com
    start_urls = [  'https://www2.lsuc.on.ca/LawyerParalegalDirectory/loadSearchPage.do']

#,                  'https://www2.lsuc.on.ca/LawyerParalegalDirectory/search.do?submitType=&searchType=STARTSWITH&memberType=B&lastName=aa&firstName=&chosenCountry=CANADA&city=&postalCode=&pa%5B0%5D.PA=false&pa%5B1%5D.PA=false&pa%5B2%5D.PA=false&pa%5B3%5D.PA=false&pa%5B4%5D.PA=false&pa%5B5%5D.PA=false&pa%5B6%5D.PA=false&pa%5B7%5D.PA=false&pa%5B8%5D.PA=false&pa%5B9%5D.PA=false&pa%5B10%5D.PA=false&pa%5B11%5D.PA=false&pa%5B12%5D.PA=false&pa%5B13%5D.PA=false&pa%5B14%5D.PA=false&pa%5B15%5D.PA=false&pa%5B16%5D.PA=false&pa%5B17%5D.PA=false&pa%5B18%5D.PA=false&pa%5B19%5D.PA=false&pa%5B20%5D.PA=false&pa%5B21%5D.PA=false&pa%5B22%5D.PA=false&pa%5B23%5D.PA=false&pa%5B24%5D.PA=false&pa%5B25%5D.PA=false&pa%5B26%5D.PA=false&pa%5B27%5D.PA=false&pa%5B28%5D.PA=false&limitedSearch=false&serviceInFrench=false&l%5B0%5D.la=false&l%5B1%5D.la=false&l%5B2%5D.la=false&l%5B3%5D.la=false&l%5B4%5D.la=false&l%5B5%5D.la=false&l%5B6%5D.la=false&l%5B7%5D.la=false&l%5B8%5D.la=false&l%5B9%5D.la=false&l%5B10%5D.la=false&l%5B11%5D.la=false&l%5B12%5D.la=false&l%5B13%5D.la=false&l%5B14%5D.la=false&l%5B15%5D.la=false&l%5B16%5D.la=false&l%5B17%5D.la=false&l%5B18%5D.la=false&l%5B19%5D.la=false&l%5B20%5D.la=false&l%5B21%5D.la=false&l%5B22%5D.la=false&l%5B23%5D.la=false&l%5B24%5D.la=false&l%5B25%5D.la=false&l%5B26%5D.la=false&l%5B27%5D.la=false&l%5B28%5D.la=false&l%5B29%5D.la=false&l%5B30%5D.la=false&l%5B31%5D.la=false&l%5B32%5D.la=false&l%5B33%5D.la=false&l%5B34%5D.la=false&l%5B35%5D.la=false&l%5B36%5D.la=false&l%5B37%5D.la=false&l%5B38%5D.la=false&limitedScopeRetainer=false&method=Submit']
    #https://www2.lsuc.on.ca/LawyerParalegalDirectory/loadSearchPage.do']

    def parse(self, response):
        alpha = ['a','b'] #list(string.ascii_lowercase)
        searchresults = []
        request = []
        #item = {'searchname' : 'test'}
        i=1
        for char_a in alpha:
            for char_b in alpha:
                self.log('i is %s' % i)
                item = char_a + char_b
                self.log('about to request %s' % item)
                request.append(scrapy.FormRequest.from_response(
                        response,
                        method='POST',
                        formdata={'lastName': char_a + char_b},
                        callback=self.save_it
                    )
                )
                searchresults.append(request)
                request[-1].meta['item'] = item
                i=i+1
        for index in range(len(request)):
            yield request[index]
        return
        #return searchresults
    '''ab = scrapy.FormRequest.from_response(
            response,
            method='POST',
            formdata={'lastName': 'ab'},
            callback=self.save_it
            )'''

    def save_it(self,response):
        self.log('Searching now = %s' % response.meta['item'])
#        filename = 'data%s.html' % response.meta['item']
#        with open(filename, 'wb') as f:
#            f.write(response.body)
#        self.log('Saved file %s' % filename)
        for div in response.css("div.marked a::attr(href)").extract():
            self.log('found %s' % div)



# page = response.url.split("/")

        #for str in range(len(page)):
         #    self.log(page[str])
        #for div in response.css("div.marked a"):
        #    self.log('found %s' % div)
        #for href in response.css("a.href"):
        #    self.log('found %s' % href)
#table td tr div.marked table tr
        #follow(url, callback=None, method='GET', headers=None, body=None, cookies=None, meta=None, encoding='utf-8', priority=0, dont_filter=False, errback=None)
        #item = response.meta['item']
        #item['other_url'] = response.url
        #page = response.url.split("/")
        #last = response.url.split("lastname")[-1]
        #filename = 'data.html' % response.request.lastname
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log('Saved file %s' % filename)
        self.log('Exiting save it')
        return

    def people(self, response):

        filename = 'data.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        return
        #return scrapy.FormRequest.from_response(
        #    response,
        #    formdata={'method':'POST', 'lastName': 'aa'},
        #    callback=self.after_login
        #        )

    def after_login(self, response):
        #for tr in response.css ('tr'):
        #    yield {
        #        'names': quote.css('td font.content a::text').extract(),
        #    }
        # check login succeed before going on
        #if "authentication failed" in response.body:
        #    self.logger.error("Login failed")
            return

        # continue scraping with authenticated session...