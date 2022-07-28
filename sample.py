from selenium import webdriver
from selenium import common
from idm import IDMan
import time
import requests

driver = webdriver.Chrome()

driver.get("<playlist url>")
playlist = driver.find_element_by_id("contents")
for element in playlist.find_elements_by_tag_name("ytd-playlist-video-renderer"):
    link = element.find_element_by_tag_name("a").get_attribute("href").split("&")[0]
    print(link)

driver.get("https://www.mp3juices.cc/")
query_box = driver.find_element_by_id("query")
query_box.send_keys("https://www.youtube.com/watch?v=YgFyi74DVjc")
button = driver.find_element_by_id("button")
time.sleep(1)
button.click()
while True:
    try:
        driver.find_element_by_id("download_0")
        break
    except common.exceptions.StaleElementReferenceException:
        continue
time.sleep(1)
container = driver.find_element_by_id("download_0")
link = container.find_element_by_class_name("url").get_attribute("href")

idm = IDMan()
idm.download("download_link", "download_path", output="file_name", confirm=False)

r = requests.get("download_link", allow_redirects=True)
open("download_path" + "\\" + "file_name", 'wb').write(r.content)
