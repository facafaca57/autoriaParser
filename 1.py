import requests
import csv
import sqlite3
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver import ActionChains

print ("----------Start----------")

conn = sqlite3.connect("cars.db") 
cursor = conn.cursor()
try:
    cursor.execute("""CREATE TABLE IF NOT EXISTS annonce
                    (id integer primary key autoincrement, Url text, Name text, City text, Phone text, isCompany text)
                """)
except:
    print("Така таблиця вже їснує..")

announcementN = 1
pageNumber = 0
totalPages = 1500
title = True

def getUrl(pageN):
    url = "https://auto.ria.com/search/?categories.main.id=1&price.USD.gte=5000&price.currency=1&abroad.not=0&custom.not=-1&size=100&page=%d/" % (pageN)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    info = requests.get(url, headers = headers)
    func(info.text)

def func(info):
    global pageNumber, announcementN
    texts = BeautifulSoup(info, 'lxml')

    page = totalPages - 1
    txt = texts.find_all('section','ticket-item new__ticket t paid')
    
    for t in txt:
        getContent(t.find('a','m-link-ticket').get('href'))
        print("%d\n%d/%d\n" % (announcementN, pageNumber, page))
        announcementN = announcementN + 1

    while pageNumber < page:
        pageNumber += 1
        getUrl(pageNumber)
        if pageNumber == page:
            cursor.close()
            conn.close()
            exit()

    print ("----------Finish----------")

def getContent(url):
    global title
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    content = requests.get(url, headers = headers)
    soup = BeautifulSoup(content.text, 'lxml')
    
    if(soup.select_one("#autoDeletedTopBlock") != None):
        return
    announcementUrl = url
    authorName = soup.select_one("#userInfoBlock > div.seller_info.mb-15 > div > h4").text
    authorCity = soup.select_one("#userInfoBlock > ul > li:nth-child(1) > div").text
    authorPhone = soup.select_one("#phonesBlock > div:nth-child(1) > span")
    authorType = soup.select_one("#userInfoBlock > div.seller_info.mb-15 > div > div.seller_info_title.grey").text  # authorPhone['data-phone-number']

    # driver = webdriver.Firefox(executable_path = 'geckodriver.exe')
    # driver.get(url)
    # try:
    #     element = driver.find_element_by_class_name('tooltip-vin_code')
    #     hover = ActionChains(driver).move_to_element(element)
    #     hover.perform()
    # except Exception as inst:
    #     print(inst)

    print("announcementUrl: %s \nauthorName: %s \nauthorCity: %s \nauthorPhone: %s \nauthorType: %s \n" % (announcementUrl, authorName, authorCity, authorPhone['data-phone-number'], authorType))
    
    try:
        with open('AutoriaAnnouncement.csv', 'a', newline='') as csvfile:
            if(title):
                fieldnames = ['Url', 'Name','City','Phone','isCompany']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'Url': announcementUrl, 'Name': authorName, 'City' : authorCity, 'Phone' : authorPhone['data-phone-number'], 'isCompany' : authorType})
                title = False
            else:
                fieldnames = ['Url', 'Name','City','Phone','isCompany']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'Url': announcementUrl, 'Name': authorName, 'City' : authorCity, 'Phone' : authorPhone['data-phone-number'], 'isCompany' : authorType})
                saveDB(announcementUrl, authorName, authorCity, authorPhone['data-phone-number'], authorType)
    except Exception as inst:
        print(inst)

def saveDB(url, name, city, phone, isCompany):
    cursor.execute("""INSERT INTO annonce (url, name, city, phone, isCompany) 
                  VALUES ('%s', '%s', '%s', '%s', '%s')""" % (url, name, city, phone, isCompany)
               )
    conn.commit()

getUrl(pageNumber)