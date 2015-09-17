#!/usr/bin/python
# -*- coding: utf-8 -*-


__author__ = 'onotole'
printResult = 1
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
    if printResult: print(numberItem)
    return numberItem


def get_metro_station(tr):
    metro_raw = tr.find('a', attrs={'href': re.compile("metro")})
    metro_station = metro_raw.get_text()
    if printResult:
        print(metro_station)
    return metro_station


def get_metro_distance(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_1'})
    metroDistance = td.find("div", attrs={'class': 'objects_item_metro'}).find_all("span")[1].get_text()
    metroDistanceMinute = re.search('\d+', metroDistance)
    metroDistanceWalk = re.search(u'пешком', metroDistance)
    metroDistanceCar = re.search(u'на машине', metroDistance)
    distanceType = ""
    if ( metroDistanceWalk != None ):
        distanceType = "пешком"
        onCar = False
    elif ( metroDistanceCar != None):
        distanceType = "на машине"
        onCar = True
    else:
        print("error with distance to metro")
        print(metroDistance)
    distanceToMetro = str(metroDistanceMinute.group()) + " мин. " + distanceType
    if onCar:
        distanceToMetroUniversal = int(metroDistanceMinute.group()) * 5
    else:
        distanceToMetroUniversal = int(metroDistanceMinute.group())
    if printResult: print(distanceToMetro)
    return distanceToMetroUniversal


def get_address(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_1'})
    address = ""
    for addressField in td.find_all("div", attrs={'class': 'objects_item_addr'}):
        address += addressField.get_text().strip() + " "
    if printResult: print(address)
    return address


def get_rooms(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_2'}).find("a").get_text()
    howMuchRooms = td
    if printResult: print(howMuchRooms)
    return howMuchRooms


def get_square_all(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_3'}).find_all("td")
    mainSize = 0
    for square in td:
        main = re.search(u'Общая: \d+ м', square.get_text())
        if main != None:
            mainSize = re.search('\d+', main.group())
            mainSize = mainSize.group()
            if printResult: print("Общая:" + str(mainSize))

    return int(mainSize)


def get_square_kitchen(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_3'}).find_all("td")
    kitchenSize = 0
    for square in td:
        kitchen = re.search(u'Кухня: \d+ м', square.get_text())
        if kitchen != None:
            kitchenSize = re.search('\d+', kitchen.group())
            kitchenSize = kitchenSize.group()
            if printResult: print("Кухня:" + str(kitchenSize))
    return int(kitchenSize)


def get_square_live(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_3'}).find_all("td")
    liveSize = 0
    for square in td:
        live = re.search(u'Жилая: \d+ м', square.get_text())
        if live != None:
            liveSize = re.search('\d+', live.group())
            liveSize = liveSize.group()
            if printResult: print("Жилая:" + str(liveSize))
    return int(liveSize)


def get_price_roubles(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_4'})
    priceRoubles = td.find('strong').get_text()
    priceRoublesDigit = re.findall('\d+',priceRoubles.strip())
    priceRoubles = ""
    for i in priceRoublesDigit:
        priceRoubles += i
    priceRoubles = int(priceRoubles)
    if printResult: print("стоимость в рублях:" + str(priceRoubles))
    return priceRoubles


def get_price_dollars(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_4'})
    priceDollars = td.find('div', attrs={'class':'objects_item_second_price'}).get_text()
    priceDollarsDigit = re.findall('\d+',priceDollars.strip())
    priceDollars =""
    for i in priceDollarsDigit:
        priceDollars += i
    priceDollars = int(priceDollars)
    if printResult: print("стоимость в долларах:" + str(priceDollars))
    return priceDollars


def get_price_per_meter(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_4'})
    pricePerMeter = td.find('div', attrs={'style':'color:green;'})
    pricePerMeter=pricePerMeter.get_text().strip()[3:]
    pricePerMeterDigit = re.findall('\d+', pricePerMeter)
    pricePerMeter = ""
    for i in pricePerMeterDigit:
        pricePerMeter += i
    pricePerMeter = int(pricePerMeter)
    if printResult: print("цена в рублях за метр^2:" + str(pricePerMeter))
    return pricePerMeter


def get_building_type(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_5'})
    houseType = td.find('div', attrs={'class':'objects_item_info_col_w'}).get_text()
    houseTypeStr = re.search(u'[-а-яА-Я]+', houseType)
    houseType = str(houseTypeStr.group().encode('utf-8')).strip()
    if printResult: print(houseType)
    return houseType


def get_floor(tr):
    td = tr.find("td", attrs={'class':'objects_item_info_col_5'})
    floor = td.find('div', attrs={'class':'objects_item_info_col_w'}).get_text()
    floorInfo = re.search('\d+/*\d*',floor)
    floor = str(floorInfo.group()).split('/')[0]
    if len(str(floorInfo.group()).split('/')) > 1:
        floorAll = str(floorInfo.group()).split('/')[1]
    floor = int(floor)
    if printResult: print("Этаж: " + str(floor))
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
    if printResult and floorAll: print("Этажность:" + str(floorAll))
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

    if printResult: print("Есть ли лифт:" + str(lift))
    if printResult: print("Есть ли балкон:" + str(balcon))
    if printResult: print("Есть ли окно на улицу:" + str(windowStreet))
    if printResult: print("Есть ли окно во двор:" + str(windowBackyard))
    if printResult: print("Есть ли телефон:" + str(phone))
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




LINKORIGINAL = 'http://www.cian.ru/cat.php?deal_type=2&obl_id=1&city%5B0%5D=1&room6=1&sost_type=1&object_type=1&p='
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
    print tr_all[5]

    #for tr in tr_all:
        #get_metro_distance(tr)
    #     try:
    #         print(tr)
    #         getInfo(tr)
    #     except Exception:
    #         print("error")
    #         pass
