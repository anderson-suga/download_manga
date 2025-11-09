import psycopg

from src.config.database import connection_info
from src.helpers.datetime import get_timestamp
from src.helpers.logger import print_logger


def get_all_mangas_from_database(logger):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT url 
                                    FROM public.mangas
                                   WHERE status = 'Active'
                                   ORDER BY url; """)
                mangas = cursor.fetchall()
                return mangas
    except Exception as e:
        message_error = f"get_all_mangas\n{e}\n"
        print_logger(logger, "error", message_error)
        return []


def get_all_chapters(logger, manga_id):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT url
                         FROM public.chapters
                        WHERE manga_id = %s; """,
                    (manga_id,),
                )
                chapters = cursor.fetchall()
                url_chapters = [chapter[0] for chapter in chapters]
                return url_chapters
    except Exception as e:
        message_error = f"get_all_chapters\n{e}\n"
        print_logger(logger, "error", message_error)
        return []


def get_all_chapters_to_download(logger):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT mangas."name", chapters.id, chapters.url
                         FROM public.chapters
                         LEFT JOIN public.mangas ON (mangas.id = chapters.manga_id)
                        WHERE chapters.status = 'Pending'
                        ORDER BY id; """
                )
                chapters = cursor.fetchall()
                return chapters
    except Exception as e:
        message_error = f"get_all_chapters_to_download\n{e}\n"
        print_logger(logger, "error", message_error)
        return []


def update_chapter_status(logger, chapter_id, status):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE public.chapters
                          SET status = %s,
                              updated_at = NOW()
                        WHERE id = %s; """,
                    (status, chapter_id),
                )
    except Exception as e:
        message_error = f"update_chapter_status - {chapter_id}\n{e}\n"
        print_logger(logger, "error", message_error)


def get_manga_rename():
    with psycopg.connect(**connection_info) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT url, name_from, name_to
                     FROM public.manga_rename; """
            )
            mangas_rename = cursor.fetchall()
            return mangas_rename


def update_manga_not_existed(logger, url):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE public.mangas
                          SET status = 'Not Existed',
                              updated_at = NOW()
                        WHERE url = %s; """,
                    (url,),
                )
    except Exception as e:
        message_error = f"update_manga_not_existed - {url}\n{e}\n"
        print_logger(logger, "error", message_error)


def check_manga_exists_database(url):
    with psycopg.connect(**connection_info) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT id
                     FROM public.mangas
                    WHERE url = %s; """,
                (url,),
            )
            row_manga = cursor.fetchone()
            if row_manga is None:
                return False, 0
            return True, row_manga[0]


def create_manga(logger, manga_info):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO public.mangas (url, name_raw, name, last_update, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, NOW(), NOW()) RETURNING id; """,
                    (
                        manga_info["url"],
                        manga_info["name_raw"],
                        manga_info["name"],
                        manga_info["last_update"],
                        manga_info["status"],
                    ),
                )
                new_manga_id = cursor.fetchone()[0]
                return new_manga_id
    except Exception as e:
        message_error = f"create_manga - {manga_info["url"]}\n{e}\n"
        print_logger(logger, "error", message_error)


def create_chapter(logger, id, url, manga_id):
    try:
        with psycopg.connect(**connection_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO public.chapters (id, url, manga_id, status, created_at, updated_at)
                        VALUES (%s, %s, %s, 'Pending', NOW(), NOW()); """,
                    (id, url, manga_id),
                )
    except Exception as e:
        message_error = f"create_chapter\n{id} - {url}\n{e}\n"
        print_logger(logger, "error", message_error)


def update_manga_info(manga_info):
    with psycopg.connect(**connection_info) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT name_raw, name
                     FROM public.mangas
                    WHERE url = %s; """,
                (manga_info["url"],),
            )
            manga = cursor.fetchone()

            db_manga_name_raw = manga[0]
            db_manga_name = manga[1]

            if (db_manga_name != manga_info["name"]):
                cursor.execute(
                    """UPDATE public.mangas
                          SET status = 'Failed',
                              updated_at = NOW()
                        WHERE url = %s; """,
                    (manga_info["url"]),
                )
                error_message = f"update_manga_info - Nome do mangá diferente - {manga_info["url"]}\n \
Nome no site: {manga_info['name_raw']} x Nome no banco: {db_manga_name_raw}\n \
Nome formatado no site: {manga_info['name']} x Nome formatado no banco: {db_manga_name}\n"
                return False, error_message
            else:
                cursor.execute(
                    """UPDATE public.mangas
                          SET last_update = %s, 
                              status = %s,
                              updated_at = NOW()
                        WHERE url = %s; """,
                    (
                        manga_info["last_update"],
                        manga_info["status"],
                        manga_info["url"],
                    ),
                )
                message_info = f"{get_timestamp()} - {manga_info['name']} - {manga_info["status"]} - Atualizado\n"
                return True, message_info


def get_all_ad_files():
    with psycopg.connect(**connection_info) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT filename
                     FROM public.ad_files; """
            )
            database_ad_files = cursor.fetchall()
    ad_files = [ad_file[0] for ad_file in database_ad_files]
    return ad_files
