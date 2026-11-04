
from contextlib import closing
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import os
import re
import secrets
import sqlite3
import datetime

from collections.abc import Mapping
from pathlib import Path


APP_STORAGE_DATA = os.environ.get("FLET_APP_STORAGE_DATA")

DATABASE_PATH = (
    Path(APP_STORAGE_DATA) / "enrollment.db"
    if APP_STORAGE_DATA
    else Path(__file__).resolve().with_name("enrollment.db")
)

PASSWORD_HASH_ITERATIONS = 600_000
CENT = Decimal("0.01")


# =====================================================
# DATABASE CONNECTION
# =====================================================

def _connect():

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")

    return connection


# =====================================================
# DATABASE MONEY HELPER
# =====================================================

def money_for_database(value):

    return Decimal(str(value)).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


def normalize_academic_year(value):

    match = re.fullmatch(
        r"\s*(\d{4})\s*-\s*(\d{4})\s*",
        str(value or ""),
    )

    if not match:
        raise ValueError(
            "Enter an academic year in YYYY - YYYY format."
        )

    start_year, end_year = map(int, match.groups())

    if end_year != start_year + 1:
        raise ValueError(
            "The second year must immediately follow the first year."
        )

    return f"{start_year} - {end_year}"


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def initialize_database():

    with closing(_connect()) as connection:

        with connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_accounts (
                    id_number TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    password_iterations INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            existing_table = connection.execute("""
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table'
                AND name = 'student_details'
            """).fetchone()

            if existing_table:

                columns = {
                    row[1]
                    for row in connection.execute(
                        "PRAGMA table_info(student_details)"
                    ).fetchall()
                }

                if "id_number" not in columns:

                    legacy_name = "student_details_legacy"
                    suffix = 1

                    while connection.execute(
                        """
                        SELECT 1
                        FROM sqlite_master
                        WHERE type = 'table'
                        AND name = ?
                        """,
                        (legacy_name,)
                    ).fetchone():

                        legacy_name = (
                            f"student_details_legacy_{suffix}"
                        )

                        suffix += 1

                    connection.execute(
                        f'ALTER TABLE student_details '
                        f'RENAME TO "{legacy_name}"'
                    )

            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_details (
                    id_number TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    middle_name TEXT NOT NULL DEFAULT '',
                    last_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    birthdate TEXT NOT NULL,
                    contact_number TEXT NOT NULL,
                    course TEXT NOT NULL,
                    major TEXT NOT NULL,
                    emergency_name TEXT NOT NULL,
                    emergency_number TEXT NOT NULL,
                    saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (id_number)
                        REFERENCES student_accounts(id_number)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                )
            """)


# =====================================================
# CHECK REGISTERED ID
# =====================================================

def is_id_registered(id_number):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        return False

    initialize_database()

    with closing(_connect()) as connection:

        row = connection.execute(
            """
            SELECT 1
            FROM student_accounts
            WHERE id_number = ?
            """,
            (normalized_id,)
        ).fetchone()

    return row is not None


# =====================================================
# CREATE STUDENT ACCOUNT
# =====================================================

def create_student_account(id_number, password):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        raise ValueError("ID number is required.")

    initialize_database()

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS
    ).hex()

    try:

        with closing(_connect()) as connection:

            with connection:

                connection.execute(
                    """
                    INSERT INTO student_accounts (
                        id_number,
                        password_hash,
                        password_salt,
                        password_iterations
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        normalized_id,
                        password_hash,
                        salt.hex(),
                        PASSWORD_HASH_ITERATIONS
                    )
                )

        return True

    except sqlite3.IntegrityError:

        if is_id_registered(normalized_id):
            return False

        raise


# =====================================================
# VERIFY STUDENT LOGIN
# =====================================================

def verify_student_login(id_number, password):

    normalized_id = (id_number or "").strip()

    if not normalized_id or not password:
        return False

    initialize_database()

    with closing(_connect()) as connection:

        row = connection.execute(
            """
            SELECT
                password_hash,
                password_salt,
                password_iterations
            FROM student_accounts
            WHERE id_number = ?
            """,
            (normalized_id,)
        ).fetchone()

    if row is None:
        return False

    stored_hash, stored_salt, iterations = row

    try:

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(stored_salt),
            int(iterations)
        ).hex()

    except (ValueError, TypeError, OverflowError):
        return False

    return secrets.compare_digest(
        calculated_hash,
        stored_hash
    )


# =====================================================
# GET STUDENT PROFILE
# =====================================================

def get_student_profile(id_number):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        return None

    initialize_database()

    with closing(_connect()) as connection:

        row = connection.execute(
            """
            SELECT
                first_name,
                middle_name,
                last_name,
                course,
                major
            FROM student_details
            WHERE id_number = ?
            """,
            (normalized_id,)
        ).fetchone()

    if row is None:
        return None

    first_name, middle_name, last_name, course, major = row

    full_name = " ".join(
        part.strip()
        for part in (first_name, middle_name, last_name)
        if part and part.strip()
    )

    return {
        "id_number": normalized_id,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "full_name": full_name,
        "course": course,
        "major": major,
    }


# =====================================================
# SAVE STUDENT DETAILS
# =====================================================

