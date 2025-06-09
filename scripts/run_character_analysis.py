"""_summary_"""
import sys
sys.path.append('./')

from src.config import settings
from src.data.loader import BookManager
from src.data.preprocessor import TextProcessor

def run_character_analysis():
    """Run the character analysis logic
    """
    loader = BookManager()

    # PATHS 
    data_dir = settings.DATA_DIR
    file_name = str(input('Enter the file name (without extension): '))

    txt_path = f'{data_dir}/Processed/{file_name}.txt'
    pdf_path = f'{data_dir}/Raw/{file_name}.pdf'

    try:
        text = loader.load_doc(txt_path)
    except FileNotFoundError:
        doc = loader.build_doc(pdf_path)
        loader.save_doc(doc, txt_path)

        text = loader.load_doc(txt_path)

    processor = TextProcessor()
    clean_text = processor.clean_text(text)
    print(clean_text)
