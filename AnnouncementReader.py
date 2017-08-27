class AnnouncementReader:
    def __init__(self):

        #self.url ='http://www.asx.com.au/asx/statistics/prevBusDayAnns.do'
        self.url ='http://www.asx.com.au/asx/statistics/todayAnns.do'



    def get_latest(self):

        unixZero = timezone('UTC').localize(datetime(1970,1,1))
        previous = recent_weekday(date.today())
        current_date = timezone('Australia/Sydney').localize(datetime(previous.year, previous.month, previous.day))
        current_date_utc = int((current_date - unixZero).total_seconds())

        pdf_url_base ='http://www.asx.com.au'

        driver = webdriver.PhantomJS()
        driver.get(self.url)
        time_delay(2,2.1)
        soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        table = soup.find("table", {"class":re.compile(r".*")})

        codes = []
        times = []
        sensitives = []
        headlines = []
        links = []

        for row in table.find_all('tr', {"class":re.compile(r".*")}):
            columns = row.find_all('td')
            #pull out values
            code        = columns[0].get_text()
            ann_time    = columns[1].get_text()
            if columns[2].find('img'):
                price_sensitive = True
            else:
                price_sensitive = False
            headline       = columns[3].get_text()
            pdf_link    = pdf_url_base+(columns[5].find('a', {"href":re.compile(r".*")}).get("href")).lower()
            ann_time_utc = current_date_utc+seconds_in_day(ann_time)

            codes.append(code)
            times.append(ann_time_utc)
            sensitives.append(price_sensitive)
            headlines.append(headline)
            links.append(pdf_link)

        return codes, times, sensitives, headlines, links


