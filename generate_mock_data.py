#!/usr/bin/env python3
"""
Oklahoma Juvenile Justice Mock Data Generator
Generates ~2,000 youth profiles with associated case notes, assessments, and outcomes.
Output: NDJSON files ready for Elasticsearch bulk indexing.
"""

import json
import random
import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Try to use Faker for realistic names; fall back to built-in lists
# ---------------------------------------------------------------------------
try:
    from faker import Faker
    fake = Faker()
    Faker.seed(42)
    USE_FAKER = True
except ImportError:
    USE_FAKER = False

random.seed(42)

# ---------------------------------------------------------------------------
# Oklahoma-specific reference data
# ---------------------------------------------------------------------------
OKLAHOMA_COUNTIES = [
    "Oklahoma", "Tulsa", "Cleveland", "Comanche", "Canadian", "Rogers",
    "Payne", "Muskogee", "Garfield", "Pottawatomie", "Creek", "Wagoner",
    "Washington", "Carter", "LeFlore", "McCurtain", "Pontotoc", "Stephens",
    "Kay", "Pittsburg", "Grady", "Osage", "Sequoyah", "Cherokee",
    "Seminole", "Okmulgee", "Jackson", "Bryan", "Mayes", "Lincoln",
    "Ottawa", "Delaware", "Caddo", "Beckham", "Garvin", "Adair",
    "McIntosh", "Haskell", "Choctaw", "Pushmataha", "Atoka", "Hughes",
    "Coal", "Latimer", "Marshall", "Love", "Johnston", "Murray",
    "Noble", "Logan", "Kingfisher", "Blaine", "Custer", "Washita",
    "Kiowa", "Tillman", "Cotton", "Jefferson", "Greer", "Harmon",
    "Roger Mills", "Dewey", "Major", "Woods", "Woodward", "Alfalfa",
    "Grant", "Texas", "Beaver", "Cimarron", "Ellis", "Harper",
    "Nowata", "Craig", "Pawnee", "Okfuskee"
]

# County weights — population-proportional (approximate)
COUNTY_WEIGHTS = [0.18, 0.15, 0.08, 0.04, 0.04, 0.03, 0.02, 0.02, 0.02, 0.02,
                  0.02, 0.015, 0.015, 0.015, 0.015, 0.01, 0.01, 0.01, 0.01, 0.01]
# Pad remaining counties equally
_remaining = len(OKLAHOMA_COUNTIES) - len(COUNTY_WEIGHTS)
_leftover = (1.0 - sum(COUNTY_WEIGHTS)) / _remaining
COUNTY_WEIGHTS.extend([_leftover] * _remaining)

COUNTY_COORDS = {
    "Oklahoma": (35.4676, -97.5164), "Tulsa": (36.1540, -95.9928),
    "Cleveland": (35.2226, -97.4395), "Comanche": (34.6036, -98.3959),
    "Canadian": (35.5418, -97.9690), "Rogers": (36.3700, -95.6200),
    "Payne": (36.0800, -96.9700), "Muskogee": (35.6200, -95.3000),
    "Garfield": (36.3800, -97.7800), "Pottawatomie": (35.2200, -96.9500),
}

CITIES_BY_COUNTY = {
    "Oklahoma": ["Oklahoma City", "Edmond", "Midwest City", "Del City", "Moore"],
    "Tulsa": ["Tulsa", "Broken Arrow", "Owasso", "Bixby", "Jenks"],
    "Cleveland": ["Norman", "Noble", "Lexington", "Moore"],
    "Comanche": ["Lawton", "Cache", "Elgin", "Fletcher"],
    "Canadian": ["Yukon", "Mustang", "El Reno", "Piedmont"],
}

DISTRICTS = [f"District {i}" for i in range(1, 13)]

