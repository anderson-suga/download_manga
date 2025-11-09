import asyncio
import os
import time
from urllib.parse import urlparse
import nest_asyncio

from src.helpers.database import get_all_chapters_to_download, update_chapter_status
from src.helpers.files import (
    compress_files,
    create_folders,
    create_download_error_log,
    delete_folder,
    download_all_images,
    remove_duplicate_from_log
)
from src.helpers.jestful import get_all_chapter_url
from src.helpers.logger import get_logger, print_logger
from src.scraper.manga_scraper import MangaScraper


def download_manga():
    nest_asyncio.apply()
    count_error_get_chapter_image = 0

    logger = get_logger("download")
    logger_error_download = create_download_error_log()

    all_chapters = get_all_chapters_to_download(logger)

    message_info = "DOWNLOAD - Início\n"
    print_logger(logger, "info", message_info)

    if len(all_chapters) != 0:
        try:
            # Inicializa o driver do navegador
            manga_scraper = MangaScraper()
            manga_scraper.login()
        except Exception as e:
            message_error = f"Erro ao iniciar o driver do navegador\n{e}\n"
            print_logger(logger, "error", message_error)
            return
    else:
        message_error = "Não há mangás ativos no banco de dados\n"
        print_logger(logger, "error", message_error)
        return

    try:
        for index, chapter in enumerate(all_chapters):
            suffix = "\n" if index == len(all_chapters) - 1 else ""

            manga_name = chapter[0]
            id_chapter = chapter[1]
            url_chapter = chapter[2]

            if count_error_get_chapter_image >= 5:
                message_error = "Muitos erros ao obter as imagens dos capítulos\n"
                print_logger(logger, "error", message_error)
                break

            manga_scraper.go_to_url(url_chapter)

            find_image, message_error = manga_scraper.wait_for(
                url_chapter, "class", "bodychapter"
            )

            if not find_image:
                count_error_get_chapter_image += 1
                print_logger(logger, "error", message_error)
                continue

            time.sleep(6)

            soup = manga_scraper.get_soup()

            list_url_chapter = get_all_chapter_url(soup)

            if len(list_url_chapter) > 0:
                dest_folder, download_folder, temp_folder = create_folders(
                    manga_name, id_chapter
                )
                # Lista de dict o nome do arquivo e a url da imagem
                download_files = []

                # Lista de arquivos baixados para facilitar no momento do zip
                downloaded_files = []

                page_number = 0

                for url_image in list_url_chapter:
                    # Increment the page number
                    page_number += 1

                    # Get the file name and extension
                    file_name, file_ext = os.path.splitext(
                        os.path.basename(urlparse(url_image).path)
                    )

                    # Get the full path to the file
                    download_file_name = os.path.join(
                        download_folder, str(page_number).zfill(3) + file_ext
                    )

                    downloaded_files.append(download_file_name)

                    download_files.append(
                        {
                            "url_image": url_image,
                            "download_file_name": download_file_name,
                        }
                    )

                # Baixar todos os imagens do capitulo
                asyncio.run(download_all_images(logger, logger_error_download, download_files))
                

                file_zip = os.path.join(dest_folder, f"{id_chapter}.zip")

                is_compactated, message = compress_files(
                    logger, downloaded_files, file_zip
                )

                message_type = "info" if is_compactated else "error"

                print_logger(logger, message_type, message)

                update_chapter_status(logger, id_chapter, "Completed")

                delete_folder(logger, temp_folder)

            else:
                count_error_get_chapter_image += 1
                message_error = (
                    f"{url_chapter} - Não foi possível obter os capítulos{suffix}"
                )
                print_logger(logger, "error", message_error)
    finally:
        manga_scraper.close_driver()

    message_info = "DOWNLOAD - Fim"
    print_logger(logger, "info", message_info)

    remove_duplicate_from_log(logger_error_download)
