import mysql.connector

from database import (
    get_all_sponsors, get_sponsor_by_id,
    insert_sponsor, update_sponsor, delete_sponsor,
)
from delete_summary import describe_related


def list_sponsors():
    """Return every sponsor, ordered by company."""
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


def get_sponsor_options():
    """Map SponsorID -> company for the manage form's dropdown, so users
    pick a sponsor instead of typing an ID."""
    return {sponsor["SponsorID"]: sponsor["Company"]
            for sponsor in get_all_sponsors()}


def get_sponsor_details(sponsor_id):
    """Return one sponsor's current values (to pre-fill the update form)."""
    return get_sponsor_by_id(sponsor_id)


def is_duplicate_company(company, sponsor_id=None):
    """True when another sponsor already uses this company name.
    sponsor.Company has no UNIQUE constraint in the schema, so unlike
    athlete.Username or sport.Name this has to be checked here instead
    of catching MySQL's error 1062. sponsor_id is the row being
    updated, which is allowed to keep its own name."""
    normalized_company = company.casefold()
    return any(
        row["Company"].strip().casefold() == normalized_company
        and row["SponsorID"] != sponsor_id
        for row in get_all_sponsors()
    )


def check_sponsor_input(company, sponsor_type, contact_information):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (company, sponsor_type,
    contact_information)."""
    company = (company or "").strip()
    sponsor_type = (sponsor_type or "").strip() or None  # optional: blank -> NULL
    contact_information = (contact_information or "").strip() or None
    values = (company, sponsor_type, contact_information)

    if not company:
        return "Company is required.", values
    if len(company) > 150:
        return "Company must be 150 characters or fewer.", values
    if sponsor_type and len(sponsor_type) > 50:
        return "Sponsor type must be 50 characters or fewer.", values
    if contact_information and len(contact_information) > 200:
        return "Contact information must be 200 characters or fewer.", values

    return None, values


def add_sponsor(company, sponsor_type, contact_information):
    """Validate the input, then insert it. Returns (success, message)."""
    error, (company, sponsor_type, contact_information) = check_sponsor_input(
        company, sponsor_type, contact_information
    )
    if error:
        return False, error

    try:
        if is_duplicate_company(company):
            return False, "A sponsor with that company name already exists."
        insert_sponsor(company, sponsor_type, contact_information)
    # No IntegrityError branch here: sponsor has no UNIQUE column and no
    # foreign key of its own, so there is no specific error to explain.
    except mysql.connector.Error as e:
        return False, f"Could not add sponsor: {e.msg}"

    return True, f'Added sponsor "{company}".'


def edit_sponsor(sponsor_id, company, sponsor_type, contact_information):
    """Validate the input, then update the sponsor. Returns (success, message)."""
    error, (company, sponsor_type, contact_information) = check_sponsor_input(
        company, sponsor_type, contact_information
    )
    if error:
        return False, error

    try:
        if is_duplicate_company(company, sponsor_id):
            return False, "A sponsor with that company name already exists."
        updated = update_sponsor(sponsor_id, company, sponsor_type,
                                 contact_information)
    except mysql.connector.Error as e:
        return False, f"Could not update sponsor: {e.msg}"

    if updated == 0:
        return False, "No matching sponsor found."
    return True, f'Updated sponsor "{company}".'


def remove_sponsor(sponsor_id):
    """Delete the sponsor together with its rewards and the redemptions
    of those rewards, in one transaction. Returns (success, message)."""
    try:
        deleted = delete_sponsor(sponsor_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # a table we did not account for points at it
            return False, "This sponsor has rewards and cannot be deleted."
        return False, f"Could not delete sponsor: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not delete sponsor: {e.msg}"

    if deleted["sponsor"] == 0:
        return False, "No matching sponsor found."
    return True, "Deleted sponsor." + describe_related(deleted, "sponsor")
