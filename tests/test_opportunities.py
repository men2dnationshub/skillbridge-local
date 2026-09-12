from datetime import date, timedelta

from modules.opportunities import validate_opportunity


def valid_values():
    return {
        "title": "Sales Data Dashboard",
        "description": "Clean sales records and build a clear Excel dashboard for management.",
        "skills_required": ["Excel", "Data cleaning"],
        "location": "Calabar",
        "work_arrangement": "Hybrid",
        "compensation_type": "Stipend",
        "compensation_amount": 25000,
        "duration_weeks": 3,
        "application_deadline": date.today() + timedelta(days=14),
    }


def test_valid_opportunity_is_normalised():
    valid, message, clean = validate_opportunity(valid_values())

    assert valid is True
    assert message == ""
    assert clean["skills_required"] == ["Excel", "Data cleaning"]
    assert clean["compensation_amount"] == 25000.0


def test_opportunity_requires_meaningful_description():
    values = valid_values()
    values["description"] = "Too short"

    valid, message, _ = validate_opportunity(values)

    assert valid is False
    assert "30 characters" in message


def test_paid_opportunity_requires_positive_amount():
    values = valid_values()
    values["compensation_amount"] = 0

    valid, message, _ = validate_opportunity(values)

    assert valid is False
    assert "greater than zero" in message


def test_unpaid_opportunity_clears_amount():
    values = valid_values()
    values["compensation_type"] = "Unpaid"
    values["compensation_amount"] = 5000

    valid, _, clean = validate_opportunity(values)

    assert valid is True
    assert clean["compensation_amount"] is None


def test_past_deadline_is_rejected():
    values = valid_values()
    values["application_deadline"] = date.today() - timedelta(days=1)

    valid, message, _ = validate_opportunity(values)

    assert valid is False
    assert "future" in message
