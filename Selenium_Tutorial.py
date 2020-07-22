# Followed From https://realpython.com/modern-web-automation-with-python-and-selenium/

import tqdm
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd

SPORT_COAT_LINKS = ['https://www.macys.com/shop/mens-clothing/mens-blazers-sports-coats/Productsperpage/120?id=16499',
                    'https://www.macys.com/shop/mens-clothing/mens-blazers-sports-coats/Pageindex,Productsperpage/2,120?id=16499',
                    'https://www.macys.com/shop/mens-clothing/mens-blazers-sports-coats/Pageindex,Productsperpage/3,120?id=16499',
                    'https://www.macys.com/shop/mens-clothing/mens-blazers-sports-coats/Pageindex,Productsperpage/4,120?id=16499']


def get_web_id(soup):
    web_id = []
    for tag in soup.find_all('div', id=True):
        web_id.append(tag['id'])
    web_id[:] = [x for x in web_id if 'a' not in x]
    web_id[:] = [x for x in web_id if 'e' not in x]
    web_id[:] = [x for x in web_id if 'o' not in x]
    web_id[:] = [x for x in web_id if 'bd' not in x]
    del web_id[0]
    return web_id

def get_brand(soup):
    brand = []
    for tag in soup.find_all(class_='productBrand'):
        brand.append(tag.text.strip())
    return brand

def get_title(soup):
    title = []  # still a little messy removing all the correct items from the list (for brands too)
    for a in soup.find_all('a', title=True):
        title.append(a['title'])
    del title[0:17]
    del title[240:249]
    del title[1::2]
    return title

def get_color(soup):
    color = []
    for tag in soup.find_all(class_="productThumbnail redesignEnabled"):
        item = tag.find(class_='color-count hide-for-large')
        if item:
            color.append(item.text.split()[0].strip())
        else:
            color.append('N/A')
    return color

def get_review(soup):
    reviews = []
    for tag in soup.find_all(class_="productDescription"):
        item_review = tag.find(class_="aggregateCount")
        if item_review:
            reviews.append(item_review.text.split()[0].strip())
        else:
            reviews.append('N/A')
    return reviews

def get_prices(soup):
    prices = [tag.text.split()
              for tag in soup.find_all(class_='prices')]

    full_prices = []
    discount_prices = []
    for price in prices:
        if len(price) == 3:
            full_price, _, discount_price = price
        else:
            full_price = price[0]
            discount_price = 'N/A'

        full_prices.append(full_price)
        discount_prices.append(discount_price)

    return full_prices, discount_prices

def getAllInfo(browser, url):
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    scraped_data = {}

    scraped_data['webID'] = get_web_id(soup)
    scraped_data['brand'] = get_brand(soup)
    scraped_data['title'] = get_title(soup)
    scraped_data['color'] = get_color(soup)
    scraped_data['reviews'] = get_review(soup)

    (full_prices, discount_prices) = get_prices(soup)  # Unpacking tuple
    scraped_data['full_price'] = full_prices
    scraped_data['discount_price'] = discount_prices

    df = pd.DataFrame.from_dict(scraped_data, orient='index')

    return df.transpose()


def get_selenium_options():
    options = Options()
    options.headless = True
    assert options.headless  # Operating in headless mode
    return options


def main():
    options = get_selenium_options()
    dfs = []
    for link in tqdm.tqdm(SPORT_COAT_LINKS):
        with Firefox(options=options) as browser:
            dfs.append(getAllInfo(browser, link))

    master_df = pd.concat(dfs)

    master_df.to_csv(r'C:\Users\christinanastos\Desktop\MacysPage.csv', index=False, header=True)

    print('The program is terminated')


if __name__ == '__main__':
    main()
