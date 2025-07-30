import streamlit as st

st.write("Denne nettsiden lager tekst for dokumenter som skal lastes opp til Master.")
st.write("Skriv først inn artikkelnummer som dokumentet eventuelt skal knyttes til. Om det er til flere artikler kan man skrive f.eks. AE2010 eller Aspect. Da vil man måtte knytte den manuelt til de artiklene den skal til i ettertid.")

artNo = st.text_input("Artikkelnummer:", placeholder="Skriv inn artikkelnummer her")

docType = st.radio(
    "Først velger du dokumenttypen som stemmer overens med det du skal laste opp.",
    ["Datablad :ledger:","Installasjonsmanual :open_book:", "Brukermanual :closed_book:", "Forenklet brukerveiledning  :clock9:", "Forenklet installasjonsveiledning :japan:", "Leverandørdokumentasjon :file_folder:", "Sertifikat :bookmark_tabs:", "Egenerklæring :memo:", "Sikkerhetsdatablad :warning:", "Godkjenning :ballot_box_with_check:", "Annet dokument :page_facing_up:"],
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
        "Master håndterer de fleste dokumenter. Om du ikke finner riktig kategori her, kan du se vår interne dokumentmodell. Den finnes på siden for opplasting på Master.",
    ],
)
if docType == "Datablad :ledger:":
    docType = "4"
    docText = "datablad"
elif docType == "Installasjonsmanual :open_book:":
    docType = "1"
    docText = "installasjonsmanual"
elif docType == "Brukermanual :closed_book:":
    docType = "0"
    docText = "brukermanual"
elif docType == "Forenklet brukerveiledning  :clock9:":
    docType = "2"
    docText = "forenklet brukerveiledning"
elif docType == "Forenklet installasjonsveiledning :japan:":
    docType = "5"
    docText = "forenklet installasjonsveiledning"
elif docType == "Leverandørdokumentasjon :file_folder:":
    docType = "9"
    docText = "leverandørdokumentasjon"
elif docType == "Sertifikat :bookmark_tabs:":
    docType = "151"
    docText = "sertifikat"
elif docType == "Egenerklæring :memo:":
    docType = "155"
    docText = "egenerklæring"
elif docType == "Sikkerhetsdatablad :warning:":
    docType = "153"
    docText = "sikkerhetsdatablad"
elif docType == "Godkjenning :ballot_box_with_check:":
    docType = "150"
    docText = "godkjenning"
elif docType == "Annet dokument :page_facing_up:":
    docType = " "
    docText = "annet dokument"  # Dette er en plassholder for andre dokumenter som ikke er spesifisert
                            # Ved dokument som ikke er speisifisert. Ellers skal denne blokken gjøre at man kan sette sammen en streng som kan brukes til å generere teksten lenger nede.
                            # Denne oversetter doktype 4 = datablad osv.
else:
    st.error("En uventet feil har oppstått. Vennligst prøv igjen.")
    st.stop()

revNo = st.text_input("Revisjonsnummer:","R1A")

quality = st.radio(
    "Først velger du dokumenttypen som stemmer overens med det du skal laste opp.",
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

språk = st.radio(
    "Språk:",
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