# SkillBridge Local

SkillBridge Local connects students and recent graduates with practical digital projects from verified small businesses.

This package contains **MVP Milestone 2**, including the application foundation, accounts, and profiles.

## Milestone 1 includes

- Streamlit multipage application shell
- SkillBridge Local visual identity
- Student, business, project, opportunity, and administrator page previews
- Environment based configuration
- Supabase client readiness check
- Offline demo mode
- Automated tests
- Secret protection templates

## Milestone 2 includes

- Student and business registration
- Email and password login
- Secure session management and logout
- Role protected dashboards
- Student profile creation and editing
- Business profile creation and verification request
- Offline demo accounts for interface testing
- Supabase authentication migration and Row Level Security policies
- Database protection against role changes and business self verification

## Run on Ubuntu

Open Terminal inside the project folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will display a local address, normally `http://localhost:8501`.

## Run the tests

```bash
pytest -q
```

## Connect Supabase

Copy the environment template:

```bash
cp .env.example .env
```

Open `.env` and add the project URL and anonymous key:

```text
SUPABASE_URL=your-project-url
SUPABASE_ANON_KEY=your-anonymous-key
```

Do not add the Supabase service role key to Streamlit or commit it to GitHub.

Open the Supabase SQL Editor and run:

```text
sql/001_milestone_2_auth_profiles.sql
```

Then enable email authentication in the Supabase Authentication settings. If email confirmation is enabled, new users must confirm their email before logging in.

## Current status

Milestone 1 and Milestone 2 are implemented. The app can create live accounts after Supabase is connected, and it includes session only demo accounts for testing without credentials. Opportunity publishing belongs to Milestone 3.

## Brand colours

- Deep Navy: `#061A40`
- Royal Blue: `#0B5ED7`
- Gold: `#F4B41A`
- White: `#FFFFFF`

## Product owner

Mfon Nsimah  
Digital Skills Trainer and Data Analyst
