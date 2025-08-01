import streamlit as st
from PIL import Image
import io, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

st.title("Fjern tomrommet på kantene av PNG/WebP-bilder og konverter til WebP")
st.sidebar.header("Innstillinger")

# Slider for WebP-kvalitet
webp_quality = st.sidebar.slider(
    "Velg WebP-kvalitet",
    min_value=0,
    max_value=100,
    value=100,
    step=1,
    help="Lavere verdi gir mindre filer, men lavere bildekvalitet"
)

uploaded_files = st.file_uploader(
    "Last opp opptil 300 PNG eller WebP-bilder samtidig.",
    type=["png", "webp"],
    accept_multiple_files=True
)

def trim_transparent(image: Image.Image) -> Image.Image:
    """Beskjærer gjennomsiktige kanter rundt bildet"""
    img = image.convert("RGBA")
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

def process_file(file, quality=90):
    """Processes a single uploaded file: trims and converts to WebP"""
    image = Image.open(file)
    trimmed_image = trim_transparent(image)

    buf = io.BytesIO()
    trimmed_image.save(buf, format="WEBP", quality=quality, method=6)
    buf.seek(0)

    out_name = f"cropped_{file.name.rsplit('.', 1)[0]}.webp"
    return out_name, buf.getvalue()

@st.cache_data(show_spinner=False)
def process_images(files, quality):
    """Process all images in parallel and cache the result"""
    files_to_process = files[:300]
    total = len(files_to_process)
    cropped_images = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, file, quality): file for file in files_to_process}

        for idx, future in enumerate(as_completed(futures), start=1):
            filename, data = future.result()
            cropped_images.append((filename, data))

            progress_bar.progress(idx / total)
            status_text.text(f"Behandler bilde {idx}/{total}...")

    status_text.text("✅ Ferdig!")
    progress_bar.empty()

    return cropped_images

if uploaded_files:
    cropped_images = process_images(uploaded_files, webp_quality)

    st.subheader("🔽 Nedlastingsvalg")

    # ZIP download
    if len(cropped_images) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for filename, data in cropped_images:
                zip_file.writestr(filename, data)
        zip_buffer.seek(0)

        st.download_button(
            label=f"Last ned alle som ZIP (WebP, kvalitet {webp_quality})",
            data=zip_buffer,
            file_name="cropped_images_webp.zip",
            mime="application/zip"
        )

    # Individual downloads
    for filename, data in cropped_images:
        st.download_button(
            label=f"Last ned {filename}",
            data=data,
            file_name=filename,
            mime="image/webp",
            key=f"dl_{filename}"
        )

    st.divider()

    # Show previews in 3 columns
    cols = st.columns(3)
    for idx, (filename, data) in enumerate(cropped_images):
        with cols[idx % 3]:
            st.image(data, caption=f"Beskåret: {filename}", use_container_width=True)
