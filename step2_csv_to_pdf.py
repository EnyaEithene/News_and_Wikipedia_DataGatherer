"""
Converts labeled articles from a CSV to PDF files.

This script reads a CSV file containing article data, checks for missing categories,
processes the articles, and saves them as PDF files in the specified output directory.
It uses the ReportLab library to create professional PDF documents with custom fonts
and metadata.

Functions:
    safe_xml(text): Replace HTML/XML entities with their corresponding character references.
    save_as_pdf(row, output_path): Save a document based on row data to a PDF file.
    csv_to_pdf(input_csv, output_dir): Convert labeled articles from a CSV to PDF files.

Usage:
    Run the script as a standalone program with the desired parameters for the input CSV
    file path and output directory.

Dependencies:
    - pandas
    - reportlab
    - os
    - re
"""


import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re

# ----- Font Registration -----
pdfmetrics.registerFont(TTFont('DejaVu',          '/usr/share/fonts/TTF/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold',     '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Italic',   '/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf'))

def safe_xml(text):
    """Replace HTML/XML entities with their corresponding character references.

    Args:
        text (str): The input string to be cleaned.

    Returns:
        str: A new string where '&', '<', and '>' are replaced by &amp;, &lt;, and &gt; respectively.
    """
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def save_as_pdf(row, output_path):
    """Save a document based on row data to a PDF file.

    Args:
        row (dict): Dictionary containing the following keys:
            title (str): Title of the document.
            category (str): Category label.
            source (str): URL or identifier of the source.
            pub_date (str): Publication date.
            link (str): URL of the document.
            description (str): Short description text.
            tags (list or iterable): Optional list of tags to be used for XML
                entity replacement.

    Returns:
        None: Saves the PDF and prints a confirmation message.

    Notes:
        The function uses ``safe_xml`` to escape HTML/XML entities in string values
        (e.g., replaces '&' with '&amp;', '<' with '&lt;', and '>' with '&gt;').
        Custom fonts are applied via a sample style sheet for the title, body,
        and italic text.
    """    

    tags = [t.strip() for t in str(row['tags']).split(',') if t.strip()]
    category = str(row['category']).strip()
    keywords_str = ', '.join(tags)

    doc = SimpleDocTemplate(output_path, pagesize=A4)

    def on_first_page(canvas, doc):
        """Render the first page of the PDF.

        Sets document metadata and adds content elements based on the ``row`` dictionary fields.

        Args:
            canvas (ReportLab.pdfbase.canvas.Canvas): The canvas on which to draw.
            doc (ReportLab.pdfbase.document.Document): The document instance.
        """
        canvas.setAuthor(str(row['source']))
        canvas.setSubject(category)
        canvas.setTitle(str(row['title']))
        canvas.setKeywords(keywords_str)

    styles = getSampleStyleSheet()
    styles['Title'].fontName  = 'DejaVu-Bold'
    styles['Normal'].fontName = 'DejaVu'
    styles['Italic'].fontName = 'DejaVu-Italic'

    story = []
    story.append(Paragraph(safe_xml(row['title']), styles['Title']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Source: {row['source']} | {row['pub_date']}", styles['Italic']))
    story.append(Paragraph(f"Category: {category}", styles['Italic']))
    story.append(Paragraph(f"Tags: {', '.join(tags)}", styles['Italic']))
    story.append(Paragraph(f"URL: {safe_xml(row['link'])}", styles['Italic']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(safe_xml(row['description']), styles['Normal']))

    doc.build(story, onFirstPage=on_first_page)
    print(f"Saved: {output_path}")

def csv_to_pdf(input_csv='articles_to_label.csv', output_dir='./labeled_articles/'):
    """Convert labeled articles from a CSV to PDF files.

    This function reads a CSV file containing article data, checks for
    missing categories, processes the articles, and saves them as PDF files
    in the specified output directory.

    Args:
        input_csv (str, optional): Path to the input CSV file. Defaults to 'articles_to_label.csv'.
        output_dir (str, optional): Directory where the PDF files will be saved. Defaults to './labeled_articles/'.

    Returns:
        None: Prints the status of the process, including any warnings and errors.

    Notes:
        - The function assumes the CSV file has at least the following columns: 'title', 'category', 'source', 'pub_date', 'link', 'description'.
        - It skips articles with no category and warns the user.
        - Existing PDFs are not overwritten; instead, they are skipped and a warning is printed.
    """
    if not os.path.exists(input_csv):
        print(f"CSV file '{input_csv}' not found. Run step1_scrape_to_csv.py first.")
        return

    df = pd.read_csv(input_csv, encoding='utf-8-sig')

    # Warn about uncategorized rows
    unlabeled = df[df['category'].isna() | (df['category'].astype(str).str.strip() == '')]
    if not unlabeled.empty:
        print(f"Warning: {len(unlabeled)} articles have no category and will be skipped.")
        df = df[~df.index.isin(unlabeled.index)]

    if df.empty:
        print("No labeled articles to process.")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Processing {len(df)} labeled articles...")

    skipped = 0
    for _, row in df.iterrows():
        try:
            filename = re.sub(r'[^\w\s-]', '', str(row['title']))[:60].strip().replace(' ', '_') + '.pdf'
            output_path = os.path.join(output_dir, filename)
            save_as_pdf(row, output_path)
        except Exception as e:
            print(f"Failed to save '{row['title']}': {e}")

    if skipped:
        print(f"Skipped {skipped} already existing PDFs.")
    print(f"\nDone. {len(df)} PDFs saved to '{output_dir}'.")

if __name__ == '__main__':
    csv_to_pdf(
        input_csv='articles_to_label.csv',
        output_dir='./Datasets/labeled_articles/'
    )
