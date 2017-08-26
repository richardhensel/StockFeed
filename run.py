import os
import csv
import string
import sys
import demjson
import json
from datetime import datetime, date, timedelta

#for the asx announcement web scraper
import random
import time
from pytz import timezone
import bs4
import re
from urllib2 import Request, urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#sending email
#import smtplib
#from email.mime.text import MIMEText

#sending sms
from twilio.rest import Client

def load_company_info(first_time_flag):

    #file_path ='/home/richard/gitRepositories/StockFeed/ASXListedCompanies.csv'  
    file_path ='./ASXListedCompanies.csv'  
    if first_time_flag==True:
        company_dict = {}
        with open(os.path.join(file_path)) as localfile:
                    reader = csv.reader(localfile,delimiter=',',quotechar='"')
                    #reader.next()
                    code_list = []
                    for row in reader:
                        csv_row = [column.upper() for column in row]
                        code_list.append(csv_row[1])
                        company_dict[csv_row[1]]=dict([('company_name',csv_row[0]),('industry_group',csv_row[2]),('quote_timestamps',[]),  ('last_prices', []), ('change_percents', []),  ('news_timestamps', []), ('news_headlines', []), ('news_publishers', []), ('news_links', []),  ('ann_timestamps', []), ('ann_headlines', []),  ('ann_links', [])]) 
        
        with open('company_dict.json', 'w') as fp:
            json.dump(company_dict, fp)
        #exit()
    
    else:
        with open('company_dict.json', 'r') as fp:
            company_dict = json.load(fp)
    
        code_list = []
        for key, value in company_dict.items() :
            code_list.append(key)
    return code_list, company_dict

def buildUrl(symbols):
    symbol_list = ','.join([symbol for symbol in symbols])
    # a deprecated but still active & correct api
    return 'http://finance.google.com/finance/info?client=ig&q=' \
        + symbol_list

def buildNewsUrl(symbol, qs='&start=0&num=1000'):
   return 'http://www.google.com/finance/company_news?output=json&q=' \
        + symbol + qs

def request(symbols):
    url = buildUrl(symbols)
    req = Request(url)
    resp = urlopen(req)
    # remove special symbols such as the pound symbol
    content = resp.read().decode('ascii', 'ignore').strip()
    content = content[3:]
    return content

def requestNews(symbol, start_time):
    url = buildNewsUrl(symbol, '&start='+str(start_time)+'&num=1000')
    print "url: ", url
    req = Request(url)
    resp = urlopen(req)
    content = resp.read()

    content_json = demjson.decode(content)

    article_json = []
    news_json = content_json['clusters']
    for cluster in news_json:
        for article in cluster:
            if article == 'a':
                article_json.extend(cluster[article])

    return article_json

def time_delay(min_time, max_time):
    if min_time>=max_time:
        raise AssertionError("max_time must be greater than min_time")
    delay = random.random()*(max_time-min_time)+min_time
    #print 'waiting ' + str(delay) + ' seconds'
    time.sleep(delay)

def recent_weekday(adate):
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate

def seconds_in_day(time_string):
    m = re.search("([0-9]*):([0-9]*)([a-z]*)", time_string)
    hours = float(m.group(1))
    minutes = float(m.group(2))
    am_pm = m.group(3)

    if am_pm == 'pm':
        extra_time = 12*3600
    else:
        extra_time = 0
    return int(extra_time + 3600 * hours + 60 * minutes)

def notify(code):
    print 'notify'
    code_watch_list =['MAH', 'ANR', 'SAS', 'AVQ', 'FBR', 'IMA', 'FGR'] 

    account_sid = os.environ['TWILIO_SID']
    auth_token = os.environ['TWILIO_AUTH']

    client = Client(account_sid, auth_token)

    if code in code_watch_list:
        print 'sending sms about '+code
        #company_dict[code]['ann_timestamps'].append(ann_time_utc)
        headline = company_dict[code]['ann_headlines'][-1]
        pdf_link = company_dict[code]['ann_links'][-1]

        client.messages.create(
             to=os.environ['MY_NUMBER'],
             from_ = os.environ['TWILIO_NUMBER'],
             body = code+'\n'+headline+'\n'+pdf_link
         )

def get_stock_quotes(code_list):
    #update the time of the last api query
    #append ASX: to each query
    dictionary_list = json.loads(request([exchange+':'+query_code for query_code in code_list]))
    for dictionary in dictionary_list:

        if dictionary['e']==exchange:
            code = dictionary['t']
            #print 'successfully added ' + code
            company_dict[code]['quote_timestamps'].append(int(current_time))
            company_dict[code]['last_prices'].append(dictionary['l'])
            company_dict[code]['change_percents'].append(dictionary['cp'])
        else:
            print 'expected code: ' + list_segment[index] + 'returned code: ' + dictionary['t'] + 'returned exchange: ' + dictionary['e']

