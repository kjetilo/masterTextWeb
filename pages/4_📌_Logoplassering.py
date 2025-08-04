import streamlit as st
from PIL import Image, UnidentifiedImageError
import io, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# Registrer HEIF/AVIF-støtte hvis tilgjengelig
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

st.title("📌 Legg til logo på bilder")

# --- Sidebar ---
st.sidebar.header("Innstillinger")
output_format = st.sidebar.radio(
    "Velg eksportformat",
    ["WebP", "PNG"],
    index=0,
    help="WebP gir mindre filer, PNG gir maksimal kompatibilitet"
)
logo_size_ratio = st.sidebar.slider(
    "Logo-størrelse (prosent av bildebredden)",
    min_value=5, max_value=50, value=15, step=1
)
position = st.sidebar.selectbox(
    "Logo-plassering",
    ["Øvre venstre", "Øvre høyre", "Nedre venstre", "Nedre høyre", "Senter"],
    index=3
)
padding = st.sidebar.slider(
    "Avstand fra kant (px)",
    min_value=0, max_value=200, value=20, step=1
)

# --- File uploads ---
uploaded_logo = st.file_uploader(
    "Last opp logo (PNG, WebP, TIFF)",
    type=["png", "webp", "tif", "tiff"]
)
uploaded_images = st.file_uploader(
    "Last opp bilder som skal merkes (PNG, WebP, TIFF, HEIC, AVIF)",
    type=["png", "webp", "tif", "tiff", "heic", "heif", "avif"],
    accept_multiple_files=True
)

def overlay_logo(image: Image.Image, logo: Image.Image, size_ratio=0.15, position="Nedre høyre", padding=20):
    """Legger logo på bildet i ønsket posisjon."""
    img = image.convert("RGBA")
    logo = logo.convert("RGBA")

    # Skaler logo
    logo_width = int(img.width * size_ratio)
    aspect_ratio = logo.width / logo.height
    logo_height = int(logo_width / aspect_ratio)
    logo_resized = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    # Beregn posisjon
    if position == "Øvre venstre":
        xy = (padding, padding)
    elif position == "Øvre høyre":
        xy = (img.width - logo_resized.width - padding, padding)
    elif position == "Nedre venstre":
        xy = (padding, img.height - logo_resized.height - padding)
    elif position == "Senter":
        xy = ((img.width - logo_resized.width)//2, (img.height - logo_resized.height)//2)
    else:  # Nedre høyre
        xy = (img.width - logo_resized.width - padding, img.height - logo_resized.height - padding)

    img.paste(logo_resized, xy, logo_resized)
    return img

def process_image(file, logo, size_ratio, position, padding, output_format):
    """Behandler ett bilde med logo."""
    try:
        image = Image.open(file)
    except UnidentifiedImageError:
        return None

    result_img = overlay_logo(image, logo, size_ratio, position, padding)

    buf = io.BytesIO()
    save_format = "WEBP" if output_format == "WebP" else "PNG"
    result_img.save(buf, format=save_format)  # alltid 100% kvalitet
    buf.seek(0)

    # Behold originalt navn
    base_name = file.name.rsplit('.', 1)[0]
    ext = output_format.lower()
    return f"{base_name}_logo.{ext}", buf.getvalue()

# --- Prosessering ---
if uploaded_logo and uploaded_images:
    logo_img = Image.open(uploaded_logo)
    st.write(f"Logo lastet opp: {uploaded_logo.name}")

    def process_all(files):
        results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(process_image, file, logo_img, logo_size_ratio/100, position, padding, output_format)
                for file in files
            ]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        return results

    processed = process_all(uploaded_images)

    st.subheader("🔽 Nedlastingsvalg")
    if len(processed) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for filename, data in processed:
                zip_file.writestr(filename, data)
        zip_buffer.seek(0)
        st.download_button(
            "Last ned alle som ZIP",
            data=zip_buffer,
            file_name=f"logoed_images.{output_format.lower()}.zip",
            mime="application/zip"
        )

    for filename, data in processed:
        st.download_button(
            label=f"Last ned {filename}",
            data=data,
            file_name=filename,
            mime=f"image/{output_format.lower()}",
            key=f"dl_{filename}"
        )

    st.divider()

    # Vis forhåndsvisning
    cols = st.columns(3)
    for idx, (filename, data) in enumerate(processed):
        with cols[idx % 3]:
            st.image(data, caption=filename, use_container_width=True)
