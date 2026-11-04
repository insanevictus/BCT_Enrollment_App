
import flet as ft

from components.header import school_header

from database import (
    get_student_profile,
    get_student_subject_status,
    normalize_academic_year,
    save_student_enrollment,
)

from data.subject_catalog import (
    get_program_key,
    get_available_year_levels,
    get_available_schedules,
    get_subjects,
    calculate_total_units,
    count_lab_subjects,
    count_hands_on_subjects,
)


BG = "#FFFCFC"
INK = "#171D2A"
LABEL = "#707786"
BLUE = "#5792E8"
ERROR = "#B42318"
SUCCESS = "#147D36"
WARNING = "#B7791F"


def show_enroll_subjects(
    page: ft.Page,
    student_id,
    on_back=None,
    on_continue=None,
):

    page.controls.clear()
    page.bgcolor = BG
    page.padding = 0

    # =================================================
    # GET STUDENT PROFILE
    # =================================================

    try:
        profile = get_student_profile(student_id)

    except Exception as error:
        print(f"Profile error: {error}")
        profile = None

    # =================================================
    # CHECK STUDENT PROFILE
    # =================================================

    if not profile:

        page.add(
            ft.Column(
                controls=[
                    ft.Text(
                        "Student details not found.",
                        color=ERROR,
                        size=18,
                    ),

                    ft.Text(
                        "Please complete your student details first."
                    ),

                    ft.TextButton(
                        "Back to Menu",
                        on_click=lambda e: on_back() if on_back else None,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        page.update()
        return

    program_key = get_program_key(
        profile["course"],
        profile["major"]
    )

    # =================================================
    # CHECK AVAILABLE CURRICULUM
    # =================================================

    if not program_key:

        page.add(
            ft.Column(
                controls=[
                    ft.Text(
                        "Curriculum unavailable.",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ERROR,
                    ),

                    ft.Text(
                        f"Course: {profile['course']}"
                    ),

                    ft.Text(
                        f"Major: {profile['major']}"
                    ),

                    ft.Text(
                        "There is currently no subject catalog "
                        "configured for this program."
                    ),

                    ft.TextButton(
                        "Back to Menu",
                        on_click=lambda e: on_back() if on_back else None,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        page.update()
        return

    # =================================================
    # GET PREVIOUS SUBJECT RESULTS
    # =================================================

    try:

        previous_subject_status = get_student_subject_status(
            student_id
        )

    except Exception as error:

        print(f"Subject status error: {error}")

        previous_subject_status = {}

    # =================================================
    # SELECTED SUBJECTS
    # =================================================

    selected_subjects = {}

    enrollment_saved = False

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
    # DISPLAY STUDENT INFORMATION
    # =================================================

    student_card = ft.Container(
        bgcolor="#FFFFFF",

        border=ft.Border.all(1, "#E0E0E0"),

        border_radius=15,

        padding=15,

        content=ft.Column(
            controls=[

                ft.Text(
                    profile["full_name"],
                    size=19,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Text(
                    f"Student ID: {student_id}",
                    size=13,
                    color=LABEL,
                ),

                ft.Text(
                    f"Course: {profile['course']}",
                    size=12,
                    color=LABEL,
                ),

                ft.Text(
                    f"Major: {profile['major'] or 'N/A'}",
                    size=12,
                    color=LABEL,
                ),

            ],
            spacing=5,
        ),
    )

    # =================================================
    # DROPDOWN BORDER
    # =================================================

    dropdown_border = ft.OutlineInputBorder(
        border_radius=12,
        side=ft.BorderSide(
            color="#E0E0E0",
            width=1
        )
    )

    # =================================================
    # SEMESTER DROPDOWN
    # =================================================

    semester_dropdown = ft.Dropdown(
        width=float("inf"),

        hint_text="Select semester",

        options=[
            ft.DropdownOption(
                key="1",
                text="1st Semester"
            ),

            ft.DropdownOption(
                key="2",
                text="2nd Semester"
            ),

            ft.DropdownOption(
                key="3",
                text="Summer"
            ),
        ],

        border=dropdown_border,
        filled=True,
        fill_color="#FFFFFF",

        on_select=lambda e: update_filters(),
    )

    # =================================================
    # SCHEDULE DROPDOWN
    # =================================================

    schedule_dropdown = ft.Dropdown(
        width=float("inf"),

        hint_text="Select schedule",

        options=[],

        disabled=True,

        border=dropdown_border,
        filled=True,
        fill_color="#FFFFFF",

        on_select=lambda e: change_schedule(),
    )

    schedule_note = ft.Text(
        "",
        size=11,
        color=LABEL,
    )

    # =================================================
    # SUBJECT LIST
    # =================================================

    subject_list = ft.Column(
        controls=[],
        spacing=8,
    )

    # =================================================
    # ENROLLMENT SUMMARY
    # =================================================

    total_units_text = ft.Text(
        "0",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=SUCCESS,
    )

    lab_count_text = ft.Text(
        "0",
        size=16,
        color=INK,
    )

    hands_on_count_text = ft.Text(
        "0",
        size=16,
        color=INK,
    )

    # =================================================
    # AVAILABLE CURRICULUM YEARS
    # =================================================

    profile_course = (
        str(profile.get("course") or "").strip().casefold()
    )

    max_year_level = (
        2
        if profile_course
        == "associate in computer technology (2 years)"
        else 4
    )

    available_years = [
        year
        for year in get_available_year_levels(program_key)
        if year <= max_year_level
    ]

    # =================================================
    # GET CURRICULUM SEMESTER
    # =================================================

    def get_curriculum_semester(year, semester):

        return (
            (year - 1) * 2
            + semester
        )

    # =================================================
    # NORMALIZE SUBJECT TITLE
    # =================================================

    def normalize_subject_title(title):

        return " ".join(
            str(title).strip().casefold().split()
        )

    # =================================================
    # GET SUBJECT STATUS ACROSS ALL SCHEDULES
    # =================================================
    #
    # Old subject IDs include schedule and row index.
    # Instead of checking only the current subject ID,
    # find the matching subject in every schedule.
    #
    # Identity:
    # Program + curriculum year + semester + title
    #
    # Status priority:
    # Passed > Enrolled > Failed
    #
    # =================================================

    def get_subject_status(subject):

        subject_year = int(subject["year_level"])

        subject_semester = int(subject["semester"])

        subject_title = normalize_subject_title(
            subject["title"]
        )

        matching_statuses = []

        schedules = get_available_schedules(
            program_key,
            subject_year,
            subject_semester
        )

        # Include the unscheduled version when applicable.
        schedules_to_check = list(schedules)

        if not schedules_to_check:
            schedules_to_check = [None]

        for schedule in schedules_to_check:

            try:

                catalog_subjects = get_subjects(
                    program_key,
                    subject_year,
                    subject_semester,
                    schedule
                )

            except Exception as error:

                print(
                    f"Could not check schedule {schedule}: {error}"
                )

                continue

            for catalog_subject in catalog_subjects:

                if normalize_subject_title(
                    catalog_subject["title"]
                ) != subject_title:

                    continue

                old_subject_id = catalog_subject["subject_id"]

                result_status = previous_subject_status.get(
                    old_subject_id
                )

                if result_status:
                    matching_statuses.append(result_status)

        # Also check the current ID directly.
        current_status = previous_subject_status.get(
            subject["subject_id"]
        )

        if current_status:
            matching_statuses.append(current_status)

        if "Passed" in matching_statuses:
            return "Passed"

        if "Enrolled" in matching_statuses:
            return "Enrolled"

        if "Failed" in matching_statuses:
            return "Failed"

        return None

    # =================================================
    # UPDATE SUMMARY
    # =================================================

    def update_summary():

        subjects = list(
            selected_subjects.values()
        )

        total_units = calculate_total_units(
            subjects
        )

        total_labs = count_lab_subjects(
            subjects
        )

        total_hands_on = count_hands_on_subjects(
            subjects
        )

        total_units_text.value = f"{total_units:g}"

        lab_count_text.value = str(total_labs)

        hands_on_count_text.value = str(total_hands_on)

        page.update()

    # =================================================
    # SUBJECT CHECKBOX FUNCTION
    # =================================================

    def subject_changed(e, subject):

        subject_id = subject["subject_id"]

        if e.control.value:

            # Recheck status before accepting selection.
            # This prevents selecting a subject that is
            # already passed or currently enrolled.
            result_status = get_subject_status(subject)

            if result_status in ("Passed", "Enrolled"):

                e.control.value = False

                show_message(
                    "This subject is already passed or enrolled."
                )

                page.update()
                return

            new_selection = dict(selected_subjects)

            new_selection[subject_id] = subject

            new_total = calculate_total_units(
                list(new_selection.values())
            )

            if new_total > 25:

                e.control.value = False

                show_message(
                    "You cannot enroll in more than 25 units."
                )

                page.update()
                return

            selected_subjects[subject_id] = subject

        else:

            selected_subjects.pop(
                subject_id,
                None
            )

        show_message(
            "",
            is_error=False
        )

        update_summary()

    # =================================================
    # GET AVAILABLE SCHEDULES FOR ALL YEARS
    # =================================================

    def get_all_available_schedules(semester):

        available = set()

        for year in available_years:

            curriculum_semester = get_curriculum_semester(
                year,
                semester
            )

            schedules = get_available_schedules(
                program_key,
                year,
                curriculum_semester
            )

            available.update(schedules)

        return sorted(available)

    # =================================================
    # CREATE SUBJECT CARD
    # =================================================

    def create_subject_card(subject):

        subject_id = subject["subject_id"]

        result_status = get_subject_status(subject)

        is_passed = result_status == "Passed"

        is_enrolled = result_status == "Enrolled"

        is_failed = result_status == "Failed"

        is_disabled = is_passed or is_enrolled

        if is_passed:

            status_label = "ALREADY TAKEN"

            status_color = SUCCESS

        elif is_enrolled:

            status_label = "ALREADY ENROLLED"

            status_color = WARNING

        elif is_failed:

            status_label = "FAILED - RETAKE AVAILABLE"

            status_color = ERROR

        else:

            status_label = "AVAILABLE"

            status_color = BLUE

        checkbox = ft.Checkbox(
            label=subject["title"],

            value=subject_id in selected_subjects,

            disabled=is_disabled,

            on_change=lambda e, s=subject: (
                subject_changed(e, s)
            ),
        )

        if subject["days"] or subject["room"]:
            details = (
                f"Time: {subject['time']}  |  "
                f"Days: {subject['days']}\n"
                f"Room: {subject['room']}  |  "
                f"Units: {subject['units']:g}"
            )
        else:
            details = (
                f"Duration: {subject['time']}\n"
                f"No fixed days or room  |  "
                f"Units: {subject['units']:g}"
            )

        tags = []

        if subject["is_lab"]:
            tags.append("LAB")

        if subject["is_hands_on"]:
            tags.append("HANDS-ON")

        tag_text = (
            "  •  ".join(tags)
            if tags
            else "Regular Subject"
        )

        return ft.Container(

            bgcolor="#F5F5F5" if is_disabled else "#FFFFFF",

            border=ft.Border.all(
                1,
                "#E0E0E0"
            ),

            border_radius=12,

            padding=10,

            content=ft.Column(
                controls=[

                    checkbox,

                    ft.Text(
                        details,
                        size=11,
                        color=LABEL,
                    ),

                    ft.Text(
                        tag_text,
                        size=10,
                        color=SUCCESS if tags else LABEL,
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Text(
                        status_label,
                        size=10,
                        color=status_color,
                        weight=ft.FontWeight.BOLD,
                    ),

                ],
                spacing=3,
            ),
        )

    # =================================================
    # REFRESH SUBJECT LIST
    # =================================================

    def refresh_subjects():

        subject_list.controls.clear()

        if not semester_dropdown.value:

            subject_list.controls.append(
                ft.Text(
                    "Select a semester to display "
                    "available subjects.",
                    color=LABEL,
                )
            )

            update_summary()
            page.update()
            return

        selected_semester = int(
            semester_dropdown.value
        )

        selected_schedule = (
            int(schedule_dropdown.value)
            if schedule_dropdown.value
            else None
        )

        total_subjects_found = 0

        # ---------------------------------------------
        # DISPLAY SUBJECTS GROUPED BY CURRICULUM YEAR
        # ---------------------------------------------

        for year in available_years:

            curriculum_semester = get_curriculum_semester(
                year,
                selected_semester
            )

            available_schedules = get_available_schedules(
                program_key,
                year,
                curriculum_semester
            )

            # Apply the selected schedule only to years
            # that actually have separate schedules.
            if available_schedules:

                if selected_schedule is None:
                    continue

                if selected_schedule not in available_schedules:
                    continue

                year_schedule = selected_schedule

            else:

                year_schedule = None

            subjects = get_subjects(
                program_key,
                year,
                curriculum_semester,
                year_schedule
            )

            if not subjects:
                continue

            total_subjects_found += len(subjects)

            # -----------------------------------------
            # YEAR HEADING
            # -----------------------------------------

            year_heading = ft.Container(
                bgcolor="#EAF1FC",

                border_radius=10,

                padding=12,

                content=ft.Text(
                    f"{year}{'st' if year == 1 else 'nd' if year == 2 else 'rd' if year == 3 else 'th'} YEAR",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=BLUE,
                ),
            )

            subject_list.controls.append(
                year_heading
            )

            # -----------------------------------------
            # SUBJECT CARDS
            # -----------------------------------------

            for subject in subjects:

                subject_list.controls.append(
                    create_subject_card(subject)
                )

        # ---------------------------------------------
        # NO SUBJECTS
        # ---------------------------------------------

        if total_subjects_found == 0:

            subject_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No subjects are currently available "
                        "for the selected semester and schedule.",
                        color=LABEL,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=20,
                )
            )

        update_summary()
        page.update()

    # =================================================
    # CHANGE SCHEDULE
    # =================================================

    def change_schedule():

        # Clear selections because the displayed class
        # schedule has changed.
        selected_subjects.clear()

        show_message(
            "",
            is_error=False
        )

        update_summary()

        refresh_subjects()

    # =================================================
    # UPDATE FILTERS
    # =================================================

    def update_filters():

        selected_subjects.clear()

        update_summary()

        if not semester_dropdown.value:

            schedule_dropdown.options = []
            schedule_dropdown.value = None
            schedule_dropdown.disabled = True

            schedule_note.value = ""

            refresh_subjects()
            return

        semester = int(
            semester_dropdown.value
        )

        available_schedules = get_all_available_schedules(
            semester
        )

        schedule_dropdown.value = None

        if available_schedules:

            schedule_dropdown.options = [

                ft.DropdownOption(
                    key=str(schedule),

                    text=(
                        "1st Schedule"
                        if schedule == 1
                        else "2nd Schedule"
                    )
                )

                for schedule in available_schedules

            ]

            schedule_dropdown.disabled = False

            schedule_note.value = (
                "Choose a schedule. Years without separate "
                "schedules will still display their subjects."
            )

        else:

            schedule_dropdown.options = []
            schedule_dropdown.disabled = True

            schedule_note.value = (
                "No separate schedule selection is required."
            )

        page.update()

        refresh_subjects()

    # =================================================
    # CONTINUE TO ASSESSMENT
    # =================================================

    def continue_to_assessment(e=None):

        nonlocal enrollment_saved

        if enrollment_saved:

            show_message(
                "This enrollment has already been saved."
            )
            return

        try:
            academic_year = normalize_academic_year(
                academic_year_field.value
            )
        except ValueError as error:
            show_message(str(error))
            return

        if not semester_dropdown.value:

            show_message(
                "Please select your semester."
            )
            return

        semester = int(
            semester_dropdown.value
        )

        available_schedules = get_all_available_schedules(
            semester
        )

        if available_schedules and not schedule_dropdown.value:

            show_message(
                "Please select your schedule."
            )
            return

        selected = list(
            selected_subjects.values()
        )

        if not selected:

            show_message(
                "Please select at least one subject."
            )
            return

        # ---------------------------------------------
        # RECHECK SUBJECT STATUS BEFORE SAVING
        # ---------------------------------------------

        for subject in selected:

            result_status = get_subject_status(subject)

            if result_status in ("Passed", "Enrolled"):

                show_message(
                    f"{subject['title']} is already passed "
                    "or currently enrolled."
                )

                return

        total_units = calculate_total_units(
            selected
        )

        if total_units < 1 or total_units > 25:

            show_message(
                "Enrollment must be between 1 and 25 units."
            )
            return

        # ---------------------------------------------
        # DETERMINE ENROLLMENT YEAR
        # ---------------------------------------------

        selected_years = sorted({
            subject["year_level"]
            for subject in selected
        })

        enrollment_year = selected_years[0]

        curriculum_semester = get_curriculum_semester(
            enrollment_year,
            semester
        )

        schedule = (
            int(schedule_dropdown.value)
            if schedule_dropdown.value
            else None
        )

        # ---------------------------------------------
        # SAVE ENROLLMENT
        # ---------------------------------------------

        try:

            enrollment_id = save_student_enrollment(
                id_number=student_id,
                program_key=program_key,
                year_level=enrollment_year,
                semester=semester,
                academic_year=academic_year,
                curriculum_semester=curriculum_semester,
                schedule=schedule,
                selected_subjects=selected,
            )

        except Exception as error:

            print(f"Enrollment error: {error}")

            show_message(
                f"Could not save enrollment: {error}"
            )

            return

        enrollment_saved = True

        continue_button.disabled = True

        show_message(
            f"Enrollment saved successfully! "
            f"Enrollment ID: {enrollment_id}",
            is_error=False,
        )

        if on_continue:

            on_continue(enrollment_id)

        else:

            dialog = ft.AlertDialog(
                modal=True,

                title=ft.Text(
                    "Enrollment Saved",
                    weight=ft.FontWeight.BOLD,
                ),

                content=ft.Text(
                    "Your selected subjects have been saved "
                    "successfully.\n\n"
                    f"Total Units: {total_units:g}\n"
                    f"Laboratory Subjects: "
                    f"{count_lab_subjects(selected)}\n"
                    f"Hands-on Subjects: "
                    f"{count_hands_on_subjects(selected)}"
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
    # CONTINUE BUTTON
    # =================================================

    continue_button = ft.Button(
        content="CONTINUE TO ASSESSMENT",
        width=260,
        height=48,
        on_click=continue_to_assessment,
    )

    academic_year_field = ft.TextField(
        width=float("inf"),
        hint_text="Example: 2026 - 2027",
        border_radius=12,
        border=ft.Border.all(1, "#E0E0E0"),
        bgcolor="#FFFFFF",
    )

    # =================================================
    # BACK TO MENU
    # =================================================

    def go_back(e=None):

        if on_back:
            on_back()

    # =================================================
    # MAIN SCREEN
    # =================================================

    screen_width = min(
        page.width or 390,
        390
    )

    screen = ft.Container(
        width=screen_width,

        bgcolor=BG,

        padding=ft.Padding(
            left=12,
            top=35,
            right=12,
            bottom=15
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
                    "ENROLL SUBJECTS",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                    text_align=ft.TextAlign.CENTER,
                ),

                student_card,

                ft.Container(height=10),

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

                ft.Text(
                    "Schedule",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=LABEL,
                ),

                schedule_dropdown,

                schedule_note,

                ft.Divider(),

                ft.Text(
                    "AVAILABLE SUBJECTS",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Text(
                    "Subjects are grouped by curriculum year. "
                    "You may select subjects from different years.",
                    size=11,
                    color=LABEL,
                ),

                subject_list,

                ft.Divider(),

                ft.Text(
                    "ENROLLMENT SUMMARY",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Row(
                    controls=[
                        ft.Text(
                            "Total Units:",
                            color=LABEL,
                        ),
                        total_units_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                ft.Row(
                    controls=[
                        ft.Text(
                            "Laboratory Subjects:",
                            color=LABEL,
                        ),
                        lab_count_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                ft.Row(
                    controls=[
                        ft.Text(
                            "Hands-on Subjects:",
                            color=LABEL,
                        ),
                        hands_on_count_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                status_text,

                ft.Container(height=10),

                ft.Row(
                    controls=[
                        continue_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

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

    page.update()

    # =================================================
    # INITIAL SUBJECT LIST
    # =================================================

    refresh_subjects()
