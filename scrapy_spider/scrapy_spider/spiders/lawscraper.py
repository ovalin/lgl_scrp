import scrapy
import string

class LoginSpider(scrapy.Spider):
    #name of the project/spider/crawler
    name = 'example.com'
    
    #SET THIS to true to turn on nextpage and profile crawling
    PROCESS_PROFILES=True
    PROCESS_NEXTPAGES=False
    

    
    #A list of search criteria to use we will be looking at the alphabet
    #list(string.ascii_lowercase)
    alpha = ['a','b']
    #Start command = scrapy crawl example.com
    start_urls = [  'https://www2.lsuc.on.ca/LawyerParalegalDirectory/loadSearchPage.do']

    #This method starts a parsing/scraping process with the start_urls as input
    #This is a standard scrapy format
    def parse(self, response):
      requests=[]
      for char_a in self.alpha:
        for request in self.request_builder(char_a,response):
          yield request
          
          
    def request_builder(self, first, response):
        searchresults = [] # a storage variable for the search results
        request = [] # Holds the request as its built
        for char_a in self.alpha:
            searchstring = first+char_a
            request.append(self.search_request(response, searchstring))
            request[-1].meta['item'] = searchstring
        for index in range(len(request)):
          yield request[index]
        return
      
   
    #Builds search request object
    def search_request(self, response, criteria):
      #self.log('i is %s' % i)
      self.log('about to request %s' % criteria)
      return scrapy.FormRequest.from_response(
          response,
          method='POST',
          formdata={'lastName': criteria},
          callback=self.process_results
        )
        
    #Makes nextpage requests
    def parse_nextpage (self, nextpage, criteria):
        nextpage = "https://www2.lsuc.on.ca" + nextpage
        self.log('Requesting %s for criteria %s' % (nextpage,criteria))
        subpage = scrapy.Request( url = nextpage, 
                                  callback = self.process_results
                                )
        subpage.meta['item'] = criteria
        yield subpage
        self.log('completed %s' % nextpage)  
    
    def childpages (self, page):
        page = "https://www2.lsuc.on.ca" + page
        self.log('Requesting %s for criteria' % (page))
        subpage = scrapy.Request( url = page, 
                                  callback = self.read_profile
                                )
        yield subpage
        self.log('completed %s' % page)  
        return
                    
    def read_profile(self, response):
        contact_data={}
        for tabled in response.xpath('//*[@id="content"]/div/form/table/tr[4]/td/div/table/tr'):
          self.log("NEXT CRITERIA")
          value = tabled.xpath('td[2]/font//text()').extract_first()
          key = tabled.xpath('td[1]/font//text()').extract_first()
          #key = key.find('r')
          row = { 'value' : value,
                  'key' : key
                }
          
          #contact_data[tabled.select('/tr/td[1]/font').extract()] = tabled.select('/tr/td[2]/font').extract()
          self.log('key %s value %s' % (key.strip(), value.strip() ))
                   #xpath('td/font//text()')[1].extract())#.select('./tr/td/font').extract())
          
                    
    #Processes page results on http requests
    def process_results(self,response):
        search_criteria=response.meta['item']
        self.log('Searching now = %s' % search_criteria)
#        filename = 'data%s.html' % response.meta['item']
#        with open(filename, 'wb') as f:
#            f.write(response.body)
#        self.log('Saved file %s' % filename)

#TODO list
#TOOD: Drill into people details from list
#TODO: Ignore toDefinitionPage & toMADefinitionPage.do?startPoint
#TODO: Handle "Search returned more than 500 records. Please narrow your search"
#TODO: Handle "There are NO RECORDS returned for this search"
#TODO: Capture files in appropriate location
#TODO:parse profiles and write to files
        error_found=False
        over500=False
        #Handling errors presented on the page No record and too many
        for message in response.xpath('//*[@id="error"]/font').extract():
          error_found=True
          if 'NO RECORDS' in message:
            self.log('ERROR: NO RECORDS for the search %s' % search_criteria)
          elif 'more than 500 records' in message:
            over500=True
            self.log('ERROR: TOO MANY RECORDS (>500) for the search %s' % search_criteria)
   
        
        profile_pages=[]
        nextpage =""
        if not error_found:
          for nxt in response.xpath('//*[@class="content"]/a/@href').extract():#/table/tr[6]/td'):
            if not ('toDefinitionPage' in nxt or 'toInformationPage' in nxt or 'loadSearchPage' in nxt) :
              if 'searchMore' in nxt:
                nextpage = nxt
                self.log('NEXT PAGE FOUND %s' % nxt)
              else:
                profile_pages.append(nxt)
                self.log('Found %s' % nxt)      
          self.log("Profile to pull %s" % profile_pages[1])
          #for prof_index in range(len(profile_pages)):
          for profile in self.childpages(profile_pages[1]):#prof_index]):
              if self.PROCESS_PROFILES:
                yield profile
          self.log("Done")

          for nxtpg in self.parse_nextpage(nextpage, search_criteria):
            if self.PROCESS_NEXTPAGES:
              yield nxtpg
   
        elif over500:
          for granular_request in self.request_builder(search_criteria, response):
            yield granular_request
          
        
        #self.log('Exiting save it')
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