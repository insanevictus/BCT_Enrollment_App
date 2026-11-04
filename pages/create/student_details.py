
import sqlite3

import flet as ft

from components.header import school_header
from database import save_student_details


BG = "#FFFCFC"
INK = "#171D2A"
LABEL = "#707786"
ERROR = "#B42318"
SUCCESS = "#147D36"

# =====================================================
# COURSE OPTIONS
# =====================================================

COURSE_OPTIONS = [
    "Associate in Computer Technology (2 years)",
    "Associate in Electronics Technology (2 years)",
    "Associate in Electrical Technology (2 years)",
    "Bachelor of Science in Information Technology (BSIT)",
    "Bachelor of Science in Industrial Technology",
    "Bachelor of Science in Computer Engineering",
    "Bachelor of Science in Industrial Education",
]


# =====================================================
# MAJOR OPTIONS
# =====================================================

MAJOR_OPTIONS = {
    "Bachelor of Science in Industrial Technology": [
        "Electricity",
        "Electronics",
        "Electrical Engineering",
    ],

    "Bachelor of Science in Industrial Education": [
        "Computer",
        "Electronics",
        "Electricity",
    ],
}


# =====================================================
# STUDENT DETAILS SCREEN
# =====================================================

def show_student_details(
    page: ft.Page,
    on_back=None,
    on_submit=None,
    id_number=None,
    on_home=None
):

    page.controls.clear()
    page.bgcolor = BG
    page.padding = 0

    fields = {}

    status_text = ft.Text(
        "",
        size=13,
        color=ERROR,
        text_align=ft.TextAlign.CENTER,
    )

    # =================================================
    # MESSAGE FUNCTION
    # =================================================

    def show_message(message, is_error=True):

        status_text.value = message
        status_text.color = ERROR if is_error else SUCCESS

        page.update()

    # =================================================
    # TEXT FIELD FUNCTION
    # =================================================

    def make_field(
        label,
        hint,
        key,
        keyboard_type=None
    ):

        field = ft.TextField(
            hint_text=hint,
            text_size=15,
            color=INK,
            keyboard_type=keyboard_type,
            border=ft.InputBorder.NONE,
            bgcolor="#FFFFFF",
            content_padding=ft.Padding(
                left=15,
                top=12,
                right=12,
                bottom=12
            ),
            expand=True,
        )

        container = ft.Container(
            content=field,
            border=ft.Border.all(1, "#E0E0E0"),
            border_radius=22,
            bgcolor="#FFFFFF",
            height=52,
            padding=0,
        )

        control = ft.Column(
            controls=[
                ft.Text(
                    label,
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=LABEL,
                ),
                container,
            ],
            spacing=1,
        )

        fields[key] = field

        return control

    # =================================================
    # DROPDOWN BORDER
    # =================================================

    dropdown_border = ft.OutlineInputBorder(
        border_radius=22,
        side=ft.BorderSide(
            color="#E0E0E0",
            width=1
        )
    )

    # =================================================
    # MAJOR DROPDOWN
    # =================================================

    major_dropdown = ft.Dropdown(
        width=float("inf"),
        height=52,
        hint_text="Select your major",

        options=[
            ft.DropdownOption(
                key="N/A",
                text="Not Applicable"
            )
        ],

        value="N/A",
        disabled=True,

        border=dropdown_border,
        filled=True,
        fill_color="#FFFFFF",

        content_padding=ft.Padding(
            left=15,
            top=10,
            right=12,
            bottom=10
        ),

        text_size=14,
    )

    # =================================================
    # COURSE DROPDOWN
    # =================================================

    def course_changed(e):

        selected_course = course_dropdown.value

        selected_majors = MAJOR_OPTIONS.get(
            selected_course,
            []
        )

        major_dropdown.value = None

        if selected_majors:

            major_dropdown.options = [
                ft.DropdownOption(
                    key=major,
                    text=major
                )
                for major in selected_majors
            ]

            major_dropdown.disabled = False

        else:

            major_dropdown.options = [
                ft.DropdownOption(
                    key="N/A",
                    text="Not Applicable"
                )
            ]

            major_dropdown.value = "N/A"
            major_dropdown.disabled = True

        page.update()

    course_dropdown = ft.Dropdown(
        width=float("inf"),
        height=52,
        hint_text="Select your course",

        options=[
            ft.DropdownOption(
                key=course,
                text=course
            )
            for course in COURSE_OPTIONS
        ],

        border=dropdown_border,
        filled=True,
        fill_color="#FFFFFF",

        content_padding=ft.Padding(
            left=15,
            top=10,
            right=12,
            bottom=10
        ),

        text_size=14,
        on_select=course_changed,
    )

    # =================================================
    # COURSE AND MAJOR SECTIONS
    # =================================================

    course_section = ft.Column(
        controls=[
            ft.Text(
                "Course",
                size=13,
                weight=ft.FontWeight.BOLD,
                color=LABEL,
            ),
            course_dropdown,
        ],
        spacing=4,
    )

    major_section = ft.Column(
        controls=[
            ft.Text(
                "Major",
                size=13,
                weight=ft.FontWeight.BOLD,
                color=LABEL,
            ),
            major_dropdown,
        ],
        spacing=4,
    )

    # =================================================
    # STUDENT INFORMATION FIELDS
    # =================================================

    form_fields = [

        make_field(
            "First Name",
            "Enter first name",
            "first_name"
        ),

        make_field(
            "Middle Name",
            "Enter middle name",
            "middle_name"
        ),

        make_field(
            "Last Name",
            "Enter last name",
            "last_name"
        ),

        make_field(
            "Address",
            "Enter address",
            "address"
        ),

        make_field(
            "Birthdate",
            "YYYY-MM-DD",
            "birthdate"
        ),

        make_field(
            "Contact Number",
            "Enter contact number",
            "contact_number",
            ft.KeyboardType.PHONE
        ),

        course_section,

        major_section,

        make_field(
            "Emergency Contact Name",
            "Enter emergency contact name",
            "emergency_name"
        ),

        make_field(
            "Emergency Contact Number",
            "Enter emergency contact number",
            "emergency_number",
            ft.KeyboardType.PHONE
        ),

    ]

    # =================================================
    # COLLECT AND VALIDATE STUDENT INFORMATION
    # =================================================

    def collect_student_data():

        required_fields = {
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "last_name": "Last Name",
            "address": "Address",
            "birthdate": "Birthdate",
            "contact_number": "Contact Number",
            "emergency_name": "Emergency Contact Name",
            "emergency_number": "Emergency Contact Number",
        }

        missing = []

        # Check text fields.
        for key, label in required_fields.items():

            value = fields[key].value or ""

            if not value.strip():
                missing.append(label)

        # Check course.
        selected_course = course_dropdown.value

        if not selected_course:
            missing.append("Course")

        # Check major.
        selected_major = major_dropdown.value

        available_majors = MAJOR_OPTIONS.get(
            selected_course,
            []
        )

        if available_majors and not selected_major:
            missing.append("Major")

        if missing:
            return None, missing

        # Courses without majors use N/A.
        if not available_majors:
            selected_major = "N/A"

        # Collect information.
        student_data = {
            key: (field.value or "").strip()
            for key, field in fields.items()
        }

        student_data["course"] = selected_course
        student_data["major"] = selected_major

        return student_data, []

    # =================================================
    # SAVE TO DATABASE
    # =================================================

    def save_to_database(student_data):

        if not id_number:
            raise ValueError(
                "Student ID is missing. Please register again."
            )

        if on_submit:

            on_submit(student_data)

        else:

            save_student_details(
                student_data,
                id_number
            )

    # =================================================
    # INCOMPLETE FORM DIALOG
    # =================================================

    def show_incomplete_dialog(missing):

        missing_list = "\n".join(
            f"• {field}"
            for field in missing
        )

        dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Incomplete Student Details",
                weight=ft.FontWeight.BOLD,
            ),

            content=ft.Text(
                "Please fill in all required fields "
                "before returning to the home screen.\n\n"
                f"Missing fields:\n{missing_list}"
            ),

            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: page.pop_dialog(),
                )
            ],

            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dialog)

    # =================================================
    # CONFIRMATION DIALOG
    # =================================================

    def show_confirmation_dialog():

        dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Confirm Student Details",
                weight=ft.FontWeight.BOLD,
            ),

            content=ft.Column(
                controls=[

                    ft.Text(
                        "Are all the details you provided correct?"
                    ),

                    ft.Container(height=8),

                    ft.Text(
                        "Please review your information carefully."
                    ),

                    ft.Container(height=8),

                    ft.Text(
                        "WARNING: Once you confirm, your details "
                        "will be saved and you will return to "
                        "the home screen. Changes cannot be made "
                        "through this registration form after "
                        "confirmation.",
                        color=ERROR,
                        weight=ft.FontWeight.BOLD,
                        size=13,
                    ),

                ],

                tight=True,
                spacing=4,
            ),

            actions=[

                ft.TextButton(
                    "Review Details",
                    on_click=lambda e: page.pop_dialog(),
                ),

                ft.Button(
                    content="Confirm",
                    on_click=confirm_details,
                ),

            ],

            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dialog)

    # =================================================
    # CONFIRM AND RETURN TO HOME
    # =================================================

    def confirm_details(e=None):

        # Ensure Home navigation is connected.
        if not on_home:

            page.pop_dialog()

            show_message(
                "Home navigation is not connected. "
                "Please check register.py."
            )

            return

        # Validate again before saving.
        data, missing = collect_student_data()

        if missing:

            page.pop_dialog()
            show_incomplete_dialog(missing)
            return

        # Save student details.
        try:

            save_to_database(data)

        except (
            sqlite3.Error,
            ValueError,
            OSError
        ) as error:

            page.pop_dialog()

            show_message(
                f"Could not save student details: {error}"
            )

            return

        # Close confirmation dialog.
        page.pop_dialog()

        # Redirect to Home Screen.
        on_home()

    # =================================================
    # BACK TO HOME
    # =================================================

    def go_home(e=None):

        if not id_number:

            show_message(
                "Student ID is missing. Please register again."
            )

            return

        # Validate all fields.
        data, missing = collect_student_data()

        if missing:

            show_incomplete_dialog(missing)
            return

        # All fields are completed.
        show_confirmation_dialog()

    # =================================================
    # SAVE BUTTON
    # =================================================

    def save_details(e=None):

        if not id_number:

            show_message(
                "Student ID is missing. Please register again."
            )

            return

        data, missing = collect_student_data()

        if missing:

            show_message(
                "Please complete all fields: "
                + ", ".join(missing)
            )

            return

        try:

            save_to_database(data)

            show_message(
                "Student details saved successfully!",
                is_error=False
            )

        except (
            sqlite3.Error,
            ValueError,
            OSError
        ) as error:

            show_message(
                f"Could not save student details: {error}"
            )

    # =================================================
    # WATERMARK
    # =================================================

    watermark = ft.Container(
        content=ft.Image(
            src="bctprofilepic-removebg-preview.png",
            width=340,
            height=340,
            fit=ft.BoxFit.CONTAIN,
            opacity=0.18,
        ),

        alignment=ft.Alignment(0, 0),
        expand=True,
    )

    # =================================================
    # HEADER
    # =================================================

    header = school_header()

    # =================================================
    # FORM CONTAINER
    # =================================================

    form = ft.Container(
        content=ft.Column(
            controls=[

                *form_fields,

                ft.Container(height=20),

                status_text,

                ft.Container(height=15),

                # SAVE BUTTON
                ft.Row(
                    controls=[
                        ft.Button(
                            content="SAVE",
                            on_click=save_details,
                            width=150,
                            height=45,
                        )
                    ],

                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # BACK TO HOME BUTTON
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Back to Home",
                            on_click=go_home,
                        )
                    ],

                    alignment=ft.MainAxisAlignment.CENTER,
                ),

            ],

            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),

        padding=ft.Padding(
            left=14,
            top=0,
            right=14,
            bottom=15
        ),

        expand=True,
    )

    # =================================================
    # FORM STACK
    # =================================================

    form_stack = ft.Stack(
        controls=[
            watermark,
            form,
        ],

        expand=True,
    )

    # =================================================
    # MAIN SCREEN
    # =================================================

    screen_width = min(page.width or 390, 390)

    screen = ft.Container(
        width=screen_width,
        bgcolor=BG,

        padding=ft.Padding(
            left=6,
            top=45,
            right=6,
            bottom=0
        ),

        content=ft.Column(
            controls=[
                header,

                ft.Container(height=8),

                form_stack,
            ],

            spacing=0,
            expand=True,
        ),
    )

    # =================================================
    # ADD TO PAGE
    # =================================================

    page.add(
        ft.Row(
            controls=[screen],

            alignment=ft.MainAxisAlignment.CENTER,

            vertical_alignment=ft.CrossAxisAlignment.STRETCH,

            expand=True,
        )
    )

    page.update()
