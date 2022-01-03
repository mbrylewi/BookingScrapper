from datetime import datetime, date, timedelta
import os
from sys import exit
import pandas as pd
import time

from selenium import webdriver
from datetime import date, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from time import gmtime, strftime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


ROW_PER_OFFSET = 25

global my_options 
my_options = Options()
my_options.add_argument("--incognito")
my_options.add_argument("--ignore-certificate-errors")
my_options.add_experimental_option('excludeSwitches', ['enable-logging'])


def create_url(city, datein, dateout=None, offset=0, people=2, no_sleep=1, currency='JPY'):
    # Checking the format of the date, has to YYYY-MM-DD
    format = "%Y-%m-%d"
    try:
        datetime.strptime(datein, format)
    except ValueError:
        raise ValueError('Incorrect data format, should be YYYY-MM-DD')
    # Check the validity of the date
    if((date.fromisoformat(datein) - date.today()).days < 0):
        print('Error. The date you selected is in the past.')
        exit()
    formated_datein = date.fromisoformat(datein)
    if dateout is None:
        dateout = formated_datein + timedelta(days=no_sleep)
        formated_dateout = dateout
    else:
        formated_dateout = date.fromisoformat(dateout)
    url = "https://www.booking.com/searchresults.html?checkin_month={in_month}" \
        "&checkin_monthday={in_day}&checkin_year={in_year}&checkout_month={out_month}" \
        "&checkout_monthday={out_day}&checkout_year={out_year}&group_adults={people}" \
        "&group_children=0&order=price&ss={city}%2C%20&offset={offset}&language=en-us&selected_currency={currency}"\
        .format(in_month=str(formated_datein.month),
                in_day=str(formated_datein.day),
                in_year=str(formated_datein.year),
                out_month=str(formated_dateout.month),
                out_day=str(formated_dateout.day),
                out_year=str(formated_dateout.year),
                people=people,
                city=city,
                offset=offset,
                currency=currency)
    return url


def next_page(booking_url, input_offset, currency='JPY'):
    # Firt, the standard link we got from searching without dates is trimmed of "&", we grab those values and separate them into a format key=value
    trimmed = booking_url.split('&')
    attributes, values = [], []
    for e in trimmed:
        attributes.append(e.partition('=')[0])
        values.append(e.partition('=')[2])

    post_list = dict(zip(attributes, values))
    post_list['offset'] = input_offset
    joined = []
    for key, value in post_list.items():
        joined.append('{}={}'.format(key, value))

    final_link = '&'.join(joined)
    # Princes are in DZA, so let's get them in JPY
    final_link = final_link+'&selected_currency={}'.format(currency)
    return final_link+'#map_closed'+'&top_ufis=1'



def format_url(booking_url, datein, dateout=None, currency='JPY',no_sleep=1):
    # Firt, the standard link we got from searching without dates is trimmed of "&", we grab those values and separate them into a format key=value
    trimmed = booking_url.split('&')
    # Checking the format
    format = "%Y-%m-%d"
    try:
        datetime.strptime(datein, format)
    except ValueError:
        raise ValueError('Incorrect data format, should be YYYY-MM-DD')
    # Check the validity of the date
    if((date.fromisoformat(datein) - date.today()).days < 0):
        print('Error. The date you selected is in the past.')
        exit()
    formated_datein = date.fromisoformat(datein)
    if dateout is None:
        dateout = formated_datein + timedelta(days=no_sleep)
        formated_dateout = dateout
        
    
    attributes, values = [], []
    for e in trimmed:
        attributes.append(e.partition('=')[0])
        values.append(e.partition('=')[2])
  
    post_list = dict(zip(attributes, values))
    post_list['checkin_year'],post_list['checkin_month'],post_list['checkin_monthday'] = formated_datein.year,formated_datein.month,formated_datein.day
    post_list['checkout_year'],post_list['checkout_month'],post_list['checkout_monthday'] = formated_dateout.year,formated_dateout.month,formated_dateout.day
    post_list['ssne'] = ''
    post_list['ssne_untouched'] = '' 
    post_list['dest_id'] = ''
    joined = []
    for key, value in post_list.items():
        joined.append('{}={}'.format(key, value))

    final_link = '&'.join(joined)
    return final_link+'&selected_currency={}'.format(currency)


def clean(input:str) -> int:
  input = input.removesuffix('Showing 1 - 25')
  k = input.replace('\n',',').replace('…','').split(',')
  return int(max(k))


