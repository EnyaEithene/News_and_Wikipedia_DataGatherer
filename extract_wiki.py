"""Extract Wikipedia articles from a dump file and save them as JSONL.

This script extracts articles from a Wikipedia dump file in bz2 compressed XML format.
It processes the XML to extract titles and plain text, categorizes the articles,
and saves them as JSONL files. The script also provides counters for skipped articles
based on various criteria.

Functions:
    extract_categories(raw_text): Extracts Wikipedia categories from raw markup text.
    detect_category(categories, title): Maps Wikipedia categories to simplified research categories.
    extract_wikipedia(dump_path, output_dir, max_articles): Extracts articles from a Wikipedia dump file.

Usage:
    Run the script as a standalone program with the desired parameters for the Wikipedia dump file path,
    output directory, and maximum number of articles to extract.

Dependencies:
    - bz2
    - json
    - os
    - re
    - xml.etree.ElementTree
    - wikitextparser
"""

import bz2
import json
import os
import re
import xml.etree.ElementTree as ET
import wikitextparser as wtp

def extract_categories(raw_text):
    """Extract Wikipedia categories from raw markup.

    This function searches for categories in the specified raw text using two patterns:
    one for the Romanian format [[Categorie:Name]] and another for the English format
    [[Category:Name]]. It returns a list of category names with leading and trailing
    whitespace removed.

    Args:
        raw_text (str): The raw markup text from which to extract categories.

    Returns:
        List[str]: A list of extracted category names.

    Notes:
        The function uses regular expressions to find and extract category names. 
        It handles both Romanian and English category formats.
    """

    # Categories are in format [[Categorie:Name]] in Romanian Wikipedia
    pattern = r'\[\[Categorie:([^\]|]+)'
    categories = re.findall(pattern, raw_text, re.IGNORECASE)
    # Also check English format just in case
    pattern_en = r'\[\[Category:([^\]|]+)'
    categories += re.findall(pattern_en, raw_text, re.IGNORECASE)
    return [c.strip() for c in categories]

