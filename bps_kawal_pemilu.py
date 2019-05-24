import time
import pandas as pd
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def crawl_data(url, second=5):
    # specify the url

    # The path to where you have your chrome webdriver stored:
    webdriver_path = '/usr/bin/chromedriver'

    # Add arguments telling Selenium to not actually open a window
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920x1080')

    # Fire up the headless browser
    browser = webdriver.Chrome(executable_path=webdriver_path,
                               options=chrome_options)

    # Load webpage
    browser.get(url)

    # It can be a good idea to wait for a few seconds before trying to parse the page
    # to ensure that the page has loaded completely.
    time.sleep(second)

    # Parse HTML, close browser
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()

    return soup


def extract_data_penduduk(value):
    # ada beberapa yang valuenya -, kembalikan None
    if value == '-':
        return None

    # hapus spasi di value
    return value.replace(' ', '')


def get_bps():
    soup = crawl_data(
        'https://www.bps.go.id/statictable/2009/02/20/1267/'
        'penduduk-indonesia-menurut-provinsi-1971-1980-1990-1995-2000-dan-2010.html'
    )

    df = pd.DataFrame(columns=['wilayah', '1971', '1980', '1990', '1995', '2000', '2010'])

    # find results within table
    for r in soup.find_all('table')[2].find_all('tr', {'class': 'xl6310505'})[1:-3]:
        value = r.find_all('td', {'class', 'xl7610505'})

        df = df.append({
            'wilayah': r.find('td', {'class', 'xl6810505'}).get_text().replace('\n', '').replace('  ', ' ').lower(),
            '1971': extract_data_penduduk(value[0].get_text()),
            '1980': extract_data_penduduk(value[1].get_text()),
            '1990': extract_data_penduduk(value[2].get_text()),
            '1995': extract_data_penduduk(value[3].get_text()),
            '2000': extract_data_penduduk(value[4].get_text()),
            '2010': extract_data_penduduk(value[5].get_text())
        }, ignore_index=True)

    return df


def get_kawal_pemilu():
    soup2 = crawl_data('https://kawalpemilu.org/#0', second=10)

    # find results within table
    results2 = soup2.find('table', {'class': 'table'})
    rows2 = results2.find_all('tr', {'class': 'row'})

    df = pd.DataFrame(columns=['wilayah', 'jokowi', 'prabowo'])

    for r in rows2:
        # find all columns per result
        data = r.find_all('td')
        # check that columns have data
        if len(data) == 0:
            continue

        satu = data[2].find('span', attrs={'class': 'abs'}).getText()
        dua = data[3].find('span', attrs={'class': 'abs'}).getText()
        # Remove decimal point
        satu = satu.replace('.', '')
        dua = dua.replace('.', '')
        # Cast Data Type Integer
        satu = int(satu)
        dua = int(dua)

        df = df.append({
            'wilayah': data[1].find('a').getText().lower(),
            'jokowi': satu,
            'prabowo': dua
        }, ignore_index=True)

    return df


provinsi = [
    'aceh', 'sumatera utara', 'sumatera barat', 'riau',
    'jambi', 'sumatera selatan', 'bengkulu', 'lampung'
]

data_bps = get_bps()

# %%
data_kawal = get_kawal_pemilu()

