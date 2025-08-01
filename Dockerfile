FROM python:3.12-slim

# Installer systembiblioteker for Pillow og HEIC/AVIF-støtte
RUN apt-get update && apt-get install -y --no-install-recommends \
    libheif1 \
    libheif-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopier requirements først for bedre caching
COPY requirements.txt ./

# Installer Python-avhengigheter
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# For google cloud run, brukes PORT-miljøvariabelen
# Bruker sh -c for å evaluere $PORT dynamisk
ENTRYPOINT ["sh", "-c", "streamlit run Hello.py --server.port=$PORT --server.address=0.0.0.0"]
