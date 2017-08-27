
class StockInfo:
    def __init__(self, first_time):

        ## load the database. (dictionary)
        if first_time:
            self.database = load_from_csv('./ASXListedCompanies.csv', './CompanyyDatabase.json')
        else:
            self.database = load_from_json('./CompanyyDatabase.json')
        # create the readers. 

        self.announcement_reader = AnnouncementReader("url")

        self.news_reader = NewsReader("url")

        self.stock_quote_reader = StockQuoteReader("url", number per query)

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


    def get_announcements(self):
        codes, times, sensitives, headlines, links = self.announcement_reader.get_latest()
        
        for i, code in enumerate(codes):
            add_to_database(code, 'ann_timestamp', times[i])
            add_to_database(code, 'ann_headline', headlines[i])
            add_to_database(code, 'ann_sensitive', sensitives[i])
            add_to_database(code, 'ann_link', links[i])


if __name__ == "__main__":
    stock_info = StockInfo(first_time=True)


        
