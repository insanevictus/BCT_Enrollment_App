
# =====================================================
# BCT ENROLLMENT SYSTEM - SUBJECT CATALOG
# =====================================================
#
# Each subject contains:
# year, semester, schedule, title, time, days, room, units
#
# Schedule:
# 1 = 1st Schedule
# 2 = 2nd Schedule
# None = No separate schedule specified
#
# LAB subjects are automatically identified by "LAB"
# in their descriptive title.
#
# Hands-on subjects are configured separately below.
# =====================================================


# =====================================================
# HANDS-ON SUBJECT CONFIGURATION
# =====================================================
#
# Add subjects here when they are classified as
# hands-on by the school.
#
# Format:
# ("PROGRAM_KEY", "EXACT SUBJECT TITLE")
#
# This is separate from laboratory classification.
# =====================================================

HANDS_ON_SUBJECTS = {
    # Example:
    # ("BSIT_ACT", "BASIC TROUBLESHOOTING TECHNIQUES"),
}


# =====================================================
# PROGRAM NAMES
# =====================================================

PROGRAM_NAMES = {
    "BSIT_ACT": "BS Information Technology / Associate in Computer Technology",
    "BIT_ELECTRICITY": "BS Industrial Technology - Electricity / Associate in Electrical Technology",
    "BIT_ELECTRONICS": "BS Industrial Technology - Electronics / Associate in Electronics Technology",
    "BS_CPE": "BS Computer Engineering",
    "BSIE": "BS Industrial Engineering",
}


# =====================================================
# PROGRAM ALIASES
# =====================================================

def get_program_key(course, major=None):

    course = (course or "").strip().casefold()
    major = (major or "").strip().casefold()

    # BSIT / ACT
    if course in {
        "bachelor of science in information technology (bsit)".casefold(),
        "associate in computer technology (2 years)".casefold(),
    }:
        return "BSIT_ACT"

    # Industrial Technology - Electricity
    if course == "bachelor of science in industrial technology":

        if major == "electricity":
            return "BIT_ELECTRICITY"

        if major == "electronics":
            return "BIT_ELECTRONICS"

        return None

    # Associate in Electrical Technology
    if course == "associate in electrical technology (2 years)":
        return "BIT_ELECTRICITY"

    # Associate in Electronics Technology
    if course == "associate in electronics technology (2 years)":
        return "BIT_ELECTRONICS"

    # Computer Engineering
    if course == "bachelor of science in computer engineering":
        return "BS_CPE"

    # Industrial Engineering
    if course in {
        "bachelor of science in industrial engineering",
        "bachelor of science in industrial engineering (bsie)",
        "bsie",
    }:
        return "BSIE"

    return None


# =====================================================
# RAW SUBJECT DATA
# =====================================================

