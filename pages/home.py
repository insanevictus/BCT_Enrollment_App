from collections.abc import Callable

import flet as ft

from components.buttons import action_button
from components.header import school_header


BG = "#FFFCFC"
INK = "#211D1D"
DARK_BROWN = "#795F5F"
LIGHT_PINK = "#EAD0D0"

SENIOR_HIGH_COURSES = [
    (
        "Academic Track: STEM",
        "Focuses on developing skills in scientific inquiry, "
        "problem-solving, and critical thinking in preparation "
        "for future careers in fields like engineering, medicine, "
        "technology, and mathematics.",
    ),
    (
        "Academic Track: HUMSS",
        "It concentrates on Social Sciences (HUMSS) and is designed "
        "to develop students' understanding of human behavior, "
        "culture, society, and people. Students explore communication, "
        "politics, psychology, and other related subjects.",
    ),
    (
        "TVL Track: Electrical Installation and Maintenance",
        "A practical and skills-based program that prepares students "
        "for electrical installation, maintenance, safety procedures, "
        "and troubleshooting.",
    ),
    (
        "TVL Track: Electronic Products Assembly and Servicing",
        "Focuses on assembling and maintaining electronic products "
        "and equipment. Students learn to inspect, test, repair, and "
        "troubleshoot electronic devices.",
    ),
    (
        "TVL Track: ICT - Computer Programming",
        "A specialized program designed to introduce students to "
        "programming concepts, coding, and software development. "
        "Students practice creating programs and solving problems "
        "using computer languages.",
    ),
    (
        "TVL Track: ICT - Computer Systems Servicing",
        "A technical program that equips students with skills in "
        "computer hardware, software installation, networking, "
        "maintenance, and troubleshooting.",
    ),
]

COLLEGE_COURSES = [
    (
        "Associate in Computer Technology (2 years)",
        "An Associate in Computer Technology (ACT) program prepares "
        "students for entry-level IT roles, including computer support "
        "and programming fundamentals.",
    ),
    (
        "Associate in Electronics Technology (2 years)",
        "A program that introduces students to electronics, basic "
        "circuitry, electronic devices, and practical skills in "
        "troubleshooting and repair.",
    ),
    (
        "Associate in Electrical Technology (2 years)",
        "An Associate in Electrical Technology is a two-year program "
        "that provides students with the skills and knowledge required "
        "for electrical installation, focusing on safety, circuits, "
        "and equipment.",
    ),
    (
        "Bachelor of Science in Information Technology (BSIT)",
        "Develop expertise in software development, networking, "
        "database systems, and information management.",
    ),
    (
        "Bachelor of Science in Industrial Technology - Major in Electricity",
        "Technical education focused on electrical industrial "
        "applications, maintenance, and troubleshooting.",
    ),
    (
        "Bachelor of Science in Industrial Technology - Major in Electronics",
        "A program covering the fundamentals of electronics, "
        "electronic devices, and electronic systems.",
    ),
    (
        "Bachelor of Science in Industrial Technology - Major in "
        "Electrical Engineering",
        "A course focused on electrical concepts and processes in "
        "manufacturing and industrial applications.",
    ),
    (
        "Bachelor of Science in Computer Engineering",
        "Computer Engineering combines electrical engineering and "
        "computer science to develop computer hardware and software "
        "systems.",
    ),
    (
        "Bachelor of Science in Industrial Education - Major in Computer",
        "This program prepares students to teach computer-related "
        "subjects in technical and vocational educational settings.",
    ),
    (
        "Bachelor of Science in Industrial Education - Major in Electronics",
        "Focuses on applying electronics knowledge in educational and "
        "technical settings.",
    ),
    (
        "Bachelor of Science in Industrial Education - Major in Electricity",
        "Prepares students for the field of electrical systems "
        "installation, safety, and technical training.",
    ),
]


def _course_card(title: str, description: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        title,
                        size=12,
                        color="#FFFFFF",
                        text_align=ft.TextAlign.CENTER,
                        font_family="Georgia",
                    ),
                    bgcolor=DARK_BROWN,
                    padding=ft.Padding(left=6, top=6, right=6, bottom=6),
                    alignment=ft.Alignment(0, 0),
                    width=float("inf"),
                ),
                ft.Container(
                    content=ft.Text(
                        description,
                        size=10,
                        color=INK,
                        font_family="Georgia",
                    ),
                    bgcolor=LIGHT_PINK,
                    padding=10,
                    width=float("inf"),
                ),
            ],
            spacing=0,
        ),
        margin=ft.Margin(bottom=10),
    )


def _section_heading(title: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            title,
            size=17,
            weight=ft.FontWeight.BOLD,
            color=INK,
            text_align=ft.TextAlign.CENTER,
            font_family="Georgia",
        ),
        bgcolor="#DCC8C8",
        border_radius=25,
        padding=ft.Padding(left=12, top=3, right=12, bottom=3),
        margin=ft.Margin(bottom=10, top=5),
        alignment=ft.Alignment(0, 0),
    )


def show_home(page: ft.Page, on_login: Callable[..., object], on_register: Callable[..., object],):
    async def scroll_to_section(section_key: str):
        await content.scroll_to(
            scroll_key=section_key,
            duration=800,
            curve=ft.AnimationCurve.EASE_IN_OUT,
        )

    async def scroll_to_senior_high(e):
        await scroll_to_section("senior_high")

    async def scroll_to_college(e):
        await scroll_to_section("college")

    navigation = ft.Column(
        controls=[
            ft.TextButton("Senior High", on_click=scroll_to_senior_high),
            ft.TextButton("College", on_click=scroll_to_college),
            ft.TextButton("Short Term", disabled=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    content = ft.Column(
        controls=[
            school_header(),
            ft.Container(height=40),
            ft.Container(
                content=ft.Text(
                    "Baguio College \nof Technology\nEnrollment System",
                    size=25,
                    color="#171313",
                    text_align=ft.TextAlign.CENTER,
                    font_family="Georgia",
                ),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding(left=0, top=3, right=0, bottom=3),
            ),
            ft.Container(height=40),
            ft.Row(
                controls=[
                    action_button(
                        "LOG IN",
                        on_login,
                        radius=12,
                        outlined=False,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=30),
            ft.Row(
                controls=[
                    action_button(
                        "Create an account",
                        on_register,
                        radius=12,
                        outlined=False,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=30),
            ft.Divider(color="#A9A1A1", thickness=2),
            ft.Container(height=30),
            ft.Container(
                content=ft.Text(
                    "Courses Offered",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                    font_family="Georgia",
                    text_align=ft.TextAlign.CENTER,
                ),
                width=float("inf"),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(
                navigation,
                width=float("inf"),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(height=30),
            ft.Divider(color="#A9A1A1", thickness=2),
            ft.Container(height=30),
            ft.Container(
                key="senior_high",
                content=_section_heading("Senior High"),
            ),
            ft.Container(height=30),
            *[
                _course_card(title, description)
                for title, description in SENIOR_HIGH_COURSES
            ],
            ft.Container(height=30),
            ft.Divider(color="#A9A1A1", thickness=2),
            ft.Container(height=30),
            ft.Container(
                key="college",
                content=_section_heading("College"),
            ),
            ft.Container(height=30),
            *[
                _course_card(title, description)
                for title, description in COLLEGE_COURSES
            ],
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )

    homepage = ft.Container(
        width=360,
        bgcolor=BG,
        padding=10,
        content=content,
    )

    page.controls.clear()
    page.add(
        ft.Row(
            controls=[homepage],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
    )
    page.update()