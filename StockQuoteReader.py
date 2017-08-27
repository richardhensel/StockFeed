


class StockInfo:
    def __init__(self, first_time):

        ## load the database. (dictionary)
        if first_time:
            self.database = load_from_csv('./ASXListedCompanies.csv', './CompanyyDatabase.json')
        else:
            self.database = load_from_json('./CompanyyDatabase.json')
        # create the readers. 

        self.announcement_reader = Announcement_Reader("url")

        self.news_reader = News_Reader("url")

        self.stock_quote_reader = Stock_Quote_Reader("url", number per query)

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
                                                ('quote_timestamps',[]),  
                                                ('last_prices', []), 
                                                ('change_percents', []),  
                                                ('news_timestamps', []), 
                                                ('news_headlines', []), 
                                                ('news_publishers', []), 
                                                ('news_links', []),  
                                                ('ann_timestamps', []), 
                                                ('ann_headlines', []),  
                                                ('ann_links', []),  
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


class Stock_Quote_Reader:
    def __init__(self):
        self.url = 
        self.








class Announcement_Reader:
    def __init__(self):






class News_Reader:
    def __init__(self):




        
