import os
import re
import shutil
import requests
import cairosvg
import PyPDF2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager




def get_score_title(soup):
    meta_tag = soup.find('meta', {'property': 'og:title'})
    if meta_tag:
        title = meta_tag.get('content')
        return title
    else:
        return None

def download_score_svg(urls, referer_url):
    # Create the subfolder if it doesn't exist
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": referer_url,
    }

    # Iterate over the list of URLs
    for i, url in enumerate(urls):
        # Define the path to save the file with an incremented number
        file_path = os.path.join("downloads", f"score_{i+1}.svg")

        # Send a GET request to the URL
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Open a file to write the SVG content
            with open(file_path, "wb") as file:
                file.write(response.content)
            #print(f"SVG file downloaded successfully and saved to {file_path}.")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

def convert_svg_to_pdf():
    # Convert the SVG file to a PDF file with A4 size
    # A4 size in pixels (96 dpi) = 210mm x 297mm = 210/25.4*96 x 297/25.4*96
    a4_width_in_pixels = 210 / 25.4 * 96
    a4_height_in_pixels = 297 / 25.4 * 96

    # Get the list of SVG files in the downloads folder
    svg_files = [file for file in os.listdir("downloads") if file.endswith(".svg")]

    # Create a subfolder for the PDF files if it doesn't exist
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

    # Iterate over the SVG files and convert them to PDF
    for svg_file in svg_files:
        # Define the path to the SVG file
        svg_path = os.path.join("downloads", svg_file)

        # Define the path to save the PDF file
        pdf_file = os.path.splitext(svg_file)[0] + ".pdf"
        pdf_path = os.path.join("pdfs", pdf_file)

        # Convert the SVG to PDF using CairoSVG
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_path, output_width=a4_width_in_pixels, output_height=a4_height_in_pixels)

        #print(f"SVG file '{svg_file}' converted to PDF and saved to '{pdf_path}'.")

def combine_pdfs(output_file_name):
    # Get the list of PDF files in the pdfs folder
    pdf_files = [file for file in os.listdir("pdfs") if file.endswith(".pdf")]

    # Function to extract the numeric part from the filename
    def extract_number(file_name):
        match = re.search(r'score_(\d+)', file_name)
        return int(match.group(1)) if match else 0

    # Sort the PDF files numerically based on the extracted number
    pdf_files.sort(key=extract_number)

    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()

    # Iterate over the PDF files and add them to the writer object
    for pdf_file in pdf_files:
        # Define the path to the PDF file
        pdf_path = os.path.join("pdfs", pdf_file)

        # Open the PDF file in read-binary mode
        with open(pdf_path, "rb") as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Iterate over the pages in the PDF file and add them to the writer object
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

    # Define the path to save the combined PDF file
    output_path = output_file_name + ".pdf"

    # Write the combined PDF file to disk
    with open(output_path, "wb") as file:
        pdf_writer.write(file)



# Initialize the WebDriver with headless option
options = Options()
#options.add_argument('--start-maximized')
options.add_argument('--force-device-scale-factor=0.01')
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

    print("Extracting Title")
    title = get_score_title(soup)

    images = []
    divs = soup.find_all('div', class_='EEnGW F16e6')
    for div in divs:
        img_tags = div.find_all('img')
        for img_tag in img_tags:
            src = img_tag.get('src')
            images.append(src)

    print("Extracting Pages...")    
    download_score_svg(images, url)
    convert_svg_to_pdf()
    print("Converting Pages...")
    combine_pdfs(title)
    print("Conversion completed")

finally:
    # Close the browser
    driver.quit()
    # Delete the downloads folder and its contents
    if os.path.exists("downloads"):
        shutil.rmtree("downloads")

    # Delete the pdfs folder and its contents
    if os.path.exists("pdfs"):
        shutil.rmtree("pdfs")