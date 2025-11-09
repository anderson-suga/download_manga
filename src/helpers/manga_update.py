import time
from src.helpers.database import (
    check_manga_exists_database,
    create_chapter,
    create_manga,
    get_all_chapters,
    get_all_mangas_from_database,
    get_manga_rename,
    update_manga_info,
)
from src.helpers.datetime import get_timestamp
from src.helpers.github import clear_list_new_manga, get_list_new_manga
from src.helpers.jestful import convert_chapter, get_manga_info, parse_manga_name
from src.helpers.logger import get_logger, print_logger
from src.helpers.process import close_chrome
from src.scraper.manga_scraper import MangaScraper



def filter_urls_by_start_letter(urls, start_letter):
    filtered = []
    base = "https://jestful.net/hwms-"

    if not start_letter:
        return urls
    
    for url in urls:
        if url.startswith(base):
            # Pega o primeiro caractere depois de 'hwms-'
            rest = url[len(base):]
            if rest and rest[0].lower() >= start_letter.lower():
                filtered.append(url)
    
    return filtered


def update_manga(start_letter=None):
    chrome_closed = close_chrome()

    if not chrome_closed:
        return

    count_error_get_manga_info = 0

    logger = get_logger("update")

    message_info = f"UPDATE - Início - {get_timestamp()}\n"
    print_logger(logger, "info", message_info)

    manga_scraper = None

    # Pega todos os mangás ativos do banco de dados
    mangas_from_database = get_all_mangas_from_database(logger)
    list_from_database = sorted([manga[0] for manga in mangas_from_database])

    # Pega todos os mangás que estão no repositório do github
    list_from_github = get_list_new_manga()

    # Juntar a lista de mangas que estão no banco de dados com a lista de mangas do github
    all_mangas = sorted(list(set(list_from_database + list_from_github)))

    # Pegar os nomes de x para de animes
    list_rename = get_manga_rename()

    if len(all_mangas) != 0:
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
    
    all_mangas = filter_urls_by_start_letter(all_mangas, start_letter)

    try:
        for manga_url in all_mangas:
            message_info = f"{manga_url}\n"
            print_logger(logger, "info", message_info)

            # Acessa a página do mangá
            manga_scraper.go_to_url(manga_url)

            # Verificar se a página do mangá existe
            not_found_manga = manga_scraper.check_not_found(logger, manga_url)

            # Se a página não existir, passa para o próximo mangá
            if not_found_manga:
                message_error = f"check_not_found\n{manga_url} - 404 Not Found\n"
                print_logger(logger, "error", message_error)
                continue
            
            # Espera a página carregar buscando pela classe "manga-info"
            found_element, message = manga_scraper.wait_for(manga_url, "class", "table table-hover")

            # Se não encontrar a classe, passa para o próximo mangá
            if not found_element:
                print_logger(logger, "error", message)
                continue

            # Pega as informações do mangá
            soup = manga_scraper.get_soup()
            manga_info = get_manga_info(logger, soup, manga_url)

            # Se não conseguir pegar as informações do mangá, passa para o próximo mangá
            if manga_info == {}:
                count_error_get_manga_info += 1
                # Se atingir a quantidade máxima de erros, parar o loop
                if count_error_get_manga_info == 3:
                    message_error = "Quantidade máxima de erros ao pegar as informações do mangá atingida\n"
                    print_logger(logger, "error", message_error)
                    break
                continue

            manga_info["name"] = parse_manga_name(
                list_rename, manga_url, manga_info["name_raw"]
            )
            manga_info["url"] = manga_url

            # Verifica se o mangá já existe no banco de dados
            manga_exists, manga_id = check_manga_exists_database(manga_url)

            # Se o mangá existir, atualiza as informações
            if manga_exists:
                is_updated, message = update_manga_info(manga_info)
                message_type = "info" if is_updated else "error"
                print_logger(logger, message_type, message)
            else:
                if len(manga_url) > 240:
                    manga_info["status"] = "Pending"
                    message_error = (
                        f"URL do mangá {manga_url} maior que 240 caracteres\n"
                    )
                    print_logger(logger, "error", message_error)

                # Criar o manga
                manga_id = create_manga(logger, manga_info)
                message_info = (
                    f"{get_timestamp()} - {manga_info['name']} - Criado com sucesso\n"
                )
                print_logger(logger, "info", message_info)

            if manga_info["status"] != "Pending":
                all_chapters_from_database = get_all_chapters(logger, manga_id)
                list_chapters = manga_info["list_chapters"]

                for chapter, chapter_url in list_chapters:
                    converted, chapter_number = convert_chapter(chapter)
                    if not converted:
                        message_error = (
                            f"Erro ao formatar o capítulo {chapter} - {chapter_url}\n"
                        )
                        print_logger(logger, "error", message_error)
                        continue
                    chapter_id = f"{manga_info["name"]} - {chapter_number}"
                    if chapter_url not in all_chapters_from_database:
                        create_chapter(logger, chapter_id, chapter_url, manga_id)
                        message_info = (
                            f"{get_timestamp()} - {chapter_id} - Criado com sucesso\n"
                        )
                        print_logger(logger, "info", message_info)
                    else:
                        message_info = f"{get_timestamp()} - {chapter_id} - Já existe no banco de dados\n"
                        print_logger(logger, "info", message_info)
    finally:
        manga_scraper.close_driver()

    clear_list_new_manga()

    message_info = f"UPDATE - Fim - {get_timestamp()}\n"
    print_logger(logger, "info", message_info)
