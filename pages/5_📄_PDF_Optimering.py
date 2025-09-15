import streamlit as st
from io import BytesIO
from datetime import date

try:
    from pypdf import PdfReader, PdfWriter
except Exception as e:  # pragma: no cover - handled at runtime
    PdfReader = None
    PdfWriter = None

try:
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover - handled at runtime
    canvas = None

st.set_page_config(page_title="PDF-optimalisering", page_icon=":page_facing_up:")

st.markdown("# 📄 PDF-optimalisering")
article_number = st.text_input("Artikkelnr")
uploaded_file = st.file_uploader("Last opp en PDF-fil", type=["pdf"])
add_watermark = st.checkbox("Legg til vannmerking")
compress_pdf = st.checkbox("Komprimer PDF", value=True)

if uploaded_file is not None:
    if PdfReader is None or PdfWriter is None:
        st.error("Modulen 'pypdf' er ikke tilgjengelig. Kan ikke behandle PDF.")
    elif add_watermark and canvas is None:
        st.error("Modulen 'reportlab' er ikke tilgjengelig. Kan ikke vannmerke PDF.")
    elif add_watermark and not article_number:
        st.error("Skriv inn artikkelnr for vannmerking.")
    elif not add_watermark and not compress_pdf:
        st.error("Velg komprimering og/eller vannmerking.")
    else:
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()
        today = date.today().isoformat()
        for page in reader.pages:
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            if add_watermark:
                watermark_text = (
                    f"Elotec AS - kun for intern bruk. Artikkelnr {article_number} {today}"
                )
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                can.saveState()
                can.translate(page_width / 2, page_height / 2)
                can.rotate(45)
                can.setFont("Helvetica", 40)
                try:
                    can.setFillAlpha(0.3)
                except Exception:
                    pass
                can.drawCentredString(0, 0, watermark_text)
                can.restoreState()
                can.save()
                packet.seek(0)
                watermark_pdf = PdfReader(packet)
                watermark_page = watermark_pdf.pages[0]
                page.merge_page(watermark_page)
            if compress_pdf:
                try:
                    page.compress_content_streams()
                except Exception:
                    pass
            writer.add_page(page)
        writer.add_metadata(reader.metadata or {})
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        success_msg = []
        if compress_pdf:
            success_msg.append("komprimert")
        if add_watermark:
            success_msg.append("vannmerket")
        status = " og ".join(success_msg)
        st.success(f"PDF-en er {status} og klar for nedlasting.")
        st.download_button(
            label="Last ned optimalisert PDF",
            data=output,
            file_name=f"optimalisert_{uploaded_file.name}",
            mime="application/pdf",
        )
