import selenium.webdriver as webdriver
from bs4 import BeautifulSoup
import csv

BASE_URL = 'https://developer.android.com'


class CrawlerException(Exception):
    pass


class Crawler:
    """
    Crawler to get jobs results from android detail docs.
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.results = []

    def write_csv_file(self):
        myFile = open('detail_page.csv', 'w')
        with myFile:
            writer = csv.writer(myFile, delimiter=',', quoting=csv.QUOTE_ALL)
            header = ['activity', 'category', 'api name', 'table_heading', 'title', 'description']
            writer.writerow(i for i in header)
            writer.writerows(self.results)

    def parse_heading(self, activity_title, article_body):
        sibling_el = article_body.find('h2', {"id": "summary"})
        heading_ele = sibling_el.find_previous_siblings('p')
        heading_text = [el.text for el in heading_ele]
        heading_text = " ".join(heading_text)
        post_data = [activity_title, '', '', '', '', heading_text]
        self.results.append(post_data)

    def parse_summary(self, activity_title, article_body):
        """
        Extract Summary elements
        """
        summary_title = article_body.find('h2', {'id': "summary"}).text
        summary_public_methods = article_body.find(
            'table', {"id": "pubmethods"})
        summary_extension_methods = article_body.find(
            'table', {"id": "extmethods"})

        # public methods table
        pm_rows = summary_public_methods.find_all("tr")
        for pm_row in pm_rows:
            all_tds = pm_row.find_all('td')
            table_title = 'Public methods'

            if len(all_tds) == 2:
                title = all_tds[0].text
                description = all_tds[1].text
                post_data = [activity_title, summary_title, '', table_title, title, description]
                self.results.append(post_data)

        # extension methods table
        inner_table = summary_extension_methods.find('table')
        em_rows = inner_table.find_all("tr")
        for em_row in em_rows:
            all_tds = em_row.find_all('td')
            table_title = 'Extension functions'

            if len(all_tds) == 2:
                title = all_tds[0].text
                description = all_tds[1].text
                post_data = [activity_title, summary_title, '', table_title, title, description]
                self.results.append(post_data)

    def parse_public_methods(self, activity_title, article_body):
        """
        Extract Public methods elements
        """
        summary_title = article_body.find('h2', {'id': "public-methods"}).text
        api_levels_div = article_body.find_all('div', {'class': 'api apilevel-'})

        for api_level in api_levels_div:
            api_name = api_level.find('h3').text
            devsite_code = api_level.find('devsite-code').text
            description_ele = api_level.find_all('p')
            description_text = [el.text for el in description_ele]
            description_text = " ".join(description_text)

            api_data = [activity_title, summary_title, api_name, '', devsite_code, description_text]
            self.results.append(api_data)

            # extract table data
            inner_table = api_level.find('table')
            em_rows = inner_table.find_all("tr")
            for em_row in em_rows:
                all_tds = em_row.find_all('td')
                table_title = 'Parameters'

                if len(all_tds) == 2:
                    title = all_tds[0].text
                    description = all_tds[1].text
                    post_data = [activity_title, summary_title, api_name, table_title, title, description]
                    self.results.append(post_data)

    def crawl(self):
        browser = webdriver.Chrome()
        crawl_url = "{}/reference/kotlin/androidx/activity/contextaware/ContextAware".format(
            self.base_url)
        browser.get(crawl_url)
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        article_body = soup.find('div', {"class": "devsite-article-body"})
        activity_title = browser.find_element_by_css_selector(
            "div.devsite-article-body>h1").text

        self.parse_heading(activity_title, article_body)
        self.parse_summary(activity_title, article_body)
        self.parse_public_methods(activity_title, article_body)

        # close browser
        browser.close()

        # write results to file
        self.write_csv_file()


def main():
    crawler = Crawler()
    crawler.crawl()


if __name__ == '__main__':
    main()
