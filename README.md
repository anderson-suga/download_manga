# Download Manga

Project to download manga chapters from the Jestful site, organize them into folders, zip chapters, and track status in PostgreSQL.

## Overview

- Entry scripts:
  - [download.py](download.py) — runs the download flow (calls [`src.helpers.manga_download.download_manga`](src/helpers/manga_download.py)).
  - [update.py](update.py) — updates manga and chapter lists (calls [`src.helpers.manga_update.update_manga`](src/helpers/manga_update.py)).
- Scraping and browser control: [`src.scraper.manga_scraper.MangaScraper`](src/scraper/manga_scraper.py)
- Core config: [`src.config.config.config`](src/config/config.py)
- File utilities: [`src.helpers.files.create_folders`](src/helpers/files.py), [`src.helpers.files.download_all_images`](src/helpers/files.py), [`src.helpers.files.compress_files`](src/helpers/files.py), [`src.helpers.files.create_download_error_log`](src/helpers/files.py), [`src.helpers.files.delete_folder`](src/helpers/files.py), [`src.helpers.files.remove_duplicate_from_log`](src/helpers/files.py)
- Database access and queries: [`src.helpers.database.get_all_chapters_to_download`](src/helpers/database.py), [`src.helpers.database.update_chapter_status`](src/helpers/database.py), [`src.helpers.database.create_manga`](src/helpers/database.py), [`src.helpers.database.create_chapter`](src/helpers/database.py), [`src.helpers.database.check_manga_exists_database`](src/helpers/database.py), [`src.helpers.database.get_all_mangas_from_database`](src/helpers/database.py)
- JST parsing helpers: [`src.helpers.jestful.get_all_chapter_url`](src/helpers/jestful.py), [`src.helpers.jestful.get_manga_info`](src/helpers/jestful.py), [`src.helpers.jestful.parse_manga_name`](src/helpers/jestful.py), [`src.helpers.jestful.convert_chapter`](src/helpers/jestful.py)
- Logging helpers: [`src.helpers.logger.get_logger`](src/helpers/logger.py), [`src.helpers.logger.print_logger`](src/helpers/logger.py)

## Requirements

- Python 3.10+
- PostgreSQL (a compose file is included: [docker-compose.yml](docker-compose.yml))
- Typical Python deps: playwright, aiohttp, beautifulsoup4, psycopg[binary], python-dotenv, unidecode, nest-asyncio

Install dependencies:

```sh
pip install --upgrade playwright requests "psycopg[binary]" python-dotenv unidecode beautifulsoup4 aiohttp nest-asyncio
playwright install
```

## Configuration

1. Copy and edit environment variables in [.env](.env). Key variables used by [`src.config.config.config`](src/config/config.py) include DB connection, `PROFILE_PATH`, `EXTENSION_PATH`, and path variables (`GDRIVE_DIRECTORY`, `TEMP_DIRECTORY`, `NOT_FOUND`, etc.).
2. To start the DB container:

```sh
docker-compose up -d
```

(see [docker-compose.yml](docker-compose.yml))

## Usage

- Update manga list / add chapters to DB:

```sh
python update.py [start_letter]
```

- Download pending chapters (zips each chapter):

```sh
python download.py
```

Logs and error files are created according to paths in [.env](.env) and handled by [`src.helpers.logger.get_logger`](src/helpers/logger.py) / [`src.helpers.logger.print_logger`](src/helpers/logger.py).

## Notes & Tips

- The scraper uses a persistent Playwright context in [`src.scraper.manga_scraper.MangaScraper`](src/scraper/manga_scraper.py). If the browser profile blocks startup, check `PROFILE_PATH` and `EXTENSION_PATH` in [`src.config.config.config`](src/config/config.py).
- To debug page content, use `MangaScraper.get_soup()` and the helpers in [`src.helpers.jestful.get_manga_info`](src/helpers/jestful.py).
- Image downloads are managed by [`src.helpers.files.download_all_images`](src/helpers/files.py) which uses [`src.helpers.files.download_image`](src/helpers/files.py) and a placeholder image defined by `NOT_FOUND` in the config.
- DB operations (create/update chapters and mangas) are in [`src.helpers.database.create_chapter`](src/helpers/database.py), [`src.helpers.database.create_manga`](src/helpers/database.py), and related functions.

## Project structure (important files)

- [download.py](download.py) — download entry (calls [`src.helpers.manga_download.download_manga`](src/helpers/manga_download.py))
- [update.py](update.py) — update entry (calls [`src.helpers.manga_update.update_manga`](src/helpers/manga_update.py))
- [docker-compose.yml](docker-compose.yml)
- [.env](.env)
- [`src.config.config.config`](src/config/config.py)
- [`src.scraper.manga_scraper.MangaScraper`](src/scraper/manga_scraper.py)
- [`src.helpers.manga_update.update_manga`](src/helpers/manga_update.py)
- [`src.helpers.manga_download.download_manga`](src/helpers/manga_download.py)
- [`src.helpers.files`](src/helpers/files.py)
- [`src.helpers.database`](src/helpers/database.py)
- [`src.helpers.jestful`](src/helpers/jestful.py)
- [`src.helpers.logger`](src/helpers/logger.py)

## Common issues

- Permission errors for `PROFILE_PATH` or extension: verify paths in [.env](.env) and [`src.config.config.config`](src/config/config.py).
- Timeouts waiting for elements: adjust `SCREEN_SIZE` and wait settings in config.
- PostgreSQL connection: check credentials and container status (see [docker-compose.yml](docker-compose.yml)).
