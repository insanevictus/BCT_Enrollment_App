import flet as ft

from pages.home import show_home
from pages.login import show_login
from pages.register import show_register


def main(page: ft.Page):
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = True
    page.title = "BCT Enrollment System"
    page.bgcolor = "#FFFCFC"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    def open_home(e=None):
        show_home(page, open_login, open_register)


    def open_login(e=None):
        show_login(page, open_home)


    def open_register(e=None):
        show_register(page, open_home)

    open_home()


ft.run(main)
