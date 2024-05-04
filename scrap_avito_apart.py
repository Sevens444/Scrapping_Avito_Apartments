import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time


class Scrapping_avito_apartments:
    def __init__(self, url):
        self.url = url
        self.page = 0
        self.max_page = 15
        self.data = pd.DataFrame()

    def __get_up_chrome_driver(self):
        options = uc.ChromeOptions()
        options.headless = False
        self.driver = uc.Chrome(options=options, version_main=124)
        print('Браузер запущен')

    def __get_url(self):
        self.driver.get(self.url)

    def __get_pages(self):
        while self.page < self.max_page and self.driver.find_element(By.CSS_SELECTOR,
                                                                 '[data-marker="pagination-button/nextPage"]'):
            self.page += 1
            print(f'Просмотр {self.page} страницы')
            self.__parse_page()
            time.sleep(2)
            self.driver.find_element(By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]').click()

        self.driver.quit()
        print(f'Было просмотрено {self.page} страниц')

    def __parse_page(self):
        for title in self.driver.find_elements(By.CSS_SELECTOR, '[data-marker="item"]'):
            name = title.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text.split(', ')
            rooms = name[0]
            square = float(name[1].replace(' м²', '').replace(',', '.'))
            flor_curr = int(name[2].split('/')[0])
            flor_all = int(name[2].split('/')[1].replace(' эт.', ''))
            try:
                desc = title.find_element(By.CSS_SELECTOR, '[class*="iva-item-description"]').text
            except Exception as e:
                desc = ''
            href = title.find_element(By.CSS_SELECTOR, '[data-marker="item-title"]').get_attribute('href')
            price = int(title.find_element(By.CSS_SELECTOR, '[itemprop="price"]').get_attribute('content'))
            currency = title.find_element(By.CSS_SELECTOR, '[itemprop="priceCurrency"]').get_attribute('content')

            # print(name, price)

            self.data = pd.concat([self.data,
                                   pd.DataFrame([[rooms, square, flor_curr, flor_all, price, currency, desc, href]])])

    def __save_data(self):
        self.data.columns = ['Rooms', 'Square', 'Flor curr', 'Flor all',
                             'Price', 'Currency', 'Description', 'Link']
        self.data = self.data.sort_values(by='Price', ascending=True)
        self.data.to_excel(f"avito apartments {pd.Timestamp.now().strftime('%d_%m_%Y')}.xlsx",
                           index=False)
        print('Информация сохранена')

    def parse(self):
        try:
            self.__get_up_chrome_driver()
            self.__get_url()
            self.__get_pages()
            self.__save_data()
        except Exception as e:
            self.driver.quit()


if __name__ == '__main__':
    saa = Scrapping_avito_apartments(
        url="https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?context=H4sIAAAAAAAA_0q0MrSqLraysFJKK8rPDUhMT1WyLrYyt1JKTixJzMlPV7KuBQQAAP__dhSE3CMAAAA&f=ASgBAQECBESSA8gQ8AeQUugW6PwBrL4NpMc1AUDS~w4khuvjAoDr4wIBRcaaDBV7ImZyb20iOjAsInRvIjo1NTAwMH0&footWalkingMetro=10"
    )
    saa.parse()
