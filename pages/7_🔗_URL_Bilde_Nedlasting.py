
import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import zipfile
import io

def get_best_image_from_srcset(srcset, base_url):
    """Parses srcset and returns the URL of the highest resolution image."""
    best_url = ""
    max_width = 0
    for item in srcset.split(','):
        item = item.strip()
        parts = item.split()
        url_part = parts[0]
        
        if len(parts) > 1 and parts[1].endswith('w'):
            try:
                width = int(parts[1][:-1])
                if width > max_width:
                    max_width = width
                    best_url = url_part
            except ValueError:
                continue  # Skip if width is not a valid number
        elif not best_url: # Fallback to the first url if no width specifier is found
            best_url = url_part

    if best_url:
        return urljoin(base_url, best_url)
    return None

st.set_page_config(page_title="URL Bilde Nedlaster", page_icon="🔗")

st.title("🔗 Last ned bilder fra URL")
st.write("Lim inn en URL nedenfor for å finne og laste ned alle bildene i høyest mulig oppløsning.")

url = st.text_input("Nettadresse (URL)", key="image_downloader_url")

if st.button("Start nedlasting", key="start_download_button"):
    if url:
        try:
            st.info(f"Kobler til {url}...")

            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options
            import time

            # Setup chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

            with st.spinner("Starter en virtuell nettleser for å laste siden... (dette kan ta et øyeblikk)"):
                # Use webdriver-manager to automatically download and manage the chromedriver
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                driver.get(url)
                
                # Wait for JavaScript to load content. A fixed sleep is simple but can be effective.
                st.spinner("Lar siden laste inn alt innhold...")
                time.sleep(5) 
                
                html_content = driver.page_source
                driver.quit()

            soup = BeautifulSoup(html_content, 'html.parser')
            img_tags = soup.find_all('img')

            if not img_tags:
                st.warning("Fant ingen bilder (<img>-tags) på denne siden, selv etter å ha brukt en virtuell nettleser.")
                st.stop()

            image_urls = []
            with st.spinner(f"Fant {len(img_tags)} bilder. Analyserer for å finne beste kvalitet..."):
                for img in img_tags:
                    best_url = None
                    # 1. Prioritize srcset for highest resolution
                    if img.has_attr('srcset'):
                        best_url = get_best_image_from_srcset(img['srcset'], url)
                    
                    # 2. Fallback to a high-res source attribute if it exists
                    if not best_url and img.has_attr('data-src-high-res'):
                         best_url = urljoin(url, img['data-src-high-res'])

                    # 3. Fallback to the standard src attribute
                    if not best_url and img.has_attr('src'):
                        src = img['src']
                        # Ignore tiny or placeholder images encoded in the URL
                        if not src.startswith('data:image'):
                            best_url = urljoin(url, src)

                    if best_url and best_url not in image_urls:
                        image_urls.append(best_url)

            if not image_urls:
                st.warning("Kunne ikke hente ut noen gyldige bilde-URLer fra <img>-taggene.")
                st.stop()

            st.success(f"Klar til å laste ned {len(image_urls)} unike bilder.")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                progress_bar = st.progress(0)
                for i, image_url in enumerate(image_urls):
                    try:
                        # Use requests to download the actual image file, as Selenium is not needed for this part
                        img_response = requests.get(image_url, stream=True, timeout=15)
                        img_response.raise_for_status()
                        
                        # Get a clean filename from the URL
                        parsed_path = urlparse(image_url).path
                        filename = os.path.basename(parsed_path)
                        if not filename or '.' not in filename:
                            # If no filename or extension, create a generic one
                            content_type = img_response.headers.get('content-type')
                            ext = '.jpg' # default
                            if content_type and 'image/' in content_type:
                                ext = '.' + content_type.split('/')[1].split('+')[0]
                            filename = f"image_{i+1}{ext}"

                        # Add file to zip
                        zip_file.writestr(filename, img_response.content)
                        progress_bar.progress((i + 1) / len(image_urls), text=f"Laster ned {filename}...")
                    
                    except requests.exceptions.RequestException as e:
                        st.error(f"Kunne ikke laste ned {image_url}: {e}")

            progress_bar.empty()
            st.success("Alle bilder er pakket i en ZIP-fil!")

            domain_name = urlparse(url).netloc.replace('.', '_')
            zip_filename = f"bilder_{domain_name}.zip"

            st.download_button(
                label=f"Last ned {zip_filename}",
                data=zip_buffer.getvalue(),
                file_name=zip_filename,
                mime="application/zip",
            )

        except Exception as e:
            st.error(f"En uventet feil oppstod: {e}")
    else:
        st.warning("Vennligst skriv inn en URL.")
