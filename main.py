#!/usr/bin/python
# -*- coding: utf-8 -*-


__author__ = 'onotole'
print_result = 1
from bs4 import BeautifulSoup
import re
import time
import urllib2
from socket import timeout
import sys
import csv
import codecs


def load_helper(uri):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    try:
        thing = opener.open(uri, None, 10)
        soup = BeautifulSoup(thing.read(), "lxml")
        if not (soup is None):
            return soup
        else:
            print "soup is None"
            load_helper(uri)
    except (timeout, urllib2.HTTPError, urllib2.URLError) as error:
        sys.stdout.write("{} encountered, hold on, bro".format(error))
        sys.stdout.flush()
        time.sleep(30)
        load_helper(uri)


def get_number(tr):
    numberItem = int(tr.find("span").get_text()[:-1])
    if print_result: print(numberItem)
    return numberItem


def get_metro_station(tr):
    metro_raw = tr.find('a', attrs={'href': re.compile("metro")})
    metro_station = metro_raw.get_text()
    if print_result:
        print(metro_station)
    return metro_station


def get_metro_distance(tr):
    walk_type = u'пешком'
    metro_distance = tr.find("span", attrs={'class': re.compile('objects_item_metro_comment')}).get_text()
    metro_distance_minute = re.search('\d+', metro_distance).group()
    metro_distance_walk = re.search(u'пешком', metro_distance)
    metro_distance_car = re.search(u'на машине', metro_distance)

    distance_type = ""
    if metro_distance_walk:
        distance_type = "пешком"
        on_car = False
    elif metro_distance_car:
        distance_type = "на машине"
        on_car = True
    else:
        print("error with distance to metro")
        print(metro_distance)
    distance_to_metro = str(metro_distance_minute) + " мин. " + distance_type
    if on_car:
        distance_to_metro_universal = int(metro_distance_minute) * 5
    else:
        distance_to_metro_universal = int(metro_distance_minute)
    if print_result: print(distance_to_metro)
    return distance_to_metro_universal


def get_address(tr):
    address = ""
    for addressField in tr.find_all("div", attrs={'class': 'objects_item_addr'}):
        address += addressField.get_text().strip() + " "
    if print_result: print(address)
    return address


def get_rooms(tr):
    how_many_rooms = tr.find("div", attrs={'class': 'objects_item_info_col_2'}).find("strong").get_text()
    if print_result: print(how_many_rooms)
    return how_many_rooms


def get_price_roubles(tr):
    print tr
    price_roubles = tr.find("div", attrs={'class' :'objects_item_price'}).get_text()
    price_roubles_digit = re.findall('\d+', price_roubles.strip())
    price_roubles = ""
    for i in price_roubles_digit:
        price_roubles += i
    price_roubles = int(price_roubles)
    if print_result: print("стоимость в рублях:" + str(price_roubles))
    return price_roubles


def get_square_all(tr):
    print tr
    td = tr.find("div", attrs={'class':'objects_item_info_col_3'}).find_all("td")
    mainSize = 0
    for square in td:
        main = re.search(u'Общая: \d+ м', square.get_text())
        if main != None:
            mainSize = re.search('\d+', main.group())
            mainSize = mainSize.group()
            if print_result: print("Общая:" + str(mainSize))

    return int(mainSize)


