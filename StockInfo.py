
class StockInfo:
    def __init__(self, first_time):

        ## load the database. (dictionary)
        if first_time:
            self.database = load_from_csv('./ASXListedCompanies.csv', './CompanyyDatabase.json')
        else:
            self.database = load_from_json('./CompanyyDatabase.json')
        # create the readers. 

        self.announcement_reader = AnnouncementReader('http://www.asx.com.au/asx/statistics/todayAnns.do')
        #self.announcement_reader = AnnouncementReader('http://www.asx.com.au/asx/statistics/prevBusDayAnns.do')

        #self.news_reader = NewsReader("url")

        self.stock_quote_reader = StockQuoteReader("url", number per query)

        # thresholds for detecting a notification condition. 
        self.ann_age_threshold = 3600*24
        self.stock_age_threshold = 3600
        self.percent_threshold = 2


    def load_from_csv(self, file_name, json_name):
        self.company_dict = {}
        self.code_list = []
        with open(os.path.join(file_name)) as localfile:
            reader = csv.reader(localfile,delimiter=',',quotechar='"')
            for row in reader:
                csv_row = [column.upper() for column in row]
                code_list.append(csv_row[1])
                company_dict[csv_row[1]]= dict([('company_name',csv_row[0]),
                                                ('industry_group',csv_row[2]),

                                                ('quote_timestamp',[]),  
                                                ('last_price', []), 
                                                ('change_percent', []),  

                                                ('news_timestamp', []), 
                                                ('news_headline', []), 
                                                ('news_publisher', []), 
                                                ('news_link', []),  

                                                ('ann_timestamp', []), 
                                                ('ann_headline', []),  
                                                ('ann_link', []),  
                                                ('ann_sensitive', [])]) 
            
        with open(json_name, 'w') as fp:
            json.dump(company_dict, fp)

        return True #code_list, company_dict

    def load_from_json(self, json_name):
        with open(json_name, 'r') as fp:
            self.company_dict = json.load(fp)    
        self.code_list = []
        for key, value in company_dict.items() :
            code_list.append(key)
        return True #code_list, company_dict

    def add_to_database(self, code, data_type, value):
        self.databse[code][data_type].append(value)

    def get_announcements(self, verbose):
        codes, times, sensitives, headlines, links = self.announcement_reader.get_latest()
        
        for i, code in enumerate(codes):
            # test if the entry already exists.
            if headlines[i] not in self.database[code]['ann_headline'] and times[i] not in self.database[code]['ann_timestamp']: 
                add_to_database(code, 'ann_timestamp', times[i])
                add_to_database(code, 'ann_headline', headlines[i])
                add_to_database(code, 'ann_sensitive', sensitives[i])
                add_to_database(code, 'ann_link', links[i])
                if verbose:
                    print code +' '+headlines[i]


    def check_condition(self):
        for code in self.code_list:
            #get the current time in utc
            unixZero = timezone('UTC').localize(datetime(1970,1,1))
            current_time = timezone('Australia/Sydney').localize(datetime.now())
            time_now = int((current_time - unixZero).total_seconds())
            #test for recent announcement
            ann_index_list = []
            for i, time in enumerate(self.database[code]['ann_timestamp']):
                if time_now-current_time<self.ann_age_threshold:
                    ann_index_list.append(index)

            #check for stock price increase
            if len(ann_index_list)>0:
                #check that most recent stock quote is recent and that it increased by a lot of percents. 
                if self.database[code]['quote_timestamp'][-1]-current_time<self.stock_age_threshold:
                    if int(self.database[code]['change_percent'][-1])>self.percent_threshold:

                                
if __name__ == "__main__":
    stock_info = StockInfo(first_time=True)
    stock_info.get_announcements(verbose=True)


        
