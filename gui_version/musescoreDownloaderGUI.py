import os
import re
import shutil
import requests
import cairosvg
import PyPDF2
import pathlib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Utilities ---
def get_score_title(soup):
    meta_tag = soup.find('meta', {'property': 'og:title'})
    return meta_tag.get('content') if meta_tag else None

def download_score_svg(urls, referer_url):
    os.makedirs("downloads", exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": referer_url,
    }
    for i, url in enumerate(urls):
        file_path = os.path.join("downloads", f"score_{i}.svg")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)

def convert_svg_to_pdf():
    a4_width_px = 210 / 25.4 * 96
    a4_height_px = 297 / 25.4 * 96
    svg_files = [f for f in os.listdir("downloads") if f.endswith(".svg")]
    os.makedirs("pdfs", exist_ok=True)
    for svg_file in svg_files:
        svg_path = os.path.join("downloads", svg_file)
        pdf_path = os.path.join("pdfs", svg_file.replace(".svg", ".pdf"))
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_path,
                         output_width=a4_width_px, output_height=a4_height_px)

def combine_pdfs(output_path):
    pdf_files = sorted(
        [f for f in os.listdir("pdfs") if f.endswith(".pdf")],
        key=lambda x: int(re.search(r'score_(\d+)', x).group(1))
    )
    writer = PyPDF2.PdfWriter()
    for pdf_file in pdf_files:
        with open(os.path.join("pdfs", pdf_file), "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def cleanup():
    shutil.rmtree("downloads", ignore_errors=True)
    shutil.rmtree("pdfs", ignore_errors=True)

# --- GUI Logic ---
def start_conversion():
    url = url_entry.get().strip()
    if not url.startswith("http"):
        status_var.set("Invalid URL")
        return

    status_var.set("Starting browser...")
    root.update_idletasks()

    try:
        options = Options()
        options.add_argument('--force-device-scale-factor=0.01')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        status_var.set("Reading score...")
        root.update_idletasks()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = get_score_title(soup)
        if not title:
            raise Exception("Could not extract score title")

        images = []
        for div in soup.find_all('div', class_='EEnGW F16e6'):
            for img_tag in div.find_all('img'):
                images.append(img_tag.get('src'))

        status_var.set("Downloading pages...")
        download_score_svg(images, url)

        status_var.set("Converting to PDF...")
        convert_svg_to_pdf()

        global current_pdf_name
        current_pdf_name = title + ".pdf"
        status_var.set("Merging PDFs...")
        combine_pdfs(current_pdf_name)

        status_var.set("Done!")
        save_button.config(state=tk.NORMAL)

    except Exception as e:
        status_var.set("Error: " + str(e))
        messagebox.showerror("Error", str(e))
    finally:
        try:
            driver.quit()
        except:
            pass
        cleanup()

def save_pdf():
    if not current_pdf_name or not os.path.exists(current_pdf_name):
        messagebox.showwarning("No PDF", "No PDF has been generated.")
        return

    # Default to the user's Downloads folder
    downloads_path = str(pathlib.Path.home() / "Downloads")
    initial_file = os.path.join(downloads_path, current_pdf_name)

    output_path = filedialog.asksaveasfilename(
        initialdir=downloads_path,
        initialfile=current_pdf_name,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if output_path:
        shutil.move(current_pdf_name, output_path)
        status_var.set(f"Saved to: {output_path}")
        messagebox.showinfo("Saved", "PDF saved successfully!")
        url_entry.delete(0, tk.END)

# --- GUI Setup ---
root = tk.Tk()
root.title("Musescore Downloader")

tk.Label(root, text="Musescore URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

start_button = tk.Button(root, text="Start Conversion", command=start_conversion)
start_button.pack(pady=5)

save_button = tk.Button(root, text="Save Final PDF", command=save_pdf, state=tk.DISABLED)
save_button.pack(pady=5)

status_var = tk.StringVar(value="Idle")
tk.Label(root, textvariable=status_var, fg="blue").pack(pady=5)

current_pdf_name = None

root.mainloop()