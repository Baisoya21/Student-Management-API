from datetime import datetime


#This function will clean school_code data.
def clean_school_code(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() in ("n/a", "null", "-"):
        return None

    normalized_value = value.upper().replace(".", "")

    school_mapping = {
        "GPS": "GPS",
        "SVS": "SVS",
        "GREENFIELD": "GPS",
        "GREENFIELD PUBLIC": "GPS",
        "SUNRISE VALLEY": "SVS",
        "SUNRISE": "SVS",
    }

    return school_mapping.get(normalized_value)


#This will clean the roll_no daata
def clean_roll_no(value):
    if value is None:
        return None

    value = str(value).strip().upper()

    if value == "" or value in ("N/A", "NULL", "-"):
        return None

    if value.startswith("ROLL "):
        value = value[5:]
    elif value.startswith("R-"):
        value = value[2:]
    elif value.startswith("R"):
        value = value[1:]

    if value.endswith(".0"):
        value = value[:-2]

    if not value.isdigit():
        return None

    return value


#This will clean inconsistent First_name
def clean_first_name(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() in ("n/a", "null", "-"):
        return None

    first_name = value.split()[0]

    return first_name.capitalize()


#This will clean inconsistent Last_name
def clean_last_name(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() in ("n/a", "null", "-"):
        return None

    return value.title()

def clean_student_names(first_name_value, last_name_value):
    first_name = clean_first_name(first_name_value)
    last_name = clean_last_name(last_name_value)

    if first_name_value is not None:
        original_first_name = str(first_name_value).strip()
    else:
        original_first_name = ""

    if original_first_name and first_name is not None:
        name_parts = original_first_name.split()

        if len(name_parts) > 1:
            first_name = name_parts[0].capitalize()

            if last_name is None:
                last_name = " ".join(name_parts[1:]).title()

    return first_name, last_name


# This will inconsistancy in fathers name or any titles like MR.or mr.
def clean_father_name(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() in ("n/a", "null", "-"):
        return None

    words = value.split()

    if words[0].lower().rstrip(".") in ("mr", "mrs", "ms", "dr", "shri"):
        words = words[1:]

    if not words:
        return None

    cleaned_name = " ".join(words).title()

    return cleaned_name


#This will remove the inconsistent or invalid classes
def clean_class(value):
    if value is None:
        return None

    value = str(value).strip().upper()

    if value == "" or value in ("N/A", "NULL", "-"):
        return None

    class_mapping = {
        "9": "9",
        "9TH": "9",
        "CLASS 9": "9",
        "IX": "9",
        "10": "10",
        "10TH": "10",
        "CLASS 10": "10",
        "X": "10",
        "11": "11",
        "11TH": "11",
        "CLASS 11": "11",
        "XI": "11",
        "12": "12",
        "12TH": "12",
        "CLASS 12": "12",
        "XII": "12",
    }

    return class_mapping.get(value)


# will remove the inconsisatncy or invalid section outside A , B & C
def clean_section(value):
    if value is None:
        return None

    value = str(value).strip().upper()

    if value == "" or value in ("N/A", "NULL", "-"):
        return None

    section_mapping = {
        "A": "A",
        "SEC A": "A",
        "B": "B",
        "SEC B": "B",
        "C": "C",
        "SEC C": "C",
    }

    return section_mapping.get(value)


#Will remove any ivalid email formats or missing mails
# This function will clean email data.
def clean_email(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    if value in ("", "n/a", "na", "null", "-"):
        return None

    if value.count("@") != 1:
        return None

    local_part, domain = value.split("@")

    if not local_part or not domain:
        return None

    if "." not in domain:
        return None

    if domain.startswith(".") or domain.endswith("."):
        return None

    if ".." in value:
        return None

    return value


#Will remove any invalid date formats or nulls

def clean_date_of_birth(value):
    if value is None:
        return None

    value = str(value).strip()

    if value.lower() in ("", "n/a", "null", "-", "na", "unknown"):
        return None

    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%y",
        "%d.%m.%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%B %d %Y",
    ]

    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(value, date_format)

            if parsed_date.date() > datetime.today().date():
                return None

            return parsed_date.strftime("%Y-%m-%d")

        except ValueError:
            continue

    return None