
import sqlite3

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import flet as ft

from components.header import school_header

from database import (
    get_student_profile,
    get_enrollment_details,
    get_latest_assessment,
    record_simulated_down_payment,
    record_simulated_installment_payment,
    save_student_assessment,
)

from fee_settings import (
    TUITION_FEE_PER_UNIT,
    MISCELLANEOUS_FEE,
    LABORATORY_FEE_PER_SUBJECT,
    HANDS_ON_FEE_PER_SUBJECT,
    MINIMUM_DOWN_PAYMENT,
    PAYMENT_SCHEDULE,
)


BG = "#FFFCFC"
INK = "#171D2A"
LABEL = "#707786"
BLUE = "#5792E8"
ERROR = "#B42318"
SUCCESS = "#147D36"

CENT = Decimal("0.01")


# =====================================================
# MONEY HELPERS
# =====================================================

def money(value):
    return Decimal(str(value)).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


def format_currency(value):
    return f"₱{money(value):,.2f}"


def is_assessment_paid(assessment):
    return money(assessment["remaining_balance"]) <= Decimal("0.00")


# =====================================================
# CALCULATE INITIAL ASSESSMENT
# =====================================================

def calculate_assessment(enrollment, down_payment):

    units = Decimal(str(enrollment["total_units"]))
    lab_count = int(enrollment["lab_count"])
    hands_on_count = int(enrollment["hands_on_count"])

    tuition = money(
        units * Decimal(str(TUITION_FEE_PER_UNIT))
    )

    miscellaneous = money(MISCELLANEOUS_FEE)

    laboratory = money(
        lab_count * Decimal(str(LABORATORY_FEE_PER_SUBJECT))
    )

    hands_on = money(
        hands_on_count * Decimal(str(HANDS_ON_FEE_PER_SUBJECT))
    )

    total = money(
        tuition
        + miscellaneous
        + laboratory
        + hands_on
    )

    down_payment = money(down_payment)

    return {
        "tuition_fee": float(tuition),
        "miscellaneous_fee": float(miscellaneous),
        "laboratory_fee": float(laboratory),
        "hands_on_fee": float(hands_on),
        "total_assessment": float(total),
        "down_payment": float(down_payment),
        "down_payment_paid": 0.0,
        "remaining_balance": float(total),
    }


# =====================================================
# CALCULATE INSTALLMENTS
# =====================================================

def calculate_installments(remaining_balance):

    remaining = money(remaining_balance)

    total_percentage = sum(
        Decimal(str(value))
        for value in PAYMENT_SCHEDULE.values()
    )

    if total_percentage != Decimal("1.0"):
        raise ValueError(
            "Payment schedule percentages must total 100%."
        )

    installments = []
    allocated = Decimal("0.00")

    schedule_items = list(PAYMENT_SCHEDULE.items())

    for index, (name, percentage) in enumerate(schedule_items):

        percentage_decimal = Decimal(str(percentage))

        if index == len(schedule_items) - 1:
            amount = money(remaining - allocated)
        else:
            amount = money(
                remaining * percentage_decimal
            )
            allocated += amount

        installments.append({
            "name": name,
            "percentage": float(percentage_decimal),
            "amount": float(amount),
            "amount_paid": 0.0,
        })

    return installments


# =====================================================
# VIEW BALANCE SCREEN
# =====================================================

