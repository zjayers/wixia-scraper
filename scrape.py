from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import re
import urllib.request

base_url = "INSERT_BASE_URL_HERE"
driver = webdriver.Chrome()
driver.get(base_url)


def scrape():
    try:

        name = input('Ready?: ')

        sections = driver.find_elements_by_css_selector('.course-section')

        def create_url(n):
            return base_url + n.get_attribute('data-lecture-url')

        lecture_dict = {}

        counter = 1

        for section in sections:
            section_title = str(counter) + ' - ' + section.find_element_by_css_selector('.section-title').text.strip()
            section_lectures = section.find_elements_by_css_selector('.section-list li')
            lecture_urls = list(map(create_url, section_lectures))
            lecture_dict[section_title] = lecture_urls
            counter += 1

        for section_title, urls in lecture_dict.items():

            save_path = f"videos/{section_title}"

            try:
                os.mkdir(save_path)
            except OSError:
                print("Creation of the directory %s failed" % save_path)
            else:
                print("Successfully created the directory %s " % save_path)

            url_counter = 1

            for url in urls:
                driver.get(url)

                try:
                    video = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "w-json-ld"))
                    )

                    script = video.get_attribute('innerHTML')
                    linkMatches = re.findall(r"https://fast.wistia.net/embed/iframe/\w+", script)
                    driver.get(linkMatches[0])
                    source = driver.page_source
                    videoMatches = re.findall(r"https://embed-ssl.wistia.com/deliveries/\w+.bin", source)
                    videoToDownload = videoMatches[0]
                    full_save_path = f"{save_path}/{str(url_counter) + ' - ' + driver.title}"
                    urllib.request.urlretrieve(videoToDownload, full_save_path)
                    print(f"Downloaded: {full_save_path}")
                    url_counter += 1
                except TimeoutException as e:
                    print("Page load Timeout Occurred ... moving to next item !!!")

    finally:
        restart = input('Restart?: ')
        if restart == 'y':
            scrape()
        else:
            driver.quit()


scrape()
