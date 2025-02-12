import sqlite3
import re

DB_FILE = "kjv.db"

# Regex patterns
BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")  # Convert [words] to <i>words</i>
DOUBLE_ANGLE_PATTERN = re.compile(r"<<([^>]*)>>")  # Extract text inside << >>

def connect_db():
    """Connects to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def format_text(text):
    """Converts [words] to <i>words</i> and ensures <<sentences>> appear on separate lines without brackets."""
    text = BRACKET_PATTERN.sub(r"<i>\1</i>", text)
    text = DOUBLE_ANGLE_PATTERN.sub(r'<div class="special">\1</div>', text)  # Remove << and >> while keeping content
    return text.strip()

def fetch_and_generate_all_books():
    """Fetches all books from the database and generates an HTML file for each."""
    conn = connect_db()
    cursor = conn.cursor()

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
    """Fetches the entire book's text and formats it for HTML output."""
    cursor.execute("""
        SELECT id FROM chapters 
        WHERE book_id = ? ORDER BY chapter_number
    """, (book_id,))
    
    chapters = cursor.fetchall()
    if not chapters:
        print(f"No chapters found for '{book_name}'. Skipping.")
        return

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
            .special {{ display: block; text-align: center; font-weight: bold; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">{book_name}</h1>
    """

    paragraph = []

    for chapter_id, in chapters:
        cursor.execute("""
            SELECT verse_number, text FROM verses 
            WHERE chapter_id = ? ORDER BY verse_number
        """, (chapter_id,))
        
        verses = cursor.fetchall()

        cursor.execute("""
            SELECT verse_number FROM paragraph_breaks 
            WHERE book_id = ? AND chapter_id = ?
        """, (book_id, chapter_id))
        
        paragraph_breaks = {row[0] for row in cursor.fetchall()}

        for verse_num, text in verses:
            formatted_text = format_text(text)
            
            if formatted_text.startswith('<div class="special">'):
                if paragraph:
                    html_content += f"<p>{' '.join(paragraph)}</p>\n"
                    paragraph = []
                html_content += formatted_text + "\n"
            else:
                paragraph.append(formatted_text)
            
            if verse_num in paragraph_breaks:
                html_content += f"<p>{' '.join(paragraph)}</p>\n"
                paragraph = []

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