import scrapy
import string

class LoginSpider(scrapy.Spider):
    #name of the project/spider/crawler
    name = 'example.com'
    
    #SET THIS to true to turn on nextpage and profile crawling
    PROCESS_PROFILES=True
    PROCESS_NEXTPAGES=True
    
    #File content
    filename = 'data.html' #% response.meta['item']
    f = None
    #with open(self.filename, 'wb') as f:  stream writting use this
    
    #A list of search criteria to use we will be looking at the alphabet
    alpha = list(string.ascii_lowercase) #['a','b']
    
    #Start command = scrapy crawl example.com
    start_urls = [  'https://www2.lsuc.on.ca/LawyerParalegalDirectory/loadSearchPage.do']

    #This method starts a parsing/scraping process with the start_urls as input
    #This is a standard scrapy format
    def parse(self, response):
      requests=[]
      
      self.f = open(self.filename, "w")
      self.f.write("Started Parsing")
      #self.log('Saved file %s' % self.filename)
      for char_a in self.alpha:
        for request in self.request_builder(char_a,response):
          yield request
          
    #builds search requests
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
      
   
    #Builds search request object payloads
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
      
    #Designed to read profile pages                
    def read_profile(self, response):
        contact_data="{'person': ["
        comm=" "#used to introduce commas
      
        for tabled in response.xpath('//*[@id="content"]/div/form/table/tr[4]/td/div/table/tr'):
          value = tabled.xpath('td[2]//text()').extract_first()
          key = tabled.xpath('td[1]//text()').extract_first()
          
          #For some reason its set to None sometimes when no data is found vs an empty string
          if key is None: 
            key = ""
          if value is None:
            value = ""

          if not key.strip() == '' or not value.strip() == '':
            row = "\n\t{'key' : '%s', 'value' : '%s' }" % (key.strip(), value.strip().replace("\r\n"," ").replace("\t","").replace("\xa0","xa0"))
            #self.log(row)
            contact_data=contact_data+comm+row
            comm=","
        contact_data+="\n\t]\n},"
        #writing to the file
        self.f.write(contact_data)
                    
    #Processes page results on http requests
    def process_results(self,response):
        search_criteria=response.meta['item']
        self.log('Searching now = %s' % search_criteria)

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

          #Drils through the next pages when there are multiple in the results
          for nxtpg in self.parse_nextpage(nextpage, search_criteria):
            if self.PROCESS_NEXTPAGES:
              yield nxtpg
        #Deals with error message stating results return too many results
        elif over500:
          for granular_request in self.request_builder(search_criteria, response):
            yield granular_request
        #self.log('Exiting save it')
        return
