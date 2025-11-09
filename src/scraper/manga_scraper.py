import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page, expect
from typing import Tuple, Optional

from src.config.config import config
from src.helpers.database import update_manga_not_existed
from src.helpers.datetime import get_current_datetime_YYYYMMDDHHMMSS

profile_path = config["PROFILE_PATH"]
extension_path = config["EXTENSION_PATH"]


def get_screen_size():
    screen_size_str = config["SCREEN_SIZE"]
    try:
        width_str, height_str = screen_size_str.split('x')
        width = int(width_str)
        height = int(height_str)
        return width, height
    except:
        print(f"Aviso: Formato de SCREEN_SIZE ('{screen_size_str}') é inválido. Usando o padrão 1920x1080.")
        return 1920, 1080


class MangaScraper:
    def __init__(self) -> None:
        screen_width, screen_height = get_screen_size()

        # Inicializando o Playwright
        self.playwright = sync_playwright().start()
        
        # Configuração dos argumentos do navegador
        self.browser_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-logging",
            f"--disable-extensions-except={extension_path}",
            f"--load-extension={extension_path}"
        ]
        
        # Configurando o navegador
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir = profile_path,
            headless = False,
            args = self.browser_args,
            viewport={'width': screen_width, 'height': screen_height},            
        )

        self.page = self.browser.new_page()

    def login(self) -> None:
        # Navegando para a URL principal
        self.page.goto(config["URL"], wait_until='domcontentloaded')
        
        # Esperando pelo elemento de navegação
        self.wait_for(config["URL"], "class", "glyphicon glyphicon-log-in")
        
        # Clicando no link de login
        self.page.click("text=Login")
        
        # Preenchendo o formulário de login
        self.page.fill("input[name='email']", config["URL_LOGIN"])
        self.page.fill("input[name='password']", config["URL_PWD"])
        
        # Clicando no botão de login
        self.page.click("#signin_submit")

        time.sleep(2)


    def go_to_url(self, url: str) -> None:
        # Navegando para a URL especificada
        self.page.goto(url, wait_until='domcontentloaded')

    def get_soup(self) -> BeautifulSoup:
        # Parseando o HTML com BeautifulSoup
        return BeautifulSoup(self.page.content(), "html.parser")

    def check_not_found(self, logger, url) -> bool:
        # Esperar por 2 segundos
        time.sleep(2)
        
        # Verificando se estamos na página 404
        if self.page.url == config["URL_404"]:
            update_manga_not_existed(logger, url)
            return True
        return False

    def wait_for(self, manga_url: str, search_type: str, search_by: str) -> Tuple[bool, str]:
        try:
            if search_type == "id":
                selector = f"#{search_by}"
            elif search_type == "class":
                selector = f".{search_by}"
            elif search_type == "tag":
                selector = search_by
            elif search_type == "css":
                selector = search_by  # passa direto se já for css válido
            elif search_type == "text":
                selector = f"text={search_by}"
            else:
                return False, "Não foi passado um tipo de busca válido"
            # Esperando o elemento aparecer na página por 5 segundos
            self.page.wait_for_selector(selector, timeout=5000)
            return True, ""
        except Exception as e:
            error_message = f"wait_for_element\n{manga_url} - search_type: {search_type} - search_by: {search_by}\n{e}\n"
            return False, error_message

    def save_html_file(self) -> None:
        # Gerando o nome do arquivo com timestamp
        file_name = f"./output_html/scraped_{get_current_datetime_YYYYMMDDHHMMSS()}.html"
        
        # Parseando e formatando o HTML
        soup = self.get_soup()
        
        # Garantindo que o diretório exista
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        # Salvando o arquivo HTML
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(soup.prettify())

    def screenshot(self, file_path: Optional[str] = None) -> None:
        """Captura uma screenshot da página atual"""
        if file_path is None:
            file_path = f"./screenshots/screenshot_{get_current_datetime_YYYYMMDDHHMMSS()}.png"
        
        # Garantindo que o diretório exista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Capturando a screenshot
        self.page.screenshot(path=file_path)

    def close_driver(self) -> None:
        # Fechando o browser e o Playwright
        self.browser.close()
        self.playwright.stop()