def save_student_details(student_data: Mapping[str, str], id_number):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        raise ValueError(
            "A student ID number is required to save the details."
        )

    initialize_database()

    with closing(_connect()) as connection:

        with connection:

            connection.execute(
                """
                INSERT INTO student_details (
                    id_number,
                    first_name,
                    middle_name,
                    last_name,
                    address,
                    birthdate,
                    contact_number,
                    course,
                    major,
                    emergency_name,
                    emergency_number
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(id_number) DO UPDATE SET
                    first_name = excluded.first_name,
                    middle_name = excluded.middle_name,
                    last_name = excluded.last_name,
                    address = excluded.address,
                    birthdate = excluded.birthdate,
                    contact_number = excluded.contact_number,
                    course = excluded.course,
                    major = excluded.major,
                    emergency_name = excluded.emergency_name,
                    emergency_number = excluded.emergency_number,
                    saved_at = CURRENT_TIMESTAMP
                """,
                (
                    normalized_id,
                    student_data["first_name"],
                    student_data.get("middle_name", ""),
                    student_data["last_name"],
                    student_data["address"],
                    student_data["birthdate"],
                    student_data["contact_number"],
                    student_data["course"],
                    student_data["major"],
                    student_data["emergency_name"],
                    student_data["emergency_number"],
                )
            )


# =====================================================
# INITIALIZE ENROLLMENT TABLES
# =====================================================

def initialize_enrollment_tables():

    initialize_database()

    with closing(_connect()) as connection:

        with connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_enrollments (

                    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,

                    id_number TEXT NOT NULL,

                    program_key TEXT NOT NULL,

                    year_level INTEGER NOT NULL,

                    semester INTEGER NOT NULL,

                    academic_year TEXT,

                    curriculum_semester INTEGER NOT NULL,

                    schedule INTEGER,

                    total_units REAL NOT NULL,

                    lab_count INTEGER NOT NULL,

                    hands_on_count INTEGER NOT NULL,

                    status TEXT NOT NULL DEFAULT 'Awaiting Assessment',

                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (id_number)
                        REFERENCES student_accounts(id_number)
                )
            """)

            enrollment_columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(student_enrollments)"
                ).fetchall()
            }

            if "academic_year" not in enrollment_columns:

                connection.execute("""
                    ALTER TABLE student_enrollments
                    ADD COLUMN academic_year TEXT
                """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS enrollment_subjects (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    enrollment_id INTEGER NOT NULL,

                    subject_id TEXT NOT NULL,

                    title TEXT NOT NULL,

                    time TEXT NOT NULL,

                    days TEXT NOT NULL,

                    room TEXT NOT NULL,

                    units REAL NOT NULL,

                    is_lab INTEGER NOT NULL DEFAULT 0,

                    is_hands_on INTEGER NOT NULL DEFAULT 0,

                    result_status TEXT NOT NULL DEFAULT 'Enrolled',

                    FOREIGN KEY (enrollment_id)
                        REFERENCES student_enrollments(enrollment_id)
                        ON DELETE CASCADE,

                    UNIQUE(enrollment_id, subject_id)
                )
            """)

            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(enrollment_subjects)"
                ).fetchall()
            }

            if "result_status" not in columns:

                connection.execute("""
                    ALTER TABLE enrollment_subjects
                    ADD COLUMN result_status TEXT
                    NOT NULL DEFAULT 'Enrolled'
                """)


# =====================================================
# GET STUDENT SUBJECT STATUS
# =====================================================

def get_student_subject_status(id_number):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        return {}

    initialize_enrollment_tables()

    with closing(_connect()) as connection:

        rows = connection.execute(
            """
            SELECT
                es.subject_id,
                es.result_status

            FROM enrollment_subjects es

            JOIN student_enrollments se
                ON se.enrollment_id = es.enrollment_id

            WHERE se.id_number = ?

            ORDER BY se.enrollment_id DESC
            """,
            (normalized_id,)
        ).fetchall()

    subject_status = {}

    for subject_id, result_status in rows:

        previous_status = subject_status.get(subject_id)

        if result_status == "Passed":

            subject_status[subject_id] = "Passed"

        elif previous_status is None:

            subject_status[subject_id] = result_status

    return subject_status


def get_student_enrolled_subjects(
    id_number,
    academic_year=None,
    semester=None,
):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        return []

    normalized_year = (
        normalize_academic_year(academic_year)
        if academic_year and str(academic_year).strip()
        else None
    )

    normalized_semester = None

    if semester is not None and str(semester).strip():
        try:
            normalized_semester = int(semester)
        except (TypeError, ValueError):
            raise ValueError("Choose a valid semester.") from None

        if normalized_semester not in (1, 2, 3):
            raise ValueError("Choose a valid semester.")

    initialize_enrollment_tables()

    with closing(_connect()) as connection:

        rows = connection.execute(
            """
            SELECT
                es.subject_id,
                es.title,
                es.units,
                es.result_status,
                es.time,
                es.days,
                es.room,
                se.academic_year,
                se.semester

            FROM enrollment_subjects es

            JOIN student_enrollments se
                ON se.enrollment_id = es.enrollment_id

            WHERE se.id_number = ?
            AND (? IS NULL OR se.academic_year = ?)
            AND (? IS NULL OR se.semester = ?)

            ORDER BY
                se.academic_year DESC,
                se.semester,
                se.enrollment_id DESC,
                es.title
            """,
            (
                normalized_id,
                normalized_year,
                normalized_year,
                normalized_semester,
                normalized_semester,
            ),
        ).fetchall()

    return [
        {
            "subject_id": row[0],
            "title": row[1],
            "units": row[2],
            "result_status": row[3],
            "time": row[4],
            "days": row[5],
            "room": row[6],
            "academic_year": row[7],
            "semester": row[8],
        }
        for row in rows
    ]