RAW_SUBJECTS = {

    # -------------------------------------------------
    # 1. BSIT / ASSOCIATE IN COMPUTER TECHNOLOGY
    # -------------------------------------------------

    "BSIT_ACT": """

1|2|1|COMPUTER PROG 2 LEC|7:30-8:30|MWF|303|3
1|2|1|COMPUTER PROG 2 LAB|8:30-9:30|MWF|201|1
1|2|1|THE CONTEMPORARY WORLD|9:30-10:30|MWF|303|3
1|2|1|LIVING IN THE IT ERA|10:30-11:30|MWF|303|3
1|2|1|DIGITAL LOGIC DESIGN|7:30-8:30|TTHS|303|3
1|2|1|PANITIKANG PILIPINO|8:30-9:30|TTHS|303|3
1|2|1|APPLIED INDUSTRIAL MATHEMATICS|9:30-10:30|TTHS|303|3
1|2|1|BASIC TROUBLESHOOTING TECHNIQUES|10:30-11:30|TTHS|303|1
1|2|1|RHYTHMIC ACTIVITIES|12:30-2:30|W|A-3|2
1|2|1|NATIONAL SERVICE TRAINING PROGRAM 2|10:30-1:30|SUN|303|1.5

1|2|2|APPLIED INDUSTRIAL MATHEMATICS|12:30-1:30|MWF|303|3
1|2|2|COMPUTER PROG 2 LEC|1:30-2:30|MWF|303|3
1|2|2|COMPUTER PROG 2 LAB|2:30-3:30|MWF|201|1
1|2|2|DIGITAL LOGIC DESIGN|3:30-4:30|MWF|303|3
1|2|2|PANITIKANG PILIPINO|11:30-12:30|TTHS|303|3
1|2|2|LIVING IN THE IT ERA|12:30-1:30|TTHS|303|3
1|2|2|BASIC TROUBLESHOOTING TECHNIQUES|1:30-2:30|TTHS|303|1
1|2|2|THE CONTEMPORARY WORLD|2:30-3:30|TTHS|303|3
1|2|2|RHYTHMIC ACTIVITIES|3:30-5:30|T|303|2
1|2|2|NATIONAL SERVICE TRAINING PROGRAM 2|7:30-10:30|SUN|303|1.5

2|4|1|READINGS IN PHILIPPINE HISTORY|7:30-8:30|MWF|403|3
2|4|1|DATA COMM & NETWORKING CONCEPTS LEC|8:30-9:30|MWF|403|3
2|4|1|DATA COMM & NETWORKING CONCEPTS LAB|9:30-10:30|MWF|201|1
2|4|1|ETHICS|10:30-11:30|MWF|403|3
2|4|1|OBJECT ORIENTED PROGRAMMING LEC|7:30-8:30|TTHS|403|3
2|4|1|OBJECT ORIENTED PROGRAMMING LAB|8:30-9:30|TTHS|201|1
2|4|1|SCIENCE, TECHNOLOGY & SOCIETY|9:30-10:30|TTHS|403|3
2|4|1|ADVANCED DATABASE SYSTEMS|10:30-11:30|MWF|201|3
2|4|1|TEAM SPORTS/GAMES|4:30-6:30|W|303|2

2|4|2|DATA COMM & NETWORKING CONCEPTS LEC|12:30-1:30|MWF|403|3
2|4|2|DATA COMM & NETWORKING CONCEPTS LAB|1:30-2:30|MWF|201|1
2|4|2|READINGS IN PHILIPPINE HISTORY|2:30-3:30|MWF|403|3
2|4|2|SCIENCE, TECHNOLOGY & SOCIETY|3:30-4:30|MWF|403|3
2|4|2|ETHICS|12:30-1:30|TTHS|403|3
2|4|2|OBJECT ORIENTED PROGRAMMING LEC|1:30-2:30|TTHS|403|3
2|4|2|OBJECT ORIENTED PROGRAMMING LAB|2:30-3:30|TTHS|201|1
2|4|2|ADVANCED DATABASE SYSTEMS|3:30-4:30|TTHS|201|3
2|4|2|TEAM SPORTS/GAMES|4:30-6:30|F|303|2

3|6|1|INFORMATION ASSURANCE & SECURITY 1|12:30-3:30|MWF|402|3
3|6|1|INTEG PROG & TECHNOLOGIES LEC|3:30-4:30|MWF|402|3
3|6|1|INTEG PROG & TECHNOLOGIES LAB|4:30-5:30|MWF|201|1
3|6|1|COMPUTER GRAPHICS & MULTIMEDIA|5:30-6:30|MWF|201|1
3|6|1|ELEC 2 - GAME DEVELOPMENT LEC|11:30-12:30|TTHS|403|3
3|6|1|ELEC 2 - GAME DEVELOPMENT LAB|12:30-1:30|TTHS|201|1
3|6|1|SYSTEM ANALYSIS & DESIGN|1:30-2:30|TTHS|201|3
3|6|1|HUMAN COMPUTER INTERACTION 2|1:30-2:30|TTHS|403|3

3|6|2|HUMAN COMPUTER INTERACTION 2|1:30-2:30|MWF|403|3
3|6|2|COMPUTER GRAPHICS & MULTIMEDIA|3:30-4:30|MWF|202|1
3|6|2|ELEC 2 - GAME DEVELOPMENT LEC|4:30-5:30|MWF|202|3
3|6|2|ELEC 2 - GAME DEVELOPMENT LAB|5:30-6:30|MWF|202|1
3|6|2|INFORMATION ASSURANCE & SECURITY 1|11:30-2:30|TTHS|204|3
3|6|2|INTEG PROG & TECHNOLOGIES LEC|2:30-3:30|TTHS|202|3
3|6|2|INTEG PROG & TECHNOLOGIES LAB|3:30-4:30|TTHS|202|1
3|6|2|SYSTEM ANALYSIS & DESIGN|4:30-5:30|TTHS|202|3

4|8|-|FIELD TRIPS & SEMINARS|2:30-3:30|W|303|1
4|8|-|CAPSTONE PROJECT & RESEARCH 2|4:30-5:30|MWF|403|3
4|8|-|QUALITY CONSCIOUSNESS, HABITS & PROCESSES|5:30-6:30|MWF|403|3
4|8|-|IT ELEC 3 - COMPUTER-AIDED DRAFTING|6:30-7:30|MWF|201/202|1
4|8|-|OCCUPATIONAL HEALTH & SAFETY|3:30-4:30|TTHS|403|3
4|8|-|FUNDAMENTALS OF ACCOUNTING|4:30-5:30|TTHS|403|3
4|8|-|ROBOTICS & EXPERT SYSTEM LEC|5:30-6:30|TTHS|403|3
4|8|-|ROBOTICS & EXPERT SYSTEM LAB|6:30-7:30|TTHS|201/202|1

1|1|1|COMPUTER PROGRAMMING 1 LEC|7:30-8:30|MWF|303|3
1|1|1|COMPUTER PROGRAMMING 1 LAB|8:30-9:30|MWF|201|1
1|1|1|DC & AC CIRCUITS ANALYSIS LEC|9:30-10:30|MWF|303|3
1|1|1|DC & AC CIRCUITS ANALYSIS LAB|10:30-11:30|MWF|303|1
1|1|1|INTRODUCTION TO COMPUTING|7:30-8:30|TTHS|303|3
1|1|1|MATHEMATICS IN THE MODERN WORLD|8:30-9:30|TTHS|303|3
1|1|1|PURPOSIVE COMMUNICATION|9:30-10:30|TTHS|303|3
1|1|1|SINING NG KOMUNIKASYON|10:30-11:30|TTHS|303|3
1|1|1|PHYSICAL FITNESS|12:30-2:30|W|A-3|2
1|1|1|NATIONAL SERVICE TRAINING PROGRAM 1|10:30-1:30|SUN|303|1.5

1|1|2|COMPUTER PROGRAMMING 1 LEC|12:30-1:30|MWF|303|3
1|1|2|COMPUTER PROGRAMMING 1 LAB|1:30-2:30|MWF|303|1
1|1|2|DC & AC CIRCUITS ANALYSIS LEC|2:30-3:30|MWF|201|3
1|1|2|DC & AC CIRCUITS ANALYSIS LAB|3:30-4:30|MWF|303|1
1|1|2|INTRODUCTION TO COMPUTING|11:30-12:30|TTHS|303|3
1|1|2|MATHEMATICS IN THE MODERN WORLD|12:30-1:30|TTHS|303|3
1|1|2|PURPOSIVE COMMUNICATION|1:30-2:30|TTHS|303|3
1|1|2|SINING NG KOMUNIKASYON|2:30-3:30|TTHS|303|3
1|1|2|PHYSICAL FITNESS|3:30-5:30|T|303|2
1|1|2|NATIONAL SERVICE TRAINING PROGRAM 1|7:30-10:30|SUN|303|1.5

2|3|1|DATA STRUCTURES & ALGORITHMS LEC|7:30-8:30|MWF|403|3
2|3|1|DATA STRUCTURES & ALGORITHMS LAB|8:30-9:30|MWF|403|1
2|3|1|INFORMATION MANAGEMENT|9:30-10:30|MWF|201|3
2|3|1|DISCRETE MATHEMATICS|10:30-11:30|MWF|403|3
2|3|1|COMPUTER TROUBLESHOOTING TECHNIQUES|7:30-8:30|TTHS|403|1
2|3|1|PROBABILITY AND STATISTICS|8:30-9:30|TTHS|201|3
2|3|1|UNDERSTANDING THE SELF|9:30-10:30|TTHS|403|3
2|3|1|ART APPRECIATION|10:30-11:30|MWF|201|3
2|3|1|INDIVIDUAL / DUAL SPORTS GAMES|4:30-6:30|W|303|2

2|3|2|DATA STRUCTURES & ALGORITHMS LEC|12:30-1:30|MWF|403|3
2|3|2|DATA STRUCTURES & ALGORITHMS LAB|1:30-2:30|MWF|201|1
2|3|2|INFORMATION MANAGEMENT|2:30-3:30|MWF|403|3
2|3|2|DISCRETE MATHEMATICS|3:30-4:30|MWF|403|3
2|3|2|COMPUTER TROUBLESHOOTING TECHNIQUES|12:30-1:30|TTHS|403|1
2|3|2|PROBABILITY AND STATISTICS|1:30-2:30|TTHS|403|3
2|3|2|UNDERSTANDING THE SELF|2:30-3:30|TTHS|201|3
2|3|2|ART APPRECIATION|3:30-4:30|TTHS|201|3
2|3|2|INDIVIDUAL / DUAL SPORTS GAMES|4:30-6:30|F|303|2

3|5|1|ELEC 1 - MOBILE PROGRAMMING LEC|12:30-3:30|MWF|402|3
3|5|1|ELEC 1 - MOBILE PROGRAMMING LAB|3:30-4:30|MWF|402|1
3|5|1|SYSTEMS INTEGRATION & ARCHITECTURE LEC|4:30-5:30|MWF|201|3
3|5|1|SYSTEMS INTEGRATION & ARCHITECTURE LAB|5:30-6:30|MWF|201|1
3|5|1|QUANTITATIVE METHODS|11:30-12:30|TTHS|403|3
3|5|1|PLATFORM TECHNOLOGIES|12:30-1:30|TTHS|201|3
3|5|1|INTRO TO HUMAN COMPUTER INTERACTION|1:30-2:30|TTHS|201|3
3|5|1|PHILIPPINE INDIGENOUS COMMUNITIES|1:30-2:30|TTHS|403|3

3|5|2|ELEC 1 - MOBILE PROGRAMMING LEC|1:30-2:30|MWF|403|3
3|5|2|ELEC 1 - MOBILE PROGRAMMING LAB|3:30-4:30|MWF|202|1
3|5|2|SYSTEMS INTEGRATION & ARCHITECTURE LEC|4:30-5:30|MWF|202|3
3|5|2|SYSTEMS INTEGRATION & ARCHITECTURE LAB|5:30-6:30|MWF|202|1
3|5|2|QUANTITATIVE METHODS|11:30-2:30|TTHS|204|3
3|5|2|PLATFORM TECHNOLOGIES|2:30-3:30|TTHS|202|3
3|5|2|INTRO TO HUMAN COMPUTER INTERACTION|3:30-4:30|TTHS|202|3
3|5|2|PHILIPPINE INDIGENOUS COMMUNITIES|4:30-5:30|TTHS|202|3

4|7|-|WEB SYSTEMS AND TECHNOLOGIES LEC|2:30-3:30|W|303|3
4|7|-|WEB SYSTEMS AND TECHNOLOGIES LAB|4:30-5:30|MWF|403|1
4|7|-|CAPSTONE PROJECT & RESEARCH 1|5:30-6:30|MWF|403|3
4|7|-|SYSTEM ADMINISTRATION & MAINTENANCE|6:30-7:30|MWF|201/202|3
4|7|-|INFORMATION ASSURANCE & SECURITY 2|3:30-4:30|TTHS|403|3
4|7|-|APPLICATIONS DEVELOPMENT & EMERGING TECHNOLOGIES|4:30-5:30|TTHS|403|3
4|7|-|LIFE AND WORKS OF DR. JOSE RIZAL|5:30-6:30|TTHS|403|3
4|7|-|SOCIAL AND PROFESSIONAL ISSUES|6:30-7:30|TTHS|201/202|3

4|9|-|INDUSTRY IMMERSION / ON-THE-JOB TRAINING|480 HOURS|||8

""",

    # -------------------------------------------------
    # 2. BS INDUSTRIAL TECHNOLOGY - ELECTRICITY
    #    / ASSOCIATE IN ELECTRICAL TECHNOLOGY
    # -------------------------------------------------

    "BIT_ELECTRICITY": """

1|2|-|LIVING IN THE IT ERA|7:30-8:30|MWF|N-201|3
1|2|-|PANITIKANG PILIPINO|8:30-9:30|MWF|N-201|3
1|2|-|APPLIED INDUSTRIAL MATHEMATICS|9:30-10:30|MWF|N-201|3
1|2|-|THE CONTEMPORARY WORLD|10:30-11:30|MWF|N-201|3
1|2|-|SOLID STATE DEVICES AND CIRCUITS LEC|7:30-8:30|TTHS|N-201|3
1|2|-|SOLID STATE DEVICES AND CIRCUITS LAB|8:30-9:30|TTHS|N-201|1
1|2|-|ELECTRICAL INSTALLATION 1 LEC|9:30-10:30|TTHS|N-202|3
1|2|-|ELECTRICAL INSTALLATION 1 LAB|10:30-11:30|TTHS|N-202|1
1|2|-|RHYTHMIC ACTIVITIES|12:30-2:30|F|WFA-3|2
1|2|-|NATIONAL SERVICE TRAINING PROGRAM 2|1:30-4:30|SUN|WFA-3|1.5

2|4|-|ETHICS|10:30-11:30|MWF|WFA-3|3
2|4|-|ELECTRICAL MACHINERIES 2 LEC|11:30-12:30|MWF|N-201|3
2|4|-|ELECTRICAL MACHINERIES 2 LAB|12:30-1:30|MWF|N-201|1
2|4|-|ELECTRICAL ESTIMATING & PLANNING|1:30-2:30|MWF|WFA-1|3
2|4|-|ELECTRICAL MOTOR CONTROL|8:30-9:30|TTHS|N-202|3
2|4|-|ELECTRICAL CIRCUITS 2|9:30-10:30|TTHS|WFA-5|3
2|4|-|READINGS IN PHILIPPINE HISTORY|10:30-11:30|TTHS|WFA-5|3
2|4|-|SCIENCE, TECHNOLOGY AND SOCIETY|11:30-12:30|TTHS|WFA-5|3
2|4|-|TEAM SPORTS/GAMES|1:30-3:30|S|WFA-3|2

3|6|-|ELT ELECT 1 - DIGITAL ELECTRONICS LEC|10:30-11:30|MWF|N-205|3
3|6|-|ELT ELECT 1 - DIGITAL ELECTRONICS LAB|11:30-12:30|MWF|N-205|1
3|6|-|EE LAWS, CONTRACTS & OBLIGATIONS|12:30-1:30|W|WFA-5|3
3|6|-|ELECTRONICS TECH DRAFTING & DESIGN|1:30-2:30|W|WFA-5|1
3|6|-|ELECT MACHINE REW & MAINTENANCE LEC|12:30-1:30|S|N-202|3
3|6|-|ELECT MACHINE REW & MAINTENANCE LAB|1:30-2:30|S|N-202|1
3|6|-|RENEWABLE ENERGY TECHNOLOGIES|2:30-3:30|TTHS|N-201|3
3|6|-|TECHNOPRENEURSHIP|3:30-4:30|TTHS|WFA-2|3

4|8|-|FIELD TRIPS & SEMINARS|2:30-3:30|F|303|1
4|8|-|CAPSTONE PROJECT & RESEARCH|3:30-4:30|MWF|LIBRARY|3
4|8|-|OCCUPATIONAL HEALTH & SAFETY|4:30-5:30|MWF|302|3
4|8|-|COMMUNICATION EQUIPMENT LEC|11:30-12:30|THS|N-201|3
4|8|-|COMMUNICATION EQUIPMENT LAB|12:30-1:30|THS|N-201|1
4|8|-|POWER ELECTRONICS|1:30-2:30|TTHS|WFA-1|3
4|8|-|SHOP LAYOUT & MANAGEMENT|2:30-3:30|TTHS|WFA-1|3
4|8|-|ELT ELEC 3 - COMPUTER-AIDED DRAFTING|4:30-5:30|TTHS|201|1

""",

    # -------------------------------------------------
    # 3. BS INDUSTRIAL TECHNOLOGY - ELECTRONICS
    #    / ASSOCIATE IN ELECTRONICS TECHNOLOGY
    # -------------------------------------------------

    "BIT_ELECTRONICS": """

1|2|-|LIVING IN THE IT ERA|7:30-8:30|MWF|N-201|3
1|2|-|PANITIKANG PILIPINO|8:30-9:30|MWF|N-201|3
1|2|-|APPLIED INDUSTRIAL MATHEMATICS|9:30-10:30|MWF|N-201|3
1|2|-|THE CONTEMPORARY WORLD|10:30-11:30|MWF|N-201|3
1|2|-|SOLID STATE DEVICES AND CIRCUITS LEC|7:30-8:30|TTHS|N-201|3
1|2|-|SOLID STATE DEVICES AND CIRCUITS LAB|8:30-9:30|TTHS|N-201|1
1|2|-|PHILIPPINE ELECTRONICS CODE|9:30-10:30|TTH|N-201|3
1|2|-|ELECTRONICS TECH DRAFTING & DESIGN|10:30-11:30|TTH|N-201|1
1|2|-|RHYTHMIC ACTIVITIES|12:30-2:30|F|WFA-3|2
1|2|-|NATIONAL SERVICE TRAINING PROGRAM 2|1:30-4:30|SUN|WFA-3|1.5

2|4|-|ETHICS|10:30-11:30|MWF|WFA-3|3
2|4|-|COMMUNICATION EQUIPMENT LEC|11:30-12:30|M|N-204|3
2|4|-|COMMUNICATION EQUIPMENT LAB|12:30-1:30|MW|N-204|1
2|4|-|COLOR MONITORS & VIDEO SYSTEMS|11:30-12:30|W|N-204|3
2|4|-|READINGS IN PHILIPPINE HISTORY|10:30-11:30|TTHS|WFA-5|3
2|4|-|SCIENCE, TECHNOLOGY AND SOCIETY|11:30-12:30|TTHS|WFA-5|3
2|4|-|ADVANCED TROUBLESHOOTING TECHNIQUES|12:30-1:30|T|WFA-2|1
2|4|-|RADIO LAWS & REGULATIONS|1:30-2:30|T|WFA-2|3
2|4|-|TEAM SPORTS/GAMES|1:30-3:30|S|WFA-3|2

3|6|-|ET ELEC 1 - NETWORKING 1 LEC|8:30-9:30|M|202|3
3|6|-|ET ELEC 1 - NETWORKING 1 LAB|8:30-9:30|WF|202|1
3|6|-|DIGITAL ELECTRONICS LEC|10:30-11:30|MWF|N-205|3
3|6|-|DIGITAL ELECTRONICS LAB|11:30-12:30|MWF|N-205|1
3|6|-|MICROCONTROLLERS LEC|12:30-1:30|T|N-204|3
3|6|-|MICROCONTROLLERS LAB|1:30-2:30|T|N-204|1
3|6|-|RENEWABLE ENERGY TECHNOLOGIES|2:30-3:30|TTHS|N-201|3
3|6|-|TECHNOPRENEURSHIP|3:30-4:30|TTHS|WFA-2|3

4|8|-|INTRODUCTION TO FIBER OPTICS|2:30-3:30|M|203|3
4|8|-|FIELD TRIPS & SEMINARS|2:30-3:30|F|303|1
4|8|-|CAPSTONE PROJECT & RESEARCH|3:30-4:30|MWF|LIBRARY|3
4|8|-|OCCUPATIONAL HEALTH & SAFETY|4:30-5:30|MWF|302|3
4|8|-|MECHATRONICS LEC|11:30-12:30|T|N-201|3
4|8|-|MECHATRONICS LAB|12:30-1:30|T|N-201|1
4|8|-|POWER ELECTRONICS|1:30-2:30|TTHS|WFA-1|3
4|8|-|SHOP LAYOUT & MANAGEMENT|2:30-3:30|TTHS|WFA-1|3
4|8|-|ET ELEC 3 - COMPUTER-AIDED DRAFTING|4:30-5:30|TTHS|201|1

""",

    # -------------------------------------------------
    # 4. BS COMPUTER ENGINEERING
    # -------------------------------------------------

    "BS_CPE": """

1|2|-|PHYSICS FOR ENGINEERS LEC|7:30-8:30|MWF|WFA-4|3
1|2|-|PHYSICS FOR ENGINEERS LAB|8:30-9:30|MWF|WFA-4|1
1|2|-|PANITIKANG PILIPINO|9:30-10:30|MWF|WFA-4|3
1|2|-|CALCULUS 2|10:30-11:30|MWF|WFA-4|3
1|2|-|PROGRAMMING LOGIC & DESIGN LEC|7:30-8:30|T|203|3
1|2|-|PROGRAMMING LOGIC & DESIGN LAB|8:30-9:30|TTH|202|1
1|2|-|COMPUTER ENGINEERING AS A DISCIPLINE|7:30-8:30|THS|203|1
1|2|-|LIVING IN THE IT ERA|9:30-10:30|TTHS|302|3
1|2|-|THE CONTEMPORARY WORLD|10:30-11:30|TTHS|302|3
1|2|-|RHYTHMIC ACTIVITIES|12:30-2:30|MWF|A-3|2
1|2|-|NATIONAL SERVICE TRAINING PROGRAM 2|10:30-1:30|SUN|303|1.5

2|4|-|ETHICS|12:30-1:30|MWF|302|3
2|4|-|SCIENCE, TECHNOLOGY & SOCIETY|1:30-2:30|MWF|302|3
2|4|-|OBJECT ORIENTED PROG LEC|2:30-3:30|M|202|3
2|4|-|OBJECT ORIENTED PROG LAB|2:30-3:30|WF|202|1
2|4|-|COMPUTER ENGG DRAFTING & DESIGN|10:30-11:30|S|202|1
2|4|-|ADVANCED MATHEMATICS|12:30-1:30|TTHS|WFA-5|3
2|4|-|READINGS IN PHILIPPINE HISTORY|1:30-2:30|TTHS|WFA-4|3
2|4|-|SOLID STATE DEVICES & CIRCUITS LEC|2:30-3:30|T|WFA-5|3
2|4|-|SOLID STATE DEVICES & CIRCUITS LAB|3:30-4:30|T|WFA-5|1
2|4|-|TEAM SPORTS/GAMES|9:30-11:30|TH|WFA-3|2

3|6|-|SOFTWARE DESIGN LEC|7:30-8:30|M|202|3
3|6|-|SOFTWARE DESIGN LAB|7:30-8:30|WF|202|1
3|6|-|CPE ELEC 1 - NETWORKING 1 LEC|8:30-9:30|M|202|3
3|6|-|CPE ELEC 1 - NETWORKING 1 LAB|8:30-9:30|WF|202|1
3|6|-|MICROCONTROLLERS LEC|12:30-1:30|T|N-204|3
3|6|-|MICROCONTROLLERS LAB|1:30-2:30|T|N-204|1
3|6|-|CPE ELEC 2 - HDL DESIGN|1:30-2:30|TH|WFA-2|3
3|6|-|HUMAN REPRODUCTION|2:30-3:30|TTHS|WFA-2|3
3|6|-|TECHNOPRENEURSHIP|3:30-4:30|TTHS|WFA-2|3

4|8|-|FIELD TRIPS & SEMINARS|2:30-3:30|F|303|1
4|8|-|COMPUTER-AIDED DRAFTING|4:30-5:30|MWF|201|1
4|8|-|OCCUPATIONAL HEALTH & SAFETY|2:30-3:30|TTHS|204|3
4|8|-|EMERGING TECHNOLOGIES IN CPE|3:30-4:30|TBA|TBA|3
4|8|-|COMPUTER NETWORKS & SECURITY LEC|12:30-1:30|TBA|TBA|3
4|8|-|COMPUTER NETWORKS & SECURITY LAB|1:30-2:30|TBA|TBA|1
4|8|-|EMBEDDED SYSTEMS LEC|11:30-12:30|TBA|TBA|3
4|8|-|EMBEDDED SYSTEMS LAB|12:30-1:30|TBA|TBA|1
4|8|-|CPE PRACTICE & DESIGN 2|1:30-2:30|TBA|TBA|2

""",

    # -------------------------------------------------
    # 5. BS INDUSTRIAL ENGINEERING
    # -------------------------------------------------

    "BSIE": """

1|2|-|PHYSICS FOR ENGINEERS LEC|7:30-8:30|MWF|WFA-4|3
1|2|-|PHYSICS FOR ENGINEERS LAB|8:30-9:30|MWF|WFA-4|1
1|2|-|PANITIKANG PILIPINO|9:30-10:30|MWF|WFA-4|3
1|2|-|CALCULUS 2|10:30-11:30|MWF|WFA-4|3
1|2|-|PRINCIPLES OF ECONOMICS|7:30-8:30|TTHS|302|3
1|2|-|BASIC ACCOUNTING|8:30-9:30|TTHS|302|3
1|2|-|LIVING IN THE IT ERA|9:30-10:30|TTHS|302|3
1|2|-|THE CONTEMPORARY WORLD|10:30-11:30|TTHS|302|3
1|2|-|RHYTHMIC ACTIVITIES|12:30-2:30|MWF|A-3|2
1|2|-|NATIONAL SERVICE TRAINING PROGRAM 2|1:30-4:30|SUN|303|1.5

2|4|-|ETHICS|12:30-1:30|MWF|302|3
2|4|-|SCIENCE, TECHNOLOGY & SOCIETY|1:30-2:30|MWF|302|3
2|4|-|STATISTICAL ANALYSIS FOR IE 2|2:30-3:30|WF|302|3
2|4|-|MANAGERIAL ACCOUNTING|3:30-4:30|WF|302|3
2|4|-|ADVANCED MATHEMATICS|12:30-1:30|TTHS|WFA-5|3
2|4|-|READINGS IN PHILIPPINE HISTORY|1:30-2:30|TTHS|WFA-4|3
2|4|-|ENGINEERING MECHANICS|2:30-3:30|TTH|WFA-4|3
2|4|-|THERMODYNAMICS|3:30-4:40|TTH|WFA-4|3
2|4|-|TEAM SPORTS/GAMES|9:30-11:30|TH|WFA-3|2

3|6|-|OPERATION RESEARCH 2|2:30-3:30|WF|203|3
3|6|-|OPERATIONS MANAGEMENT LEC|3:30-4:30|MW|203|3
3|6|-|OPERATIONS MANAGEMENT LAB|3:30-4:30|F|203|1
3|6|-|ENVIRONMENTAL SCIENCE|4:30-5:30|MWF|203|3
3|6|-|INDUSTRIAL MATERIALS & PROCESS 2 LEC|12:30-1:30|THS|N-204|3
3|6|-|INDUSTRIAL MATERIALS & PROCESS 2 LAB|1:30-2:30|THS|N-204|1
3|6|-|HUMAN REPRODUCTION|2:30-3:30|TTHS|WFA-2|3
3|6|-|TECHNOPRENEURSHIP|3:30-4:30|TTHS|WFA-2|3

4|8|-|SYSTEMS ENGINEERING|2:30-3:30|MW|204|3
4|8|-|FIELD TRIPS & SEMINARS|2:30-3:30|F|303|1
4|8|-|IE ELEC 3 - INTELLECTUAL PROPERTY RIGHTS|3:30-4:30|WF|204|3
4|8|-|ERGONOMICS 2 LEC|4:30-5:30|M|204|2
4|8|-|ERGONOMICS 2 LAB|4:30-5:30|WF|204|1
4|8|-|OCCUPATIONAL HEALTH & SAFETY|2:30-3:30|TTHS|204|3
4|8|-|IE CAPSTONE PROJECT LEC|3:30-4:30|T|204|1
4|8|-|IE CAPSTONE PROJECT LAB|3:30-4:30|THS|204|2
4|8|-|COMPUTER-AIDED DRAFTING|4:30-5:30|TTHS|201|1

""",

}