def detect_category(categories, title):
    """Map Wikipedia categories to simplified research categories.

    Args:
        categories (list of str): List of Wikipedia categories.
        title (str): Title of the document.

    Returns:
        str: Simplified research category ('Sport', 'Politic', 'Economie',
             'Știință', 'Tehnologie', 'Cultură', 'Istorie', 'Geografie',
             'Religie', 'Educație', 'Sănătate', 'Mediu', 'Lingvistică',
             or 'unknown' if no match is found).
    """

    combined = ' '.join(categories).lower() + ' ' + title.lower()

    category_map = {
    'Sport': [
        'fotbal', 'sport', 'olimpic', 'atletism', 'tenis', 'baschet',
        'handbal', 'rugby', 'volei', 'înot', 'gimnastică', 'box',
        'ciclism', 'schi', 'hochei', 'golf', 'meci', 'campionat',
        'turneu', 'jocuri olimpice', 'fifa', 'uefa', 'arte marțiale',
        'fotbaliști', 'sportivi', 'cluburi', 'stadion', 'antrenor'
    ],
    'Politic': [
        'politică', 'partid', 'guvern', 'parlament', 'președinte',
        'ministru', 'alegeri', 'democrație', 'republică', 'stat',
        'lege', 'constituție', 'senat', 'deputat', 'premier',
        'diplomatic', 'ambasador', 'tratat', 'uniunea europeană',
        'țări', 'state', 'liste de țări', 'orașe', 'capitale',
        'românia', 'județe', 'comune', 'municipii', 'administrativ'
    ],
    'Economie': [
    'economie', 'bancă', 'finanțe', 'bursă', 'companie', 'firmă',
    'industrie', 'comerț', 'export', 'import', 'pib', 'inflație',
    'investiție', 'acțiuni', 'piață', 'afaceri', 'antreprenor',
    'corporație', 'monopol', 'concurență', 'întreprinderi', 'societăți comerciale',
    'liste de companii'
    ],    
    'Știință': [
        'știință', 'fizică', 'chimie', 'biologie', 'matematică',
        'astronomie', 'medicină', 'cercetare', 'experiment', 'teorie',
        'descoperire', 'laborator', 'atom', 'moleculă', 'genetică',
        'evoluție', 'geologie', 'meteorologie', 'informatică',
        'astrofizică', 'metrologie', 'articole cu definiții',
        'eponime ale asteroizilor', 'fizicieni', 'chimiști',
        'biologi', 'matematicieni', 'astronomi', 'inventatori',
        'pământ', 'planeta', 'sistem solar', 'univers', 'eponime ale elementelor',
        'antropologie', 'sociologie', 'psihologie', 'filozofie', 'filosofie',
        'mecanică clasică', 'concepte fizice', 'simboluri'
    ],
    'Tehnologie': [
        'tehnologie', 'calculator', 'computer', 'software', 'hardware',
        'internet', 'rețea', 'program', 'algoritm', 'inteligență artificială',
        'robotică', 'telecomunicații', 'satelit', 'electronic', 'digital',
        'cybersecurity', 'cloud', 'smartphone', 'aplicație',
        'informatică', 'programare', 'sisteme de operare', 'web',
        'inginerie', 'unicode', 'codificări', 'date de calculatoare',
        'tehnologia informației', 'baze de date', 'distribuții linux',
        'freebsd', 'mac os', 'macos', 'netbsd', 'bsd', 'variante unix',
        'logică binară', 'unități de informație', 'sisteme de numerație',
        'sistem binar', 'octet', 'prefixe binare'
    ],
    'Cultură': [
        'film', 'muzică', 'artă', 'literatură', 'teatru', 'pictură',
        'sculptură', 'arhitectură', 'fotografie', 'dans', 'operă',
        'roman', 'poezie', 'scriitor', 'regizor', 'actor', 'muzician',
        'festival', 'expoziție', 'muzeu', 'cultură', 'arte',
        'formații', 'trupe', 'albume', 'cântăreți', 'compozitori',
        'dramaturgi', 'poeți', 'romancieri', 'benzi desenate',
        'jocuri video', 'animație', 'televiziune', 'radio',
        'emisiuni', 'seriale', 'artă', 'arte după tip',
        'formații rock', 'formații pop', 'trupe rock', 'iris',
        'mihai eminescu', 'nicolae iorga'
    ],
    'Istorie': [
        'război', 'istorie', 'rege', 'împărat', 'medieval', 'antic',
        'revoluție', 'independență', 'imperiul', 'bătălie', 'tratat',
        'monarhie', 'dinastie', 'cucerire', 'colonialism', 'civilizație',
        'arheologie', 'monument', 'patrimoniu', 'secol', 'mileniu',
        'eveniment', 'personaje istorice', 'conducători', 'domni',
        'voievozi', 'regi', 'împărați', 'faraoni', 'antichitate',
        'titluri nobiliare', 'titluri otomane', 'voievod',
        'nașteri în', 'decese în'
    ],
    'Geografie': [
        'geografie', 'oraș', 'țară', 'continent', 'munte', 'râu',
        'lac', 'ocean', 'mare', 'insulă', 'peninsula', 'deltă',
        'câmpie', 'deal', 'regiune', 'județ', 'comună', 'sat',
        'populație', 'hartă', 'climă', 'relief', 'localități',
        'munți', 'râuri', 'lacuri', 'mări', 'oceane', 'insule',
        'peninsule', 'continente', 'regiuni', 'cartiere',
        'dunărea', 'fluvii', 'văi', 'depresiuni', 'câmpii', 'podișuri'
    ],
    'Religie': [
        'religie', 'biserică', 'ortodox', 'catolic', 'protestant',
        'islam', 'iudaism', 'budism', 'hinduism', 'biblie', 'coran',
        'sfânt', 'preot', 'episcop', 'mănăstire', 'catedrală',
        'rugăciune', 'credință', 'dumnezeu', 'teologie',
        'creștinism', 'musulmani', 'evrei', 'buddhism', 'hinduși',
        'mitologie', 'zeități', 'ritualuri', 'sărbători religioase'
    ],
    'Educație': [
        'educație', 'școală', 'universitate', 'facultate', 'profesor',
        'student', 'liceu', 'diplomă', 'doctorat', 'cercetare',
        'academie', 'bibliotecă', 'curs', 'examen', 'bursă',
        'enciclopedii', 'enciclopedie', 'dicționare', 'manuale',
        'instituții de învățământ', 'colegii', 'institute'
    ],
    'Sănătate': [
        'sănătate', 'medicină', 'boală', 'tratament', 'spital',
        'doctor', 'vaccin', 'virus', 'bacterie', 'epidemie',
        'pandemie', 'farmacie', 'chirurgie', 'diagnostic', 'terapie',
        'nutriție', 'fitness', 'psihologie', 'psihiatrie',
        'boli', 'afecțiuni', 'sindroame', 'anatomie', 'fiziologie',
        'otologie', 'cardiologie', 'neurologie', 'dermatologie', 'oftalmologie',
        'ortopedie', 'pediatrie', 'ginecologie', 'urologie', 'oncologie'
    ],
    'Mediu': [
        'mediu', 'ecologie', 'climă', 'schimbări climatice', 'poluare',
        'reciclare', 'energie regenerabilă', 'solar', 'eolian',
        'biodiversitate', 'specie', 'pădure', 'defrișare',
        'plastic', 'emisii', 'carbon', 'sustenabilitate',
        'animale', 'plante', 'flori', 'arbori', 'păsări',
        'mamifere', 'reptile', 'amfibieni', 'pești', 'insecte'
    ],
    'Lingvistică': [
        'limbă', 'lingvistică', 'gramatică', 'sintaxă', 'morfologie',
        'fonologie', 'semantică', 'dialect', 'alfabet', 'scriere',
        'limba română', 'limba engleză', 'limba franceză', 'limbi',
        'limbi artificiale', 'esperanto', 'cuvinte', 'etimologie'
    ],
}
    # Check raw Wikipedia categories first (more reliable)
    for wiki_cat in categories:
        wiki_cat_lower = wiki_cat.lower()
        for category, keywords in category_map.items():
            for keyword in keywords:
                if keyword in wiki_cat_lower:
                    return category

    # Fall back to title matching
    title_lower = title.lower()
    for category, keywords in category_map.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category

    return 'unknown'


