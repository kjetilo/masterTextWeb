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

st.title("Fjern tomrommet på kantene av bilder og konverter")
st.sidebar.header("Innstillinger")

# Velg utdataformat
output_format = st.sidebar.radio(
    "Velg nedlastingsformat",
    ["WebP", "PNG"],
    index=0,
    help="WebP gir mindre filer, PNG gir maks kompatibilitet"
)

# Slider for WebP-kvalitet (vises kun hvis WebP valgt)
if output_format == "WebP":
    webp_quality = st.sidebar.slider(
        "Velg WebP-kvalitet",
        min_value=0,
        max_value=100,
        value=100,
        step=1,
        help="Lavere verdi gir mindre filer, men lavere bildekvalitet"
    )
else:
    webp_quality = 100  # Brukes for internprosessering

# Mulighet for kvadratiske bilder med luft
make_square_images = st.sidebar.checkbox("Lag kvadratiske bilder med luft", value=False)
padding_ratio = 0.0
if make_square_images:
    padding_ratio = st.sidebar.slider(
        "Luft rundt bildet (prosent av bildet)",
        min_value=0,
        max_value=50,
        value=10,
        step=1
    ) / 100

# Filnavnvalg
st.sidebar.subheader("Filnavnvalg")
article_number = st.sidebar.text_input(
    "Artikkelnummer for filnavn",
    value="",
    help="Fyll inn hvis du vil at filene skal hete f.eks. AE2010R, 1.webp"
)
keep_original_names = st.sidebar.checkbox(
    "Behold opprinnelige filnavn",
    value=False
)

uploaded_files = st.file_uploader(
    "Last opp opptil 300 bilder (.png, .jpg, .jpeg, .gif, .bmp, .tiff, .tif, .webp, .avif, .heic, .heif)",
    type=["png", "webp", "jpg", "jpeg", "gif", "bmp", "tiff", "tif", "avif", "heic", "heif"],
    accept_multiple_files=True
)

def trim_transparent(image: Image.Image) -> Image.Image:
    """Beskjærer gjennomsiktige kanter rundt bildet"""
    img = image.convert("RGBA")
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

def make_square(image: Image.Image, padding_ratio: float = 0.1) -> Image.Image:
    """Gjør bildet til et kvadrat med gjennomsiktig luft rundt"""
    w, h = image.size
    max_side = max(w, h)
    padded_side = int(max_side * (1 + padding_ratio * 2))  # Luft på alle sider

    square_img = Image.new("RGBA", (padded_side, padded_side), (0, 0, 0, 0))
    x = (padded_side - w) // 2
    y = (padded_side - h) // 2
    square_img.paste(image, (x, y))

    return square_img

def process_file(file, idx, quality=90, article_number="", keep_original=False, make_square_images=False, padding_ratio=0.1, output_format="WebP"):
    """Behandler en fil: Trimmer og konverterer til valgt format"""
    try:
        image = Image.open(file)
    except UnidentifiedImageError:
        return f"unsupported_{file.name}", None

    trimmed_image = trim_transparent(image)

    # Hvis valgt, gjør bildet kvadratisk med luft
    if make_square_images:
        trimmed_image = make_square(trimmed_image, padding_ratio)

    # Bestem filformat og konverter
    buf = io.BytesIO()
    ext = output_format.lower()
    save_format = "WEBP" if output_format == "WebP" else "PNG"

    if output_format == "WebP":
        trimmed_image.save(buf, format=save_format, quality=quality, method=6)
    else:
        # PNG ignorerer kvalitet, lagres tapsfritt
        trimmed_image.save(buf, format=save_format)

    buf.seek(0)

    # Bestem filnavn
    if keep_original or not article_number.strip():
        out_name = f"cropped_{file.name.rsplit('.', 1)[0]}.{ext}"
    else:
        out_name = f"{article_number.strip()}, {idx + 1}.{ext}"

    return out_name, buf.getvalue()

@st.cache_data(show_spinner=False)
def process_images(files, quality, article_number="", keep_original=False, make_square_images=False, padding_ratio=0.1, output_format="WebP"):
    """Prosesserer alle bilder parallelt og cacher resultatet"""
    files_to_process = files[:300]
    total = len(files_to_process)
    processed_images = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(
                process_file, file, idx, quality, article_number, keep_original, make_square_images, padding_ratio, output_format
            ): file
            for idx, file in enumerate(files_to_process)
        }

        for idx, future in enumerate(as_completed(futures), start=1):
            filename, data = future.result()
            if data:
                processed_images.append((filename, data))

            progress_bar.progress(idx / total)
            status_text.text(f"Behandler bilde {idx}/{total}...")

    status_text.text("✅ Ferdig!")
    progress_bar.empty()

    return processed_images

if uploaded_files:
    processed_images = process_images(
        uploaded_files, webp_quality, article_number, keep_original_names, make_square_images, padding_ratio, output_format
    )

    st.subheader("🔽 Nedlastingsvalg")

    # ZIP download
    if len(processed_images) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for filename, data in processed_images:
                zip_file.writestr(filename, data)
        zip_buffer.seek(0)

        st.download_button(
            label=f"Last ned alle som ZIP ({output_format})",
            data=zip_buffer,
            file_name=f"cropped_images.{output_format.lower()}.zip",
            mime="application/zip"
        )

    # Individual downloads
    for filename, data in processed_images:
        st.download_button(
            label=f"Last ned {filename}",
            data=data,
            file_name=filename,
            mime=f"image/{output_format.lower()}",
            key=f"dl_{filename}"
        )

    st.divider()

    # Show previews in 3 columns
    cols = st.columns(3)
    for idx, (filename, data) in enumerate(processed_images):
        with cols[idx % 3]:
            st.image(data, caption=f"Beskåret: {filename}", use_container_width=True)