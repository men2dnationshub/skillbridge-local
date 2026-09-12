from modules.auth import AuthUser
from modules.profiles import profile_completion


def test_student_profile_completion():
    user = AuthUser("student-1", "student@example.com", "student", "Student")
    profile = {
        "full_name": "Student One",
        "location": "Calabar",
        "education": "Digital skills training",
        "skills": ["Excel"],
        "tools": ["Microsoft Excel"],
        "bio": "Entry level data analyst",
        "availability": "10 hours per week",
    }

    assert profile_completion(user, profile) == 100


def test_empty_business_profile_completion():
    user = AuthUser("business-1", "business@example.com", "business", "Owner")

    assert profile_completion(user, {}) == 0