OJA_FACILITIES = [
    "Central Oklahoma Juvenile Center", "Southwest Oklahoma Juvenile Center",
    "Oklahoma Youth Academy", "LeFlore County Residential",
    "Norman Transition Living Center", "Tulsa Group Home East",
    "Tulsa Group Home West", "OKC Community Intervention Center",
    "Lawton Youth Services Center", "Muskogee Regional Youth Shelter"
]

OFFENSES = {
    "Property": ["Burglary", "Larceny-Theft", "Motor Vehicle Theft", "Arson",
                 "Vandalism", "Shoplifting", "Criminal Mischief"],
    "Person": ["Assault", "Robbery", "Simple Assault", "Intimidation",
               "Domestic Assault", "Battery"],
    "Drug": ["Drug Possession", "Drug Paraphernalia", "Distribution",
             "Possession of Marijuana", "Under the Influence"],
    "Public Order": ["Disorderly Conduct", "Trespassing", "Curfew Violation",
                     "Truancy", "Runaway", "Underage Drinking", "Public Intoxication"],
    "Status": ["Truancy", "Runaway", "Ungovernable Behavior",
               "Curfew Violation", "Tobacco Possession"]
}

OFFENSE_SEVERITY = {
    "Property": "Moderate", "Person": "High", "Drug": "Moderate",
    "Public Order": "Low", "Status": "Low"
}

REFERRAL_SOURCES = [
    "Law Enforcement", "School", "Parent/Guardian", "District Attorney",
    "Court", "Self-Referral", "DHS", "Other Agency"
]

SUPERVISION_LEVELS = ["Community", "Intensive", "Standard", "Administrative"]

PLACEMENT_TYPES = [
    "Community Supervision", "Group Home", "Residential Facility",
    "Shelter Care", "Foster Care", "Independent Living", "Detention"
]

CASE_STATUSES = ["Active", "Inactive", "Closed", "Pending", "Transferred"]

GENDERS = ["Male", "Female", "Non-Binary"]
GENDER_WEIGHTS = [0.72, 0.25, 0.03]

RACES = ["White", "Black/African American", "American Indian/Alaska Native",
         "Two or More Races", "Asian", "Native Hawaiian/Pacific Islander"]
RACE_WEIGHTS = [0.45, 0.25, 0.18, 0.08, 0.025, 0.015]

ETHNICITIES = ["Non-Hispanic", "Hispanic/Latino"]
ETHNICITY_WEIGHTS = [0.82, 0.18]

NOTE_TYPES = [
    "Initial Contact", "Home Visit", "Office Visit", "Phone Contact",
    "School Contact", "Court Hearing", "Incident Report", "Treatment Update",
    "Community Service Check", "Drug Test Result", "Placement Review",
    "Family Meeting", "Discharge Planning", "Supervision Check-In"
]

NOTE_SUBJECTS_BY_TYPE = {
    "Home Visit": [
        "Routine home visit - stable environment",
        "Home visit - concerns about supervision in the home",
        "Follow-up home visit after placement change",
        "Home environment assessment completed"
    ],
    "Drug Test Result": [
        "Random drug screen - negative results",
        "Random drug screen - positive for THC",
        "Scheduled drug test - all clear",
        "Drug test - refused, documented refusal"
    ],
    "Court Hearing": [
        "Review hearing - progress noted by judge",
        "Dispositional hearing completed",
        "Modification hearing - supervision level adjusted",
        "Violation hearing - continued on supervision"
    ],
    "Treatment Update": [
        "Counseling session update - making progress",
        "Behavioral therapy progress report",
        "Substance abuse treatment - attended all sessions",
        "Anger management program update"
    ],
    "School Contact": [
        "School attendance verification - attending regularly",
        "Meeting with school counselor re: behavior concerns",
        "IEP review meeting attended",
        "School reported truancy - 3 unexcused absences"
    ],
    "Incident Report": [
        "Altercation with peer at facility",
        "Curfew violation - returned 2 hours late",
        "Contraband found during room check",
        "Verbal altercation with staff - de-escalated"
    ]
}

