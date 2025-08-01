import streamlit as st
from PIL import Image
import io, zipfile

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

if uploaded_files:
    files_to_process = uploaded_files[:100]
    st.write(f"Antall bilder lastet opp: {len(files_to_process)}")

    cropped_images = []

    # --- Progress bar and status ---
    progress_bar = st.progress(0)
    status_text = st.empty()

    # --- Process files ---
    for idx, file in enumerate(files_to_process, start=1):
        image = Image.open(file)
        trimmed_image = trim_transparent(image)

        # Lagre beskåret bilde som WebP med valgt kvalitet
        buf = io.BytesIO()
        trimmed_image.save(buf, format="WEBP", quality=webp_quality, method=6)
        buf.seek(0)

        # Gi nytt navn med .webp
        out_name = f"cropped_{file.name.rsplit('.', 1)[0]}.webp"
        cropped_images.append((out_name, buf.getvalue()))

        # --- Update progress ---
        progress_bar.progress(idx / len(files_to_process))
        status_text.text(f"Behandler bilde {idx}/{len(files_to_process)}...")

    # --- Done ---
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
