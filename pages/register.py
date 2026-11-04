
import sqlite3
import flet as ft

from components.header import school_header
from database import create_student_account, is_id_registered
from pages.create.student_details import show_student_details


BG = "#FFFCFC"
INK = "#211D1D"
ERROR = "#B42318"
SUCCESS = "#147D36"
MUTED = "#707786"


def show_register(page: ft.Page, show_home):

    page.controls.clear()

    # Message displayed directly on the registration screen.
    status_text = ft.Text(
        "",
        size=13,
        color=ERROR,
        text_align=ft.TextAlign.CENTER,
    )

    def show_message(message, is_error=True, show_popup=True):

        status_text.value = message
        status_text.color = ERROR if is_error else SUCCESS

        # Also display a temporary notification.
        if show_popup:
            try:
                page.show_dialog(
                    ft.SnackBar(
                        content=ft.Text(message),
                        bgcolor=ERROR if is_error else SUCCESS,
                    )
                )
            except Exception:
                pass

        page.update()

    # ID NUMBER
    id_number_field = ft.TextField(
        width=float("inf"),
        hint_text="Enter your ID number",
        border_radius=15,
        border=ft.Border.all(2, "#000000"),
        bgcolor="#FFFFFF",
        text_size=16,
    )

    # PASSWORD
    password_field = ft.TextField(
        width=float("inf"),
        hint_text="Create a password",
        password=True,
        can_reveal_password=True,
        border_radius=15,
        border=ft.Border.all(2, "#000000"),
        bgcolor="#FFFFFF",
        text_size=16,
    )

    # CONFIRM PASSWORD
    confirm_password_field = ft.TextField(
        width=float("inf"),
        hint_text="Re-enter your password",
        password=True,
        can_reveal_password=True,
        border_radius=15,
        border=ft.Border.all(2, "#000000"),
        bgcolor="#FFFFFF",
        text_size=16,
    )

    # CREATE ACCOUNT FUNCTION
    def create_account(e=None):

        print("Create Account button clicked")

        student_id = (id_number_field.value or "").strip()
        password = password_field.value or ""
        confirm_password = confirm_password_field.value or ""

        # 1. Check ID number
        if not student_id:

            show_message("Please enter your ID number.")
            return

        # 2. Check duplicate ID
        try:

            if is_id_registered(student_id):

                show_message(
                    "This ID number is already registered. "
                    "Please use another ID."
                )
                return

        except (sqlite3.Error, OSError) as error:

            show_message(
                f"Could not check ID number: {error}"
            )
            return

        # 3. Check password length
        # More than 8 characters means at least 9.
        if len(password) <= 8:

            show_message(
                "Password must be at least 9 characters long."
            )
            return

        # 4. Require at least one letter
        if not any(character.isalpha() for character in password):

            show_message(
                "Password must contain at least one letter."
            )
            return

        # 5. Require at least one number
        if not any(character.isdigit() for character in password):

            show_message(
                "Password must contain at least one number."
            )
            return

        # 6. Require at least one symbol
        if not any(
            not character.isalnum() and not character.isspace()
            for character in password
        ):

            show_message(
                "Password must contain at least one symbol, "
                "such as @, #, or $."
            )
            return

        # 7. Confirm password
        if password != confirm_password:

            show_message(
                "Confirm Password does not match Password."
            )
            return

        # 8. Save account
        try:

            account_created = create_student_account(
                student_id,
                password
            )

        except (sqlite3.Error, OSError, ValueError) as error:

            show_message(
                f"Account could not be created: {error}"
            )
            return

        if not account_created:

            show_message(
                "This ID number is already registered. "
                "Please use another ID."
            )
            return

        # 9. Account successfully created.
        # Pass the registered ID to the Student Details page.
        show_student_details(
            page,
            id_number=student_id,
            on_back=lambda: show_register(page, show_home),
            on_home=show_home,
        )

        # Display success notification on the new screen.
        try:

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Account created successfully! "
                        "Please complete your student details."
                    ),
                    bgcolor=SUCCESS,
                )
            )

            page.update()

        except Exception:
            pass

    # REGISTRATION SCREEN
    register_screen = ft.Container(
        width=360,
        bgcolor=BG,
        padding=10,

        content=ft.Column(
            controls=[

                school_header(),

                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Back",
                            on_click=show_home,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),

                ft.Container(height=20),

                ft.Text(
                    "CREATE AN ACCOUNT",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                    font_family="Georgia",
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=25),

                # ID NUMBER
                ft.Text(
                    "ID number",
                    size=16,
                    color=INK,
                    font_family="Georgia",
                ),

                id_number_field,

                ft.Container(height=15),

                # PASSWORD
                ft.Text(
                    "Password",
                    size=16,
                    color=INK,
                    font_family="Georgia",
                ),

                password_field,

                ft.Text(
                    "Use at least 9 characters, including "
                    "a letter, a number, and a symbol.",
                    size=11,
                    color=MUTED,
                ),

                ft.Container(height=10),

                # CONFIRM PASSWORD
                ft.Text(
                    "Confirm Password",
                    size=16,
                    color=INK,
                    font_family="Georgia",
                ),

                confirm_password_field,

                ft.Container(height=18),

                # VALIDATION MESSAGE
                status_text,

                ft.Container(height=12),

                # CREATE ACCOUNT BUTTON
                ft.Row(
                    controls=[
                        ft.Button(
                            content="Create Account",
                            on_click=create_account,
                            width=220,
                            height=50,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],

            spacing=5,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.add(
        ft.Row(
            controls=[register_screen],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
    )

    page.update()