def extract_wikipedia(dump_path, output_dir='./wiki_ro/', max_articles=50000):
    """Extract articles from a Wikipedia dump file and save them as JSONL.

    Args:
        dump_path (str): Path to the Wikipedia dump file (bz2 compressed XML).
        output_dir (str): Directory to save the extracted articles (default is './wiki_ro/').
        max_articles (int): Maximum number of articles to extract (default is 50000).

    Returns:
        None: Saves the extracted articles as 'wiki_articles.jsonl' in the output directory.
    """

    meta_skipped = 0
    year_skipped = 0
    disambig_skipped = 0

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'wiki_articles.jsonl')
    count = 0
    skipped = 0

    print(f"Extracting from {dump_path}...")
    with bz2.open(dump_path, 'rt', encoding='utf-8') as f, \
         open(output_file, 'w', encoding='utf-8') as out:
        title = ''
        raw_text = ''

        for event, elem in ET.iterparse(f, events=('start', 'end')):
            tag = elem.tag.split('}')[-1]


            if event == 'start' and tag == 'page':
                title = ''
                raw_text = ''

            elif event == 'end' and tag == 'title':
                title = elem.text or ''

            elif event == 'end' and tag == 'text':
                # Debug counters
                if any(title.startswith(prefix) for prefix in
                       ['Wikipedia:', 'Ajutor:', 'Categorie:', 'Modul:', 'Fișier:', 'Portal:']):
                    meta_skipped += 1
                    elem.clear()
                    continue
                if title in ['Wikipedia']:
                    meta_skipped += 1
                    elem.clear()
                    continue
                if title.endswith('(dezambiguizare)') or title.endswith('(disambiguation)'):
                    disambig_skipped += 1
                    elem.clear()
                    continue
                if re.match(r'^\d{3,4}$', title):
                    year_skipped += 1
                    elem.clear()
                    continue
                raw_text = elem.text or ''
                parsed = wtp.parse(raw_text)
                text = parsed.plain_text().strip()

                if len(text) > 200:
                    categories = extract_categories(raw_text)
                    category = detect_category(categories, title)
                    article = {
                        'title':      title,
                        'text':       text,
                        'url':        f'https://ro.wikipedia.org/wiki/{title.replace(" ", "_")}',
                        'categories': categories,
                        'category':   category,
                    }
                    out.write(json.dumps(article, ensure_ascii=False) + '\n')
                    count += 1
                    if count % 1000 == 0:
                        print(f"Extracted {count} articles... (skipped {skipped} stubs)")
                    if count >= max_articles:
                        print(f"Reached limit: {max_articles} articles.")
                        return
                else:
                    skipped += 1
                elem.clear()

    print(f"Done. {count} articles saved, {skipped} stubs skipped.")
    print(f"Meta skipped: {meta_skipped}")
    print(f"Year skipped: {year_skipped}")
    print(f"Disambig skipped: {disambig_skipped}")
    print(f"Stub skipped: {skipped}")

if __name__ == '__main__':
    extract_wikipedia(
        dump_path='./rowiki-latest-pages-articles.xml.bz2',
        output_dir='./wiki_ro/',
        max_articles=50000
    )
