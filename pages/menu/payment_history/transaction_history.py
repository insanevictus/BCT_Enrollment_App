
import flet as ft

from components.header import school_header

from database import (
    get_student_payment_history,
    get_payment_receipt,
)


BG = "#FFFCFC"
WHITE = "#FFFFFF"
INK = "#171D2A"
LABEL = "#707786"
BLUE = "#5792E8"
SUCCESS = "#147D36"
ERROR = "#B42318"


def show_transaction_history(
    page: ft.Page,
    student_id,
    on_back=None,
):

    page.controls.clear()
    page.bgcolor = BG
    page.padding = 0

    # =================================================
    # LOAD PAYMENT HISTORY
    # =================================================

    transactions = []

    try:
        transactions = get_student_payment_history(student_id)

        transactions = [
            dict(transaction)
            for transaction in transactions
        ]

    except Exception as error:
        print(f"Transaction history error: {error}")

    # =================================================
    # RECEIPT DETAILS
    # =================================================

    def show_receipt(receipt_number):

        try:
            receipt = get_payment_receipt(
                receipt_number,
                student_id,
            )

            if receipt is None:
                raise ValueError("Receipt could not be found.")

            receipt = dict(receipt)

        except Exception as error:

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Receipt Error"),
                    content=ft.Text(str(error)),
                    actions=[
                        ft.TextButton(
                            "Close",
                            on_click=lambda e: page.pop_dialog(),
                        )
                    ],
                )
            )
            return

        # ---------------------------------------------
        # RECEIPT INFORMATION
        # ---------------------------------------------

        receipt_content = ft.Column(
            controls=[

                ft.Text(
                    "BAGUIO COLLEGE OF TECHNOLOGY",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=INK,
                ),

                ft.Text(
                    "PAYMENT RECEIPT",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=BLUE,
                ),

                ft.Divider(),

                ft.Text(
                    f"Receipt No.: {receipt.get('receipt_number', '')}",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    f"Date: {receipt.get('payment_date', '')}",
                    size=12,
                ),

                ft.Divider(),

                ft.Text(
                    "STUDENT INFORMATION",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    f"Name: {receipt.get('student_name', 'N/A')}",
                    size=12,
                ),

                ft.Text(
                    f"Student ID: {student_id}",
                    size=12,
                ),

                ft.Text(
                    f"Course: {receipt.get('course', 'N/A')}",
                    size=12,
                ),

                ft.Text(
                    f"Major: {receipt.get('major', 'N/A')}",
                    size=12,
                ),

                ft.Divider(),

                ft.Text(
                    "PAYMENT INFORMATION",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    f"Payment Type: {receipt.get('payment_type', 'N/A')}",
                    size=12,
                ),

                ft.Text(
                    f"Payment Method: {receipt.get('payment_method', 'N/A')}",
                    size=12,
                ),

                ft.Text(
                    f"Amount Paid: ₱{float(receipt.get('amount', 0)):,.2f}",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=SUCCESS,
                ),

                ft.Divider(),

                ft.Text(
                    f"Total Assessment: "
                    f"₱{float(receipt.get('total_assessment', 0)):,.2f}",
                    size=12,
                ),

                ft.Text(
                    f"Remaining Balance: "
                    f"₱{float(receipt.get('remaining_balance', 0)):,.2f}",
                    size=12,
                ),

                ft.Container(height=5),

                ft.Text(
                    "This is a simulated payment receipt. "
                    "No actual money was transferred.",
                    size=10,
                    italic=True,
                    color=LABEL,
                    text_align=ft.TextAlign.CENTER,
                ),

            ],
            spacing=8,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
        )

        page.show_dialog(
            ft.AlertDialog(
                modal=True,

                title=ft.Text(
                    "Receipt Details",
                    weight=ft.FontWeight.BOLD,
                ),

                content=ft.Container(
                    width=340,
                    content=receipt_content,
                ),

                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda e: page.pop_dialog(),
                    )
                ],

                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    # =================================================
    # TRANSACTION CARD
    # =================================================

    def transaction_card(transaction):

        receipt_number = transaction.get(
            "receipt_number",
            "N/A",
        )

        amount = float(transaction.get("amount", 0))

        payment_type = transaction.get(
            "payment_type",
            "Payment",
        )

        payment_date = transaction.get(
            "payment_date",
            "Unknown date",
        )

        return ft.Container(
            bgcolor=WHITE,

            border=ft.Border.all(
                1,
                "#E0E0E0",
            ),

            border_radius=14,

            padding=15,

            content=ft.Column(
                controls=[

                    ft.Row(
                        controls=[

                            ft.Column(
                                controls=[

                                    ft.Text(
                                        payment_type,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=INK,
                                    ),

                                    ft.Text(
                                        str(payment_date),
                                        size=11,
                                        color=LABEL,
                                    ),

                                ],
                                spacing=3,
                                expand=True,
                            ),

                            ft.Text(
                                f"₱{amount:,.2f}",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=SUCCESS,
                            ),

                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),

                    ft.Divider(),

                    ft.Text(
                        f"Receipt: {receipt_number}",
                        size=12,
                        color=LABEL,
                    ),

                    ft.Button(
                        content="VIEW RECEIPT",
                        width=160,
                        height=38,
                        on_click=lambda e, number=receipt_number: (
                            show_receipt(number)
                        ),
                    ),

                ],
                spacing=8,
            ),
        )

    # =================================================
    # TRANSACTION LIST
    # =================================================

    history_content = ft.Column(
        controls=[],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    if transactions:

        for transaction in transactions:
            history_content.controls.append(
                transaction_card(transaction)
            )

    else:

        history_content.controls.append(

            ft.Container(
                bgcolor=WHITE,
                border=ft.Border.all(1, "#E0E0E0"),
                border_radius=14,
                padding=25,

                content=ft.Column(
                    controls=[

                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            size=45,
                            color=LABEL,
                        ),

                        ft.Text(
                            "No Transactions Yet",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=INK,
                        ),

                        ft.Text(
                            "Your successful payments and "
                            "receipts will appear here.",
                            size=12,
                            color=LABEL,
                            text_align=ft.TextAlign.CENTER,
                        ),

                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
            )

        )

    # =================================================
    # MAIN SCREEN
    # =================================================

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
                    "TRANSACTION HISTORY",
                    size=23,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Text(
                    f"Student ID: {student_id}",
                    size=12,
                    color=LABEL,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=10),

                ft.Text(
                    f"TOTAL TRANSACTIONS: {len(transactions)}",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=INK,
                ),

                history_content,

            ],
            spacing=10,
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
