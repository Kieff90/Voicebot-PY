"""
Scraper per i servizi del Comune di Cherasco.

Uso:
    python ingestion/scraper_cherasco.py

Output: data/services_cherasco.jsonl  (un chunk per riga, formato identico a fallback_services.jsonl)

Il file generato NON sovrascrive fallback_services.jsonl: è un corpus separato.
Per usarlo al posto del fallback, impostare RAG_CORPUS_PATH=data/services_cherasco.jsonl in .env.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

from ingestion.pulizia import filtra_chunk

BASE_URL = "https://www.comune.cherasco.cn.it"
SERVIZI_URL = f"{BASE_URL}/servizi"
OUTPUT_PATH = Path("data/services_cherasco.jsonl")

# Sezioni AGID attese in ogni scheda servizio (ordine canonico)
SEZIONI_AGID = [
    "A chi è rivolto",
    "Descrizione",
    "Come fare",
    "Cosa serve",
    "Cosa si ottiene",
    "Tempi e scadenze",
    "Quanto costa",
    "Contatti",
]


def _normalizza(testo: str) -> str:
    return re.sub(r"\s+", " ", testo).strip()


def _estrai_sezioni(html: str, nome_servizio: str, url_fonte: str) -> list[dict]:
    """
    Dato l'HTML di una pagina servizio, estrae le sezioni AGID e le
    trasforma in chunk pronti per il corpus.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    chunks: list[dict] = []

    for sezione in SEZIONI_AGID:
        heading = soup.find(
            lambda tag: tag.name in ("h2", "h3", "h4")
            and sezione.lower() in tag.get_text(strip=True).lower()
        )
        if not heading:
            continue

        testi: list[str] = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ("h2", "h3", "h4"):
                break
            t = _normalizza(sibling.get_text(separator=" "))
            if t:
                testi.append(t)

        testo = " ".join(testi)
        if not testo or len(testo) < 20:
            continue

        chunks.append(
            {
                "testo": testo,
                "servizio": nome_servizio,
                "sezione": sezione,
                "fonte": f"Comune di Cherasco — {url_fonte}",
                "aggiornato": "",
            }
        )

    return chunks


async def _scrapa_servizio(crawler, url: str, nome: str) -> list[dict]:
    from crawl4ai import CrawlerRunConfig

    result = await crawler.arun(url, config=CrawlerRunConfig(wait_until="networkidle"))
    if not result.success:
        print(f"  WARN: fetch fallito per {url}", file=sys.stderr)
        return []
    chunks = _estrai_sezioni(result.html, nome, url)
    print(f"  {nome}: {len(chunks)} sezioni estratte")
    return chunks


async def _lista_servizi(crawler) -> list[tuple[str, str]]:
    """
    Restituisce lista di (url_assoluto, nome_servizio) unici.
    Raccoglie i link /servizi/faq/NNN/ dalla pagina principale
    e da tutte le pagine categoria /servizio/NNN/.
    """
    from bs4 import BeautifulSoup
    from crawl4ai import CrawlerRunConfig

    cfg = CrawlerRunConfig(wait_until="networkidle")

    # Carica pagina principale
    result = await crawler.arun(SERVIZI_URL, config=cfg)
    if not result.success:
        print("ERRORE: impossibile caricare la pagina dei servizi", file=sys.stderr)
        return []

    soup_main = BeautifulSoup(result.html, "html.parser")

    # Raccoglie URL categorie /servizio/NNN/
    categorie: set[str] = set()
    for a in soup_main.find_all("a", href=True):
        if re.match(r"^/servizio/\d+/", a["href"]):
            categorie.add(a["href"])

    # Funzione helper per estrarre link faq da un soup
    def _faq_da_soup(s) -> dict[str, str]:
        faq: dict[str, str] = {}
        for a in s.find_all("a", href=True):
            href = a["href"]
            if re.match(r"^/servizi/faq/\d+/", href):
                nome = _normalizza(a.get_text())
                if nome:
                    faq[href] = nome
        return faq

    # Raccoglie faq dalla pagina principale
    tutti: dict[str, str] = _faq_da_soup(soup_main)

    # Raccoglie faq da ogni categoria
    for cat in sorted(categorie):
        r = await crawler.arun(BASE_URL + cat, config=cfg)
        if r.success:
            tutti.update(_faq_da_soup(BeautifulSoup(r.html, "html.parser")))

    servizi = [(BASE_URL + href, nome) for href, nome in tutti.items()]
    print(f"Trovati {len(servizi)} servizi")
    return servizi


async def main() -> None:
    from crawl4ai import AsyncWebCrawler

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with AsyncWebCrawler() as crawler:
        servizi = await _lista_servizi(crawler)
        if not servizi:
            print("Nessun servizio trovato.", file=sys.stderr)
            sys.exit(1)

        all_chunks: list[dict] = []
        for url, nome in servizi:
            chunks = await _scrapa_servizio(crawler, url, nome)
            all_chunks.extend(chunks)

    # Corpus building: scarta i chunk-stub senza contenuto (rinvii all'ufficio).
    grezzi = len(all_chunks)
    all_chunks = filtra_chunk(all_chunks)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(
        f"\nCorpus salvato: {OUTPUT_PATH} ({len(all_chunks)} chunk da {len(servizi)} "
        f"servizi; {grezzi - len(all_chunks)} stub scartati)"
    )


if __name__ == "__main__":
    asyncio.run(main())
