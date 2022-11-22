import selenium.webdriver as webdriver
from bs4 import BeautifulSoup
import csv

BASE_URL = 'https://developer.android.com'


class CrawlerException(Exception):
    pass


class Crawler:
    """
    Crawler to get jobs results from android docs.
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.results = []

    def write_csv_file(self):
        myFile = open('crawler_data.csv', 'w')
        with myFile:
            writer = csv.writer(myFile, delimiter=',', quoting=csv.QUOTE_ALL)
            header = ['activity', 'category', 'title', 'link', 'description']
            writer.writerow(i for i in header)
            writer.writerows(self.results)

    def crawl(self):
        browser = webdriver.Chrome()
        crawl_url = "{}/reference/kotlin/androidx/activity/contextaware/package-summary".format(
            self.base_url)
        browser.get(crawl_url)
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        results = soup.find('div', {"class": "devsite-article-body"})
        activity_title = browser.find_element_by_css_selector(
            "div.devsite-article-body>h1").text
        all_tables = results.find_all('table')

        for table in all_tables:
            parent_div = table.find_parent('div')
            category = parent_div.find_all_previous('h2')
            if category:
                category = category[0].text

            rows = table.find_all("tr")
            for row in rows:
                detail_url = ''
                title = ''
                description = ''
                all_tds = row.find_all('td')
                detail_url_el = row.find('td').find('a')

                if detail_url_el:
                    detail_url = "{}{}".format(
                        self.base_url, detail_url_el.get('href'))
                    title = row.find('td').find('a').text
                else:
                    title = row.find('td').text
                    detail_url = title

                if len(all_tds) == 2:
                    description = row.find_all('td')[1].text
                post_data = [activity_title, category,
                             title, detail_url, description]
                self.results.append(post_data)

        browser.close()

        # write results to file
        self.write_csv_file()


def main():
    crawler = Crawler()
    crawler.crawl()


if __name__ == '__main__':
    main()