def get_number_pages(web_driver: WebDriver) -> int:
    try:
        all_pages = WebDriverWait(web_driver, timeout=5).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR,'[data-testid="pagination"]')))
    except TimeoutException:
        print('Cannot find number of pages')
        return 0
    else:
        return clean(all_pages.text)



def get_hotel_name(hotel_driver: WebDriver):
    try:
        hotel_name = WebDriverWait(hotel_driver, timeout=5).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="title"]')))
    except TimeoutException:
        print("Exception has been thrown. ")
        print('Cannot find hotel name element')
        
        return 'Hotel name unknown'
    else:
        return hotel_name.text.strip()


def get_hotel_price(hotel: WebDriver):
    try:
        price = WebDriverWait(hotel, timeout=5).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME,'bui-price-display__value')))
    except TimeoutException:
        print("Exception has been thrown. ")
        print('Cannot find hotel price element')        
        return ""
    else:
        return price.text.replace('¥', '').replace(',', '').strip()


def get_hotel_price_simple(hotel_driver:WebDriver):
    try: 
        price = WebDriverWait(hotel_driver, timeout=3).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR,'[data-testid="price-and-discounted-price"]')))
    except TimeoutException:
        print("Exception has been thrown. ")
        print('Cannot find hotel price element')
        price = ''
        return 'hotel price unknown'
    else:
        return price.text.strip()



def get_hotel_details_link(hotel_driver: WebDriver):
    try:
        link = WebDriverWait(hotel_driver, timeout=5).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR,'[data-testid="title-link"]')))
    except TimeoutException:
        print("Exception has been thrown. ")
        print('Cannot find link element.')
        return None
    else:
        return link.get_attribute('href')


def get_max_occupancy_room_type(hotel_driver:WebDriver):
    try:
        room_string = WebDriverWait(hotel_driver, timeout=3).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME,'room_link')))
    except TimeoutException:
        print("Exception has been thrown. ")
        print('Cannot find link element.')
        return "",""        
    else:
        room_string = room_string.replace('Max people', ' Max people').replace(
            '–', '').replace('-', '').replace('\n', '').replace('•­', '').replace('•', '')

        splitted_room_string = room_string.split('Max people:')

        if ' '.join(splitted_room_string) == room_string:
            room_type, max_occupancy = room_string, ""

        elif len(splitted_room_string) < 2:
            room_type = room_string
            max_occupancy = ""

        else:
            room_type, max_occupancy = splitted_room_string[0].strip(), splitted_room_string[1].strip()   
        return room_type, max_occupancy


def url_parser(website_url):
    trimmed = website_url.split('&')
    attributes, values = [], []
    for e in trimmed:
        attributes.append(e.partition('=')[0])
        values.append(e.partition('=')[2])

    post_list = dict(zip(attributes, values))
    print(post_list)


def generate_file(dest, datein, path, hotels_dict):
    """
    This function filters the hotels retrieved in the process. It first removes all the "Capsule Hotels" and "Hostels". Then, it separates them
    into two sheets : Stay Sakura's hotels, and the others that do not belong to them.
    """
    #Create columns name for each data type.
    hotel_columns = ['hotel_name', 'room_type', 'room_size',
                     'room_price', 'max_occupancy', 'meal_info','remaining_rooms']
    hotels = pd.DataFrame.from_dict(
        hotels_dict, orient='index', columns=hotel_columns)

    hotels['checkin_date'] = datein
    

    # First remove all Hostels and Capsule hotels
    filtered = hotels.drop(hotels[hotels['hotel_name'].str.contains(
        'Hostel |HOSTEL |hostel|capsule|Capsule|CAPSULE')].index)
    
    #SEPARATE DATAFRAMES & GENERATE TWO SHEETS 
    stayjap_hotels = filtered[filtered['hotel_name'].str.contains(
        '[A-a]sakusa [Y-y]okozuna |art deco |ART DECO|[E-e]do [N-n]o [M-m]ai|[T-t]okyo [A-a]sakusa [T-t]ownhouse|[A-a]rt [D-d]eco|[H-h]yaku [K-k]ura|HYAKU KURA')]
    different_hotels = filtered.drop(filtered[filtered['hotel_name'].str.contains(
        '[A-a]sakusa [Y-y]okozuna |art deco |ART DECO|[E-e]do [N-n]o [M-m]ai|[T-t]okyo [A-a]sakusa [T-t]ownhouse|[A-a]rt [D-d]eco')].index)
    
    
    # Generating the name of the file so it will be unique
    date_time_obj = datetime.now()
    time_stamp = date_time_obj.strftime('%H_%M_%S')
    file_name = '_'.join([dest, datein, time_stamp])
    
    # Saving under a path :
    saving_path = '{}\\{}.xlsx'.format(path, file_name)
    
    # Write each dataframe to a different worksheet.
    with pd.ExcelWriter('{}\\{}.xlsx'.format(path, file_name), engine='xlsxwriter') as writer:
        different_hotels.to_excel(writer, sheet_name='other_hotels')
        stayjap_hotels.to_excel(writer, sheet_name='stay_sakura_hotels')
        
    return saving_path


