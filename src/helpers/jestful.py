import re

from bs4 import BeautifulSoup, element
from unidecode import unidecode

from src.config.config import config
from src.helpers.database import get_all_ad_files


def get_manga_info(logger, soup: BeautifulSoup, manga_url: str):
    manga_info = {}
    list_chapters = []

    try:
        ul_manga_info = soup.find("ul", class_="manga-info")

        name = ul_manga_info.h3.text.strip()
        last_update = ul_manga_info.i.span.text.strip()

        tbody_chapters = soup.find("table", class_="table table-hover").tbody

        for tr in tbody_chapters:
            if isinstance(tr, element.Tag):
                first_td = tr.find("td")
                if first_td:
                    chapter = first_td.a.b.text.strip().lower()
                    chapter_url = first_td.a["href"]
                    list_chapters.insert(0, (chapter, f"{config["URL"]}/{chapter_url}"))

        # Status do manga
        status = "Active"

        # Pausar se não tiver atualização há mais de 1 ano
        if "year" in last_update.lower():
            status = "On Hold"

        # Verificar se o mangá está completo
        is_completed = (
            True
            if ul_manga_info.find_all("li")[2].a.text.strip() == "Complete"
            else False
        )

        if is_completed:
            status = "Completed"

        manga_info["name_raw"] = name
        manga_info["last_update"] = last_update
        manga_info["list_chapters"] = list_chapters
        manga_info["status"] = status
    except Exception as e:
        manga_info = {}
        message_error = f"get_manga_info - {manga_url}\n{e}\n"
        print(message_error.rstrip())
        logger.error(message_error)

    return manga_info


def parse_manga_name(list_rename, url: str, manga_name: str) -> str:
    # Consultar na lista com os nomes para trocar
    exists = [url for manga_url, _, _ in list_rename if manga_url == url]

    if exists:
        for rename in list_rename:
            if rename[0] == url:
                return rename[2]
    else:
        input_string = unidecode(manga_name)

        # Deixar tudo em maiúsculo
        input_string = input_string.upper()

        # Substituir "- RAW", "@COMICO" e " (MANGA)" por uma string vazia
        input_string = re.sub(r"- RAW|\s*@COMIC| \(MANGA\)", "", input_string)

        # Manter somente letras de A a Z, números, hífen e espaços
        input_string = re.sub(r"[^A-Z0-9- ]+", "", input_string)

        # Remover hífen não entre letras ou números
        input_string = re.sub(r"(?<![A-Z0-9])-|-(?![A-Z0-9])", "", input_string)

        # Substituir múltiplos espaços por um único espaço
        input_string = re.sub(r"\s+", " ", input_string).strip()

        return input_string


def convert_chapter(chapter_str):
    # Extrai o número usando regex
    match = re.search(r"chapter (\d+(\.\d+)?)", chapter_str, re.IGNORECASE)
    if match:
        # Converte para float para preservar decimais e formatar corretamente
        number = float(match.group(1))
        # Formata o número como string com 4 dígitos inteiros e 2 decimais
        formatted_number = f"{number:07.2f}"
        return True, formatted_number
    else:
        return False, None


def get_all_chapter_url(soup):
    list_url_chapter = []
    list_ad_files = get_all_ad_files()

    imagens = soup.find_all('img', class_='chapter-img', alt=lambda value: value and value.startswith("Page "))

    for image in imagens:
        # Verificar se a url da imagem não contém a url de um anúncio
        if not any(ad in image["src"].strip() for ad in list_ad_files):
            list_url_chapter.append(image["src"].strip())

    return list_url_chapter
