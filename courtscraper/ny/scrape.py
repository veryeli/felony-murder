
import time
import pickle

from selenium import webdriver

from courtscraper.data_utils.consts import NY_SCRAPE_PATH, NY_URL


def get_info_from_page(driver):
    """Get info from page"""
    person_info = []
    time.sleep(1)

    rows = driver.find_elements('css selector', 'tr')
    for _ in rows:
        if _.text:
            person_info.append(_.text)

    rows2 = driver.find_elements("class name", 'row')
    for _ in rows2:
        if _.text:
            person_info.append(_.text)
    return person_info


def get_id_num(info):
    """Get id number"""
    if not info[1].strip():
        return None
    first = info[1].split()[0]
    if first == 'DWI:ALCOHOL/DRUGS-2ND':
        return None
    if any(_.isnumeric() for _ in first):
        return first


def get_new_driver_for_name(last_name, first_name):
    """Get new driver for name"""
    url = NY_URL
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get(url)
    time.sleep(6)
    driver.find_element('id', 'lst').send_keys(last_name)
    driver.find_element('id', 'fst').send_keys(first_name)
    driver.find_element('xpath', "//button[@type='submit']").click()
    return driver


def load_data():
    """Load data from pickle file"""
    # return pickle.load(open(NY_SCRAPE_PATH, 'rb'))
    return []

def get_start_letters(data):
    """When reloading data, which is alphabetically listed, start where you left off"""
    if not data:
        return 'A', 'A'
    last = data[-1]
    name = [_ for _ in last if ',' in _ and 'DIN' not in _][0].split('\n')[0].strip()
    last_name, first_name = name.split(',')
    if any(_.isnumeric() for _ in last_name):
        last_name = last_name.split()[1]
    last_name = last_name.strip()[:3]
    first_name = first_name.strip().split()[0]
    return first_name, last_name

def run_scraper():
    """Main functions"""
    infos = load_data()
    first_name, last_name = get_start_letters(infos)
    driver = get_new_driver_for_name(last_name, first_name)
    while 'Next →' in driver.page_source:
        while True:
            rows = driver.find_elements('css selector', 'tr')
            rows = [_ for _ in rows if _.text]
            for i, row in enumerate(rows):
                new_rows = driver.find_elements('css selector', 'tr')
                new_rows = [_ for _ in new_rows if _.text]

                row = new_rows[i]
                if i == 0 or not row.text or 'Race/Ethnicity' in row.text:
                    continue

                last_name = row.text.split()[1]
                if ',' in row.text:
                    text = row.text.replace(',,', ',')
                    first_name = text.split(',')[1].strip().split()[0]
                else: first_name = ''
                
                # ignore old and new DINS
                if int(row.text[:2]) < 7 or int(row.text[:2]) > 19:
                    continue
                elem = row.find_element('tag name', 'a')
                if not elem: 
                    continue
                elem.click()
                page_info = get_info_from_page(driver)
                infos.append(page_info)
                elem = driver.find_element('link text', '< Back to Search Results')
                elem.click()
            elem = driver.find_element('link text', 'Next →')
            elem.click()
            time.sleep(2)
            # save progress every 100 people
            if len(infos) % 100 == 0:
                pickle.dump(infos, open('infos.p', 'wb'))
                print(f'{first_name} {last_name} {len(infos)}', end = '')

    pickle.dump(infos, open(NY_SCRAPE_PATH, 'wb'))


if __name__ == '__main__':
    main()