def traverse_dates(start_date, interval_in_days=30):
    delta = timedelta(days=1)
    start_date = date.fromisoformat(start_date)
    for _ in range(0, interval_in_days):
        iso_start_date = start_date.isoformat()
        print(iso_start_date)
        start_date += delta
        
def get_room_type(hotel):
    try:
        hotel.find_element(By.CLASS_NAME,'hprt-roomtype-link')
    except NoSuchElementException:
        return None
    return hotel.find_element(By.CLASS_NAME,'hprt-roomtype-link').text


def get_room_size(hotel):
    try:
        hotel.find_element(By.CSS_SELECTOR,"[data-name-en='room size']")
    except NoSuchElementException:
        return None
    return hotel.find_element(By.CSS_SELECTOR,"[data-name-en='room size']").text


def get_meal_info(hotel):
    """
    With this function, we fetch the option for the meal. There are 3 types : All Inclusive, Breakfast & Dinner included and Breakfast only.
    :return -> str
    """
    meal_info = "Without meals"
    try:
        hotel.find_element(By.CLASS_NAME,'bicon-allinclusive')
    except NoSuchElementException:
        try:
            hotel.find_element(By.CLASS_NAME,'bicon-forkknife')
        except NoSuchElementException:
            try:
                hotel.find_element(By.CLASS_NAME,'bicon-coffee')
            except NoSuchElementException:
                return meal_info
            return "With breakfast"
        return "With breakfast & dinner"
    return "All Inclusive"



def get_max_occupancy(hotel):
    """
    This function fetches the maximum number of persons per room.
    """
    try:
        hotel.find_element(By.CLASS_NAME,
            'hprt-occupancy-occupancy-info').get_attribute("innerText")
    except NoSuchElementException:
        return ""
    string = hotel.find_element(By.CLASS_NAME,
        'hprt-occupancy-occupancy-info').get_attribute("innerText")
    max_occupancy = [int(s) for s in string.split() if s.isdigit()]
    return max_occupancy[-1]

def get_remaining_rooms(hotel):
    """
    This function fetches the remaining rooms for a type of room.
    """
    try:
        hotel.find_element(By.CLASS_NAME,'top_scarcity')
    except NoSuchElementException:
        return None
    return hotel.find_element(By.CLASS_NAME,'top_scarcity').text


def get_hotel_details(hotel_id, hotel_name, web_driver, hotel_link,date_in,verbosity=False):
    """
    This function is the one that opens a new tab for each hotel, fetches all the rooms it offers (with its type,surface, price and occupancy).
    """
    # Open a new window
    web_driver.execute_script("window.open('');")
    # Switch to the new window and open new URL
    web_driver.switch_to.window(web_driver.window_handles[1])
    web_driver.get(hotel_link)
    web_driver.implicitly_wait(3)
    hotel_info = []
    hotel = {}
    default_type = None
    default_size = None
    default_remaining_rooms = None
    table = web_driver.find_elements(By.CLASS_NAME,'js-rt-block-row')
    if table is not None:
        for row in table:
            room_type = get_room_type(row)
            if room_type is None:
                room_type = default_type
            else:
                default_type = room_type
            max_occupancy = get_max_occupancy(row)
            room_price = get_hotel_price(row)
            room_breakfast = get_meal_info(row)
            room_size = get_room_size(row)
            remaining_rooms = get_remaining_rooms(row)
            if remaining_rooms is None:
                 remaining_rooms = default_remaining_rooms
            else:
                default_remaining_rooms = remaining_rooms
            if room_size is None:
                room_size = default_size
            else:
                default_size = room_size
            hotel_info = [hotel_name, room_type, room_size,
                          room_price, max_occupancy, room_breakfast,remaining_rooms,date_in]
            if verbosity:   
                print(hotel_info)

            hotel[hotel_id] = hotel_info
            hotel_id += 1
        if verbosity:    
            print('[~] Finished retrieving details for {}'.format(hotel_name))

        web_driver.switch_to.window(web_driver.window_handles[-1])
        web_driver.close()
        web_driver.switch_to.window(web_driver.window_handles[0])
        return hotel_id, hotel
    else:
        print('Not available')

    