# =====================================================
# UPDATE SUBJECT RESULT
# =====================================================

def update_subject_result(
    enrollment_id,
    subject_id,
    result_status,
    id_number=None
):

    allowed_statuses = {
        "Enrolled",
        "Passed",
        "Failed",
    }

    if result_status not in allowed_statuses:
        raise ValueError("Invalid subject result status.")

    initialize_enrollment_tables()

    with closing(_connect()) as connection:

        with connection:

            if id_number:

                cursor = connection.execute(
                    """
                    UPDATE enrollment_subjects

                    SET result_status = ?

                    WHERE enrollment_id = ?
                    AND subject_id = ?

                    AND EXISTS (
                        SELECT 1
                        FROM student_enrollments

                        WHERE student_enrollments.enrollment_id =
                            enrollment_subjects.enrollment_id

                        AND id_number = ?
                    )
                    """,
                    (
                        result_status,
                        enrollment_id,
                        subject_id,
                        id_number
                    )
                )

            else:

                cursor = connection.execute(
                    """
                    UPDATE enrollment_subjects

                    SET result_status = ?

                    WHERE enrollment_id = ?
                    AND subject_id = ?
                    """,
                    (
                        result_status,
                        enrollment_id,
                        subject_id
                    )
                )

            if cursor.rowcount == 0:

                raise ValueError(
                    "Subject record could not be found."
                )

    return True


# =====================================================
# SAVE STUDENT ENROLLMENT
# BLOCK ENROLLMENT IF ANY BALANCE IS OUTSTANDING
# =====================================================

