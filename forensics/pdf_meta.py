from pathlib import Path
import sys

import pikepdf

def get_pdf_metadata(pdf_file):
    with pikepdf.Pdf.open(pdf_file) as pdf:
        return dict(pdf.docinfo)

def print_pdf_metadata(metadata):
    for key, value in metadata.items():
        print(f"{key} : {value}")

if __name__ == "__main__":
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("Proiect.pdf")
    print_pdf_metadata(get_pdf_metadata(pdf_path))