def generate_file_date(dest, path:str, hotels_dict):
    """
    This function filters the hotels retrieved in the process. It first removes all the "Capsule Hotels" and "Hostels". Then, it separates them
    into two sheets : Stay Sakura's hotels, and the others that do not belong to them.
    """
    #Create columns name for each data type.
    hotel_columns = ['hotel_name', 'room_type', 'room_size',
                     'room_price', 'max_occupancy', 'meal_info','remaining_rooms','checkin_date']
    
    hotels = pd.DataFrame.from_dict(
        hotels_dict, orient='index', columns=hotel_columns)

    

    # First remove all Hostels and Capsule hotels
    filtered = hotels.drop(hotels[hotels['hotel_name'].str.contains(
        'Hostel |HOSTEL |hostel|capsule|Capsule|CAPSULE')].index)
    
    #SEPARATE DATAFRAMES & GENERATE TWO SHEETS 
    stayjap_hotels = filtered[filtered['hotel_name'].str.contains(
        '[A-a]sakusa [Y-y]okozuna |art deco |ART DECO|[E-e]do [N-n]o [M-m]ai|[T-t]okyo [A-a]sakusa [T-t]ownhouse|[A-a]rt [D-d]eco|[H-h]yaku [K-k]ura|HYAKU KURA')]
    different_hotels = filtered.drop(filtered[filtered['hotel_name'].str.contains(
        '[A-a]sakusa [Y-y]okozuna |art deco |ART DECO|[E-e]do [N-n]o [M-m]ai|[T-t]okyo [A-a]sakusa [T-t]ownhouse|[A-a]rt [D-d]eco')].index)
    
    
    # Generating the name of the file so it will be unique
    date_time_obj = datetime.now()
    time_stamp = date_time_obj.strftime('%H_%M_%S')
    file_name = '_'.join([dest, time_stamp])
    
    path = path.replace('/','\\')
    # Saving under a path :
    saving_path = '{}\{}.xlsx'.format(path, file_name)
    
    # Write each dataframe to a different worksheet.
    with pd.ExcelWriter(saving_path, engine='xlsxwriter') as writer:
        different_hotels.to_excel(writer, sheet_name='other_hotels')
        stayjap_hotels.to_excel(writer, sheet_name='stay_sakura_hotels')
        
    return saving_path



def scrapper(destination, checkin, is_verbose=False,path=os.getcwd(),checkout=None,interval=1,limit_page=3):
    """
    This function is redirecting the link with the input destination and date for each page.
    """
    starting_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print('Process started at {}'.format(starting_time))

    delta = timedelta(days=1)
    
    s=Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=s,options=my_options)

    hotel_id = 0

    for _ in range(0, interval):
        if is_verbose:
            print('[~] Searching for the date of {}'.format(checkin))

        starting_url = create_url(
            city=destination, datein=checkin, dateout=checkout)

        if is_verbose:
            print("[~] Url created:" + "\n" + "\t" + starting_url)

        browser.get(starting_url)
        browser.implicitly_wait(2)

        number_of_pages = get_number_pages(browser)
        
        if limit_page != 3:
            number_of_pages = limit_page
                    

        if is_verbose:
            print(print("[~] Pages to fetch: {}".format(number_of_pages)))

        offset = 0
        hotels = {}
        
        hotels_list = browser.find_elements(By.CSS_SELECTOR,'[data-testid="property-card"]')
        
        if is_verbose:
            print('[~] Hotels by page : {}'.format(len(hotels_list)))
        try:
            for page in range(0, number_of_pages):

                if is_verbose:
                    print('[~] Scrapping page {}...'.format(page+1))

                for hotel_el in hotels_list:
                    hotel_name = get_hotel_name(hotel_el)
                    hotel_link = get_hotel_details_link(hotel_el)
                    if hotel_link is not None:

                        if is_verbose:
                            print('[~] Fetching details for {}, may take a while...'.format(hotel_name))

                        hotel_id, hotels_from_link = get_hotel_details(hotel_id=hotel_id,
                                                                       hotel_name=hotel_name,
                                                                       web_driver=browser,
                                                                       hotel_link=hotel_link,
                                                                       date_in=checkin,
                                                                       verbosity = is_verbose)
                        hotels.update(hotels_from_link)
                        hotel_id += 1
                    else:
                        continue
                time.sleep(0.5)


                offset += ROW_PER_OFFSET
                next_page_var = next_page(browser.current_url, input_offset=offset)
                browser.get(next_page_var)
                browser.implicitly_wait(2)


            checkin = date.fromisoformat(checkin)
            checkin += delta
            iso_start_date = checkin.isoformat()
            checkin = iso_start_date
        except (KeyboardInterrupt,Exception):
            print('Exception happened.')
        finally:
            if is_verbose:
                    print("[~] Finished retrieved data. \n[~] Generating file...")

            generate_file_date(dest=destination,
                              path=path, 
                              hotels_dict=hotels)

            ending_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print('Process ended at at {}'.format(ending_time))
    
    