CONTACT_METHODS = ["In Person", "Phone", "Video Call", "Email", "Text Message"]

ASSESSMENT_TYPES = ["YASI", "SAVRY", "MAYSI-2", "LSI-R", "OJA Risk Assessment"]

ASSESSMENT_DOMAINS = [
    "Criminal History", "Family", "Education", "Peers",
    "Substance Abuse", "Mental Health", "Attitudes", "Skills"
]

DISCHARGE_REASONS = [
    "Successful Completion", "Aged Out", "Transferred to Adult System",
    "Revocation", "Court Order", "Absconded", "Administrative Closure",
    "Moved Out of State"
]

EDUCATION_OUTCOMES = [
    "Enrolled in School", "GED Obtained", "High School Diploma",
    "Vocational Training", "Dropped Out", "Not Applicable"
]

SERVICES = [
    "Cognitive Behavioral Therapy", "Substance Abuse Treatment",
    "Family Counseling", "Anger Management", "Life Skills Training",
    "Educational Tutoring", "Vocational Training", "Mentoring Program",
    "Community Service", "Restorative Justice Program", "Trauma-Informed Care"
]

# ---------------------------------------------------------------------------
# Name generation
# ---------------------------------------------------------------------------
FIRST_NAMES_M = ["James", "John", "Robert", "Michael", "David", "William",
    "Christopher", "Daniel", "Matthew", "Anthony", "Joshua", "Andrew",
    "Joseph", "Ryan", "Brandon", "Tyler", "Justin", "Austin", "Caleb",
    "Ethan", "Isaiah", "Jayden", "Elijah", "Cameron", "Malik", "Deshawn",
    "Tyrone", "Marcus", "Dante", "Terrell", "Carlos", "Miguel", "Jose",
    "Luis", "Diego", "Adrian", "Tanner", "Cody", "Hunter", "Wyatt"]

FIRST_NAMES_F = ["Mary", "Jennifer", "Jessica", "Ashley", "Amanda",
    "Sarah", "Brittany", "Samantha", "Emily", "Megan", "Hannah",
    "Kayla", "Alexis", "Madison", "Taylor", "Jasmine", "Destiny",
    "Aaliyah", "Breanna", "Kiara", "Maria", "Gabriella", "Sofia",
    "Valentina", "Isabella", "Autumn", "Cheyenne", "Savannah", "Dakota",
    "Sierra"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson",
    "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson",
    "Thompson", "White", "Harris", "Sanchez", "Clark", "Lewis",
    "Robinson", "Walker", "Young", "Allen", "King", "Wright",
    "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Ramirez",
    "Campbell", "Mitchell", "Roberts", "Chuculate", "Sixkiller",
    "Walkingstick", "Cornsilk", "Swimmer", "Wildcat", "Harjo",
    "Tiger", "Fixico", "Bear"]

OFFICER_FIRST = ["Sarah", "Michael", "Jennifer", "David", "Lisa",
    "Robert", "Karen", "James", "Patricia", "Thomas", "Maria", "Charles",
    "Angela", "Kevin", "Laura"]

OFFICER_LAST = ["Thompson", "Reynolds", "Chen", "Blackwood", "Morales",
    "Patterson", "Whitehorse", "Sullivan", "Hawkins", "Nguyen",
    "Birdsong", "Redhawk", "Yellowhammer"]


def gen_name(gender):
    if USE_FAKER:
        if gender == "Male":
            return fake.first_name_male(), fake.last_name()
        elif gender == "Female":
            return fake.first_name_female(), fake.last_name()
        else:
            return random.choice(FIRST_NAMES_M + FIRST_NAMES_F), random.choice(LAST_NAMES)
    pool = FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F if gender == "Female" else FIRST_NAMES_M + FIRST_NAMES_F
    return random.choice(pool), random.choice(LAST_NAMES)


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, max(delta.days, 1)))