def save_student_enrollment(
    id_number,
    program_key,
    year_level,
    semester,
    academic_year,
    curriculum_semester,
    schedule,
    selected_subjects
):

    normalized_id = (id_number or "").strip()
    normalized_academic_year = normalize_academic_year(
        academic_year
    )

    if not normalized_id:
        raise ValueError("Student ID number is required.")

    profile = get_student_profile(normalized_id)

    if profile is None:
        raise ValueError("Student details could not be found.")

    profile_course = (
        str(profile.get("course") or "").strip().casefold()
    )

    if (
        profile_course == "associate in computer technology (2 years)"
        and year_level > 2
    ):
        raise ValueError(
            "Associate in Computer Technology enrollment is limited "
            "to the first two year levels."
        )

    if semester not in (1, 2, 3):
        raise ValueError("Choose a valid semester.")

    if not selected_subjects:
        raise ValueError("Please select at least one subject.")

    if semester == 3 and not (
        year_level == 4
        and curriculum_semester == 9
        and len(selected_subjects) == 1
        and selected_subjects[0]["title"]
        == "INDUSTRY IMMERSION / ON-THE-JOB TRAINING"
    ):
        raise ValueError(
            "Summer enrollment is limited to the configured "
            "fourth-year on-the-job training subject."
        )

    total_units = sum(
        float(subject["units"])
        for subject in selected_subjects
    )

    lab_count = sum(
        1 for subject in selected_subjects
        if subject["is_lab"]
    )

    hands_on_count = sum(
        1 for subject in selected_subjects
        if subject["is_hands_on"]
    )

    if not 1 <= total_units <= 25:
        raise ValueError(
            "Enrollment must be between 1 and 25 units."
        )

    initialize_assessment_tables()

    with closing(_connect()) as connection:

        connection.execute("BEGIN IMMEDIATE")

        try:

            outstanding = connection.execute(
                """
                SELECT
                    remaining_balance

                FROM student_assessments

                WHERE id_number = ?
                AND remaining_balance > 0.005

                LIMIT 1
                """,
                (normalized_id,)
            ).fetchone()

            if outstanding is not None:

                balance = money_for_database(outstanding[0])

                raise ValueError(
                    "You cannot enroll in another semester while "
                    f"you have an outstanding balance of ₱{balance:,.2f}. "
                    "Please settle your previous assessment first."
                )

            previous_subjects = connection.execute(
                """
                SELECT
                    es.subject_id,
                    es.result_status

                FROM enrollment_subjects es

                JOIN student_enrollments se
                    ON se.enrollment_id = es.enrollment_id

                WHERE se.id_number = ?

                ORDER BY se.enrollment_id DESC
                """,
                (normalized_id,)
            ).fetchall()

            previous_status = {}

            for subject_id, result_status in previous_subjects:

                current_status = previous_status.get(subject_id)

                if result_status == "Passed":

                    previous_status[subject_id] = "Passed"

                elif current_status is None:

                    previous_status[subject_id] = result_status

            for subject in selected_subjects:

                subject_id = subject["subject_id"]

                status = previous_status.get(subject_id)

                if status == "Passed":

                    raise ValueError(
                        f"{subject['title']} has already been passed "
                        "and cannot be enrolled again."
                    )

                if status == "Enrolled":

                    raise ValueError(
                        f"{subject['title']} is already enrolled."
                    )

            cursor = connection.execute(
                """
                INSERT INTO student_enrollments (
                    id_number,
                    program_key,
                    year_level,
                    semester,
                    academic_year,
                    curriculum_semester,
                    schedule,
                    total_units,
                    lab_count,
                    hands_on_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_id,
                    program_key,
                    year_level,
                    semester,
                    normalized_academic_year,
                    curriculum_semester,
                    schedule,
                    total_units,
                    lab_count,
                    hands_on_count
                )
            )

            enrollment_id = cursor.lastrowid

            for subject in selected_subjects:

                connection.execute(
                    """
                    INSERT INTO enrollment_subjects (
                        enrollment_id,
                        subject_id,
                        title,
                        time,
                        days,
                        room,
                        units,
                        is_lab,
                        is_hands_on,
                        result_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        enrollment_id,
                        subject["subject_id"],
                        subject["title"],
                        subject["time"],
                        subject["days"],
                        subject["room"],
                        subject["units"],
                        int(subject["is_lab"]),
                        int(subject["is_hands_on"]),
                        "Enrolled"
                    )
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    return enrollment_id


# =====================================================
# INITIALIZE ASSESSMENT TABLES
# =====================================================

def initialize_assessment_tables():

    initialize_enrollment_tables()

    with closing(_connect()) as connection:

        with connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_assessments (

                    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,

                    enrollment_id INTEGER NOT NULL UNIQUE,

                    id_number TEXT NOT NULL,

                    tuition_fee REAL NOT NULL,

                    miscellaneous_fee REAL NOT NULL,

                    laboratory_fee REAL NOT NULL,

                    hands_on_fee REAL NOT NULL,

                    total_assessment REAL NOT NULL,

                    down_payment REAL NOT NULL,

                    down_payment_paid REAL NOT NULL DEFAULT 0,

                    remaining_balance REAL NOT NULL,

                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (enrollment_id)
                        REFERENCES student_enrollments(enrollment_id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (id_number)
                        REFERENCES student_accounts(id_number)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS assessment_installments (

                    installment_id INTEGER PRIMARY KEY AUTOINCREMENT,

                    assessment_id INTEGER NOT NULL,

                    payment_name TEXT NOT NULL,

                    percentage REAL NOT NULL,

                    amount REAL NOT NULL,

                    amount_paid REAL NOT NULL DEFAULT 0,

                    FOREIGN KEY (assessment_id)
                        REFERENCES student_assessments(assessment_id)
                        ON DELETE CASCADE,

                    UNIQUE(assessment_id, payment_name)
                )
            """)

            assessment_columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(student_assessments)"
                ).fetchall()
            }

            if "down_payment_paid" not in assessment_columns:

                connection.execute("""
                    ALTER TABLE student_assessments
                    ADD COLUMN down_payment_paid REAL NOT NULL DEFAULT 0
                """)

                connection.execute("""
                    UPDATE student_assessments
                    SET remaining_balance = total_assessment
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM assessment_installments i
                        WHERE i.assessment_id =
                            student_assessments.assessment_id
                        AND i.amount_paid > 0
                    )
                """)


# =====================================================
# GET ENROLLMENT DETAILS
# =====================================================

def get_enrollment_details(enrollment_id, id_number):

    initialize_assessment_tables()

    with closing(_connect()) as connection:

        row = connection.execute(
            """
            SELECT
                enrollment_id,
                id_number,
                program_key,
                year_level,
                semester,
                curriculum_semester,
                schedule,
                total_units,
                lab_count,
                hands_on_count

            FROM student_enrollments

            WHERE enrollment_id = ?
            AND id_number = ?
            """,
            (enrollment_id, id_number)
        ).fetchone()

    if row is None:
        return None

    keys = [
        "enrollment_id",
        "id_number",
        "program_key",
        "year_level",
        "semester",
        "curriculum_semester",
        "schedule",
        "total_units",
        "lab_count",
        "hands_on_count",
    ]

    return dict(zip(keys, row))


# =====================================================
# SAVE OR UPDATE STUDENT ASSESSMENT
# =====================================================

def save_student_assessment(
    enrollment_id,
    id_number,
    assessment_data,
    installments
):

    initialize_assessment_tables()

    enrollment = get_enrollment_details(
        enrollment_id,
        id_number
    )

    if enrollment is None:
        raise ValueError("Enrollment record could not be found.")

    with closing(_connect()) as connection:

        with connection:

            existing_assessment = connection.execute(
                """
                SELECT assessment_id, down_payment_paid

                FROM student_assessments

                WHERE enrollment_id = ?
                """,
                (enrollment_id,)
            ).fetchone()

            if existing_assessment:

                payment_exists = connection.execute(
                    """
                    SELECT 1

                    FROM assessment_installments

                    WHERE assessment_id = ?
                    AND amount_paid > 0

                    LIMIT 1
                    """,
                    (existing_assessment[0],)
                ).fetchone()

                if existing_assessment[1] > 0 or payment_exists:

                    raise ValueError(
                        "The payment plan cannot be changed after "
                        "a payment has been recorded."
                    )

            balance = money_for_database(
                assessment_data["remaining_balance"]
            )

            enrollment_status = (
                "Paid" if balance <= 0 else "Assessed"
            )

            connection.execute(
                """
                INSERT INTO student_assessments (
                    enrollment_id,
                    id_number,
                    tuition_fee,
                    miscellaneous_fee,
                    laboratory_fee,
                    hands_on_fee,
                    total_assessment,
                    down_payment,
                    down_payment_paid,
                    remaining_balance
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(enrollment_id) DO UPDATE SET
                    tuition_fee = excluded.tuition_fee,
                    miscellaneous_fee = excluded.miscellaneous_fee,
                    laboratory_fee = excluded.laboratory_fee,
                    hands_on_fee = excluded.hands_on_fee,
                    total_assessment = excluded.total_assessment,
                    down_payment = excluded.down_payment,
                    down_payment_paid = excluded.down_payment_paid,
                    remaining_balance = excluded.remaining_balance,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    enrollment_id,
                    id_number,
                    assessment_data["tuition_fee"],
                    assessment_data["miscellaneous_fee"],
                    assessment_data["laboratory_fee"],
                    assessment_data["hands_on_fee"],
                    assessment_data["total_assessment"],
                    assessment_data["down_payment"],
                    assessment_data.get("down_payment_paid", 0),
                    assessment_data["remaining_balance"],
                )
            )

            assessment_id = connection.execute(
                """
                SELECT assessment_id

                FROM student_assessments

                WHERE enrollment_id = ?
                """,
                (enrollment_id,)
            ).fetchone()[0]

            connection.execute(
                """
                DELETE FROM assessment_installments

                WHERE assessment_id = ?
                """,
                (assessment_id,)
            )

            for payment in installments:

                connection.execute(
                    """
                    INSERT INTO assessment_installments (
                        assessment_id,
                        payment_name,
                        percentage,
                        amount
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        assessment_id,
                        payment["name"],
                        payment["percentage"],
                        payment["amount"],
                    )
                )

            connection.execute(
                """
                UPDATE student_enrollments

                SET status = ?

                WHERE enrollment_id = ?
                """,
                (enrollment_status, enrollment_id)
            )

    return assessment_id


# =====================================================
# INTERNAL: APPLY DOWN PAYMENT
# =====================================================

def _apply_down_payment(connection, enrollment_id, id_number):

    assessment = connection.execute(
        """
        SELECT
            assessment_id,
            total_assessment,
            down_payment,
            down_payment_paid

        FROM student_assessments

        WHERE enrollment_id = ?
        AND id_number = ?
        """,
        (enrollment_id, id_number)
    ).fetchone()

    if assessment is None:
        raise ValueError("Assessment record could not be found.")

    assessment_id, total, planned, already_paid = assessment

    total = money_for_database(total)
    planned = money_for_database(planned)
    already_paid = money_for_database(already_paid)

    if already_paid >= planned:
        raise ValueError("The down payment has already been paid.")

    installment_payment = connection.execute(
        """
        SELECT COALESCE(SUM(amount_paid), 0)

        FROM assessment_installments

        WHERE assessment_id = ?
        """,
        (assessment_id,)
    ).fetchone()[0]

    if money_for_database(installment_payment) > 0:
        raise ValueError(
            "The down payment must be paid before installments."
        )

    remaining = money_for_database(total - planned)

    connection.execute(
        """
        UPDATE student_assessments

        SET down_payment_paid = down_payment,
            remaining_balance = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE assessment_id = ?
        """,
        (float(remaining), assessment_id)
    )

    connection.execute(
        """
        UPDATE student_enrollments

        SET status = ?

        WHERE enrollment_id = ?
        """,
        (
            "Paid" if remaining <= 0 else "Assessed",
            enrollment_id
        )
    )

    return assessment_id, planned, remaining


# =====================================================
# RECORD DOWN PAYMENT
# =====================================================

def record_assessment_down_payment(enrollment_id, id_number):

    initialize_assessment_tables()

    with closing(_connect()) as connection:

        with connection:

            _, _, remaining = _apply_down_payment(
                connection,
                enrollment_id,
                id_number
            )

    return float(remaining)


# =====================================================
# INTERNAL: APPLY INSTALLMENT PAYMENT
# =====================================================

def _apply_installment_payment(
    connection,
    assessment_id,
    id_number,
    amount
):

    try:

        payment = money_for_database(amount)

    except (InvalidOperation, ValueError, TypeError):

        raise ValueError(
            "Enter a valid payment amount."
        ) from None

    if payment <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    assessment = connection.execute(
        """
        SELECT
            enrollment_id,
            down_payment,
            down_payment_paid,
            remaining_balance

        FROM student_assessments

        WHERE assessment_id = ?
        AND id_number = ?
        """,
        (assessment_id, id_number)
    ).fetchone()

    if assessment is None:
        raise ValueError("Assessment record could not be found.")

    enrollment_id, planned, paid, balance = assessment

    planned = money_for_database(planned)
    paid = money_for_database(paid)
    balance = money_for_database(balance)

    if paid < planned:
        raise ValueError(
            "Pay the down payment before making installment payments."
        )

    if balance <= 0:
        raise ValueError("This assessment has already been fully paid.")

    if payment > balance:
        raise ValueError(
            "Payment cannot exceed the remaining balance."
        )

    installments = connection.execute(
        """
        SELECT installment_id, amount, amount_paid

        FROM assessment_installments

        WHERE assessment_id = ?

        ORDER BY installment_id
        """,
        (assessment_id,)
    ).fetchall()

    unpaid_installments = [
        (
            installment_id,
            money_for_database(amount),
            money_for_database(amount_paid),
        )
        for installment_id, amount, amount_paid in installments
        if money_for_database(amount_paid) < money_for_database(amount)
    ]

    if not unpaid_installments:
        raise ValueError("There are no installments left to pay.")

    _, first_amount, first_paid = unpaid_installments[0]

    minimum_payment = first_amount - first_paid

    if payment < minimum_payment:
        raise ValueError(
            f"Minimum payment for the current installment is "
            f"{minimum_payment:.2f}."
        )

    amount_to_allocate = payment

    for installment_id, amount, amount_paid in unpaid_installments:

        due = amount - amount_paid
        allocation = min(due, amount_to_allocate)

        if allocation > 0:

            connection.execute(
                """
                UPDATE assessment_installments

                SET amount_paid = ?

                WHERE installment_id = ?
                """,
                (
                    float(amount_paid + allocation),
                    installment_id
                )
            )

            amount_to_allocate -= allocation

        if amount_to_allocate == 0:
            break

    if amount_to_allocate > 0:
        raise ValueError(
            "Installment schedule does not match the remaining balance."
        )

    new_balance = money_for_database(balance - payment)

    if new_balance < 0:
        new_balance = Decimal("0.00")

    connection.execute(
        """
        UPDATE student_assessments

        SET remaining_balance = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE assessment_id = ?
        """,
        (float(new_balance), assessment_id)
    )

    connection.execute(
        """
        UPDATE student_enrollments

        SET status = ?

        WHERE enrollment_id = ?
        """,
        (
            "Paid" if new_balance <= 0 else "Assessed",
            enrollment_id
        )
    )

    return enrollment_id, new_balance


# =====================================================
# RECORD INSTALLMENT PAYMENT
# =====================================================

def record_assessment_installment_payment(
    assessment_id,
    id_number,
    amount
):

    initialize_assessment_tables()

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        raise ValueError("Student ID number is required.")

    with closing(_connect()) as connection:

        with connection:

            _, new_balance = _apply_installment_payment(
                connection,
                assessment_id,
                normalized_id,
                amount
            )

    return float(new_balance)


# =====================================================
# GET STUDENT ASSESSMENT
# =====================================================

def get_latest_assessment(id_number, enrollment_id=None):

    initialize_assessment_tables()

    with closing(_connect()) as connection:

        if enrollment_id is not None:

            row = connection.execute(
                """
                SELECT
                    a.assessment_id,
                    a.enrollment_id,
                    a.id_number,
                    a.tuition_fee,
                    a.miscellaneous_fee,
                    a.laboratory_fee,
                    a.hands_on_fee,
                    a.total_assessment,
                    a.down_payment,
                    a.down_payment_paid,
                    a.remaining_balance,
                    a.created_at,
                    e.total_units,
                    e.lab_count,
                    e.hands_on_count,
                    e.year_level,
                    e.semester,
                    e.schedule,
                    e.program_key

                FROM student_assessments a

                JOIN student_enrollments e
                    ON e.enrollment_id = a.enrollment_id

                WHERE a.id_number = ?
                AND a.enrollment_id = ?

                LIMIT 1
                """,
                (id_number, enrollment_id)
            ).fetchone()

        else:

            row = connection.execute(
                """
                SELECT
                    a.assessment_id,
                    a.enrollment_id,
                    a.id_number,
                    a.tuition_fee,
                    a.miscellaneous_fee,
                    a.laboratory_fee,
                    a.hands_on_fee,
                    a.total_assessment,
                    a.down_payment,
                    a.down_payment_paid,
                    a.remaining_balance,
                    a.created_at,
                    e.total_units,
                    e.lab_count,
                    e.hands_on_count,
                    e.year_level,
                    e.semester,
                    e.schedule,
                    e.program_key

                FROM student_assessments a

                JOIN student_enrollments e
                    ON e.enrollment_id = a.enrollment_id

                WHERE a.id_number = ?

                ORDER BY a.assessment_id DESC

                LIMIT 1
                """,
                (id_number,)
            ).fetchone()

        if row is None:
            return None

        keys = [
            "assessment_id",
            "enrollment_id",
            "id_number",
            "tuition_fee",
            "miscellaneous_fee",
            "laboratory_fee",
            "hands_on_fee",
            "total_assessment",
            "down_payment",
            "down_payment_paid",
            "remaining_balance",
            "created_at",
            "total_units",
            "lab_count",
            "hands_on_count",
            "year_level",
            "semester",
            "schedule",
            "program_key",
        ]

        assessment = dict(zip(keys, row))

        installment_rows = connection.execute(
            """
            SELECT
                payment_name,
                percentage,
                amount,
                amount_paid

            FROM assessment_installments

            WHERE assessment_id = ?

            ORDER BY installment_id
            """,
            (assessment["assessment_id"],)
        ).fetchall()

        assessment["installments"] = [
            {
                "name": item[0],
                "percentage": item[1],
                "amount": item[2],
                "amount_paid": item[3],
            }
            for item in installment_rows
        ]

    return assessment


# =====================================================
# GET ACTIVE UNPAID ASSESSMENTS
# =====================================================

def get_active_assessments(id_number):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        return []

    initialize_assessment_tables()

    with closing(_connect()) as connection:

        rows = connection.execute(
            """
            SELECT
                a.assessment_id,
                a.enrollment_id,
                a.total_assessment,
                a.remaining_balance,
                a.created_at,
                e.year_level,
                e.semester,
                e.status

            FROM student_assessments a

            JOIN student_enrollments e
                ON e.enrollment_id = a.enrollment_id

            WHERE a.id_number = ?
            AND a.remaining_balance > 0.005

            ORDER BY a.assessment_id DESC
            """,
            (normalized_id,)
        ).fetchall()

    keys = [
        "assessment_id",
        "enrollment_id",
        "total_assessment",
        "remaining_balance",
        "created_at",
        "year_level",
        "semester",
        "status",
    ]

    return [
        dict(zip(keys, row))
        for row in rows
    ]


# =====================================================
# SIMULATED PAYMENT TRANSACTIONS TABLE
# =====================================================

def initialize_payment_transaction_table():

    initialize_assessment_tables()

    with closing(_connect()) as connection:

        with connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS payment_transactions (

                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

                    receipt_number TEXT NOT NULL UNIQUE,

                    assessment_id INTEGER NOT NULL,

                    enrollment_id INTEGER NOT NULL,

                    id_number TEXT NOT NULL,

                    payment_type TEXT NOT NULL,

                    amount REAL NOT NULL,

                    payment_method TEXT NOT NULL DEFAULT 'Simulated Payment',

                    payment_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    balance_after_payment REAL NOT NULL DEFAULT 0,

                    FOREIGN KEY (assessment_id)
                        REFERENCES student_assessments(assessment_id),

                    FOREIGN KEY (enrollment_id)
                        REFERENCES student_enrollments(enrollment_id),

                    FOREIGN KEY (id_number)
                        REFERENCES student_accounts(id_number)
                )
            """)

            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(payment_transactions)"
                ).fetchall()
            }

            if "balance_after_payment" not in columns:

                connection.execute("""
                    ALTER TABLE payment_transactions
                    ADD COLUMN balance_after_payment REAL NOT NULL DEFAULT 0
                """)

                # Reconstruct historical balances from later payments.
                connection.execute("""
                    UPDATE payment_transactions

                    SET balance_after_payment = COALESCE(
                        (
                            SELECT
                                sa.remaining_balance +
                                COALESCE(
                                    (
                                        SELECT SUM(later.amount)

                                        FROM payment_transactions later

                                        WHERE later.assessment_id =
                                            payment_transactions.assessment_id

                                        AND later.transaction_id >
                                            payment_transactions.transaction_id
                                    ),
                                    0
                                )

                            FROM student_assessments sa

                            WHERE sa.assessment_id =
                                payment_transactions.assessment_id
                        ),
                        0
                    )
                """)


