from selenium import webdriver
from selenium import common
import time
import os

download_using = "requests"
overwrite = False
silent = False
logs = True
max_no_of_fails = 5
limit = 10

url = input("Enter a playlist url: ")
while True:
    download_path = input("Enter download path: ")
    if os.path.exists(download_path):
        break
    else:
        print("Path does not exist")

# chrome_options = webdriver.ChromeOptions()
# if not logs:
#     chrome_options.add_argument('log-level=3')
# if silent:
#     chrome_options.add_argument('--headless')
# driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Edge()


def get_links_from_playlist(playlist_url):
    youtube_links = {}
    driver.get(playlist_url)
    playlist = driver.find_element_by_id("contents")
    for element in playlist.find_elements_by_tag_name("ytd-playlist-video-renderer"):
        link = element.find_element_by_id("video-title").get_attribute("href").split("&")[0]
        name = element.find_element_by_id("video-title").get_attribute("title").split("&")[0]
        if logs:
            print("Name:" + name)
            print("Youtube link:" + link)
            print()
        youtube_links[link] = [name + ".mp3"]
    return youtube_links


def get_download_links_from_mp3juices(download_links):
    driver.get("https://www.mp3juices.cc/")
    query_box = driver.find_element_by_id("query")
    button = driver.find_element_by_id("button")

    start = 0

    for link in download_links.keys():
        if limit < start:
            break
        start += 1
        if logs:
            print()
        for attempt_no in range(1, max_no_of_fails + 1):
            download_link = get_download_link_from_mp3juices(link, query_box, button)
            # if download_data[0] == "" or "http" not in download_data[0]:
            if "http" not in download_link:
                if logs:
                    print("ERROR: unable to find the download link. Attempt no:"
                          + str(attempt_no) + " out of " + str(max_no_of_fails))
            else:
                # download_links[link] = download_data
                download_links[link].append(download_link)
                break
    return download_links


def get_download_link_from_mp3juices(single_link, query_box, button):
    if logs:
        print("Youtube link: " + single_link)
    query_box.send_keys(single_link)
    time.sleep(1)
    button.click()
    while True:
        try:
            driver.find_element_by_id("download_0")
            break
        except common.exceptions.StaleElementReferenceException:
            continue
    # time.sleep(1)
    container = driver.find_element_by_id("download_0")
    # download_link = container.find_element_by_class_name("url").get_attribute("href")
    while True:
        status = container.find_element_by_class_name("progress").text
        if status == "The file is ready. Please click the download button to start the download.":
            download_link = container.find_element_by_class_name("url").get_attribute("href")
            break
        elif status == "An error has occurred (code: e1-3). Please try to convert a different video.":
            download_link = "404"
            break
        elif status == "initializing":
            continue
        else:
            if logs:
                print("current status: " + status)

    # name = container.find_element_by_class_name("name").text + ".mp3"
    # download_data = [download_link, name]
    if logs:
        # print("Name :" + name)
        print("Download Link: " + download_link)

    query_box.clear()
    # return download_data
    return download_link


def start_download(download_links):
    if download_using == "requests":
        download_using_requests(download_links)
    elif download_using == "IDM":
        download_using_idm(download_links)
    else:
        print("unable to find this module, exiting")


def download_using_idm(download_links):
    from idm import IDMan
    idm = IDMan()

    for link in download_links:
        print()
        try:
            idm.download(download_links[link][1],
                         download_path,
                         output=download_links[link][0],
                         confirm=False)
        except Exception as ex:
            print("Unable to download music at link : " + link + " , error: " + ex.args[0])


def download_using_requests(download_links):
    import math
    import requests
    total = len(download_links)
    current = 1
    for link in download_links:
        print()
        print("downloading file :" + str(current) + " of " + str(total))
        try:
            r = requests.get(download_links[link][1], allow_redirects=True)
            open(download_path + "\\" + make_name_valid(download_links[link][0]), 'wb').write(r.content)
        except Exception as ex:
            print("Unable to download music at link :" + link + " , error: " + str(ex.args))
        print("downloaded file :" + str(current) + " of " + str(total) + ", " +
              str(math.ceil(current * 100 / total)) + "% done")
        current += 1


def make_name_valid(name):
    name = name.replace("/", "-")
    name = name.replace("\\", "-")
    name = name.replace(":", "-")
    name = name.replace("\"", "-")
    name = name.replace("<", "-")
    name = name.replace(">", "-")
    name = name.replace("?", "-")
    name = name.replace("*", "-")
    name = name.replace("|", "-")
    return name


def apply_overwrite_filter(download_links):
    invalid_links = []
    for link in download_links.keys():
        if os.path.isfile(download_path + "\\" + make_name_valid(download_links[link][0])):
            if logs:
                print("file already present in folder: name: " + download_links[link][0] + " link: " + link)
            invalid_links.append(link)
    for link in invalid_links:
        download_links.pop(link)
    return download_links


playlist_data = get_links_from_playlist(url)
if not overwrite:
    playlist_data = apply_overwrite_filter(playlist_data)
start_download(get_download_links_from_mp3juices(playlist_data))
driver.close()
