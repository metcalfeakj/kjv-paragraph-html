from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.util import Inches, Pt
import glob
import os

def extract_paragraphs_from_html(html_file):
    """Extract paragraphs from an HTML file."""
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    
    book_title = soup.find("h1").text if soup.find("h1") else "Unknown"
    paragraphs = [p.text.strip() for p in soup.find_all("p") if p.text.strip()]
    
    return book_title, paragraphs

def add_text_to_slide(slide, text):
    """Add text to a slide with dynamically adjusted font size and line breaks to prevent overflow."""
    textbox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(7))
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    
    # Dynamically reduce font size if needed
    font_sizes = [40, 36, 32, 28, 26, 24, 22, 20, 18, 16]
    
    for size in font_sizes:
        text_frame.clear()  # Clear previous attempts
        
        p = text_frame.add_paragraph()
        p.text = text
        p.font.size = Pt(size)
        p.space_after = Pt(6)  # Reduce extra spacing between paragraphs
        
        # Estimate character limit based on font size
        max_chars = 600 if size >= 36 else 500 if size >= 28 else 400 if size >= 22 else 300
        
        if len(text) <= max_chars:
            break

def create_pptx_for_each_book(html_folder, output_folder):
    """Generate a separate PowerPoint presentation for each book from HTML files, ensuring text fits within slides."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for html_file in sorted(glob.glob(os.path.join(html_folder, "*.html"))):
        book_title, paragraphs = extract_paragraphs_from_html(html_file)
        
        prs = Presentation()
        
        current_slide_text = ""
        max_chars_per_slide = 500  # Base limit to prevent text overflow
        
        for paragraph in paragraphs:
            if len(paragraph) > max_chars_per_slide:
                # Split large paragraphs into smaller chunks
                split_paragraphs = [paragraph[i:i+max_chars_per_slide] for i in range(0, len(paragraph), max_chars_per_slide)]
                for part in split_paragraphs:
                    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Use blank layout with no title space
                    add_text_to_slide(slide, part)
            else:
                if len(current_slide_text) + len(paragraph) > max_chars_per_slide:
                    slide = prs.slides.add_slide(prs.slide_layouts[6])
                    add_text_to_slide(slide, current_slide_text)
                    current_slide_text = ""
                
                current_slide_text += paragraph + "\n"
        
        # Add remaining text to the last slide
        if current_slide_text:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            add_text_to_slide(slide, current_slide_text)
        
        output_pptx = os.path.join(output_folder, f"{book_title}.pptx")
        prs.save(output_pptx)
        print(f"PowerPoint saved as {output_pptx}")

if __name__ == "__main__":
    html_folder = "./"  # Update this to the folder where HTML files are stored
    output_folder = "./powerpoints"  # Folder to save PowerPoint files
    create_pptx_for_each_book(html_folder, output_folder)
