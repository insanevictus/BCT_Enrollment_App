from collections.abc import Callable

import flet as ft


BLUE = "#5792E8"


def action_button(
    label: str,
    on_click: Callable | None,
    *,
    width: int | None = None,
    height: int | None = None,
    size: int = 14,
    radius: int = 30,
    disabled: bool = False,
    outlined: bool = True,
) -> ft.Button:
    return ft.Button(
        content=label,
        width=width,
        height=height,
        disabled=disabled,
        on_click=on_click,
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(size=size),
            bgcolor=BLUE,
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=radius),
            side=ft.BorderSide(2, "#000000") if outlined else None,
        ),
    )