# =====================================================
# REPORTED TOTAL UNITS
# =====================================================
#
# These are the totals printed in your supplied sample.
# They are reference values only.
#
# The enrollment calculator will sum the individual
# selected subjects rather than relying on these totals.
# =====================================================

REPORTED_TOTAL_UNITS = {

    # BSIT / ACT
    ("BSIT_ACT", 1, 1, 1): 23.5,
    ("BSIT_ACT", 1, 1, 2): 23.5,
    ("BSIT_ACT", 1, 2, 1): 23.5,
    ("BSIT_ACT", 1, 2, 2): 23.5,
    ("BSIT_ACT", 2, 3, 1): 22,
    ("BSIT_ACT", 2, 3, 2): 22,
    ("BSIT_ACT", 2, 4, 1): 22,
    ("BSIT_ACT", 2, 4, 2): 22,
    ("BSIT_ACT", 3, 5, 1): 20,
    ("BSIT_ACT", 3, 5, 2): 20,
    ("BSIT_ACT", 3, 6, 1): 18,
    ("BSIT_ACT", 3, 6, 2): 18,
    ("BSIT_ACT", 4, 7, None): 22,
    ("BSIT_ACT", 4, 8, None): 18,
    ("BSIT_ACT", 4, 9, None): 8,

    # Industrial Technology - Electricity
    ("BIT_ELECTRICITY", 1, 2, None): 23.5,
    ("BIT_ELECTRICITY", 2, 4, None): 24,
    ("BIT_ELECTRICITY", 3, 6, None): 18,
    ("BIT_ELECTRICITY", 4, 8, None): 18,

    # Industrial Technology - Electronics
    ("BIT_ELECTRONICS", 1, 2, None): 23.5,
    ("BIT_ELECTRONICS", 2, 4, None): 22,
    ("BIT_ELECTRONICS", 3, 6, None): 18,
    ("BIT_ELECTRONICS", 4, 8, None): 21,

    # Computer Engineering
    ("BS_CPE", 1, 2, None): 24.5,
    ("BS_CPE", 2, 4, None): 23,
    ("BS_CPE", 3, 6, None): 21,
    ("BS_CPE", 4, 8, None): 18,

    # Industrial Engineering
    ("BSIE", 1, 2, None): 26,
    ("BSIE", 2, 4, None): 26,
    ("BSIE", 3, 6, None): 20,

}


