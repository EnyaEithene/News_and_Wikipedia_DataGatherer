# News_and_Wikipedia_DataGatherer 

Creates structured Romanian datasets for NLP pipeline testing and model training. This repository aggregates data from news RSS feeds and Wikipedia to produce clean, labeled text samples.

## File Structure
- `step1_scrape_to_csv.py` - Scrapes RSS feeds from 8 Romanian news websites (Digi24, HotNews, G4Media, etc.) → CSV output
- `step2_csv_to_pdf.py` - Converts labeled articles to PDF documents with metadata, fonts, and categorization
- `extract_wiki.py` - Extracts categorized Wikipedia articles from dump files → JSONL format

## Workflow
### PDFs from news articles
1. **Run step1**: Scrape news articles → `articles_to_label.csv` (requires manual category/tag labeling)
2. **Run step2**: Convert CSV → PDF in `./labeled_articles/` directory

From the gathered data, it can be used to simulate a real-life scenario where an user might have multiple PDF files on their computer.
I personally used it for NLP semantic search, but the PDFs created could be tested on NLP classification as well.

### JSONL data from Wikipedia Dump
1. **Run Extract Wiki**: Parse Wikipedia dump → `wiki_articles.jsonl` with auto-categorized topics

I used it for NLP semantic search and classification; this has an easier time with classification, as it doesn't require manual tagging for proper testing.

## Dataset Categories (for Wikipedia articles) 
- Sport,
- Politic,
- Economie,
- Știință,
- Tehnologie,
- Cultură
- Istorie,
- Geografie,
- Religie,
- Educație,
- Sănătate,
- Mediu,
- Lingvistică,
- Unknown (fallback)

## Dependencies
- `requests`, `beautifulsoup4`, `pandas`
- `reportlab` (for PDF generation)
- `bz2`, `json`, `xml.etree.ElementTree`, `wikitextparser`

## Usage
```bash
# RSS Feeds
python step1_scrape_to_csv.py --sources list --max_articles 50
python step2_csv_to_pdf.py --input_csv articles.csv --output_dir ./labeled/

# Wikipedia Dump
python extract_wiki.py --dump_path path/to/dump.xml.bz2 --output_dir ./wiki_ro/
```

## To Do
- [] Fix PDF format (remove tags on page, as it can affect NLP classification)

## Disclaimer
For the creation of this program I used AI:
- ChatGPT/ Claude to help with the creation of the code
- Local LLM model (qwen2.5-coder:14b) to help with docstrings
