import sqlite3
import re

DB_FILE = "kjv.db"

# Regex pattern to convert [words] to <i>words</i>
BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")

def connect_db():
    """Connects to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def format_text(text):
    """Converts [words] to <i>words</i> for HTML rendering."""
    return BRACKET_PATTERN.sub(r"<i>\1</i>", text)

def fetch_and_generate_all_books():
    """Fetches all books from the database and generates an HTML file for each."""
    conn = connect_db()
    cursor = conn.cursor()

    # Get all books ordered by ID
    cursor.execute("SELECT id, name FROM books ORDER BY id")
    books = cursor.fetchall()

    if not books:
        print("No books found in the database.")
        return

    for book_id, book_name in books:
        generate_html_for_book(cursor, book_id, book_name)

    conn.close()
    print("All books have been generated as HTML files.")

def generate_html_for_book(cursor, book_id, book_name):
    """Fetches the entire book's text and formats it for HTML output as pure paragraphs."""
    # Fetch all chapters
    cursor.execute("""
        SELECT id FROM chapters 
        WHERE book_id = ? ORDER BY chapter_number
    """, (book_id,))
    
    chapters = cursor.fetchall()
    if not chapters:
        print(f"No chapters found for '{book_name}'. Skipping.")
        return

    # Start building HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{book_name}</title>
        <style>
            body {{ font-family: Atkinson Hyperlegible Next, sans-serif; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; }}
            p {{ margin-bottom: 10px; }}
            i {{ font-style: italic; }}
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">{book_name}</h1>
    """

    paragraph = []

    # Process each chapter (without headings)
    for chapter_id, in chapters:
        # Fetch verses for the chapter
        cursor.execute("""
            SELECT verse_number, text FROM verses 
            WHERE chapter_id = ? ORDER BY verse_number
        """, (chapter_id,))
        
        verses = cursor.fetchall()

        # Fetch paragraph breaks
        cursor.execute("""
            SELECT verse_number FROM paragraph_breaks 
            WHERE book_id = ? AND chapter_id = ?
        """, (book_id, chapter_id))
        
        paragraph_breaks = {row[0] for row in cursor.fetchall()}  # Convert to set for quick lookup

        # Combine verses into paragraphs
        for verse_num, text in verses:
            formatted_text = format_text(text)  # Apply italics for bracketed words
            paragraph.append(formatted_text)

            # If a paragraph break is found, close current paragraph and start a new one
            if verse_num in paragraph_breaks:
                html_content += f"<p>{' '.join(paragraph)}</p>\n"
                paragraph = []

    # Append any remaining text as the last paragraph
    if paragraph:
        html_content += f"<p>{' '.join(paragraph)}</p>\n"

    html_content += """
    </body>
    </html>
    """

    filename = f"{book_id:02d}_{book_name.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"File saved: {filename}")

if __name__ == "__main__":
    fetch_and_generate_all_books()