# =====================================================
# PARSE SUBJECT DATA
# =====================================================

def _parse_program_subjects(program_key, raw_data):

    subjects = []

    for index, line in enumerate(
        raw_data.strip().splitlines(),
        start=1
    ):

        line = line.strip()

        if not line:
            continue

        parts = line.split("|")

        if len(parts) != 8:
            raise ValueError(
                f"Invalid subject record in {program_key}: {line}"
            )

        (
            year,
            semester,
            schedule,
            title,
            time,
            days,
            room,
            units
        ) = parts

        units_value = float(units)

        if units_value.is_integer():
            units_value = int(units_value)

        schedule_value = (
            None if schedule == "-"
            else int(schedule)
        )

        is_lab = "LAB" in title.upper()

        is_hands_on = (
            program_key,
            title.strip().casefold()
        ) in {
            (key, name.casefold())
            for key, name in HANDS_ON_SUBJECTS
        }

        subjects.append({

            "subject_id": (
                f"{program_key}-"
                f"{int(year)}-"
                f"{int(semester)}-"
                f"{schedule_value or 0}-"
                f"{index:03d}"
            ),

            "program_key": program_key,

            "year_level": int(year),

            "semester": int(semester),

            "schedule": schedule_value,

            "title": title.strip(),

            "time": time.strip(),

            "days": days.strip(),

            "room": room.strip(),

            "units": units_value,

            "is_lab": is_lab,

            "is_hands_on": is_hands_on,

        })

    return subjects


