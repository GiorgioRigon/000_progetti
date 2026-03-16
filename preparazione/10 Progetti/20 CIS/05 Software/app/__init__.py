from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

from app.csv_import import ImportResult, import_leads_csv
from app.data_access import (
    ContactCreate,
    ContactRepository,
    Database,
    OrganizationCreate,
    OrganizationRepository,
)


def create_app() -> Flask:
    base_dir = Path(__file__).resolve().parent.parent
    template_dir = base_dir / "templates"
    app = Flask(__name__, template_folder=str(template_dir))
    database = Database()
    organizations = OrganizationRepository(database)
    contacts = ContactRepository(database)

    @app.get("/")
    def home() -> str:
        return render_template("home.html")

    @app.route("/organizations", methods=["GET", "POST"])
    def organizations_list() -> str:
        import_result = ImportResult()

        if request.method == "POST":
            form_type = request.form.get("form_type")

            if form_type == "manual":
                name = request.form.get("name", "").strip()
                if name:
                    organizations.create(
                        OrganizationCreate(
                            name=name,
                            organization_type=request.form.get("organization_type", "").strip() or None,
                            sector=request.form.get("sector", "").strip() or None,
                            city=request.form.get("city", "").strip() or None,
                            region=request.form.get("region", "").strip() or None,
                            country=request.form.get("country", "").strip() or None,
                            website=request.form.get("website", "").strip() or None,
                            email=request.form.get("email", "").strip() or None,
                            phone=request.form.get("phone", "").strip() or None,
                            notes=request.form.get("notes", "").strip() or None,
                        )
                    )
                    return redirect(url_for("organizations_list"))

                import_result.errors.append("Il nome della organization e obbligatorio.")

            elif form_type == "csv_import":
                uploaded_file = request.files.get("csv_file")
                if uploaded_file is None or uploaded_file.filename == "":
                    import_result.errors.append("Seleziona un file CSV da importare.")
                else:
                    try:
                        csv_text = uploaded_file.read().decode("utf-8-sig")
                    except UnicodeDecodeError:
                        import_result.errors.append(
                            "Il file non e in formato UTF-8 leggibile."
                        )
                    else:
                        import_result = import_leads_csv(
                            csv_text=csv_text,
                            organizations=organizations,
                            contacts=contacts,
                        )

        return render_template(
            "organizations.html",
            organizations=organizations.list_all(),
            import_result=import_result,
        )

    @app.route("/organizations/<int:organization_id>", methods=["GET", "POST"])
    def organization_detail(organization_id: int) -> str:
        organization = organizations.get(organization_id)
        if organization is None:
            abort(404)

        if request.method == "POST":
            form_type = request.form.get("form_type", "organization")

            if form_type == "organization":
                name = request.form.get("name", "").strip()
                if not name:
                    abort(400, description="Il nome della organization e obbligatorio.")

                organizations.update(
                    organization_id,
                    OrganizationCreate(
                        name=name,
                        organization_type=request.form.get("organization_type", "").strip() or None,
                        sector=request.form.get("sector", "").strip() or None,
                        city=request.form.get("city", "").strip() or None,
                        region=request.form.get("region", "").strip() or None,
                        country=request.form.get("country", "").strip() or None,
                        website=request.form.get("website", "").strip() or None,
                        email=request.form.get("email", "").strip() or None,
                        phone=request.form.get("phone", "").strip() or None,
                        notes=request.form.get("notes", "").strip() or None,
                    ),
                )
            elif form_type == "contact":
                full_name = request.form.get("full_name", "").strip()
                first_name = request.form.get("first_name", "").strip()
                last_name = request.form.get("last_name", "").strip()
                if not any([full_name, first_name, last_name]):
                    abort(400, description="Inserisci almeno un nome per il contatto.")

                contacts.create(
                    ContactCreate(
                        organization_id=organization_id,
                        first_name=first_name or None,
                        last_name=last_name or None,
                        full_name=full_name or None,
                        role=request.form.get("role", "").strip() or None,
                        email=request.form.get("email", "").strip() or None,
                        phone=request.form.get("phone", "").strip() or None,
                        linkedin_url=request.form.get("linkedin_url", "").strip() or None,
                        notes=request.form.get("notes", "").strip() or None,
                    )
                )
            elif form_type == "edit_contact":
                contact_id_raw = request.form.get("contact_id", "").strip()
                if not contact_id_raw.isdigit():
                    abort(400, description="ID contatto non valido.")

                full_name = request.form.get("full_name", "").strip()
                first_name = request.form.get("first_name", "").strip()
                last_name = request.form.get("last_name", "").strip()
                if not any([full_name, first_name, last_name]):
                    abort(400, description="Inserisci almeno un nome per il contatto.")

                contact_id = int(contact_id_raw)
                existing_contact = contacts.get(contact_id)
                if existing_contact is None or existing_contact["organization_id"] != organization_id:
                    abort(404)

                contacts.update(
                    contact_id,
                    ContactCreate(
                        organization_id=organization_id,
                        first_name=first_name or None,
                        last_name=last_name or None,
                        full_name=full_name or None,
                        role=request.form.get("role", "").strip() or None,
                        email=request.form.get("email", "").strip() or None,
                        phone=request.form.get("phone", "").strip() or None,
                        linkedin_url=request.form.get("linkedin_url", "").strip() or None,
                        notes=request.form.get("notes", "").strip() or None,
                    ),
                )

            return redirect(url_for("organization_detail", organization_id=organization_id))

        organization = organizations.get(organization_id)

        return render_template(
            "organization_detail.html",
            organization=organization,
            contacts=contacts.list_by_organization(organization_id),
        )

    return app
