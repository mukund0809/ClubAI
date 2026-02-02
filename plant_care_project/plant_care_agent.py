import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional

LOG_FILE = "garden_log.json"


# ---------- Data Models ----------

@dataclass
class LogEntry:
    timestamp: str
    plant_name: str
    action: str
    notes: str
    next_due: Optional[str] = None  # ISO datetime string or None


# ---------- Gardening Log ----------

class GardeningLog:
    def __init__(self, filepath: str = LOG_FILE):
        self.filepath = filepath
        self.entries: List[LogEntry] = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entries = [LogEntry(**e) for e in data]
            except Exception:
                self.entries = []
        else:
            self.entries = []

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self.entries], f, indent=2)

    def add_entry(self, plant_name: str, action: str, notes: str, next_due: Optional[datetime] = None):
        entry = LogEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            plant_name=plant_name,
            action=action,
            notes=notes,
            next_due=next_due.isoformat(timespec="seconds") if next_due else None,
        )
        self.entries.append(entry)
        self._save()

    def get_recent_entries(self, limit: int = 10) -> List[LogEntry]:
        return sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def get_upcoming_tasks(self) -> List[LogEntry]:
        now = datetime.now()
        upcoming = []
        for e in self.entries:
            if not e.next_due:
                continue
            try:
                due = datetime.fromisoformat(e.next_due)
                if due >= now:
                    upcoming.append(e)
            except Exception:
                continue
        upcoming.sort(key=lambda e: e.next_due)
        return upcoming


# ---------- Plant Knowledge Base (Simple Rules) ----------

PLANT_DATABASE: Dict[str, Dict] = {
    "snake plant": {
        "water": "Water lightly every 2–3 weeks; let soil dry completely between waterings.",
        "light": "Bright indirect to low light; avoid harsh direct sun.",
        "soil": "Well-draining cactus/succulent mix.",
        "fertilizer": "Balanced liquid fertilizer at 1/2 strength once a month in growing season.",
    },
    "pothos": {
        "water": "Water when top 2–3 cm (1 inch) of soil is dry.",
        "light": "Bright indirect light; tolerates low light but grows slower.",
        "soil": "Standard indoor potting mix with good drainage.",
        "fertilizer": "Balanced houseplant fertilizer every 4–6 weeks in spring/summer.",
    },
    "tomato": {
        "water": "Keep soil consistently moist, not soggy; deep watering 2–3 times per week.",
        "light": "Full sun (6–8+ hours per day).",
        "soil": "Rich, well-drained soil with compost.",
        "fertilizer": "High-phosphorus fertilizer or tomato-specific fertilizer every 2–3 weeks.",
    },
    "basil": {
        "water": "Keep soil evenly moist; do not let it fully dry out.",
        "light": "6+ hours of sunlight or strong grow light.",
        "soil": "Well-draining, fertile soil.",
        "fertilizer": "Light feeding every 2–4 weeks with balanced fertilizer.",
    },
}


def normalize_plant_name(name: str) -> str:
    return name.strip().lower()


# ---------- Disease / Issue Diagnosis (Rule-based) ----------

def diagnose_disease(symptoms: str) -> Dict[str, str]:
    text = symptoms.lower()
    possible = []

    if "yellow" in text and "leaf" in text:
        possible.append(
            ("Nutrient deficiency or overwatering",
             "Check drainage, avoid waterlogging, and consider a balanced fertilizer. Ensure pot has drainage holes.")
        )
    if "brown" in text and "tip" in text:
        possible.append(
            ("Low humidity or underwatering",
             "Increase humidity (tray of water, humidifier) and check that you are watering evenly.")
        )
    if "spots" in text and ("black" in text or "brown" in text):
        possible.append(
            ("Fungal or bacterial leaf spot",
             "Remove heavily affected leaves, improve air circulation, avoid overhead watering. Consider a fungicide if severe.")
        )
    if "white" in text and ("powder" in text or "powdery" in text):
        possible.append(
            ("Powdery mildew",
             "Remove affected leaves, increase airflow, avoid wetting foliage. Use a safe fungicidal spray if needed.")
        )
    if "soft" in text or "mushy" in text or "rot" in text:
        possible.append(
            ("Root or stem rot (usually overwatering)",
             "Reduce watering, improve drainage, trim rotten roots/stems if possible, and repot into fresh dry soil.")
        )
    if "bugs" in text or "insect" in text or "aphid" in text or "mealy" in text or "mites" in text:
        possible.append(
            ("Pest infestation",
             "Isolate the plant, wash leaves with water, and treat with insecticidal soap or neem oil. Repeat weekly until resolved.")
        )

    if not possible:
        return {
            "summary": "No clear match from the symptom rules.",
            "advice": "Check for pests under leaves, inspect roots for rot, and review watering and light conditions. If possible, compare visuals to trusted plant diagnosis resources."
        }

    summary = "; ".join([p[0] for p in possible])
    advice = "\n\n".join([f"- {p[0]}: {p[1]}" for p in possible])

    return {
        "summary": summary,
        "advice": advice,
    }


# ---------- Plant Care Advisor Logic ----------

