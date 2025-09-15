import streamlit as st
from io import BytesIO
try:
    from pypdf import PdfReader, PdfWriter
except Exception as e:  # pragma: no cover - handled at runtime
    PdfReader = None
    PdfWriter = None

st.set_page_config(page_title="PDF-optimalisering", page_icon=":page_facing_up:")

st.markdown("# 📄 PDF-optimalisering")
uploaded_file = st.file_uploader("Last opp en PDF-fil", type=["pdf"])

if uploaded_file is not None:
    if PdfReader is None:
        st.error("Modulen 'pypdf' er ikke tilgjengelig. Kan ikke optimalisere PDF.")
    else:
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()
        for page in reader.pages:
            try:
                page.compress_content_streams()
            except Exception:
                pass
            writer.add_page(page)
        writer.add_metadata(reader.metadata or {})
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        st.success("PDF-en er optimalisert og klar for nedlasting.")
        st.download_button(
            label="Last ned optimalisert PDF",
            data=output,
            file_name=f"optimalisert_{uploaded_file.name}",
            mime="application/pdf",
        )
