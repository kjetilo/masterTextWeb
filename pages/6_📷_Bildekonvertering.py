import streamlit as st
from PIL import Image, UnidentifiedImageError
import io
import zipfile

st.set_page_config(layout="wide")

st.title("📷 Bildekonvertering til 250x250")
st.sidebar.header("Innstillinger")

# 1. Output format selection
output_format = st.sidebar.radio(
    "Velg eksportformat",
    ["PNG", "WebP", "JPG"],
    index=0, # Default to PNG
    help="Velg formatet bildene skal lagres i."
)

# 2. File uploader
uploaded_files = st.file_uploader(
    "Last opp bilder for konvertering",
    type=["png", "webp", "jpg", "jpeg", "gif", "bmp", "tiff"],
    accept_multiple_files=True
)

def process_image(uploaded_file, output_format):
    """Resizes and converts a single image, preserving aspect ratio with white bars."""
    try:
        image = Image.open(uploaded_file)
        
        # Use a consistent working mode, converting at the end if necessary.
        # RGBA is safer to work with to preserve transparency.
        image = image.convert('RGBA')

        # Create a thumbnail (preserves aspect ratio)
        thumb = image.copy()
        thumb.thumbnail((250, 250), Image.Resampling.LANCZOS)

        # Create a new image with a light gray background.
        # The background should be RGBA to allow pasting a transparent thumb on it.
        background = Image.new('RGBA', (250, 250), (248, 250, 252, 255))

        # Paste the thumbnail onto the center of the background
        paste_position = (
            (250 - thumb.width) // 2,
            (250 - thumb.height) // 2
        )
        background.paste(thumb, paste_position, thumb)

        # --- Saving logic ---
        buf = io.BytesIO()
        ext = output_format.lower()
        save_format = "JPEG" if ext == "jpg" else ext.upper()

        final_image = background
        if save_format == "JPEG":
            # JPEG doesn't support alpha, so convert to RGB.
            final_image = background.convert('RGB')
            final_image.save(buf, format=save_format, quality=95)
        elif save_format == "WEBP":
            final_image.save(buf, format=save_format, quality=90, lossless=False)
        else: # PNG
            final_image.save(buf, format=save_format)

        buf.seek(0)

        # Generate filename
        original_name = uploaded_file.name.rsplit('.', 1)[0]
        new_filename = f"{original_name}_250x250.{ext}"

        return new_filename, buf.getvalue()

    except (UnidentifiedImageError, Exception) as e:
        st.warning(f"Kunne ikke behandle {uploaded_file.name}. Feil: {e}")
        return None, None


if uploaded_files:
    st.subheader("Behandlede bilder")
    processed_images = []
    for file in uploaded_files:
        filename, data = process_image(file, output_format)
        if filename and data:
            processed_images.append((filename, data))

    if processed_images:
        # Display download buttons and previews
        cols = st.columns(4)
        for idx, (filename, data) in enumerate(processed_images):
            with cols[idx % 4]:
                st.image(data, caption=filename, use_container_width=True)
                st.download_button(
                    label=f"Last ned {filename}",
                    data=data,
                    file_name=filename,
                    mime=f"image/{output_format.lower()}",
                    key=f"dl_{filename}"
                )

        # ZIP download for multiple files
        if len(processed_images) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for filename, data in processed_images:
                    zip_file.writestr(filename, data)
            zip_buffer.seek(0)

            st.sidebar.divider()
            st.sidebar.download_button(
                label=f"Last ned alle som ZIP",
                data=zip_buffer,
                file_name=f"bilder_250x250_{output_format.lower()}.zip",
                mime="application/zip",
                use_container_width=True
            )