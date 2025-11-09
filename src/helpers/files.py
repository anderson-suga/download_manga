import asyncio
import datetime
import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse

from aiohttp import ClientSession

from src.config.config import config
from src.helpers.logger import print_logger

gdrive_directory = config["GDRIVE_DIRECTORY"]
temp_directory = config["TEMP_DIRECTORY"]
image_not_found = config["NOT_FOUND"]
manga_url = config["URL"] + "/"


def create_folders(manga_name: str, chapter_id: str) -> Tuple[str, str, str]:
    """
    Args:
        manga_name (str): The name of the manga.
        chapter_id (str): The id of the chapter.

    Returns:
        Tuple[str, str, str]: A tuple with the path to the destination folder, download folder and temp folder.
    """
    # Create the folders
    dest_folder = os.path.join(gdrive_directory, manga_name)
    temp_folder = os.path.join(temp_directory, manga_name)
    download_folder = os.path.join(temp_folder, chapter_id)

    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    Path(temp_folder).mkdir(parents=True, exist_ok=True)
    Path(download_folder).mkdir(parents=True, exist_ok=True)

    return dest_folder, download_folder, temp_folder


async def download_image(logger, logger_error_download, session, download_file_name, url_image):
    try:
        headers = {
            "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Host": urlparse(url_image).netloc,
            "Referer": manga_url,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0",
        }

        async with session.get(url_image, headers=headers) as response:
            if response.status == 200:
                with open(download_file_name, "wb") as f:
                    f.write(await response.read())
            else:
                # Em caso de erro, copia o arquivo de erro
                with open(image_not_found, "rb") as f_src:
                    with open(download_file_name, "wb") as f_dest:
                        f_dest.write(f_src.read())
                message_error = f"Erro ao baixar - Status {response.status}\n{download_file_name}\n{url_image}"
                print_logger(logger, "error", message_error)

    except Exception as e:
        # Em caso de exceção, também copia o arquivo de erro
        with open(image_not_found, "rb") as f_src:
            with open(download_file_name, "wb") as f_dest:
                f_dest.write(f_src.read())
        manga_name = os.path.basename(os.path.dirname(download_file_name))
        with open(logger_error_download, "a", encoding="utf-8") as file_error_download:
            file_error_download.write(f"{manga_name}\n")
        
        message_error = f"Erro ao baixar\n{download_file_name}\n{url_image}\n{e}"
        print_logger(logger, "error", message_error)


async def download_all_images(logger, logger_error_download, list_chapters):
    async with ClientSession() as session:
        tasks = []
        for chapter in list_chapters:
            task = asyncio.ensure_future(
                download_image(
                    logger, logger_error_download, session, chapter["download_file_name"], chapter["url_image"]
                )
            )
            tasks.append(task)
        await asyncio.gather(*tasks)


# Function to compress files
def compress_files(logger, files: List[str], file_name: str) -> bool:
    """
    Args:
        files (List[str]): The list of files to compress.
        dest_folder (str): The path to the destination folder.
        file_name (str): The name of the zip file.

    Returns:
        bool: True if the files were compressed, False otherwise.
    """
    # Variable to check if the files were compressed
    compressed = True

    message = """"""

    try:
        # Compress the files
        with zipfile.ZipFile(file_name, "w") as zip_file:
            # Iterate over the files
            for file in files:
                # Add the file to the zip file
                zip_file.write(file, os.path.basename(file))
        message = f"{Path(file_name).stem} - OK"
    except Exception as e:
        # If an error occurred, change the variable
        compressed = False

        message = f"Erro ao comprimir o arquivo {file_name}\n{e}"

    return compressed, message


# Function to delete a folder
def delete_folder(logger, path: str) -> None:
    """
    Args:
        path (str): The path to the folder to delete.
    Returns:
        bool: True if the folder was deleted, False otherwise.
    """
    try:
        # Delete the folder
        shutil.rmtree(path)
    except Exception as e:
        message_error = f"Erro ao deletar a pasta {path}\n{e}"
        print_logger(logger, "error", message_error)


def create_download_error_log():
    filename = datetime.datetime.now().strftime(
        f"{config["LOG_DIRECTORY"]}/download_error_%Y%m%d_%H%M%S.log"
    )
    open(filename, "w").close()
    return filename


def remove_duplicate_from_log(filepath):
    try:
        with open(filepath, 'r') as f:
            rows = f.readlines()

        # Remove quebras de linha e duplicados
        chapters_with_error = sorted(set(row.strip() for row in rows if row.strip()))

        if not chapters_with_error:
            print('Não foi encontrado nenhum arquivo para baixar novamente')
            return

        with open(filepath, 'w') as f:
            for chapter_id in chapters_with_error:
                f.write(f"'{chapter_id}',\n")
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {filepath}")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")