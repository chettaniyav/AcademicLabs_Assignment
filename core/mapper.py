
def map_study_to_schema(study):
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    contact_module = protocol.get("contactsLocationsModule", {})
    location_list = contact_module.get("locations", [])
    eligibility = protocol.get("eligibilityModule", {})

    principal_investigator = {"name": "", "affiliation": ""}

    responsible_party = sponsor.get("responsibleParty", {})
    if isinstance(responsible_party, dict) and responsible_party.get("type") == "PRINCIPAL_INVESTIGATOR":
        principal_investigator["name"] = responsible_party.get(
            "investigatorFullName", "")
        principal_investigator["affiliation"] = responsible_party.get(
            "investigatorAffiliation", "")
    data = {
        "trialId": identification.get("nctId"),
        "title": identification.get("briefTitle"),
        "startDate": status.get("startDateStruct", {}).get("date"),
        "endDate": status.get("completionDateStruct", {}).get("date"),
        "phase": status.get("phase", ["Other"])[0] if status.get("phase") else "Other",
        "principalInvestigator": principal_investigator,
        "locations": [
            {
                "facility": location.get("facility"),
                "city": location.get("city"),
                "country": location.get("country")
            }
            for location in location_list
        ],
        "eligibilityCriteria": eligibility.get("eligibilityCriteria", "")
    }
    return data