# =====================================================
# BUILD COMPLETE CATALOG
# =====================================================

SUBJECT_CATALOG = {

    program_key: _parse_program_subjects(
        program_key,
        raw_data
    )

    for program_key, raw_data in RAW_SUBJECTS.items()

}


# =====================================================
# GET SUBJECTS
# =====================================================

def get_subjects(
    program_key,
    year_level,
    semester,
    schedule=None
):

    subjects = SUBJECT_CATALOG.get(
        program_key,
        []
    )

    return [

        subject.copy()

        for subject in subjects

        if subject["year_level"] == int(year_level)

        and subject["semester"] == int(semester)

        and (
            schedule is None
            or subject["schedule"] == int(schedule)
        )

    ]


# =====================================================
# GET AVAILABLE YEAR LEVELS
# =====================================================

def get_available_year_levels(program_key):

    subjects = SUBJECT_CATALOG.get(
        program_key,
        []
    )

    return sorted({

        subject["year_level"]

        for subject in subjects

    })


# =====================================================
# GET AVAILABLE SEMESTERS
# =====================================================

def get_available_semesters(
    program_key,
    year_level
):

    subjects = SUBJECT_CATALOG.get(
        program_key,
        []
    )

    return sorted({

        subject["semester"]

        for subject in subjects

        if subject["year_level"] == int(year_level)

    })


# =====================================================
# GET AVAILABLE SCHEDULES
# =====================================================

def get_available_schedules(
    program_key,
    year_level,
    semester
):

    subjects = get_subjects(
        program_key,
        year_level,
        semester
    )

    return sorted({

        subject["schedule"]

        for subject in subjects

        if subject["schedule"] is not None

    })


# =====================================================
# GET TOTAL UNITS
# =====================================================

def calculate_total_units(selected_subjects):

    return sum(
        subject["units"]
        for subject in selected_subjects
    )


# =====================================================
# COUNT LAB SUBJECTS
# =====================================================

def count_lab_subjects(selected_subjects):

    return sum(
        1
        for subject in selected_subjects
        if subject["is_lab"]
    )


# =====================================================
# COUNT HANDS-ON SUBJECTS
# =====================================================

def count_hands_on_subjects(selected_subjects):

    return sum(
        1
        for subject in selected_subjects
        if subject["is_hands_on"]
    )


# =====================================================
# GET REPORTED TOTAL UNITS
# =====================================================

def get_reported_total_units(
    program_key,
    year_level,
    semester,
    schedule=None
):

    return REPORTED_TOTAL_UNITS.get(
        (
            program_key,
            int(year_level),
            int(semester),
            schedule
        )
    )
