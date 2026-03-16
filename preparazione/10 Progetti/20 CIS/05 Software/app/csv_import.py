from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO

from app.data_access import ContactCreate, ContactRepository, OrganizationCreate, OrganizationRepository


REQUIRED_COLUMNS = {"organization_name"}


@dataclass(slots=True)
class ImportResult:
    imported_organizations: int = 0
    imported_contacts: int = 0
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def import_leads_csv(
    csv_text: str,
    organizations: OrganizationRepository,
    contacts: ContactRepository,
) -> ImportResult:
    result = ImportResult()
    delimiter = _detect_delimiter(csv_text)
    reader = csv.DictReader(StringIO(csv_text), delimiter=delimiter)

    if reader.fieldnames is None:
        result.errors.append("Il file CSV e vuoto oppure non contiene intestazioni.")
        return result

    normalized_fieldnames = {field.strip() for field in reader.fieldnames if field}
    missing_columns = REQUIRED_COLUMNS - normalized_fieldnames
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        result.errors.append(f"Manca la colonna obbligatoria: {missing}.")
        return result

    for row_number, row in enumerate(reader, start=2):
        organization_name = (row.get("organization_name") or "").strip()
        if not organization_name:
            result.errors.append(
                f"Riga {row_number}: organization_name e obbligatorio."
            )
            continue

        organization_id = organizations.create(
            OrganizationCreate(
                name=organization_name,
                organization_type=_clean(row.get("organization_type")),
                sector=_clean(row.get("sector")),
                city=_clean(row.get("city")),
                region=_clean(row.get("region")),
                country=_clean(row.get("country")),
                website=_clean(row.get("website")),
                phone=_clean(row.get("organization_phone")),
                email=_clean(row.get("organization_email")),
                source=_clean(row.get("source")) or "csv_import",
                notes=_clean(row.get("organization_notes")),
            )
        )
        result.imported_organizations += 1

        contact_full_name = _clean(row.get("contact_full_name"))
        contact_email = _clean(row.get("contact_email"))
        contact_phone = _clean(row.get("contact_phone"))
        contact_role = _clean(row.get("contact_role"))

        if any([contact_full_name, contact_email, contact_phone, contact_role]):
            contacts.create(
                ContactCreate(
                    organization_id=organization_id,
                    first_name=_clean(row.get("contact_first_name")),
                    last_name=_clean(row.get("contact_last_name")),
                    full_name=contact_full_name,
                    role=contact_role,
                    email=contact_email,
                    phone=contact_phone,
                    linkedin_url=_clean(row.get("contact_linkedin_url")),
                    notes=_clean(row.get("contact_notes")),
                )
            )
            result.imported_contacts += 1

    return result


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _detect_delimiter(csv_text: str) -> str:
    sample = csv_text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        return dialect.delimiter
    except csv.Error:
        first_line = sample.splitlines()[0] if sample.splitlines() else ""
        if ";" in first_line and "," not in first_line:
            return ";"
        return ","
