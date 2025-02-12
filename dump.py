import json
import re

INPUT_FILE = "kjv_data.json"

# Regex patterns
BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")  # Convert [words] to <i>words</i>
DOUBLE_ANGLE_PATTERN = re.compile(r"<<([^>]*)>>")  # Extract text inside << >>

def format_text(text):
    """Formats text by converting [words] to <i>words</i> and placing <<sentences>> at the end of their paragraph."""
    special_blocks = DOUBLE_ANGLE_PATTERN.findall(text)
    text = DOUBLE_ANGLE_PATTERN.sub("", text)  # Remove <<...>> from inline text
    text = BRACKET_PATTERN.sub(r"<i>\1</i>", text)

    # Process special text separately to remove outer brackets and italicize words inside
    cleaned_special_blocks = [BRACKET_PATTERN.sub(r"<i>\1</i>", block.strip("[]")) for block in special_blocks]

    return text.strip(), cleaned_special_blocks

def load_json():
    """Loads KJV data from JSON."""
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_html_for_book(book_id, book_data):
    """Generates an HTML file for a single book."""
    book_name = book_data["name"]
    html_parts = [f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{book_name}</title>
        <style>
            body {{ 
                font-family: Atkinson Hyperlegible Next, sans-serif; 
                line-height: 1.6; 
                max-width: 800px; 
                margin: auto; 
                padding: 20px; 
            }}
            p {{ 
                margin-bottom: 10px;
                page-break-inside: avoid; /* Prevent paragraphs from being split across pages */
            }}
            i {{ font-style: italic; }}
            .special {{ 
                font-weight: bold; 
                text-align: center;
                display: inline-block; /* Keep special text inline */
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">{book_name}</h1>
    """]

    for chapter_number, chapter_data in book_data["chapters"].items():
        paragraph = []
        special_text_inline = ""

        for verse in chapter_data["verses"]:
            verse_num = verse["verse_number"]
            text = verse["text"]
            is_paragraph_break = verse["paragraph_break"]

            formatted_text, special_blocks = format_text(text)

            # Append special text at the end of its paragraph
            if special_blocks:
                special_text_inline = f' <span class="special">{" ".join(special_blocks)}</span>'

            if formatted_text:
                paragraph.append(formatted_text)

            if is_paragraph_break:
                html_parts.append(f"<p>{' '.join(paragraph)}{special_text_inline}</p>\n")
                paragraph = []
                special_text_inline = ""

        if paragraph:
            html_parts.append(f"<p>{' '.join(paragraph)}{special_text_inline}</p>\n")

    html_parts.append("</body></html>")

    filename = f"{book_id:02d}_{book_name.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write("".join(html_parts))  # Use efficient string joining

    print(f"File saved: {filename}")

def generate_all_html():
    """Generates HTML files for all books from the JSON data."""
    data = load_json()
    for book_id, book_data in data.items():
        generate_html_for_book(int(book_id), book_data)
    print("All books have been generated as HTML files.")

if __name__ == "__main__":
    generate_all_html()