import scrapy
import string

class LoginSpider(scrapy.Spider):
    #name of the project
    name = 'example.com'
    #Start command = scrapy crawl example.com
    start_urls = [  'https://www2.lsuc.on.ca/LawyerParalegalDirectory/loadSearchPage.do']

    #This method starts a parsing/scraping process with the start_urls as input
    #This is a standard scrapy format
    def parse(self, response):
        #A list of search criteria to use we will be looking at the alphabet
        alpha = ['a','b'] #list(string.ascii_lowercase)
        searchresults = [] # a storage variable for the search results
        request = [] # Holds the request as its built
        
        i=1 # a counter used to identify/enumerate searchs
        
        for char_a in alpha:
          for char_b in alpha:
            request.append(self.search_request(response, char_a + char_b, i))
            request[-1].meta['item'] = char_a + char_b
            i+=1
        for index in range(len(request)):
          yield request[index]
        return
        #self.search_trigger(request)

    #Builds search request object
    def search_request(self, response, criteria,i):
      self.log('i is %s' % i)
      self.log('about to request %s' % criteria)
      return scrapy.FormRequest.from_response(
          response,
          method='POST',
          formdata={'lastName': criteria},
          callback=self.process_results
        )
      
    #Triggers the searh (DOESNT WORK???)
    def search_trigger(self ,request):
      for index in range(len(request)):
        yield request[index]
      return
      
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
        error_found=False
        #Handling errors presented on the page No record and too many
        for message in response.xpath('//*[@id="error"]/font').extract():
          error_found=True
          if 'NO RECORDS' in message:
            self.log('ERROR: NO RECORDS for the search %s' % search_criteria)
          elif 'more than 500 records' in message:
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
        #UNCOMMENT THIS to turn on nextpage crawling
        #self.parse_nextpage(nextpage, criteria)  
        
        
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