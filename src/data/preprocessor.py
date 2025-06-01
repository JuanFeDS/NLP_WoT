"""Preprocessor module for cleaning the text data."""
import re
import unicodedata

class TextProcessor:
    """Class to process and clean text data."""
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """_summary_

        Args:
            text (str): _description_

        Returns:
            str: _description_
        """

        # Remove end-of-line characters
        clean_text = re.sub(r"www\.lectulandia\.com\s*-\s*Página\s*\d+", "", text)

        # Remove any non-ASCII characeters
        clean_text = (
            unicodedata.normalize("NFKD", clean_text)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )

        return clean_text

    # Metodo para separar texto por capitulos
    def split_by_chapters(self, text: str):
        """_summary_

        Args:
            text (str): _description_
        """
        chapters_pattern = r"\n\s*(\d{1,2})\s+([^\n]+)"
        matchs = list(re.finditer(chapters_pattern, text))

        glosary_init = re.search('glosario', text)

        # Guardamos el texto por capítulos
        for i in enumerate(matchs):
            ini_cap = matchs[i[0]].start()
            fin_cap = matchs[i[0] + 1].start() if i[0] + 1 < len(matchs) else len(text)

            if fin_cap > glosary_init.start():
                fin_cap = glosary_init.start()

            titulo = matchs[i[0]].group(2).replace(' ', '_').lower()

            num_archivo = i[0] + 1 if len(str(i[0] + 1)) == 2 else f'0{i[0]+1}'
            nombre_archivo = f'{num_archivo}.{titulo}.txt'

            with open(f'../Data/Clean/01_EOdM/{nombre_archivo}', 'w', encoding='utf-8') as file:
                file.write(text[ini_cap:fin_cap])
