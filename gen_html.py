import json
import re

INPUT_FILE = "kjv.json"

# Regex patterns
BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")  # Convert [words] to <i>words</i>
DOUBLE_ANGLE_PATTERN = re.compile(r"<<([^>]*)>>")  # Extract text inside << >>

def format_text(text):
    """Formats text by converting [words] to <i>words</i> and ensuring <<sentences>> appear correctly."""
    special_blocks = DOUBLE_ANGLE_PATTERN.findall(text)
    text = DOUBLE_ANGLE_PATTERN.sub("", text)  # Remove <<...>> from inline text

    cleaned_special_blocks = []
    for block in special_blocks:
        block = block.strip()

        # First, detect `<<[ ... ]>>` and treat it as special text
        if block.startswith("[") and block.endswith("]"):
            block = block[1:-1]  # Remove outer brackets
            formatted_block = BRACKET_PATTERN.sub(r"<i>\1</i>", block)  # Italicize internal [words]
        else:
            formatted_block = BRACKET_PATTERN.sub(r"<i>\1</i>", block)  # Normal processing

        # If special text is the entire verse (Psalms case), treat it as a separate paragraph
        if text.strip() == "":
            cleaned_special_blocks.append(f'<p class="special">{formatted_block}</p>')
        else:
            # Keep inline if it comes at the end of a verse (Romans case)
            cleaned_special_blocks.append(f'<span class="special">{formatted_block}</span>')

    # Fully process bracketed words in the main text AFTER special blocks
    text = BRACKET_PATTERN.sub(r"<i>\1</i>", text)

    # Ensure we return special text correctly formatted
    special_text = " ".join(cleaned_special_blocks) if cleaned_special_blocks else ""

    return text.strip(), special_text

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
                display: block;  /* Make it behave like a block element */
                width: 100%;  /* Ensure it spans the full width */
                margin: 10px auto; /* Center with automatic margins */
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

            # Use special_blocks as raw HTML, prevent extra wrapping
            special_text_inline = "".join(special_blocks)  # No extra span wrapping here!

            if formatted_text:
                paragraph.append(formatted_text)

            if is_paragraph_break:
                html_parts.append(f"<p>{' '.join(paragraph)} {special_text_inline}</p>\n")
                paragraph = []
                special_text_inline = ""

        if paragraph:
            html_parts.append(f"<p>{' '.join(paragraph)} {special_text_inline}</p>\n")

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