def jitter_coords(base, radius_deg=0.15):
    lat, lon = base
    return round(lat + random.uniform(-radius_deg, radius_deg), 4), \
           round(lon + random.uniform(-radius_deg, radius_deg), 4)


# ---------------------------------------------------------------------------
# Case note body templates
# ---------------------------------------------------------------------------
def gen_note_body(note_type, youth_first, gender):
    pronoun = "he" if gender == "Male" else "she" if gender == "Female" else "they"
    poss = "his" if gender == "Male" else "her" if gender == "Female" else "their"
    cap_pronoun = pronoun.capitalize()

    templates = {
        "Home Visit": [
            f"Conducted a home visit with {youth_first} and {poss} guardian. The home environment appears stable. {cap_pronoun} reports doing well in school and completing community service hours. Guardian confirms compliance with curfew.",
            f"Home visit completed. {youth_first}'s guardian was present. Discussed {poss} progress in treatment and school attendance. Some concerns about peer associations in the neighborhood. Recommended increased supervision.",
            f"Attempted home visit — guardian was not home. Neighbor confirmed {youth_first} was at school. Will reschedule for next week.",
        ],
        "Drug Test Result": [
            f"Administered random urinalysis to {youth_first}. Results negative for all substances. {cap_pronoun} continues to comply with drug testing requirements.",
            f"Random drug screen conducted. {youth_first} tested positive for THC. Discussed results with youth and guardian. Referral to substance abuse counseling updated. Will increase testing frequency to weekly.",
            f"{youth_first} reported for scheduled drug test. All results negative. Encouraged continued sobriety.",
        ],
        "Court Hearing": [
            f"Attended review hearing for {youth_first} in juvenile court. Judge noted positive progress in treatment and school attendance. Supervision to continue at current level. Next review in 90 days.",
            f"Disposition hearing completed for {youth_first}. Court ordered continued probation with community service. {cap_pronoun} must complete 40 hours within 60 days.",
            f"Appeared in court for {youth_first}'s violation hearing. Judge continued {pronoun} on supervision with additional conditions including weekly check-ins and substance abuse evaluation.",
        ],
        "Treatment Update": [
            f"{youth_first} attended {poss} weekly counseling session. Therapist reports {pronoun} is engaging more in sessions and demonstrating improved coping skills. Recommend continuing current treatment plan.",
            f"Received update from {youth_first}'s behavioral therapist. {cap_pronoun} has completed 8 of 12 anger management sessions. Progress noted in emotional regulation.",
            f"Family counseling session held with {youth_first} and guardian. Communication between {pronoun} and {poss} guardian has improved. Therapist recommends continued family sessions bi-weekly.",
        ],
        "School Contact": [
            f"Spoke with {youth_first}'s school counselor. Attendance has been consistent this month — no unexcused absences. Grades are improving in math and science. {cap_pronoun} joined the after-school tutoring program.",
            f"Received report from school — {youth_first} had 3 unexcused absences this week. Met with guardian to discuss. Guardian will ensure transportation. Set up daily attendance verification.",
            f"Attended IEP meeting for {youth_first}. Team updated accommodations for {poss} learning needs. {cap_pronoun} is on track to earn credits for the semester.",
        ],
        "Incident Report": [
            f"Incident at {random.choice(OJA_FACILITIES)}: {youth_first} was involved in a verbal altercation with another resident. Staff intervened and de-escalated. No injuries. Behavioral review scheduled.",
            f"{youth_first} violated curfew by 2 hours on the reported date. Guardian was unaware of {poss} whereabouts. Discussed consequences and updated supervision plan.",
            f"During routine room inspection, staff found contraband (cell phone) in {youth_first}'s area. Item confiscated. Behavioral consequence assigned per facility policy.",
        ],
        "Supervision Check-In": [
            f"Regular check-in with {youth_first}. {cap_pronoun} reports things are going well at home and school. Reviewed goals and upcoming court date. No concerns at this time.",
            f"Office visit with {youth_first}. Discussed progress on community service — {pronoun} has completed {random.randint(5, 30)} of {random.randint(30, 60)} required hours. Encouraged {pronoun} to stay on track.",
        ],
        "Phone Contact": [
            f"Phone contact with {youth_first}'s guardian. Guardian reports {pronoun} is following house rules and attending school regularly. No concerns.",
        ],
    }

    if note_type in templates:
        return random.choice(templates[note_type])
    return f"Contact with {youth_first} regarding {note_type.lower()}. {cap_pronoun} is progressing as expected. Will follow up at next scheduled contact."


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------
NUM_YOUTH = 2000
OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "data"

