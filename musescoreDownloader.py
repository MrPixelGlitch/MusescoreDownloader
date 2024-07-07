from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests


def get_score_title(soup):
    meta_tag = soup.find('meta', {'property': 'og:title'})
    if meta_tag:
        title = meta_tag.get('content')
        return title
    else:
        return None

def download_score_svg(urls):
    # Create the subfolder if it doesn't exist
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    # Iterate over the list of URLs
    for i, url in enumerate(urls):
        # Define the path to save the file with an incremented number
        file_path = os.path.join("downloads", f"score_{i+1}.svg")

        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Open a file to write the SVG content
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"SVG file downloaded successfully and saved to {file_path}.")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")


# Initialize the WebDriver with headless option
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--force-device-scale-factor=0.01')
#options.add_argument('--headless')  # Run in headless mode if you don't need to see the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# main script
print('Welcome to Musescore Downloader')
print('Please paste the Musescore URL you wish to download')
print('URL:')

#todo: check url validity
url = input()
#url = 'https://musescore.com/user/2830596/scores/1421196'

driver.get(url)

# Wait for the JavaScript to load and render the desired element
try:
    # Get the page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    title = get_score_title(soup)

    # Save the page source to an HTML file
    #with open(f'{title}.html', 'w', encoding='utf-8') as file:
    #    file.write(page_source)


    images = []
    divs = soup.find_all('div', class_='EEnGW F16e6')
    for div in divs:
        img_tags = div.find_all('img')
        for img_tag in img_tags:
            src = img_tag.get('src')
            images.append(src)
    
    #print("Images found:")
    #for image in images:
    #    print(image)
    
    download_score_svg(images)

finally:
    # Close the browser
    driver.quit()