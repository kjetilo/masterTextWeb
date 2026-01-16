import streamlit as st

st.set_page_config(page_title="Master-tekst",page_icon=":robot_face:",)


st.markdown("# 📚Master-tekstgenerator")

st.write("## Tekstgenerator for Master")
st.write("Skriv først inn artikkelnummer som dokumentet eventuelt skal knyttes til. Om det er til flere artikler kan man skrive f.eks. AE2010 eller Aspect. Da vil man måtte knytte den manuelt til de artiklene den skal til i ettertid.")
st.write("#### Artikkelnummer")
artNo = st.text_input("Skriv inn artikkelnummer her")
st.write("#### Dokumenttype")
docType = st.radio(
    "Velg dokumenttypen som stemmer overens med det du skal laste opp.",
    ["Datablad :ledger:","Installasjonsmanual :open_book:", "Brukermanual :closed_book:", "Forenklet brukerveiledning  :clock9:", "Forenklet installasjonsveiledning :japan:", "Leverandørdokumentasjon :file_folder:", 
     "Sertifikat :bookmark_tabs:", "Egenerklæring :memo:", "Sikkerhetsdatablad :warning:", "Godkjenning :ballot_box_with_check:", "Brosjyre  :chart_with_upwards_trend:", "Annet dokument :page_facing_up:"],
    captions=[
        "Datablad beskriver tekniske spesifikasjoner og egenskaper. Brukes ofte som FDV i vår bransje.",
        "Installasjonsmanual beskriver hvordan man installerer produktet, men ikke hvordan man bruker det. Brukermanual er ofte for sluttbruker, mens installasjonsmanual er for installatør.",
        "Brukermanual beskriver hvordan man bruker produktet, men ikke hvordan man installerer det. Noen manualer kan beskrive litt av begge deler.",
        "Om det er kun en brukermanual, skal ikke denne kategorien brukes. Denne kategorien er for brukermanualer som er forenklet, og ikke inneholder all informasjonen som en vanlig brukermanual gjør.",
        "Om det kun er en installasjonsveiledning, skal ikke denne kategorien brukes.",
        "Leverandørdokumentasjon er dokumentasjon som vi har mottatt fra leverandør, og som ikke skal endres eller lignende.",
        "Dokumenterer at produktet oppfyller bestemte krav og standarder.",
        "En erklæring fra produsenten om at produktet oppfyller de relevante sikkerhetskravene, vanligvis i forbindelse med CE-merking.",
        "Et sikkerhetsdatablad (SDS) er et dokument som gir detaljert informasjon om et kjemisk stoff eller en stoffblanding.",
        "Viser om produktet er godkjent iht. gitte standarder.",
        "Brosjyre for markedsføring eller lignende",
        "Master håndterer de fleste dokumenter. Om du ikke finner riktig kategori her, kan du se vår interne dokumentmodell. Den finnes på siden for opplasting på Master.",
    ],
)
# Mapping of document types to code and description
doc_type_map = {
    "Datablad :ledger:": ("4", "datablad"),
    "Installasjonsmanual :open_book:": ("1", "installasjonsmanual"),
    "Brukermanual :closed_book:": ("0", "brukermanual"),
    "Forenklet brukerveiledning  :clock9:": ("2", "forenklet brukerveiledning"),
    "Forenklet installasjonsveiledning :japan:": ("5", "forenklet installasjonsveiledning"),
    "Leverandørdokumentasjon :file_folder:": ("9", "leverandørdokumentasjon"),
    "Sertifikat :bookmark_tabs:": ("151", "sertifikat"),
    "Egenerklæring :memo:": ("155", "egenerklæring"),
    "Sikkerhetsdatablad :warning:": ("153", "sikkerhetsdatablad"),
    "Godkjenning :ballot_box_with_check:": ("150", "godkjenning"),
    "Brosjyre  :chart_with_upwards_trend:": ("3", "brosjyre"),
    "Annet dokument :page_facing_up:": ("", "annet dokument"),  # Default placeholder
}

# Look up selected document type; stop execution on unexpected values
docType, docText = doc_type_map.get(docType, (None, None))
if docType is None:
    st.error("En uventet feil har oppstått. Vennligst prøv igjen.")
    st.stop()


st.write("#### Revisjonsnummer")
revNo = st.text_input("Kontroller at revisjonsnummer stemmer overens med det i dokumentet.","R1A")

st.write("#### Kvalitet")
quality = st.radio(
    "Velg kvalitet i henhold til dokumentets kvalitet og egenskap.",
    ["Web", "Print", "Stamme"],
    captions=[
        "Brukes til nett og generelt til det meste.",
        "Om dokumentet spesifikt skal printes.",
        "Ofte redigerbare dokument som .docx, .indd osv.",]
)

if quality == "Web":
    quality = "12" 
elif quality == "Print":
    quality = "13"
elif quality == "Stamme":
    quality = "17"
st.write("#### Språk")
språk = st.radio(
    "Velg språket som er brukt i dokumentet.",
    ["Norsk", "Engelsk", "Ikke språk"],
    captions=[
        "Norsk språk.",
        "Engelsk språk.",
        "Ikke spesifisert språk."
    ]
)

if språk == "Norsk":
    språk = " NO"
elif språk == "Engelsk":
    språk = " EN"
else:
    språk = ""  # Ikke spesifisert språk

if docType in ["150", "151", "153", "155"]:
    toBeCopy = (f"{docType}¤{artNo} {docText}{språk}¤{artNo}¤{revNo}")
else:
    toBeCopy = (f"{quality}{docType}¤{artNo} {docText}{språk}¤{artNo}¤{revNo}")

st.code(toBeCopy, language="text")