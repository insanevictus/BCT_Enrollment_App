import flet as ft

from components.header import school_header
from database import (
    get_student_enrolled_subjects,
    normalize_academic_year,
)


BG = "#FFFCFC"
INK = "#171D2A"
LABEL = "#707786"
ERROR = "#B42318"
SUCCESS = "#147D36"


def show_view_subjects(
    page: ft.Page,
    student_id,
    on_back=None,
):

    page.controls.clear()
    page.bgcolor = BG
    page.padding = 0

    status_text = ft.Text(
        "",
        size=13,
        color=ERROR,
        text_align=ft.TextAlign.CENTER,
    )

    subject_list = ft.Column(
        controls=[],
        spacing=8,
    )

    academic_year_field = ft.TextField(
        width=float("inf"),
        hint_text="2026 - 2027",
        border_radius=12,
        border=ft.Border.all(1, "#E0E0E0"),
        bgcolor="#FFFFFF",
    )

    semester_dropdown = ft.Dropdown(
        width=float("inf"),
        value="all",
        options=[
            ft.DropdownOption(key="all", text="All semesters"),
            ft.DropdownOption(key="1", text="1st Semester"),
            ft.DropdownOption(key="2", text="2nd Semester"),
            ft.DropdownOption(key="3", text="Summer"),
        ],
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(color="#E0E0E0", width=1),
        ),
        filled=True,
        fill_color="#FFFFFF",
    )

    semester_labels = {
        1: "1st Semester",
        2: "2nd Semester",
        3: "Summer",
    }

    def display_subjects(subjects):

        subject_list.controls.clear()

        if not subjects:
            subject_list.controls.append(
                ft.Text(
                    "No enrolled subjects were found for the selected filters.",
                    size=13,
                    color=LABEL,
                )
            )
            return

        grouped_subjects = {}

        for subject in subjects:
            academic_year = (
                subject["academic_year"]
                or "Academic year unknown (legacy enrollment)"
            )
            semester_label = semester_labels[subject["semester"]]
            group_key = (academic_year, semester_label)
            grouped_subjects.setdefault(group_key, []).append(subject)

        for (academic_year, semester_label), semester_subjects in (
            grouped_subjects.items()
        ):
            subject_list.controls.append(
                ft.Container(
                    bgcolor="#EAF1FC",
                    border_radius=10,
                    padding=10,
                    content=ft.Text(
                        f"{academic_year}  |  {semester_label}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),
                )
            )

            for subject in semester_subjects:
                result_status = subject["result_status"]
                status_color = (
                    SUCCESS
                    if result_status == "Passed"
                    else ERROR
                    if result_status == "Failed"
                    else LABEL
                )

                subject_list.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        border=ft.Border.all(1, "#E0E0E0"),
                        border_radius=12,
                        padding=12,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    subject["title"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=INK,
                                ),
                                ft.Text(
                                    f"Units: {subject['units']:g}",
                                    size=12,
                                    color=LABEL,
                                ),
                                ft.Text(
                                    f"Status: {result_status}",
                                    size=12,
                                    color=status_color,
                                ),
                            ],
                            spacing=4,
                        ),
                    )
                )

    def load_subjects(e=None):

        academic_year = (academic_year_field.value or "").strip()

        if academic_year:
            try:
                academic_year = normalize_academic_year(academic_year)
            except ValueError as error:
                status_text.value = str(error)
                status_text.color = ERROR
                page.update()
                return

        selected_semester = semester_dropdown.value
        semester = (
            int(selected_semester)
            if selected_semester and selected_semester != "all"
            else None
        )

        status_text.value = ""

        try:
            subjects = get_student_enrolled_subjects(
                student_id,
                academic_year,
                semester,
            )
        except Exception as error:
            print(f"Subject history error: {error}")
            status_text.value = f"Could not load enrolled subjects: {error}"
            status_text.color = ERROR
            page.update()
            return

        display_subjects(subjects)

        page.update()

    def go_back(e=None):

        if on_back:
            on_back()

    screen_width = min(
        page.width or 390,
        390,
    )

    screen = ft.Container(
        width=screen_width,
        bgcolor=BG,
        padding=ft.Padding(
            left=12,
            top=35,
            right=12,
            bottom=15,
        ),
        content=ft.Column(
            controls=[
                school_header(),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Back to Menu",
                            on_click=go_back,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Text(
                    "VIEW SUBJECTS",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Academic Year",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=LABEL,
                ),
                academic_year_field,
                ft.Text(
                    "Semester",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=LABEL,
                ),
                semester_dropdown,
                ft.Button(
                    content="View Subjects",
                    on_click=load_subjects,
                ),
                status_text,
                ft.Divider(),
                subject_list,
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

    page.add(
        ft.Row(
            controls=[screen],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
    )

    load_subjects()
    page.update()