def show_balance(
    page: ft.Page,
    student_id,
    enrollment_id=None,
    on_back=None,
    on_enroll=None,
    on_transaction_history=None,
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

    student_name = (
        profile["full_name"]
        if profile
        else "Student"
    )

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
    # LOAD ENROLLMENT AND ASSESSMENT
    # =================================================

    enrollment = None
    assessment = None

    try:

        if enrollment_id is not None:

            enrollment = get_enrollment_details(
                enrollment_id,
                student_id
            )

            if enrollment is None:
                raise ValueError(
                    "Enrollment record could not be found."
                )

            assessment = get_latest_assessment(
                student_id,
                enrollment_id
            )

            # Create initial assessment if one does not exist.
            if assessment is None:

                initial_down_payment = money(
                    MINIMUM_DOWN_PAYMENT
                )

                assessment_data = calculate_assessment(
                    enrollment,
                    initial_down_payment
                )

                installments = calculate_installments(
                    money(
                        assessment_data["total_assessment"]
                        - assessment_data["down_payment"]
                    )
                )

                save_student_assessment(
                    enrollment_id,
                    student_id,
                    assessment_data,
                    installments
                )

                assessment = get_latest_assessment(
                    student_id,
                    enrollment_id
                )

        else:

            assessment = get_latest_assessment(student_id)

    except (ValueError, TypeError, OSError, sqlite3.Error) as error:

        print(f"Assessment loading error: {error}")

        show_message(
            f"Unable to load assessment: {error}"
        )

    # =================================================
    # NO ASSESSMENT FOUND
    # =================================================

    if assessment is None:

        screen = ft.Container(
            width=min(page.width or 390, 390),
            bgcolor=BG,
            padding=20,

            content=ft.Column(
                controls=[

                    school_header(),

                    ft.Container(height=30),

                    ft.Text(
                        "VIEW BALANCE",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),

                    ft.Container(height=20),

                    ft.Text(
                        "No assessment found.",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ERROR,
                    ),

                    ft.Text(
                        "Please enroll your subjects first "
                        "before viewing your assessment."
                    ),

                    ft.Container(height=20),

                    ft.Button(
                        content="ENROLL SUBJECTS",
                        width=220,
                        height=45,
                        on_click=(
                            lambda e: on_enroll()
                            if on_enroll else None
                        ),
                    ),

                    ft.TextButton(
                        "Back to Menu",
                        on_click=(
                            lambda e: on_back()
                            if on_back else None
                        ),
                    ),

                    status_text,

                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
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
        return

    # =================================================
    # DOWN PAYMENT FIELD
    # =================================================

    down_payment_field = ft.TextField(
        label="Down Payment Amount",
        value=f"{assessment['down_payment']:.2f}",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix=ft.Text("₱"),
        border_radius=12,
        border=ft.Border.all(1, "#D0D0D0"),
        bgcolor="#FFFFFF",
        text_size=15,
    )

    # =================================================
    # DISPLAY CONTAINERS
    # =================================================

    fee_breakdown = ft.Column(
        controls=[],
        spacing=12,
    )

    payment_breakdown = ft.Column(
        controls=[],
        spacing=12,
    )

    installment_balance_display = ft.Column(
        controls=[],
        spacing=0,
    )

    payment_action = ft.Column(
        controls=[],
        spacing=10,
    )

    payment_amount_field = ft.TextField(
        label="Payment Amount",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix=ft.Text("₱"),
        border_radius=12,
        border=ft.Border.all(1, "#D0D0D0"),
        bgcolor="#FFFFFF",
        text_size=15,
    )

    # =================================================
    # DISPLAY ROW HELPER
    # =================================================

    def display_row(label, value, bold=False):

        return ft.Row(
            controls=[

                ft.Text(
                    label,
                    size=13,
                    color=INK,
                    weight=(
                        ft.FontWeight.BOLD
                        if bold
                        else ft.FontWeight.NORMAL
                    ),
                    expand=True,
                ),

                ft.Text(
                    format_currency(value),
                    size=14,
                    color=INK,
                    weight=ft.FontWeight.BOLD,
                ),

            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    # =================================================
    # UPDATE PAYMENT PLAN
    # =================================================

    def update_payment_plan(e=None):

        if money(assessment["down_payment_paid"]) > 0:
            show_message(
                "The payment plan cannot be changed after "
                "the down payment has been paid."
            )
            return

        if is_assessment_paid(assessment):
            show_message(
                "This assessment has already been fully paid."
            )
            return

        try:

            entered_amount = Decimal(
                (down_payment_field.value or "")
                .replace(",", "")
                .replace("₱", "")
                .strip()
            )

            if not entered_amount.is_finite():
                raise InvalidOperation

            down_payment = money(entered_amount)

        except (InvalidOperation, ValueError):

            show_message(
                "Please enter a valid down payment amount."
            )
            return

        total = money(assessment["total_assessment"])
        minimum = money(MINIMUM_DOWN_PAYMENT)

        if down_payment < minimum:
            show_message(
                f"Minimum down payment is {format_currency(minimum)}."
            )
            return

        if down_payment > total:
            show_message(
                "Down payment cannot exceed the total assessment."
            )
            return

        installment_balance = money(
            total - down_payment
        )

        updated_installments = calculate_installments(
            installment_balance
        )

        updated_assessment = {
            "tuition_fee": assessment["tuition_fee"],
            "miscellaneous_fee": assessment["miscellaneous_fee"],
            "laboratory_fee": assessment["laboratory_fee"],
            "hands_on_fee": assessment["hands_on_fee"],
            "total_assessment": assessment["total_assessment"],
            "down_payment": float(down_payment),
            "down_payment_paid": 0.0,
            "remaining_balance": assessment["remaining_balance"],
        }

        try:

            save_student_assessment(
                assessment["enrollment_id"],
                student_id,
                updated_assessment,
                updated_installments,
            )

            assessment.update(updated_assessment)
            assessment["installments"] = updated_installments

            show_message(
                "Payment plan updated successfully!",
                is_error=False,
            )

            refresh_display()

        except (ValueError, sqlite3.Error, OSError) as error:

            show_message(
                f"Unable to update payment plan: {error}"
            )

    # =================================================
    # PAY DOWN PAYMENT
    # =================================================

    def pay_down_payment(e=None):

        if is_assessment_paid(assessment):
            show_message(
                "This assessment has already been fully paid."
            )
            return

        try:

            entered_amount = money(
                Decimal(
                    (down_payment_field.value or "")
                    .replace(",", "")
                    .replace("₱", "")
                    .strip()
                )
            )

        except (InvalidOperation, ValueError):

            show_message(
                "Please enter a valid down payment amount."
            )
            return

        if entered_amount != money(assessment["down_payment"]):

            show_message(
                "Update the payment plan before paying the "
                "changed down payment amount."
            )
            return

        try:

            receipt_number = record_simulated_down_payment(
                assessment["enrollment_id"],
                student_id,
            )

            updated_assessment = get_latest_assessment(
                student_id,
                assessment["enrollment_id"],
            )

            if updated_assessment is None:
                raise ValueError(
                    "Assessment record could not be reloaded."
                )

            assessment.clear()
            assessment.update(updated_assessment)

            show_message(
                f"Down payment recorded successfully! "
                f"Receipt: {receipt_number}",
                is_error=False,
            )

            refresh_display()

        except (ValueError, sqlite3.Error, OSError) as error:

            show_message(
                f"Unable to record down payment: {error}"
            )

    # =================================================
    # PAY INSTALLMENT
    # =================================================

    def pay_installment(e=None):

        if is_assessment_paid(assessment):
            show_message(
                "This assessment has already been fully paid."
            )
            return

        try:

            entered_amount = Decimal(
                (payment_amount_field.value or "")
                .replace(",", "")
                .replace("₱", "")
                .strip()
            )

            if not entered_amount.is_finite():
                raise InvalidOperation

            payment = money(entered_amount)

        except (InvalidOperation, ValueError):

            show_message(
                "Please enter a valid payment amount."
            )
            return

        try:

            receipt_number = record_simulated_installment_payment(
                assessment["assessment_id"],
                student_id,
                payment,
            )

            updated_assessment = get_latest_assessment(
                student_id,
                assessment["enrollment_id"],
            )

            if updated_assessment is None:
                raise ValueError(
                    "Assessment record could not be reloaded."
                )

            assessment.clear()
            assessment.update(updated_assessment)

            show_message(
                f"Payment recorded successfully! "
                f"Receipt: {receipt_number}",
                is_error=False,
            )

            refresh_display()

        except (ValueError, sqlite3.Error, OSError) as error:

            show_message(
                f"Unable to record payment: {error}"
            )

    # =================================================
    # REFRESH ASSESSMENT DISPLAY
    # =================================================

    def refresh_display():

        remaining_balance = money(
            assessment["remaining_balance"]
        )

        installment_balance_display.controls = [
            display_row(
                "Remaining Balance",
                remaining_balance,
                bold=True,
            )
        ]

        fee_breakdown.controls.clear()
        payment_breakdown.controls.clear()
        payment_action.controls.clear()

        fee_items = [
            ("Tuition Fee", assessment["tuition_fee"]),
            ("Miscellaneous Fee", assessment["miscellaneous_fee"]),
            ("Laboratory Fee", assessment["laboratory_fee"]),
            ("Hands-on Fee", assessment["hands_on_fee"]),
        ]

        for label, value in fee_items:
            fee_breakdown.controls.append(
                display_row(label, value)
            )

        fee_breakdown.controls.extend([

            ft.Divider(),

            display_row(
                "TOTAL ASSESSMENT",
                assessment["total_assessment"],
                bold=True,
            ),

            display_row(
                (
                    "Down Payment Paid"
                    if money(assessment["down_payment_paid"]) > 0
                    else "Down Payment Due"
                ),
                (
                    assessment["down_payment_paid"]
                    if money(assessment["down_payment_paid"]) > 0
                    else assessment["down_payment"]
                ),
            ),

            display_row(
                "REMAINING BALANCE",
                remaining_balance,
                bold=True,
            ),

        ])

        unpaid_installments = [
            installment
            for installment in assessment["installments"]
            if money(installment["amount_paid"])
            < money(installment["amount"])
        ]

        current_installment = (
            unpaid_installments[0]
            if unpaid_installments
            else None
        )

        # ---------------------------------------------
        # INSTALLMENT BREAKDOWN
        # ---------------------------------------------

        for installment in assessment["installments"]:

            amount = money(installment["amount"])
            amount_paid = money(installment["amount_paid"])

            amount_due = max(
                money(amount - amount_paid),
                Decimal("0.00"),
            )

            if amount_due == 0:
                installment_status = "PAID"

            elif installment is current_installment:
                installment_status = "DUE NOW"

            else:
                installment_status = "UPCOMING"

            payment_breakdown.controls.append(

                ft.Row(
                    controls=[

                        ft.Column(
                            controls=[

                                ft.Text(
                                    installment["name"],
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    f"{installment['percentage'] * 100:g}%"
                                    f"  |  {installment_status}",
                                    size=11,
                                    color=(
                                        SUCCESS
                                        if amount_due == 0
                                        else LABEL
                                    ),
                                ),

                                ft.Text(
                                    f"Paid: {format_currency(amount_paid)}"
                                    f"  |  Remaining: {format_currency(amount_due)}",
                                    size=11,
                                    color=LABEL,
                                ),

                            ],
                            spacing=2,
                            expand=True,
                        ),

                        ft.Text(
                            format_currency(amount_due),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=INK,
                        ),

                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )

        # ---------------------------------------------
        # PAYMENT ACTIONS
        # ---------------------------------------------

        if is_assessment_paid(assessment):

            payment_action.controls.extend([

                ft.Text(
                    "ASSESSMENT FULLY PAID",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=SUCCESS,
                ),

                ft.Text(
                    "Your outstanding balance for this semester "
                    "is zero. Your payment records remain available "
                    "in Transaction History.",
                    size=12,
                    color=LABEL,
                    text_align=ft.TextAlign.CENTER,
                ),

            ])

        elif money(assessment["down_payment_paid"]) < money(
            assessment["down_payment"]
        ):

            payment_action.controls.extend([

                ft.Text(
                    "DOWN PAYMENT",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Text(
                    f"Minimum down payment: "
                    f"{format_currency(MINIMUM_DOWN_PAYMENT)}",
                    size=12,
                    color=LABEL,
                ),

                ft.Text(
                    f"Amount to pay: "
                    f"{format_currency(assessment['down_payment'])}",
                    size=12,
                    color=LABEL,
                ),

                down_payment_field,

                ft.Button(
                    content="UPDATE PAYMENT PLAN",
                    width=230,
                    height=45,
                    on_click=update_payment_plan,
                ),

                ft.Button(
                    content="PAY DOWN PAYMENT",
                    width=230,
                    height=45,
                    on_click=pay_down_payment,
                ),

            ])

        elif current_installment is not None:

            minimum_payment = money(
                current_installment["amount"]
                - current_installment["amount_paid"]
            )

            payment_amount_field.value = f"{minimum_payment:.2f}"

            payment_action.controls.extend([

                ft.Text(
                    f"PAY {current_installment['name'].upper()}",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Text(
                    f"Minimum payment: {format_currency(minimum_payment)}. "
                    "Additional payment applies to later installments in order.",
                    size=12,
                    color=LABEL,
                ),

                payment_amount_field,

                ft.Button(
                    content="PAY",
                    width=230,
                    height=45,
                    on_click=pay_installment,
                ),

            ])

        # ---------------------------------------------
        # TRANSACTION HISTORY BUTTON
        # ---------------------------------------------

        if on_transaction_history:

            payment_action.controls.append(

                ft.Button(
                    content="VIEW TRANSACTION HISTORY",
                    width=230,
                    height=45,
                    on_click=lambda e: on_transaction_history(),
                )

            )

        page.update()

    # =================================================
    # STUDENT INFORMATION
    # =================================================

    semester_number = assessment["semester"]

    semester_label = (
        "1st Semester"
        if semester_number == 1
        else "2nd Semester"
        if semester_number == 2
        else "Summer"
    )

    student_card = ft.Container(
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, "#E0E0E0"),
        border_radius=15,
        padding=15,

        content=ft.Column(
            controls=[

                ft.Text(
                    student_name,
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
                    f"Year Level: {assessment['year_level']} Year",
                    size=12,
                    color=LABEL,
                ),

                ft.Text(
                    f"Semester: {semester_label}",
                    size=12,
                    color=LABEL,
                ),

                ft.Text(
                    f"Total Units: {assessment['total_units']:g}",
                    size=12,
                    color=LABEL,
                ),

                ft.Text(
                    f"Laboratory Subjects: {assessment['lab_count']}",
                    size=12,
                    color=LABEL,
                ),

                ft.Text(
                    f"Hands-on Subjects: {assessment['hands_on_count']}",
                    size=12,
                    color=LABEL,
                ),

            ],
            spacing=5,
        ),
    )

    # =================================================
    # MAIN BALANCE SCREEN
    # =================================================

    refresh_display()

    screen = ft.Container(
        width=min(page.width or 390, 390),
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
                            on_click=(
                                lambda e: on_back()
                                if on_back else None
                            ),
                        ),

                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),

                ft.Text(
                    "STUDENT ASSESSMENT",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=10),

                student_card,

                ft.Container(height=10),

                ft.Text(
                    "ASSESSMENT BREAKDOWN",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#E0E0E0"),
                    border_radius=15,
                    padding=15,
                    content=fee_breakdown,
                ),

                ft.Container(height=10),

                payment_action,

                ft.Container(height=10),

                ft.Text(
                    "BREAKDOWN OF PAYMENT",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#E0E0E0"),
                    border_radius=15,
                    padding=15,

                    content=ft.Column(
                        controls=[

                            ft.Text(
                                "Current unpaid assessment balance",
                                size=12,
                                color=LABEL,
                            ),

                            installment_balance_display,

                            ft.Divider(),

                            payment_breakdown,

                        ],
                        spacing=12,
                    ),
                ),

                ft.Container(height=10),

                ft.Text(
                    "Payments are simulated. No real money is transferred. "
                    "Each successful payment is saved as a transaction "
                    "with a receipt number.",
                    size=11,
                    color=LABEL,
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),

                status_text,

            ],
            spacing=10,
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
