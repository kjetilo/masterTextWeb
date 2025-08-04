import os
import streamlit as st
from openai import OpenAI

# Load API key from Streamlit secrets (local) or environment variable (Cloud Run)
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OpenAI API key not found. Set it in .streamlit/secrets.toml (local) or as an env var in Cloud Run.")
    st.stop()

client = OpenAI(api_key=api_key)

st.title("🔴 Elotecify Document Processor")

uploaded_file = st.file_uploader("Last opp dokument (Word, PDF, TXT)", type=["docx", "pdf", "txt"])

if uploaded_file:
    st.write("✅ Dokument lastet opp! Nå kan du behandle teksten.")

    # Here you could extract text, send to OpenAI, and display output
    if st.button("Generer Elotec-tekst"):
        with st.spinner("Behandler nå dokument standard prompt..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional translator that rewrites documents into Elotec style, short, technical, and precise."},
                    {"role": "user", "content": "Here is the document text:\n\n" + uploaded_file.getvalue().decode("utf-8", errors="ignore")}
                ]
            )

        ai_text = response.choices[0].message.content
        st.subheader("🔹 Generert Elotec-tekst")
        st.text_area("Kopier teksten herfra:", ai_text, height=400)
