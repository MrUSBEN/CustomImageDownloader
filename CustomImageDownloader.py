# ================================ Made by: "USBEN" ========================================
# This program is a custom image downloader , this was only made for specific website.
# Only to be used as a reference on how to use Web parsers like BEAUTIFUL SOUP and SELENIUM
# Replace SAMPLETEXTS with your stuff , it might work.
# ==========================================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import re
import urllib.parse as urlparse
import requests
from bs4 import *


# url = "https://wallpapers.com/minimalist"


# ==============EXAMPLE FUNCTIONS==================================


def joinurl(baseurl, path):  # Joins url (needs work)
    return '/'.join([baseurl, path.lstrip("/")])


def RootDomain(url):  # Generates root domain to attach with trailing URLs
    URLsplit = urlparse.urlsplit(url)
    # print("URL data: ", URLsplit)
    rootURL = URLsplit.netloc
    URLscheme = URLsplit.scheme+":/"
    # URLcombined = urlparse.urljoin(str(URLscheme), rootURL)
    # print(URLcombined)
    URLcombined = joinurl(URLscheme, rootURL)
    return URLcombined


def GetLinks(url):  # (NOT-USED-FUNCTION) Just kept this function as a example of BeautifulSoup useage
    startLinks = []
    imageDatalinks = []
    imageDataDictionary = {}
    pass1counter = 0
    urlParsed = ParseHTML(url, "link")

    # first pass to get high resolution links
    for item in urlParsed.find_all("a"):
        try:
            itemparse = ParseHTML(item, "string")
            if(itemparse.a.attrs.__contains__("class")):
                if(itemparse.a["class"].__contains__("image_wrapper")):
                    pass1counter += 1
                    tailURL = itemparse.a["href"]
                    fullURL = joinurl(RootDomain(url), tailURL)
                    startLinks.append(fullURL)

                    #print(fullURL, "\n")
        except:
            continue
    print("[PASS1]Total Links: ", pass1counter)

    # Get image data link
    for item in startLinks:
        itemparse = ParseHTML(item, "link")
        for item in itemparse.find_all("img"):
            itemparse = ParseHTML(item, "string")
            try:
                if(itemparse.img["alt"].__contains__("SAMPLETEXT")):
                    link = itemparse.img["src"]
                    name = RegexName(link)
                    imageDataDictionary.update({name: link})
                    imageDatalinks.append(link)
                    print(link)
            except:
                continue

# =================================================================


def SoupImageLinks(linkList):  # (WAY FASTER -USE THIS) over SeleniumImageLinks function
    print("Started SoupImageLinks(This takes a while please wait)...")
    imageLinks = []
    for item in linkList:
        itemparse = ParseHTML(item, "link")
        for item in itemparse.find_all("img"):
            itemparse = ParseHTML(item, "string")
            try:
                if(itemparse.img["alt"].__contains__("SAMPLE TEXT")):
                    link = itemparse.img["src"]
                    # name = RegexName(link)
                    # imageDataDictionary.update({name: link})
                    imageLinks.append(link)
                    # print(link)
            except:
                continue
    WriteToFile("finallinks.txt", imageLinks)


def ParseHTML(content, type):  # Returns Parsed HTML data
    try:
        if(type == "link"):
            getURL = requests.get(content)
            parse = BeautifulSoup(getURL.text, "html.parser")
        elif(type == "string"):
            getURL = str(content)
            parse = BeautifulSoup(getURL, "html.parser")
        else:
            print("Invalid type specified.")
            return
        return parse
    except:
        print(
            "Something went wrong in ParseHTML. Make sure the link starts with (http[s]://).")


def WriteToFile(filename, data):  # Writes text data to file

    with open(os.path.join(os.getcwd(), filename), "w+", encoding="utf-8") as file:
        file.write(str(data))
        print("Data written to ", filename, ".\n")


def RegexName(urlData):  # Custom regex to get filename in link
    patternRegex = re.compile("[0-9]+.jpg")
    resultRegex = patternRegex.findall(urlData)
    returnResult = resultRegex[0].replace(".jpg", ".webp")
    return returnResult


def SeleniumSetup():  # Selenium driver setup with headless option

    driverOptions = webdriver.FirefoxOptions()
    driverOptions.headless = True
    driver = webdriver.Firefox(options=driverOptions)
    return driver


def GetInitialLinks(url):  # Extract links from the landing page provided

    driver = SeleniumSetup()
    driver.get(url)

    mainlinks = []

    # Main links extraction
    targetElement = driver.find_elements(
        By.XPATH, "//a[@class='SAMPLE_TEXT']")
    for all in targetElement:
        mainlink = all.get_attribute("href")
        # print(mainlink)
        mainlinks.append(mainlink)

    WriteToFile("startlinks.txt", mainlinks)


# (SLOW ASF, USE Beautiful soup version) Extract high-resolution image links
def SeleniumImageLinks(linkList):
    imagelinkList = []
    driver = SeleniumSetup()
    #  Getting content links
    for item in linkList:
        parselink = driver.get(item)
        targetelement = driver.find_element(
            By.XPATH, "//img[@alt='SAMPLE TEXT']")
        finallink = targetelement.get_attribute("src")
        # print(finallink)
        imagelinkList.append(finallink)

    WriteToFile("finallinks.txt", imagelinkList)


def ReadFileData(name):  # Reads file and returns as the respective data type
    with open(name, "r") as file:
        fileData = eval(file.read())
    return fileData


# Downloads image by accessing link with custom header data
def DownloadImage(url, imageName):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36", "referer": "https://www.[[SAMPLETEXT]].com/"}
    # Headers needed to bypass 403 Forbidden errors
    urlrequest = requests.get(url, headers=headers)

    imagePath = os.path.join(os.getcwd(), imageName)

    try:
        with open(imagePath, "wb") as imageFile:
            imageFile.write(urlrequest.content)
            print("Image ", imageName, " downloaded.")
    except:
        print("Image not downloaded. Check URL or directory.")


def DownloadAll(folderName, linkList):  # Custom function to bulk download all images
    try:
        os.mkdir(folderName)
        print(folderName, " folder created.")
    except:
        print("Folder already exists.")

    for item in linkList:
        DownloadImage(item, os.path.join(folderName, RegexName(item)))


def CoreLoop(url, index):
    # === CORE-LOOP======
    print("=== Started work on Page: ", index, " ====")

    GetInitialLinks(url)
    print("Initial page links obtained...")

    print("Getting main links...")
    firstData = ReadFileData("startlinks.txt")
    SoupImageLinks(firstData)
    print("Main image links obtained...")

    secondData = ReadFileData("finallinks.txt")
    folderName = "Page "+index
    DownloadAll(folderName, secondData)

    print("\nPage: ", index, " cleared.\n")
    # ====================


def PageIndexer(startPoint, loopLength):
    for i in range(startPoint, loopLength):
        iteratedURL = "[[SAMPLE TEXT]]" + \
            str(i)

        CoreLoop(iteratedURL, str(i))


def MAIN():

    print("\n---IMAGE DOWNLOADER STARTED---\n")

    # PageIndexer(31, 33)

    # DownloadAll("Page 30", ReadFileData("finallinks.txt"))


MAIN()
