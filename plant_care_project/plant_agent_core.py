import json
import openai
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
load_dotenv()


LOG_FILE = "garden_log.json"


_openai_client = None

_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    _openai_client = openai.OpenAI(api_key=api_key)
    return _openai_client


# ---------- Data Models ----------

@dataclass
class LogEntry:
    timestamp: str
    plant_name: str
    action: str
    notes: str
    next_due: Optional[str] = None  # ISO datetime string or None


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


# ---------- Simple Plant Knowledge Base ----------

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


# ---------- LLM Integration Stub ----------

def call_llm(prompt: str) -> str | None:
    """
    Call OpenAI Chat Completions API using your personal API key.
    """
    client = get_openai_client()

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # or gpt-4.1, gpt-4o-mini, etc.
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful gardening assistant. "
                        "Explain things clearly, step by step, for beginner gardeners."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[call_llm] OpenAI error: {e}")
        return None



def maybe_refine_with_llm(prompt: str, fallback: str, use_llm: bool) -> str:
    if not use_llm:
        return fallback
    try:
        resp = call_llm(prompt)
    except NotImplementedError:
        resp = None
    return resp or fallback


# ---------- Disease / Issue Diagnosis ----------

def diagnose_disease(symptoms: str, use_llm: bool = False) -> Dict[str, str]:
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
    if any(k in text for k in ["bugs", "insect", "aphid", "mealy", "mites", "scale"]):
        possible.append(
            ("Pest infestation",
             "Isolate the plant, wash leaves with water, and treat with insecticidal soap or neem oil. Repeat weekly until resolved.")
        )

    if not possible:
        base_summary = "No clear match from the symptom rules."
        base_advice = ("Check for pests under leaves, inspect roots for rot, and review watering and light conditions. "
                       "If possible, compare visuals to trusted plant diagnosis resources or consult a local gardening expert.")
    else:
        base_summary = "; ".join([p[0] for p in possible])
        base_advice = "\n\n".join([f"- {p[0]}: {p[1]}" for p in possible])

    summary_prompt = (
        f"User symptoms: {symptoms}\n\nRule-based summary: {base_summary}\n\n"
        "Rewrite the summary in clear, friendly language for a home gardener."
    )
    advice_prompt = (
        f"User symptoms: {symptoms}\n\nRule-based advice:\n{base_advice}\n\n"
        "Rewrite this advice as clear, step-by-step instructions for a beginner gardener."
    )

    refined_summary = maybe_refine_with_llm(summary_prompt, base_summary, use_llm)
    refined_advice = maybe_refine_with_llm(advice_prompt, base_advice, use_llm)

    return {
        "summary": refined_summary,
        "advice": refined_advice,
    }


# ---------- Plant Care Advisor ----------

def generate_care_plan(plant_name: str,
                       light: str,
                       watering_habit: str,
                       issues: Optional[str] = None,
                       use_llm: bool = False) -> str:
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
        diag = diagnose_disease(issues, use_llm=use_llm)
        lines.append("\nPreliminary issue diagnosis:")
        lines.append(f"Possible causes: {diag['summary']}")
        lines.append("Suggested actions:")
        lines.append(diag["advice"])

    lines.append("\nGeneral best practices:")
    lines.append("- Check soil moisture with your finger before watering.")
    lines.append("- Rotate the plant every 1–2 weeks for even growth.")
    lines.append("- Remove dead or yellowing leaves to reduce stress and disease risk.")

    care_text = "\n".join(lines)

    if not use_llm:
        return care_text

    prompt = (
        "Rewrite the following plant care plan so it is very clear, friendly, and easy to follow for a beginner gardener. "
        "Keep all important details, but feel free to organize it with headings and bullet points.\n\n"
        f"{care_text}"
    )
    return maybe_refine_with_llm(prompt, care_text, use_llm)


# ---------- Next-Due Suggestion ----------

def suggest_next_due(action: str) -> Optional[datetime]:
    action_l = action.lower()
    if "water" in action_l:
        return datetime.now() + timedelta(days=3)
    if "fertiliz" in action_l:
        return datetime.now() + timedelta(weeks=4)
    if "prune" in action_l or "trim" in action_l:
        return datetime.now() + timedelta(weeks=8)
    if "repot" in action_l:
        return datetime.now() + timedelta(days=180)
    return None


def generate_upcoming_task_from_logs(log: 'GardeningLog', use_llm: bool = False) -> Optional[str]:
    """
    Analyze recent log entries and generate an intelligent upcoming task reminder.
    Returns a formatted string with the suggested task, or None if no suggestion.
    """
    if not use_llm:
        return None

    recent = log.get_recent_entries(limit=10)
    if not recent:
        return None

    # Format recent entries for LLM context
    log_summary = []
    for entry in recent[:5]:  # Use top 5 most recent
        log_summary.append(
            f"- {entry.timestamp}: {entry.plant_name} - {entry.action}"
            + (f" (Notes: {entry.notes})" if entry.notes else "")
            + (f" [Next due: {entry.next_due}]" if entry.next_due else "")
        )

    log_text = "\n".join(log_summary)

    prompt = f"""Based on the following recent gardening log entries, suggest ONE upcoming task or reminder that would be helpful for the gardener.

Recent log entries:
{log_text}

Consider:
- What plants might need attention soon based on their care patterns
- Any follow-up actions based on recent activities
- Seasonal or routine maintenance that might be due

Provide a concise, actionable task in 1-2 sentences. Format: "Task: [action needed] - [brief explanation]"
"""

    try:
        result = call_llm(prompt)
        return result
    except Exception as e:
        print(f"[generate_upcoming_task_from_logs] Error: {e}")
        return None