# From the market index website
def get_asx_index_announcements():
    print 'get announcements'
    pdf_link_base = 'https://newswire.iguana2.com/af5f4d73c1a54a33/'
    url = 'http://www.marketindex.com.au/asx-announcements#'

    unixZero = timezone('UTC').localize(datetime(1970,1,1))
    previous = recent_weekday(date.today())
    current_date = timezone('Australia/Sydney').localize(datetime(previous.year, previous.month, previous.day))
    current_date_utc = int((current_date - unixZero).total_seconds())

    #driver = webdriver.Firefox()
    #driver.get(url)
    #time_delay(1,2)
    #element = driver.find_element_by_name('priceSensitiveOnly').click()
    
    #soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    #driver.close()
    soup = bs4.BeautifulSoup(urlopen(url), 'html.parser')
    table = soup.find("table", attrs={"id":"ucf_table"})
    print table
    
    for row in table.find_all('tr', {"data-quoteapi-id":re.compile(r".*")}):
        tag = row.get("data-quoteapi-id").split('/')
        ann_time = row.find('td', {"data-quoteapi":"$cur.time"}).get_text()
        code = row.find('a', {"data-quoteapi":"$cur.symbol href=/asx/{$cur.symbol} (stockLink)"}).get_text()
        title = row.find('td', {"class": "quoteapi-announcement-heading"}).get_text()
        page_count = row.find('td', {"data-quoteapi":"$cur.pageCount"}).get_text()
        file_size = row.find('td', {"data-quoteapi":"$cur.fileSize"}).get_text()
        pdf_link = pdf_link_base+tag[0]+'/'+tag[1]+'/'+title.replace(' ','_')

        ann_time_utc = current_date_utc+seconds_in_day(ann_time)
	print code
	print title
        print pdf_link


        try:
            if title not in company_dict[code]['ann_headlines'] and ann_time_utc not in company_dict[code]['ann_timestamps']: 
                #print 'adding ' + code
                company_dict[code]['ann_timestamps'].append(ann_time_utc)
                company_dict[code]['ann_headlines'].append(title)
                company_dict[code]['ann_links'].append(pdf_link)

                notify(code)
           # else: 
                #print code +' '+ title + ' already added'
                #print code
        except:
            print 'error adding '+code
            continue


#from asx website
def get_asx_announcements():
    url ='http://www.asx.com.au/asx/statistics/todayAnns.do' 

    unixZero = timezone('UTC').localize(datetime(1970,1,1))
    previous = recent_weekday(date.today())
    current_date = timezone('Australia/Sydney').localize(datetime(previous.year, previous.month, previous.day))
    current_date_utc = int((current_date - unixZero).total_seconds())

    #driver = webdriver.Firefox()
    #driver.get(url)
    #time_delay(1,2)
    #element = driver.find_element_by_name('priceSensitiveOnly').click()
   
     
    #soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    soup = bs4.BeautifulSoup(urlopen(url), 'html.parser')
    #driver.close()
    table = soup.find("table", attrs={"id":"ucf_table"})
    tbody = table.find("body", attrs={"data-quoteapi":"items"})
    
    for row in table.find_all('tr', {"data-quoteapi-id":re.compile(r".*")}):
        ann_time = row.find('td', {"data-quoteapi":"$cur.time"}).get_text()
        code = row.find('a', {"data-quoteapi":"$cur.symbol href=/asx/{$cur.symbol} (stockLink)"}).get_text()
        title = row.find('td', {"class": "quoteapi-announcement-heading"}).get_text()
        page_count = row.find('td', {"data-quoteapi":"$cur.pageCount"}).get_text()
        file_size = row.find('td', {"data-quoteapi":"$cur.fileSize"}).get_text()
        pdf_link = pdf_link_base+tag[0]+'/'+tag[1]+'/'+title.replace(' ','_')

        ann_time_utc = current_date_utc+seconds_in_day(ann_time)

        try:
            if title not in company_dict[code]['ann_headlines'] and ann_time_utc not in company_dict[code]['ann_timestamps']: 
                print 'adding ' + code
                company_dict[code]['ann_timestamps'].append(ann_time_utc)
                company_dict[code]['ann_headlines'].append(title)
                company_dict[code]['ann_links'].append(pdf_link)

                notify(code)
                #break
                 
            #else: 
                #print code +' '+ title + ' already added'
                #print code
        except:
            #print 'error adding '+code
            continue

def get_news():
    #get latest news
    for query_code in query_code_list:
        try:
            dictionary_list = requestNews(query_code, 0)
            #print dictionary_list
            for dictionary in dictionary_list:
                news_timestamp = int(dictionary['tt'])
                #if news less than 2 days old
                if current_time - news_timestamp < 2*24*3600:
                    try:
                        print dictionary['t']
                        print dictionary['d']
                        company_dict[query_code]['news_timestamps'].append(news_timestamp)
                        company_dict[query_code]['news_headlines'].append(dictionary['t'])
                        company_dict[query_code]['news_publishers'].append(dictionary['s'])
                        company_dict[query_code]['news_links'].append(dictionary['sru'])
                    except:
                        continue
        except:
            continue

########################################## 
#begin main
#########################################

exchange = 'ASX'
price_limit = 1.5

codes_per_query = 1
min_seconds_between_queries = 10

#code_list, company_dict = load_company_info(first_time_flag=False)
code_list, company_dict = load_company_info(first_time_flag=True)

indices = range(0, len(code_list), codes_per_query)
last_time = time.time()
count = 0
while True:

    current_time = time.time()
    index_start = indices[count] 
    if current_time-last_time > min_seconds_between_queries:
        #housekeeping
        # start again from beginning
        if count<len(indices)-1:
            count += 1
        else:
            count = 0
        last_time = current_time 

        #construct the list of codes to be used in this query
        index_end = index_start + codes_per_query
        query_code_list = code_list[index_start:index_end]

        #query the google finance api and update the company information
        #get_stock_quotes(query_code_list)

        #get the latest asx announcements.
        #from the market index website
        get_asx_index_announcements()
        #from the asx website
        #get_asx_announcements()

        #get latest news.
        #get_news()

        #save the company dict
        with open('company_dict.json', 'w') as fp:
            json.dump(company_dict, fp)






# the information for each company is polled from the stock price api, and is stored in a dictionary along with a timestamp. 

