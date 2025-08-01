import streamlit as st
from PIL import Image
import io, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

st.title("Fjern tomrommet på kantene av PNG/WebP-bilder og konverter til WebP")
st.sidebar.header("Innstillinger")

# Slider for WebP-kvalitet
webp_quality = st.sidebar.slider(
    "Velg WebP-kvalitet",
    min_value=50,
    max_value=100,
    value=90,
    step=1,
    help="Lavere verdi gir mindre filer, men lavere bildekvalitet"
)

uploaded_files = st.file_uploader(
    "Last opp opptil 100 PNG eller WebP-bilder samtidig. Send mail til kjetilo@elotec.no for forslag eller problemer.",
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

    # Save as WebP in memory
    buf = io.BytesIO()
    trimmed_image.save(buf, format="WEBP", quality=quality, method=6)
    buf.seek(0)

    out_name = f"cropped_{file.name.rsplit('.', 1)[0]}.webp"
    return out_name, buf.getvalue()

if uploaded_files:
    files_to_process = uploaded_files[:100]
    st.write(f"Antall bilder lastet opp: {len(files_to_process)}")

    # --- Progress bar ---
    progress_bar = st.progress(0)
    status_text = st.empty()

    cropped_images = []
    total = len(files_to_process)

    # Process images in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all tasks to the executor
        futures = {executor.submit(process_file, file, webp_quality): file for file in files_to_process}

        # Collect results as they complete
        for idx, future in enumerate(as_completed(futures), start=1):
            filename, data = future.result()
            cropped_images.append((filename, data))

            # Update progress
            progress_bar.progress(idx / total)
            status_text.text(f"Behandler bilde {idx}/{total}...")

    # Done
    status_text.text("✅ Ferdig!")
    progress_bar.empty()

    # --- Nedlastingsknapper øverst ---
    st.subheader("🔽 Nedlastingsvalg")

    # ZIP-nedlasting
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

    # Individuelle nedlastingsknapper rett under ZIP
    for filename, data in cropped_images:
        st.download_button(
            label=f"Last ned {filename}",
            data=data,
            file_name=filename,
            mime="image/webp",
            key=f"dl_{filename}"
        )

    st.divider()  # Skillelinje før forhåndsvisningene

    # --- Vis alle bilder nederst i 3 kolonner ---
    cols = st.columns(3)
    for idx, (filename, data) in enumerate(cropped_images):
        with cols[idx % 3]:
            st.image(data, caption=f"Beskåret: {filename}", use_container_width=True)
