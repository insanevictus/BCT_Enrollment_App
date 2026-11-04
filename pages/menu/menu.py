
import flet as ft

from components.header import school_header
from components.buttons import action_button


BG = "#FFFCFC"
INK = "#000000"
BLUE = "#5792E8"
LABEL = "#707786"

def show_menu(
    page: ft.Page,
    on_view_subjects=None,
    on_enroll_subjects=None,
    on_view_balance=None,
    on_transaction_history=None,
    on_sign_out=None,
    student_name="Student",
    student_id="",
):

    page.controls.clear()
    page.bgcolor = BG
    page.padding = 0

    # =================================================
    # STUDENT PROFILE CARD
    # =================================================

    profile_card = ft.Container(
        width=340,

        bgcolor="#FFFFFF",

        border=ft.Border.all(
            1,
            "#E0E0E0"
        ),

        border_radius=15,

        padding=ft.Padding(
            left=18,
            top=14,
            right=18,
            bottom=14
        ),

        content=ft.Column(
            controls=[

                ft.Text(
                    f"Welcome, {student_name}!",
                    size=19,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Row(
                    controls=[
                        ft.Text(
                            "Student ID:",
                            size=13,
                            color=LABEL,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            student_id,
                            size=13,
                            color=INK,
                        ),
                    ],

                    spacing=6,
                ),

            ],

            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    # =================================================
    # SIGN OUT CONFIRMATION
    # =================================================

    def confirm_sign_out(e=None):

        page.pop_dialog()

        if on_sign_out:
            on_sign_out()

    def sign_out(e=None):

        dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Sign Out",
                weight=ft.FontWeight.BOLD,
            ),

            content=ft.Text(
                "Are you sure you want to sign out "
                "of your account?"
            ),

            actions=[

                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: page.pop_dialog(),
                ),

                ft.Button(
                    content="Sign Out",
                    on_click=confirm_sign_out,
                ),

            ],

            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dialog)

    # =================================================
    # FADED SCHOOL LOGO
    # =================================================

    watermark = ft.Container(
        content=ft.Image(
            src="bctprofilepic-removebg-preview.png",
            width=350,
            height=350,
            fit=ft.BoxFit.CONTAIN,
            opacity=0.20,
        ),

        alignment=ft.Alignment(0, 0),
    )

    # =================================================
    # MAIN MENU BUTTONS
    # =================================================

    menu_buttons = ft.Column(
        controls=[

            action_button(
                "View Subjects",
                on_view_subjects,
                width=220,
                height=46,
                size=19,
                radius=30,
                outlined=False,
            ),

            action_button(
                "Enroll Subjects",
                on_enroll_subjects,
                width=220,
                height=46,
                size=19,
                radius=30,
                outlined=False,
            ),

            action_button(
                "View Balance",
                on_view_balance,
                width=220,
                height=46,
                size=19,
                radius=30,
                outlined=False,
            ),

            action_button(
                "Transaction History",
                on_transaction_history,
                width=220,
                height=46,
                size=18,
                radius=30,
                outlined=False,
            ),

        ],

        spacing=42,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # =================================================
    # WATERMARK AND MENU BUTTONS
    # =================================================

    menu_content = ft.Stack(
        controls=[

            ft.Container(
                content=watermark,
                alignment=ft.Alignment(0, 0),
                expand=True,
            ),

            ft.Container(
                content=menu_buttons,
                alignment=ft.Alignment(0, 0),
                expand=True,
            ),

        ],

        expand=True,
    )

    # =================================================
    # MAIN MENU SCREEN
    # =================================================

    menu_screen = ft.Container(
        width=390,
        bgcolor=BG,

        padding=ft.Padding(
            left=6,
            top=45,
            right=6,
            bottom=15
        ),

        content=ft.Column(
            controls=[

                # SCHOOL HEADER
                school_header(),

                ft.Container(height=14),

                # LOGGED-IN STUDENT INFORMATION
                profile_card,

                ft.Container(height=16),

                # MENU TITLE
                ft.Text(
                    "MENU",
                    size=48,
                    color=INK,
                    text_align=ft.TextAlign.CENTER,
                    font_family="Arial",
                ),

                ft.Container(height=10),

                # MENU BUTTONS
                menu_content,

                ft.Container(height=10),

                # SIGN OUT BUTTON
                ft.TextButton(
                    content=ft.Text(
                        "Sign out",
                        size=20,
                        color=INK,
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.UNDERLINE,
                        ),
                    ),

                    on_click=sign_out,
                ),

            ],

            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )

    # =================================================
    # ADD TO PAGE
    # =================================================

    page.add(
        ft.Row(
            controls=[menu_screen],

            alignment=ft.MainAxisAlignment.CENTER,

            vertical_alignment=ft.CrossAxisAlignment.STRETCH,

            expand=True,
        )
    )

    page.update()
