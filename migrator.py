import csv
from pathlib import Path

INPUT_CSV = "the_knot_guest_list.csv"
OUTPUT_CSV = "with_joy_guest_list.csv"

JOY_HEADERS = [
    "First Name",
    "Last Name",
    "Email (Optional)",
    "Phone Number (Optional)",
    "Name on Envelope (Optional)",
    "Party (Optional)",
    "Address Line 1 (Optional)",
    "Address Line 2 (Optional)",
    "City (Optional)",
    "State/Region (Optional)",
    "Postal Code (Optional)",
    "Country (Optional)",
    "Tags (Optional)",
]

KNOT_TO_JOY_DIRECT_MAP = {
    "First Name": "First Name",
    "Last Name": "Last Name",
    "Email": "Email (Optional)",
    "Phone": "Phone Number (Optional)",
    "Party": "Party (Optional)",
    "Street Address 1": "Address Line 1 (Optional)",
    "Street Address 2": "Address Line 2 (Optional)",
    "City": "City (Optional)",
    "State/Province": "State/Region (Optional)",
    "Zip/Postal Code": "Postal Code (Optional)",
    "Country": "Country (Optional)",
}

EVENT_FIELDS = [
    "Nigerian Traditional Ceremony - RSVP",
    "Nigerian Traditional Ceremony - Thank You Sent",
    "Nigerian Traditional Ceremony - Gift Received",
    "Wedding Ceremony - RSVP",
    "Wedding Ceremony - Thank You Sent",
    "Wedding Ceremony - Gift Received",
    "Reception - RSVP",
    "Reception - Thank You Sent",
    "Reception - Gift Received",
    "Send a note to the couple?",
]

def clean(value):
    if value is None:
        return ""
    return str(value).strip()

def truthy(value):
    v = clean(value).lower()
    return v in {"yes", "y", "true", "1", "sent", "received"}

def nonempty(value):
    return clean(value) != ""

def build_name_on_envelope(row):
    """
    Preference:
    1. Party, if present
    2. First + Last
    """
    party = clean(row.get("Party"))
    if party:
        return party

    first = clean(row.get("First Name"))
    last = clean(row.get("Last Name"))
    return f"{first} {last}".strip()

def normalize_tag_piece(text):
    return clean(text).replace("|", "/")

def build_tags(row):
    tags = []

    # Preserve general notes as a tag only if short.
    # You may want to remove this if your notes are long/freeform.
    my_notes = clean(row.get("My Notes"))
    if my_notes:
        tags.append(f"note:{normalize_tag_piece(my_notes)}")

    # Preserve event-specific RSVP and gift workflow info in tags
    for field in EVENT_FIELDS:
        value = clean(row.get(field))
        if not value:
            continue

        field_tag = field.lower()
        field_tag = field_tag.replace(" - ", ":")
        field_tag = field_tag.replace(" ", "_")
        field_tag = field_tag.replace("?", "")

        value_tag = value.lower().replace(" ", "_")
        tags.append(f"{field_tag}:{value_tag}")

    return "|".join(tags)

def transform_row(row):
    out = {header: "" for header in JOY_HEADERS}

    # Direct mappings
    for knot_col, joy_col in KNOT_TO_JOY_DIRECT_MAP.items():
        out[joy_col] = clean(row.get(knot_col))

    # Derived fields
    out["Name on Envelope (Optional)"] = build_name_on_envelope(row)
    out["Tags (Optional)"] = build_tags(row)

    return out

def main():
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)

    if not input_path.exists():
        raise FileNotFoundError(f"Could not find input file: {INPUT_CSV}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    transformed_rows = [transform_row(row) for row in rows]

    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=JOY_HEADERS)
        writer.writeheader()
        writer.writerows(transformed_rows)

    print(f"Done. Wrote {len(transformed_rows)} guests to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