# =====================================================
# GENERATE RECEIPT NUMBER
# =====================================================

def _generate_receipt_number(connection):

    date_part = datetime.datetime.now().strftime("%Y%m%d")

    row = connection.execute(
        """
        SELECT COUNT(*)

        FROM payment_transactions

        WHERE receipt_number LIKE ?
        """,
        (f"BCT-{date_part}-%",)
    ).fetchone()

    sequence = int(row[0]) + 1

    return f"BCT-{date_part}-{sequence:04d}"


# =====================================================
# SAVE PAYMENT TRANSACTION
# =====================================================

def _save_payment_transaction(
    connection,
    assessment_id,
    enrollment_id,
    id_number,
    payment_type,
    amount,
    remaining_balance
):

    receipt_number = _generate_receipt_number(connection)

    connection.execute(
        """
        INSERT INTO payment_transactions (
            receipt_number,
            assessment_id,
            enrollment_id,
            id_number,
            payment_type,
            amount,
            balance_after_payment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            receipt_number,
            assessment_id,
            enrollment_id,
            id_number,
            payment_type,
            float(amount),
            float(remaining_balance)
        )
    )

    return receipt_number


# =====================================================
# GET STUDENT PAYMENT HISTORY
# =====================================================

def get_student_payment_history(id_number):

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        return []

    initialize_payment_transaction_table()

    with closing(_connect()) as connection:

        rows = connection.execute(
            """
            SELECT
                pt.transaction_id,
                pt.receipt_number,
                pt.assessment_id,
                pt.enrollment_id,
                pt.payment_type,
                pt.amount,
                pt.payment_method,
                pt.payment_date,
                e.year_level,
                e.semester,
                e.status AS enrollment_status,
                a.total_assessment,
                pt.balance_after_payment

            FROM payment_transactions pt

            JOIN student_enrollments e
                ON e.enrollment_id = pt.enrollment_id

            JOIN student_assessments a
                ON a.assessment_id = pt.assessment_id

            WHERE pt.id_number = ?

            ORDER BY pt.transaction_id DESC
            """,
            (normalized_id,)
        ).fetchall()

    keys = [
        "transaction_id",
        "receipt_number",
        "assessment_id",
        "enrollment_id",
        "payment_type",
        "amount",
        "payment_method",
        "payment_date",
        "year_level",
        "semester",
        "enrollment_status",
        "total_assessment",
        "remaining_balance",
    ]

    return [
        dict(zip(keys, row))
        for row in rows
    ]


# =====================================================
# GET PAYMENT RECEIPT
# =====================================================

def get_payment_receipt(receipt_number, id_number):

    normalized_id = (id_number or "").strip()

    if not receipt_number or not normalized_id:
        return None

    initialize_payment_transaction_table()

    with closing(_connect()) as connection:

        row = connection.execute(
            """
            SELECT
                pt.transaction_id,
                pt.receipt_number,
                pt.assessment_id,
                pt.enrollment_id,
                pt.id_number,
                pt.payment_type,
                pt.amount,
                pt.payment_method,
                pt.payment_date,

                sd.first_name,
                sd.middle_name,
                sd.last_name,
                sd.course,
                sd.major,

                sa.total_assessment,
                pt.balance_after_payment,

                e.year_level,
                e.semester,
                e.status AS enrollment_status

            FROM payment_transactions pt

            JOIN student_details sd
                ON sd.id_number = pt.id_number

            JOIN student_assessments sa
                ON sa.assessment_id = pt.assessment_id

            JOIN student_enrollments e
                ON e.enrollment_id = pt.enrollment_id

            WHERE pt.receipt_number = ?
            AND pt.id_number = ?

            LIMIT 1
            """,
            (receipt_number, normalized_id)
        ).fetchone()

    if row is None:
        return None

    keys = [
        "transaction_id",
        "receipt_number",
        "assessment_id",
        "enrollment_id",
        "id_number",
        "payment_type",
        "amount",
        "payment_method",
        "payment_date",
        "first_name",
        "middle_name",
        "last_name",
        "course",
        "major",
        "total_assessment",
        "remaining_balance",
        "year_level",
        "semester",
        "enrollment_status",
    ]

    receipt = dict(zip(keys, row))

    receipt["student_name"] = " ".join(
        part.strip()
        for part in (
            receipt["first_name"],
            receipt["middle_name"],
            receipt["last_name"],
        )
        if part and part.strip()
    )

    return receipt


# =====================================================
# GET ASSESSMENT PAYMENT STATUS
# =====================================================

def get_assessment_payment_status(enrollment_id, id_number):

    assessment = get_latest_assessment(
        id_number,
        enrollment_id
    )

    if assessment is None:
        return "Unpaid"

    total = money_for_database(
        assessment["total_assessment"]
    )

    balance = money_for_database(
        assessment["remaining_balance"]
    )

    if balance <= 0:
        return "Fully Paid"

    if balance < total:
        return "Partially Paid"

    return "Unpaid"


# =====================================================
# RECORD SIMULATED DOWN PAYMENT WITH RECEIPT
# ATOMIC: PAYMENT + BALANCE + RECEIPT
# =====================================================

def record_simulated_down_payment(enrollment_id, id_number):

    initialize_payment_transaction_table()

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        raise ValueError("Student ID number is required.")

    with closing(_connect()) as connection:

        connection.execute("BEGIN IMMEDIATE")

        try:

            row = connection.execute(
                """
                SELECT assessment_id, down_payment

                FROM student_assessments

                WHERE enrollment_id = ?
                AND id_number = ?
                """,
                (enrollment_id, normalized_id)
            ).fetchone()

            if row is None:
                raise ValueError(
                    "Assessment record could not be found."
                )

            assessment_id, amount = row

            _, paid_amount, remaining = _apply_down_payment(
                connection,
                enrollment_id,
                normalized_id
            )

            receipt_number = _save_payment_transaction(
                connection,
                assessment_id,
                enrollment_id,
                normalized_id,
                "Down Payment",
                paid_amount,
                remaining
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    return {
        "receipt_number": receipt_number,
        "amount": float(paid_amount),
        "payment_type": "Down Payment",
        "remaining_balance": float(remaining),
    }


# =====================================================
# RECORD SIMULATED INSTALLMENT PAYMENT WITH RECEIPT
# ATOMIC: PAYMENT + BALANCE + RECEIPT
# =====================================================

def record_simulated_installment_payment(
    assessment_id,
    id_number,
    amount
):

    initialize_payment_transaction_table()

    normalized_id = (id_number or "").strip()

    if not normalized_id:
        raise ValueError("Student ID number is required.")

    payment = money_for_database(amount)

    if payment <= 0:
        raise ValueError("Payment must be greater than zero.")

    with closing(_connect()) as connection:

        connection.execute("BEGIN IMMEDIATE")

        try:

            enrollment_id, remaining = _apply_installment_payment(
                connection,
                assessment_id,
                normalized_id,
                payment
            )

            receipt_number = _save_payment_transaction(
                connection,
                assessment_id,
                enrollment_id,
                normalized_id,
                "Installment Payment",
                payment,
                remaining
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    return {
        "receipt_number": receipt_number,
        "amount": float(payment),
        "payment_type": "Installment Payment",
        "remaining_balance": float(remaining),
    }
