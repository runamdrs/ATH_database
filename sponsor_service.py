import mysql.connector

from database import (
    delete_sponsor,
    get_all_sponsors,
    insert_sponsor,
    update_sponsor,
)


def list_sponsors():
    return get_all_sponsors()


def get_sponsor_types():
    types = {
        sponsor["SponsorType"]
        for sponsor in get_all_sponsors()
        if sponsor["SponsorType"]
    }
    return ["All"] + sorted(types)


def search_sponsors(search="", sponsor_type="All"):
    search = (search or "").lower()
    results = []
    for sponsor in get_all_sponsors():
        searchable_text = " ".join([
            str(sponsor["Company"] or ""),
            str(sponsor["SponsorType"] or ""),
            str(sponsor["ContactInformation"] or ""),
        ]).lower()
        type_matches = (
            sponsor_type == "All"
            or sponsor["SponsorType"] == sponsor_type
        )
        if search in searchable_text and type_matches:
            results.append(sponsor)
    return results


def _duplicate_company(company, sponsor_id=None):
    normalized_company = company.casefold()
    return any(
        row["Company"].strip().casefold() == normalized_company
        and row["SponsorID"] != sponsor_id
        for row in get_all_sponsors()
    )


def add_sponsor(company, sponsor_type, contact_information):
    company = (company or "").strip()
    sponsor_type = (sponsor_type or "").strip() or None
    contact_information = (contact_information or "").strip() or None

    if not company:
        return False, "Company is required."
    if len(company) > 150:
        return False, "Company must be 150 characters or fewer."
    if sponsor_type and len(sponsor_type) > 50:
        return False, "Sponsor type must be 50 characters or fewer."
    if contact_information and len(contact_information) > 200:
        return False, "Contact information must be 200 characters or fewer."

    try:
        if _duplicate_company(company):
            return False, "A sponsor with that company name already exists."
        insert_sponsor(company, sponsor_type, contact_information)
    except mysql.connector.Error as error:
        return False, f"Could not add sponsor: {error.msg}"

    return True, f'Added sponsor "{company}".'


def edit_sponsor(sponsor_id, company, sponsor_type, contact_information):
    company = (company or "").strip()
    sponsor_type = (sponsor_type or "").strip() or None
    contact_information = (contact_information or "").strip() or None

    if not company:
        return False, "Company is required."
    if len(company) > 150:
        return False, "Company must be 150 characters or fewer."
    if sponsor_type and len(sponsor_type) > 50:
        return False, "Sponsor type must be 50 characters or fewer."
    if contact_information and len(contact_information) > 200:
        return False, "Contact information must be 200 characters or fewer."

    try:
        sponsors = get_all_sponsors()
        if not any(row["SponsorID"] == sponsor_id for row in sponsors):
            return False, "That sponsor no longer exists."
        if any(
            row["Company"].strip().casefold() == company.casefold()
            and row["SponsorID"] != sponsor_id
            for row in sponsors
        ):
            return False, "A sponsor with that company name already exists."
        update_sponsor(
            sponsor_id, company, sponsor_type, contact_information,
        )
    except mysql.connector.Error as error:
        return False, f"Could not update sponsor: {error.msg}"

    return True, f'Updated sponsor "{company}".'


def remove_sponsor(sponsor_id):
    try:
        if not any(row["SponsorID"] == sponsor_id for row in get_all_sponsors()):
            return False, "That sponsor no longer exists."
        delete_sponsor(sponsor_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1451:
            return False, "This sponsor has rewards and cannot be deleted."
        return False, f"Could not delete sponsor: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not delete sponsor: {error.msg}"

    return True, "Sponsor deleted."
