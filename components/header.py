
import flet as ft


def school_header():
    return ft.Container(
        width=340,
        content=ft.Row(
            controls=[
                ft.Image(
                    src="bctprofilepic-removebg-preview.png",
                    width=45,
                    height=45,
                    fit=ft.BoxFit.CONTAIN,
                ),
                ft.Text(
                    "Baguio College of Technology",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#211D1D",
                    font_family="Georgia",
                    expand=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#E8E0E0",
        border_radius=25,
        padding=8,
    )
