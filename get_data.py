"""
@author: Carlos Eduardo Gonçalves de Oliveira (cego669)


******************************************************************************
Description: this .py file contains all the code for taking data about apartments
in Goiânia according to the website vivareal. One requirement is that you
must have chromedriver.exe in the path of this script. You can download it here:
https://chromedriver.chromium.org/downloads
Pay attention to which version of Google Chrome you have in your computer.
When you run this .py file, it will open your browser.
DON'T CLOSE THE BROWSER!
******************************************************************************
This script worked in 09/16/2021
"""



import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import time



def getApHrefs():
    
    url = "https://www.vivareal.com.br/venda/goias/goiania/apartamento_residencial/"
    
    # initializing browser
    browser = webdriver.Chrome()
    browser.get(url)
    
    # getting href of each immobile in each page
    hrefs = []
    while True:
        html_text = browser.page_source
        soup = BeautifulSoup(html_text, "lxml")
        
        # for each "a" tag, get href
        apartments = soup.find_all("a", class_ = "property-card__content-link js-card-title")
        hrefs.extend([apartment["href"] for apartment in apartments])
        
        # then go to the next page, if it is possible
        try:
            next_page = browser.find_element_by_xpath("//li[@class='pagination__item']/a[@title='Próxima página']")
            next_page.click()
        except:
            try:
                cookie = browser.find_element_by_id("cookie-notifier-cta")
                cookie.click()
            except:
                break
        
        # wait some time until the page is loaded
        time.sleep(3)
        
    # quitting browser
    browser.quit()
    
    return list(set(hrefs))



def scrapAp(href):
    
    # initializing dictionary
    data = {"time": [],
           "price": [],
           "address": [],
           "area": [],
           "bedroom": [],
           "bathroom": [],
           "parking": [],
           "characteristic": [],
           "condominium": []}
    
    # acces url for the specified apartment
    html_text = requests.get("https://www.vivareal.com.br" + href).text
    
    # get soup
    soup = BeautifulSoup(html_text, "lxml")
    
    # wait some time
    time.sleep(3)
    
    # get data
    try:
        data["price"].append(soup.find("h3", class_ = "price__price-info js-price-sale").text)
    except:
        data["price"].append("")
    
    try:
        data["address"].append(soup.find("p", class_ = "title__address js-address").text)
    except:
        data["address"].append("")
    
    try:
        data["area"].append(soup.find("li", class_ = "features__item features__item--area js-area").text)
    except:
        data["area"].append("")
    
    try:
        data["bedroom"].append(soup.find("li", class_ = "features__item features__item--bedroom js-bedrooms").text)
    except:
        data["bedroom"].append("")
    
    try:
        data["bathroom"].append(soup.find("li", class_ = "features__item features__item--bathroom js-bathrooms").text)
    except:
        data["bathroom"].append("")
    
    try:
        data["parking"].append(soup.find("li", class_ = "features__item features__item--parking js-parking").text)
    except:
        data["parking"].append("")
    
    try:
        data["characteristic"] = soup.find("ul", class_ = "amenities__list").text
    except:
        data["characteristic"].append("")
    
    try:
        data["condominium"].append(soup.find("span", class_ = "price__list-value condominium js-condominium").text)
    except:
        data["condominium"].append("")
    
    data["time"].append(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    
    return pd.DataFrame(data)



if __name__ == "__main__":
    
    # initialize data
    data = pd.DataFrame({"time": [],
                            "price": [],
                           "address": [],
                           "area": [],
                           "bedroom": [],
                           "bathroom": [],
                           "parking": [],
                           "characteristic": [],
                           "condominium": []})
    
    # get href of all apartments
    hrefs = getApHrefs()
    for href in hrefs:
        # scrap each apartment and append the row of informations to dataframe
        data = pd.concat([data, scrapAp(href)], ignore_index = True)
    
    # finally, save the data
    data.to_csv("apartments_gyn.csv", index = False)