# Pre-generate a pool of officers
OFFICERS = [f"{random.choice(OFFICER_FIRST)} {random.choice(OFFICER_LAST)}" for _ in range(40)]


def generate_youth_profiles():
    profiles = []
    now = datetime(2026, 6, 1)

    for i in range(NUM_YOUTH):
        gender = random.choices(GENDERS, GENDER_WEIGHTS)[0]
        first, last = gen_name(gender)
        county = random.choices(OKLAHOMA_COUNTIES, COUNTY_WEIGHTS)[0]

        # Age 10-17 at intake
        age_at_intake = random.choices(range(10, 18), weights=[2, 4, 8, 14, 20, 22, 18, 12])[0]
        intake_date = random_date(datetime(2023, 1, 1), datetime(2026, 5, 1))
        dob = intake_date - timedelta(days=age_at_intake * 365 + random.randint(0, 364))
        referral_date = intake_date - timedelta(days=random.randint(1, 60))

        # Some cases are closed
        is_closed = random.random() < 0.45
        discharge_date = None
        case_status = random.choice(["Active", "Pending"]) if not is_closed else "Closed"
        if is_closed:
            los = random.randint(30, 730)
            discharge_date = intake_date + timedelta(days=los)
            if discharge_date > now:
                discharge_date = now - timedelta(days=random.randint(1, 30))

        offense_cat = random.choices(
            list(OFFENSES.keys()),
            weights=[0.30, 0.25, 0.20, 0.15, 0.10]
        )[0]

        base_coords = COUNTY_COORDS.get(county, (35.5, -97.0))
        lat, lon = jitter_coords(base_coords)

        city_list = CITIES_BY_COUNTY.get(county, [f"{county} City"])

        profile = {
            "youth_id": f"OJA-{2023 + i // 700}-{str(i + 1).zfill(5)}",
            "first_name": first,
            "last_name": last,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "age_at_intake": age_at_intake,
            "gender": gender,
            "race": random.choices(RACES, RACE_WEIGHTS)[0],
            "ethnicity": random.choices(ETHNICITIES, ETHNICITY_WEIGHTS)[0],
            "county": county,
            "city": random.choice(city_list),
            "zip_code": f"7{random.randint(3000, 4999)}",
            "geo_location": {"lat": lat, "lon": lon},
            "referral_source": random.choice(REFERRAL_SOURCES),
            "referral_date": referral_date.strftime("%Y-%m-%d"),
            "intake_date": intake_date.strftime("%Y-%m-%d"),
            "discharge_date": discharge_date.strftime("%Y-%m-%d") if discharge_date else None,
            "case_status": case_status,
            "supervision_level": random.choice(SUPERVISION_LEVELS),
            "primary_offense": random.choice(OFFENSES[offense_cat]),
            "offense_category": offense_cat,
            "offense_severity": OFFENSE_SEVERITY[offense_cat],
            "prior_referrals": random.choices(range(0, 8), weights=[35, 25, 15, 10, 7, 4, 2, 2])[0],
            "placement_type": random.choices(PLACEMENT_TYPES, weights=[0.40, 0.12, 0.15, 0.10, 0.08, 0.05, 0.10])[0],
            "facility_name": random.choice(OJA_FACILITIES) if random.random() > 0.45 else None,
            "assigned_officer": random.choice(OFFICERS),
            "district": random.choice(DISTRICTS),
            "school_enrolled": random.random() < 0.75,
            "mental_health_flag": random.random() < 0.35,
            "substance_abuse_flag": random.random() < 0.28,
            "tags": random.sample(["at-risk", "gang-involved", "special-needs", "trauma-history",
                                   "family-instability", "chronic-truant", "mental-health",
                                   "substance-use", "sex-offense-protocol"], k=random.randint(0, 3)),
            "_intake_dt": intake_date,
            "_discharge_dt": discharge_date,
            "_gender": gender,
            "_first_name": first,
        }
        profiles.append(profile)
    return profiles