def scrapper_competitive(competitors, checkin, path, is_verbose=False,interval=1):
    """
    This function is redirecting the link given a list of competitors and date for each page.
    """
    
    URL = 'https://www.booking.com/'
    starting_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print('Process started at {}'.format(starting_time))

    delta = timedelta(days=1)
    
    s=Service(ChromeDriverManager().install())

    browser = webdriver.Chrome(service=s,options=my_options)

    hotel_id = 0
    hotels = {}
    count = 0
    for _ in range(0, interval):
        print('[~] Searching for the date of {}'.format(checkin))
        try:
            for competitor in competitors:
                browser.get(URL) 
                browser.implicitly_wait(1) 
                inputElement = browser.find_element(By.ID,'ss')     
                if count >= 1:
                    browser.execute_script("document.getElementById('ss').value = ''")

                inputElement.send_keys(competitor)
                inputElement.send_keys(Keys.ENTER)

                current_url = browser.current_url
                gen_url = format_url(current_url,checkin)

                if is_verbose:
                    print("[~] Url created:" + "\n" + "\t" + gen_url)

                gen_url = browser.get(gen_url)
                browser.implicitly_wait(3)

                hotels_list = browser.find_elements(By.CSS_SELECTOR,'[data-testid="property-card"]')

                competitor_hotel = hotels_list[0] #This will get the first element of the page
                hotel_name = get_hotel_name(competitor_hotel)
                hotel_link = get_hotel_details_link(competitor_hotel)
                if hotel_link is not None:
                    
                    if is_verbose:
                        print('[~] Fetching details for {}, may take a while...'.format(hotel_name))

                    hotel_id, hotels_from_link = get_hotel_details(hotel_id=hotel_id,
                                                                   hotel_name=hotel_name,
                                                                   web_driver=browser,
                                                                   hotel_link=hotel_link,
                                                                   date_in=checkin,
                                                                   verbosity=is_verbose)

                    hotels.update(hotels_from_link)
                    hotel_id += 1
                    count += 1
                else:
                    continue

            checkin = date.fromisoformat(checkin)
            checkin += delta
            iso_start_date = checkin.isoformat()
            checkin = iso_start_date
        except (KeyboardInterrupt,Exception): 
            print('Exception happened.')
        finally:
            if is_verbose:
                print("[~] Finished retrieved data. \n[~] Generating file...")   

            generate_file_date(dest='competitors',
                                path=path, 
                                hotels_dict=hotels)

            ending_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print('Process ended at at {}'.format(ending_time))
    
    
    
    
def simple_scrapper(destination, checkin, is_verbose=False,limit_page=None): 
    """This version returns quickly the hotel name and its price,without the details (room type, occupancy, number of left rooms,etc...)"""
    
    
    
    s=Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=s,options=my_options)
    
    # Redirecting the link with the input destination and date
    starting_url = create_url(city=destination,
                              datein=checkin)
    
    if is_verbose:
        print("[~] Url created:" + "\n" + "\t" + starting_url)

    browser.get(starting_url)
    browser.implicitly_wait(2)

    number_of_pages = get_number_pages(browser)
    
    if limit_page is not None:
        number_of_pages = limit_page
    
    offset = 0
    hotels = {}
    hotel_id = 0
    if is_verbose:
        print(print("[~] Pages to fetch: {}".format(number_of_pages)))

    for page in range(0, number_of_pages):
        
        if is_verbose:
            print('[~] Scrapping page {}...'.format(page+1))

        for hotel_el in browser.find_elements(By.CSS_SELECTOR,'[data-testid="property-card"]'):
            hotel_name = get_hotel_name(hotel_el)
            hotel_price = get_hotel_price_simple(hotel_el)
            
            hotel = [hotel_name, hotel_price]
            
            if is_verbose:
                print(hotel)
                
            hotels[hotel_id] = hotel
            hotel_id += 1
            time.sleep(0.5) 
         
          
        offset += ROW_PER_OFFSET
        next_page_var = next_page(browser.current_url, input_offset=offset)
        browser.get(next_page_var)
        browser.implicitly_wait(3)
