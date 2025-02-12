from weasyprint import HTML
import os
import glob

HTML_FOLDER = "./"
PDF_FOLDER = "./pdf_output/"
CSS_FILE = "custom_font.css"

os.makedirs(PDF_FOLDER, exist_ok=True)

def convert_html_to_pdf():
    """Converts all HTML files to PDFs using WeasyPrint with page numbers."""
    html_files = glob.glob(os.path.join(HTML_FOLDER, "*.html"))

    for html_file in html_files:
        book_name = os.path.basename(html_file).replace(".html", ".pdf")
        output_pdf_path = os.path.join(PDF_FOLDER, book_name)

        print(f"Converting {html_file} -> {output_pdf_path} ...")
        HTML(html_file).write_pdf(output_pdf_path, stylesheets=[CSS_FILE])

    print("All HTML files have been converted to PDFs.")

if __name__ == "__main__":
    convert_html_to_pdf()