def generate_case_notes(profiles):
    notes = []
    for p in profiles:
        intake = p["_intake_dt"]
        end = p["_discharge_dt"] or datetime(2026, 6, 1)
        span_days = (end - intake).days
        num_notes = max(1, span_days // random.randint(12, 30))
        num_notes = min(num_notes, 40)

        officer = p["assigned_officer"]
        for _ in range(num_notes):
            note_type = random.choice(NOTE_TYPES)
            note_date = random_date(intake, end)
            subject_pool = NOTE_SUBJECTS_BY_TYPE.get(note_type, [f"{note_type} for {p['first_name']}"])

            notes.append({
                "note_id": str(uuid.uuid4()),
                "youth_id": p["youth_id"],
                "author": officer if random.random() < 0.7 else random.choice(OFFICERS),
                "author_role": random.choice(["Probation Officer", "Case Manager", "Counselor",
                                              "Facility Staff", "Supervisor"]),
                "note_date": note_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "note_type": note_type,
                "subject": random.choice(subject_pool),
                "body": gen_note_body(note_type, p["_first_name"], p["_gender"]),
                "sentiment": random.choices(["Positive", "Neutral", "Negative", "Concerning"],
                                            weights=[0.30, 0.40, 0.15, 0.15])[0],
                "contact_method": random.choice(CONTACT_METHODS),
                "follow_up_required": random.random() < 0.35,
                "follow_up_date": (note_date + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d") if random.random() < 0.35 else None,
                "tags": random.sample(["urgent", "compliance", "positive-progress", "violation",
                                       "family-involvement", "treatment", "education"], k=random.randint(0, 2))
            })
    return notes


def generate_assessments(profiles):
    assessments = []
    for p in profiles:
        intake = p["_intake_dt"]
        end = p["_discharge_dt"] or datetime(2026, 6, 1)
        num_assessments = random.randint(1, 4)

        for j in range(num_assessments):
            assess_date = intake + timedelta(days=j * random.randint(60, 180))
            if assess_date > end:
                break

            # Scores tend to improve over time
            base_risk = random.uniform(0.2, 0.9)
            improvement = j * random.uniform(0.02, 0.08)
            risk = max(0.1, base_risk - improvement)

            domain_scores = []
            for domain in ASSESSMENT_DOMAINS:
                max_s = 10.0
                score = round(random.uniform(1, max_s) * risk, 1)
                domain_scores.append({"domain": domain, "score": score, "max_score": max_s})

            overall = round(sum(d["score"] for d in domain_scores), 1)
            risk_level = "Low" if overall < 25 else "Moderate" if overall < 45 else "High" if overall < 60 else "Very High"

            assessments.append({
                "assessment_id": str(uuid.uuid4()),
                "youth_id": p["youth_id"],
                "assessment_type": random.choice(ASSESSMENT_TYPES),
                "assessment_date": assess_date.strftime("%Y-%m-%d"),
                "assessor": random.choice(OFFICERS),
                "overall_risk_score": overall,
                "risk_level": risk_level,
                "domain_scores": domain_scores,
                "criminal_history_score": domain_scores[0]["score"],
                "family_score": domain_scores[1]["score"],
                "education_score": domain_scores[2]["score"],
                "peer_score": domain_scores[3]["score"],
                "substance_abuse_score": domain_scores[4]["score"],
                "mental_health_score": domain_scores[5]["score"],
                "attitudes_score": domain_scores[6]["score"],
                "skills_score": domain_scores[7]["score"],
                "recommended_supervision": random.choice(SUPERVISION_LEVELS),
                "notes": f"Assessment completed for {p['first_name']} {p['last_name']}. Risk level: {risk_level}."
            })
    return assessments


def generate_outcomes(profiles):
    outcomes = []
    for p in profiles:
        if p["case_status"] != "Closed" or not p["_discharge_dt"]:
            continue

        discharge_dt = p["_discharge_dt"]
        los = (discharge_dt - p["_intake_dt"]).days
        completed = random.random() < 0.62

        recid_6 = random.random() < 0.18
        recid_12 = recid_6 or (random.random() < 0.12)

        outcomes.append({
            "outcome_id": str(uuid.uuid4()),
            "youth_id": p["youth_id"],
            "discharge_date": discharge_dt.strftime("%Y-%m-%d"),
            "discharge_reason": random.choices(DISCHARGE_REASONS,
                                               weights=[0.45, 0.15, 0.08, 0.10, 0.08, 0.05, 0.06, 0.03])[0],
            "length_of_stay_days": los,
            "program_completed": completed,
            "recidivism_6mo": recid_6,
            "recidivism_12mo": recid_12,
            "recidivism_offense": random.choice(
                [o for cat in OFFENSES.values() for o in cat]) if recid_12 else None,
            "recidivism_date": (discharge_dt + timedelta(days=random.randint(30, 365))).strftime(
                "%Y-%m-%d") if recid_12 else None,
            "education_outcome": random.choice(EDUCATION_OUTCOMES),
            "employment_at_discharge": random.random() < 0.30,
            "risk_score_change": round(random.uniform(-25, 5), 1),
            "services_completed": random.sample(SERVICES, k=random.randint(1, 5)),
            "restitution_paid": random.random() < 0.55,
            "community_service_hours": random.randint(0, 120)
        })
    return outcomes


def write_ndjson(records, index_name, filepath):
    """Write records as NDJSON with Elasticsearch bulk action lines."""
    with open(filepath, "w") as f:
        for rec in records:
            # Remove internal fields
            clean = {k: v for k, v in rec.items() if not k.startswith("_")}
            action = {"index": {"_index": index_name}}
            f.write(json.dumps(action) + "\n")
            f.write(json.dumps(clean) + "\n")
    print(f"  Wrote {len(records)} records to {filepath}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating 2,000 youth profiles...")
    profiles = generate_youth_profiles()
    write_ndjson(profiles, "youth_profiles", OUTPUT_DIR / "youth_profiles.ndjson")

    print("Generating case notes...")
    notes = generate_case_notes(profiles)
    write_ndjson(notes, "case_notes", OUTPUT_DIR / "case_notes.ndjson")

    print("Generating assessments...")
    assessments = generate_assessments(profiles)
    write_ndjson(assessments, "assessments", OUTPUT_DIR / "assessments.ndjson")

    print("Generating outcomes...")
    outcomes = generate_outcomes(profiles)
    write_ndjson(outcomes, "outcomes", OUTPUT_DIR / "outcomes.ndjson")

    print(f"\nDone! Files in: {OUTPUT_DIR}")
    print(f"  Youth profiles: {len(profiles)}")
    print(f"  Case notes:     {len(notes)}")
    print(f"  Assessments:    {len(assessments)}")
    print(f"  Outcomes:       {len(outcomes)}")


if __name__ == "__main__":
    main()
