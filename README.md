# News_and_Wikipedia_DataGatherer 

Creates structured Romanian datasets for NLP pipeline testing and model training. This repository aggregates data from news RSS feeds and Wikipedia to produce clean, labeled text samples.

## File Structure
- `step1_scrape_to_csv.py` - Scrapes RSS feeds from 8 Romanian news websites (Digi24, HotNews, G4Media, etc.) → CSV output
- `step2_csv_to_pdf.py` - Converts labeled articles to PDF documents with metadata, fonts, and categorization
- `extract_wiki.py` - Extracts categorized Wikipedia articles from dump files → JSONL format

## Workflow
1. **Run step1**: Scrape news articles → `articles_to_label.csv` (requires manual category/tag labeling)
2. **Step2**: Convert CSV → PDF in `./labeled_articles/` directory
3. **Extract Wiki**: Parse Wikipedia dump → `wiki_articles.jsonl` with auto-categorized topics

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

# Wikipedia dump
python extract_wiki.py --dump_path path/to/dump.xml.bz2 --output_dir ./wiki_ro/
```

## Disclaimer
For the creation of this program I used AI:
- ChatGPT/ Claude to help with the creation of the code
- Local LLM model (qwen2.5-coder:14b) to help with docstrings