def get_square_kitchen(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_3'}).find_all("td")
    kitchenSize = 0
    for square in td:
        kitchen = re.search(u'Кухня: \d+ м', square.get_text())
        if kitchen != None:
            kitchenSize = re.search('\d+', kitchen.group())
            kitchenSize = kitchenSize.group()
            if print_result: print("Кухня:" + str(kitchenSize))
    return int(kitchenSize)


def get_square_live(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_3'}).find_all("td")
    liveSize = 0
    for square in td:
        live = re.search(u'Жилая: \d+ м', square.get_text())
        if live != None:
            liveSize = re.search('\d+', live.group())
            liveSize = liveSize.group()
            if print_result: print("Жилая:" + str(liveSize))
    return int(liveSize)


def get_price_per_meter(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_4'})
    pricePerMeter = td.find('div', attrs={'style':'color:green;'})
    pricePerMeter=pricePerMeter.get_text().strip()[3:]
    pricePerMeterDigit = re.findall('\d+', pricePerMeter)
    pricePerMeter = ""
    for i in pricePerMeterDigit:
        pricePerMeter += i
    pricePerMeter = int(pricePerMeter)
    if print_result: print("цена в рублях за метр^2:" + str(pricePerMeter))
    return pricePerMeter


def get_building_type(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_5'})
    houseType = td.find('div', attrs={'class':'objects_item_info_col_w'}).get_text()
    houseTypeStr = re.search(u'[-а-яА-Я]+', houseType)
    houseType = str(houseTypeStr.group().encode('utf-8')).strip()
    if print_result: print(houseType)
    return houseType


def get_floor(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_5'})
    floor = td.find('div', attrs={'class':'objects_item_info_col_w'}).get_text()
    floorInfo = re.search('\d+/*\d*',floor)
    floor = str(floorInfo.group()).split('/')[0]
    if len(str(floorInfo.group()).split('/')) > 1:
        floorAll = str(floorInfo.group()).split('/')[1]
    floor = int(floor)
    if print_result: print("Этаж: " + str(floor))
    return floor


def get_floor_all(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_5'})
    floor = td.find('div', attrs={'class':'objects_item_info_col_w'}).get_text()
    floorAll = 0
    floorInfo = re.search('\d+/*\d*',floor)
    floor = str(floorInfo.group()).split('/')[0]
    if len(str(floorInfo.group()).split('/')) > 1:
        floorAll = str(floorInfo.group()).split('/')[1]
    floorAll = int(floorAll)
    if print_result and floorAll: print("Этажность:" + str(floorAll))
    return floorAll


def get_additional_properties(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_6'})
    td = td.find("table", attrs={'class':'objects_item_details'})
    td = td.find_all("td")
    lift = td[0]
    liftExist = re.search('\d+', str(lift))
    if liftExist == None:
        lift = 0
    else:
        lift = 1
    balcon = td[1]
    balconExist = re.search('\d+', str(balcon))
    if balconExist == None:
        balcon = 0
    else:
        balcon = 1

    window =  td[3].get_text().encode('utf-8')
    windowStreetExist = re.search('улица',window)
    if windowStreetExist != None:
        windowStreet = 1
    else : windowStreet = 0

    windowBackyardExist = re.search('двор',window)
    if windowBackyardExist != None:
        windowBackyard = 1
    else: windowBackyard = 0

    phone = td[4].get_text().encode('utf-8')
    phoneExist = re.search('да', phone)
    if phoneExist != None:
        phone = 1
    else: phone =0

    if print_result: print("Есть ли лифт:" + str(lift))
    if print_result: print("Есть ли балкон:" + str(balcon))
    if print_result: print("Есть ли окно на улицу:" + str(windowStreet))
    if print_result: print("Есть ли окно во двор:" + str(windowBackyard))
    if print_result: print("Есть ли телефон:" + str(phone))
    return [lift, balcon, windowStreet, windowBackyard, phone]


def get_info(tr):
    number = get_number(tr)
    print(number)
    metro_station = get_metro_station(tr)
    metro_distance = get_metro_distance(tr)
    address = get_address(tr)
    rooms = get_rooms(tr)
    square_all = get_square_all(tr)
    square_kitchen = get_square_kitchen(tr)
    square_live = get_square_live(tr)
    # fix cian bug
    if square_kitchen + square_live > square_all:
        square_kitchen = 0
        square_live = 0
    price_roubles = get_price_roubles(tr)
    price_dollars = get_price_dollars(tr)
    price_per_meter = get_price_per_meter(tr)
    building_type = get_building_type(tr)
    floor = get_floor(tr)
    floor_all = get_floor_all(tr)
    ap = get_additional_properties(tr)
    full_info = str(number) + "," + metro_station.encode('utf-8') + "," + str(metro_distance) + ',"' +\
                address.encode('utf-8') + '",' + rooms.encode('utf-8') + "," + str(square_all) + "," +\
                str(square_kitchen) + "," + str(square_live) + "," + str(price_roubles) + "," + str(price_dollars) + \
                "," + str(price_per_meter) + "," + building_type + "," + str(floor) + "," + str(floor_all) + "," \
                + str(ap[0]) + "," + str(ap[1]) + "," + str(ap[2]) + "," + str(ap[3]) + ',' +str(ap[4]) + '\n'
    full_info = full_info.decode('utf-8')
    print("saving file")
    file_table = codecs.open("6roomsflat.csv", "a", "utf-8")
    file_table.write(full_info)
    file_table.close()

rooms = 2
LINKORIGINAL = 'http://www.cian.ru/cat.php?deal_type=2&obl_id=1&city%5B0%5D=1&room' + str(rooms) + \
               '=1&sost_type=1&object_type=1&p='
for page_number in range(2, 3):
    time.sleep(2)
    LINK = LINKORIGINAL
    if page_number == 0:
        continue
    if page_number == 1:
        LINK = LINK[:-3]
    else:
        LINK += str(page_number)
    page = load_helper(LINK)

    tr_all = page.find_all("div", attrs={'class': re.compile('offer_container')})

    get_price_roubles(tr_all[3])

    #for tr in tr_all:
        #print tr
    #    get_rooms(tr)
    #     try:
    #         print(tr)
    #         getInfo(tr)
    #     except Exception:
    #         print("error")
    #         pass
