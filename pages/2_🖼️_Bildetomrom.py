import streamlit as st
from PIL import Image
import io, zipfile

st.title("Fjern tomrommet på kantene av PNG/WebP-bilder")

uploaded_files = st.file_uploader(
    "Last opp opptil 100 PNG eller WebP-bilder samtidig. Send mail til kjetilo@elotec.no for forslag eller opplever problemer.",
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

    for file in files_to_process:
        image = Image.open(file)
        trimmed_image = trim_transparent(image)

        # Lagre beskåret bilde i minnet
        buf = io.BytesIO()
        trimmed_image.save(buf, format="PNG")
        buf.seek(0)
        cropped_images.append((f"cropped_{file.name}.png", buf.getvalue()))

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
            label="Last ned alle som ZIP",
            data=zip_buffer,
            file_name="cropped_images.zip",
            mime="application/zip"
        )

    # Individuelle nedlastingsknapper rett under ZIP
    for filename, data in cropped_images:
        st.download_button(
            label=f"Last ned {filename}",
            data=data,
            file_name=filename,
            mime="image/png",
            key=f"dl_{filename}"
        )

    st.divider()  # Skillelinje før forhåndsvisningene

    # --- Vis alle bilder nederst ---
    for filename, data in cropped_images:
        st.image(data, width=200, caption=f"Beskåret: {filename}")