def generate_care_plan(plant_name: str,
                       light: str,
                       watering_habit: str,
                       issues: Optional[str] = None) -> str:
    key = normalize_plant_name(plant_name)
    base = PLANT_DATABASE.get(key)

    lines = [f"Plant care plan for **{plant_name}**"]

    if base:
        lines.append("\nBasic profile (from built-in database):")
        lines.append(f"- Watering: {base['water']}")
        lines.append(f"- Light: {base['light']}")
        lines.append(f"- Soil: {base['soil']}")
        lines.append(f"- Fertilizer: {base['fertilizer']}")
    else:
        lines.append("\nI don't have this plant in the small built-in database, so here are general indoor plant guidelines:")
        lines.append("- Water when the top 2–3 cm (1 inch) of soil feels dry, unless it is a cactus/succulent.")
        lines.append("- Provide bright, indirect light if possible.")
        lines.append("- Use well-draining potting mix and ensure the pot has drainage holes.")
        lines.append("- Fertilize lightly during the active growing season (spring/summer).")

    lines.append("\nYour described conditions:")
    lines.append(f"- Light: {light}")
    lines.append(f"- Watering habit: {watering_habit}")

    if issues:
        lines.append(f"- Reported issues: {issues}")
        diag = diagnose_disease(issues)
        lines.append("\nPreliminary issue diagnosis:")
        lines.append(f"Possible causes: {diag['summary']}")
        lines.append("Suggested actions:")
        lines.append(diag["advice"])

    lines.append("\nGeneral best practices:")
    lines.append("- Check soil moisture with your finger before watering.")
    lines.append("- Rotate the plant every 1–2 weeks for even growth.")
    lines.append("- Remove dead or yellowing leaves to reduce stress and disease risk.")

    return "\n".join(lines)


# ---------- Helper: Suggested Next-Due Logic ----------

def suggest_next_due(action: str) -> Optional[datetime]:
    action = action.lower()
    if "water" in action:
        return datetime.now() + timedelta(days=3)
    if "fertiliz" in action:
        return datetime.now() + timedelta(weeks=4)
    if "prune" in action or "trim" in action:
        return datetime.now() + timedelta(weeks=8)
    if "repot" in action:
        return datetime.now() + timedelta(days=180)
    return None


# ---------- CLI Interface ----------

def print_menu():
    print("\n=== Plant Care Advisor & Gardening Log ===")
    print("1. Get plant care advice")
    print("2. Diagnose plant problem")
    print("3. Log gardening action")
    print("4. View recent log entries")
    print("5. View upcoming tasks")
    print("0. Exit")


def handle_care_advice(log: GardeningLog):
    plant = input("Plant name: ").strip()
    light = input("Describe available light (e.g., bright indirect, low light, full sun): ").strip()
    watering = input("Describe your watering habit (e.g., once a week, when soil is dry): ").strip()
    issues = input("Any visible issues? (leave blank if none): ").strip()
    if issues == "":
        issues = None

    plan = generate_care_plan(plant, light, watering, issues)
    print("\n" + plan + "\n")

    # Optionally auto-log that you ‘reviewed care’
    choice = input("Log this as a 'care review' for this plant? (y/n): ").strip().lower()
    if choice == "y":
        log.add_entry(plant_name=plant, action="care review", notes=f"Conditions: light={light}, watering={watering}")
        print("Logged care review.")


def handle_diagnosis(log: GardeningLog):
    plant = input("Plant name (optional, press Enter to skip): ").strip()
    symptoms = input("Describe the symptoms in detail: ").strip()

    result = diagnose_disease(symptoms)
    print("\nDiagnosis Summary:")
    print(result["summary"])
    print("\nAdvice:")
    print(result["advice"])
    print()

    choice = input("Log this diagnosis for future reference? (y/n): ").strip().lower()
    if choice == "y":
        plant_name = plant if plant else "Unknown plant"
        log.add_entry(plant_name=plant_name, action="diagnosis", notes=symptoms)
        print("Diagnosis logged.")


def handle_log_action(log: GardeningLog):
    plant = input("Plant name: ").strip()
    action = input("Action (e.g., watered, fertilized, pruned, repotted): ").strip()
    notes = input("Any notes (optional): ").strip()

    next_due = suggest_next_due(action)
    log.add_entry(plant_name=plant, action=action, notes=notes, next_due=next_due)
    print("Action logged.")
    if next_due:
        print(f"Suggested next reminder: {next_due.strftime('%Y-%m-%d %H:%M')}")


def handle_view_recent(log: GardeningLog):
    entries = log.get_recent_entries()
    if not entries:
        print("No log entries yet.")
        return
    print("\nRecent log entries:")
    for e in entries:
        print(f"- [{e.timestamp}] {e.plant_name} | {e.action} | {e.notes or 'no notes'}"
              f"{' | next due: ' + e.next_due if e.next_due else ''}")


def handle_upcoming_tasks(log: GardeningLog):
    tasks = log.get_upcoming_tasks()
    if not tasks:
        print("No upcoming tasks scheduled.")
        return
    print("\nUpcoming tasks:")
    for e in tasks:
        print(f"- {e.next_due} | {e.plant_name} | {e.action} | {e.notes or 'no notes'}")


def main():
    log = GardeningLog()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            handle_care_advice(log)
        elif choice == "2":
            handle_diagnosis(log)
        elif choice == "3":
            handle_log_action(log)
        elif choice == "4":
            handle_view_recent(log)
        elif choice == "5":
            handle_upcoming_tasks(log)
        elif choice == "0":
            print("Goodbye and happy gardening!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()