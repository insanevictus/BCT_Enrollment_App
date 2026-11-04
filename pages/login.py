
import sqlite3
import flet as ft

from components.header import school_header

from pages.menu.menu import show_menu
from pages.menu.enroll.enroll_subjects import show_enroll_subjects
from pages.menu.subjects.view_subjects import show_view_subjects
from pages.menu.balance.view_balance import show_balance
from pages.menu.payment_history.transaction_history import (
    show_transaction_history,
)

from database import (
    verify_student_login,
    get_student_profile,
)


BG = "#FFFCFC"
INK = "#211D1D"
ERROR = "#B42318"
SUCCESS = "#147D36"


def show_login(page, show_home):

    page.controls.clear()
    page.bgcolor = BG
    page.padding = 0

    # =================================================
    # STATUS MESSAGE
    # =================================================

    status_text = ft.Text(
        "",
        size=13,
        color=ERROR,
        text_align=ft.TextAlign.CENTER,
    )

    def show_message(message, is_error=True):

        status_text.value = message

        status_text.color = (
            ERROR if is_error else SUCCESS
        )

        page.update()

    # =================================================
    # ID NUMBER FIELD
    # =================================================

    id_number_field = ft.TextField(
        width=float("inf"),
        hint_text="Enter your ID number",
        border_radius=15,
        border=ft.Border.all(2, "#000000"),
        bgcolor="#FFFFFF",
        text_size=18,
    )

    # =================================================
    # PASSWORD FIELD
    # =================================================

    password_field = ft.TextField(
        width=float("inf"),
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        border_radius=15,
        border=ft.Border.all(2, "#000000"),
        bgcolor="#FFFFFF",
        text_size=18,
    )

    # =================================================
    # OPEN STUDENT MENU
    # =================================================

    def open_student_menu(student_id, student_name):

        # ---------------------------------------------
        # OPEN SUBJECT HISTORY
        # ---------------------------------------------

        def open_subjects(e=None):

            show_view_subjects(
                page,
                student_id=student_id,
                on_back=lambda: open_student_menu(
                    student_id,
                    student_name
                ),
            )

        # ---------------------------------------------
        # OPEN ENROLLMENT
        # ---------------------------------------------

        def open_enrollment(e=None):

            show_enroll_subjects(
                page,

                student_id=student_id,

                on_back=lambda: open_student_menu(
                    student_id,
                    student_name
                ),

                on_continue=lambda enrollment_id: show_balance(
                    page,

                    student_id=student_id,

                    enrollment_id=enrollment_id,

                    on_back=lambda: open_student_menu(
                        student_id,
                        student_name
                    ),

                    on_enroll=open_enrollment,
                ),
            )

        # ---------------------------------------------
        # OPEN BALANCE
        # ---------------------------------------------

        def open_balance(e=None):

            show_balance(
                page,

                student_id=student_id,

                on_back=lambda: open_student_menu(
                    student_id,
                    student_name
                ),

                on_enroll=open_enrollment,
            )

        # ---------------------------------------------
        # OPEN TRANSACTION HISTORY
        # ---------------------------------------------

        def open_transaction_history(e=None):

            show_transaction_history(
                page,

                student_id=student_id,

                on_back=lambda: open_student_menu(
                    student_id,
                    student_name
                ),
            )

        # ---------------------------------------------
        # DISPLAY MENU
        # ---------------------------------------------

        show_menu(
            page,

            on_view_subjects=open_subjects,

            on_enroll_subjects=open_enrollment,

            on_view_balance=open_balance,

            on_transaction_history=open_transaction_history,

            student_name=student_name,

            student_id=student_id,

            on_sign_out=lambda: show_login(
                page,
                show_home
            ),
        )

    # =================================================
    # LOGIN FUNCTION
    # =================================================

    def login(e=None):

        student_id = (
            id_number_field.value or ""
        ).strip()

        password = password_field.value or ""

        if not student_id:

            show_message(
                "Please enter your ID number."
            )

            return

        if not password:

            show_message(
                "Please enter your password."
            )

            return

        try:

            authenticated = verify_student_login(
                student_id,
                password
            )

            if not authenticated:

                show_message(
                    "Incorrect ID number or password."
                )

                password_field.value = ""
                page.update()

                return

            profile = get_student_profile(
                student_id
            )

            student_name = (
                profile["full_name"]
                if profile
                else "Student"
            )

            print(
                f"Student {student_id} logged in successfully."
            )

            open_student_menu(
                student_id,
                student_name
            )

        except (sqlite3.Error, OSError) as error:

            print(f"Login error: {error}")

            show_message(
                "Unable to access the database. "
                "Please try again."
            )

    # =================================================
    # FORGOT PASSWORD
    # =================================================

    def forgot_password(e=None):

        show_message(
            "Password recovery is not available yet. "
            "Please contact the administrator."
        )

    # =================================================
    # LOGIN SCREEN
    # =================================================

    login_screen = ft.Container(
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

                ft.Container(height=80),

                ft.Text(
                    "ID number",
                    size=18,
                    color=INK,
                    font_family="Georgia",
                ),

                id_number_field,

                ft.Container(height=20),

                ft.Text(
                    "Password",
                    size=18,
                    color=INK,
                    font_family="Georgia",
                ),

                password_field,

                ft.Container(height=15),

                status_text,

                ft.Container(height=25),

                ft.Row(
                    controls=[
                        ft.Button(
                            content="Enter",
                            on_click=login,
                            width=220,
                            height=45,
                        )
                    ],

                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                ft.Container(height=10),

                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Forgot password?",
                            on_click=forgot_password,
                        )
                    ],

                    alignment=ft.MainAxisAlignment.CENTER,
                ),

            ],

            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.add(
        ft.Row(
            controls=[login_screen],

            alignment=ft.MainAxisAlignment.CENTER,

            vertical_alignment=ft.CrossAxisAlignment.START,

            expand=True,
        )
    )

    page.update()
