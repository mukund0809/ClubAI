import streamlit as st
from datetime import datetime
from PIL import Image


from plant_agent_core import (
    GardeningLog,
    generate_care_plan,
    diagnose_disease,
    suggest_next_due,
    generate_upcoming_task_from_logs,
)

import os
# ... keep your other imports

SAMPLES_DIR = os.path.join("assets", "disease_samples")
PLANTS_DIR = os.path.join("assets", "plants")

PLANT_CARE_SAMPLES = [
    {
        "name": "Rose",
        "image": os.path.join(PLANTS_DIR, "rose.png"),
        "light": "Full sun (6+ hours daily)",
        "watering": "Water deeply 2-3 times per week, keep soil moist but not soggy",
    },
    {
        "name": "Pothos",
        "image": os.path.join(PLANTS_DIR, "pothos.png"),
        "light": "Bright indirect light",
        "watering": "When the top inch of soil is dry",
    },
    {
        "name": "Basil",
        "image": os.path.join(PLANTS_DIR, "basil.png"),
        "light": "6+ hours of sunlight daily",
        "watering": "Keep soil evenly moist, water when top feels dry",
    },
    {
        "name": "Apple",
        "image": os.path.join(PLANTS_DIR, "apple.png"),
        "light": "Full sun (at least 6-8 hours daily)",
        "watering": "Deep watering weekly, more during fruit development",
    },
    {
        "name": "Strawberry",
        "image": os.path.join(PLANTS_DIR, "strawberry.png"),
        "light": "Full sun (6-8 hours daily)",
        "watering": "Keep soil consistently moist, water regularly especially during fruiting",
    },
]

DISEASE_SAMPLES = [
    {
        "title": "Rose buds with aphids",
        "plant": "Rose",
        "image": os.path.join(SAMPLES_DIR, "rose_buds_aphids.png"),
        "symptoms": "Rose buds covered with small green insects clustered on buds and stems; sticky residue; distorted growth.",
        "expected": "Aphids (common on rose buds)",
    },
    {
        "title": "Orange leaves turning yellow",
        "plant": "Orange tree",
        "image": os.path.join(SAMPLES_DIR, "orange_leaves_yellowing.png"),
        "symptoms": "Citrus leaves turning pale yellow, sometimes with greener veins; overall chlorosis; slow growth.",
        "expected": "Chlorosis (often nutrient deficiency like iron/nitrogen) or watering stress",
    },
    {
        "title": "Tomato plant with yellow leaves",
        "plant": "Tomato",
        "image": os.path.join(SAMPLES_DIR, "tomato_yellow_leaves.png"),
        "symptoms": "Older tomato leaves yellowing from bottom up; sometimes soft stems; may progress upward.",
        "expected": "Nitrogen deficiency, overwatering/root stress, or disease depending on spotting/wilting",
    },

    # Optional extras (add files to assets/disease_samples/)
    {
        "title": "Rose black spot",
        "plant": "Rose",
        "image": os.path.join(SAMPLES_DIR, "rose_black_spot.png"),
        "symptoms": "Rose leaves with black/dark circular spots, yellowing around spots, leaves dropping.",
        "expected": "Black spot (fungal disease)",
    },
    {
        "title": "Tomato septoria leaf spot",
        "plant": "Tomato",
        "image": os.path.join(SAMPLES_DIR, "tomato_septoria_leaf_spot.png"),
        "symptoms": "Many small circular spots with darker edges on lower leaves; yellowing; spots multiply.",
        "expected": "Septoria leaf spot (fungal)",
    },
]

THUMB_SIZE = (420, 280)  # (width, height) – tweak as you like

def make_thumb(img_path: str, size=THUMB_SIZE):
    """Center-crop + resize to a consistent thumbnail size."""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    target_w, target_h = size
    target_ratio = target_w / target_h
    img_ratio = w / h

    # center-crop to target aspect ratio
    if img_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img.resize(size, Image.Resampling.LANCZOS)


def main():
    st.set_page_config(page_title="Love your Garden", page_icon="🌿", layout="wide")

    # Header with image and title
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists(os.path.join(SAMPLES_DIR, "main_page.png")):
            header_img = make_thumb(os.path.join(SAMPLES_DIR, "main_page.png"), size=(200, 200))
            st.image(header_img)
    with col2:
        st.title("🌿 Love your Garden")
        st.subheader("Plant Care Advisor & Gardening Log")
        st.write("Get care advice, diagnose issues, and track your gardening tasks in one place.")

    # Keep the log in session so it persists across interactions
    if "log" not in st.session_state:
        st.session_state.log = GardeningLog()

    log: GardeningLog = st.session_state.log

    # Sidebar settings
    with st.sidebar:
        st.header("Settings")
        use_llm = st.checkbox("Use LLM refinement (if configured in code)", value=False)
        st.markdown(
            "LLM refinement is optional. Edit `call_llm` in `plant_agent_core.py` "
            "to connect it to your preferred model."
        )

    tab1, tab2, tab3 = st.tabs(["Plant Care Advisor", "Disease Diagnosis", "Log & Tasks"])

    # --- Tab 1: Plant Care Advisor ---
    with tab1:
        st.subheader("Plant Care Advice")

        st.markdown("### Popular plants (click to get care advice)")

        # Session state for selected plant
        if "selected_plant" not in st.session_state:
            st.session_state.selected_plant = None

        cols = st.columns(5)
        for i, plant in enumerate(PLANT_CARE_SAMPLES):
            col = cols[i % 5]
            with col:
                with st.container():
                    if os.path.exists(plant["image"]):
                        thumb = make_thumb(plant["image"], size=(120, 120))
                        st.image(thumb, use_container_width=True)
                    else:
                        st.info(f"Add image:\n{os.path.basename(plant['image'])}")

                    if st.button(plant["name"], key=f"plant_{i}", use_container_width=True):
                        st.session_state.selected_plant = plant

        # Show care plan for selected plant
        if st.session_state.selected_plant:
            plant = st.session_state.selected_plant
            st.markdown(f"---")
            st.markdown(f"### Care plan for **{plant['name']}**")

            with st.spinner("Generating care advice..."):
                plan = generate_care_plan(
                    plant_name=plant["name"],
                    light=plant["light"],
                    watering_habit=plant["watering"],
                    issues=None,
                    use_llm=use_llm,
                )
                st.markdown(plan)

                if st.checkbox(f"Log this care review for {plant['name']}", value=False, key="log_plant_sample"):
                    log.add_entry(
                        plant_name=plant["name"],
                        action="care review",
                        notes=f"Reviewed care plan. Light: {plant['light']}, Watering: {plant['watering']}",
                    )
                    st.success(f"Care review for {plant['name']} logged.")

        st.markdown("---")
        st.markdown("### Custom plant care advice")

        with st.form("care_form"):
            plant_name = st.text_input("Plant name", value="Pothos")
            light = st.text_input("Light conditions", value="bright indirect light")
            watering = st.text_input("Watering habit", value="when the top inch of soil is dry")
            issues = st.text_area("Any visible issues? (optional)", "")
            submitted = st.form_submit_button("Generate Care Plan")

        if submitted:
            plan = generate_care_plan(
                plant_name=plant_name,
                light=light,
                watering_habit=watering,
                issues=issues or None,
                use_llm=use_llm,
            )
            st.markdown("### Care Plan")
            st.markdown(plan)

            if st.checkbox("Log this as a care review", value=True):
                log.add_entry(
                    plant_name=plant_name,
                    action="care review",
                    notes=f"Conditions: light={light}, watering={watering}",
                )
                st.success("Care review logged.")

    # --- Tab 2: Disease Diagnosis ---
    with tab2:
        st.subheader("Disease / Issue Diagnosis")

        st.markdown("### Sample disease photos (click to auto-fill)")

        # session state for selected example
        if "selected_sample" not in st.session_state:
            st.session_state.selected_sample = None

        cols = st.columns(3)
        for i, sample in enumerate(DISEASE_SAMPLES):
            col = cols[i % 3]
            with col:
                with st.container():
                    if os.path.exists(sample["image"]):
                        thumb = make_thumb(sample["image"])
                        st.image(thumb, use_container_width=True)
                    else:
                        st.warning(f"Missing: {os.path.basename(sample['image'])}")

                    st.caption(sample["title"])  # use caption below; avoids varying caption spacing

                    if st.button(f"Use: {sample['title']}", key=f"use_sample_{i}", use_container_width=True):
                        st.session_state.selected_sample = sample


        # If user selected a sample, show its predicted issue + run your diagnosis
        if st.session_state.selected_sample:
            s = st.session_state.selected_sample
            st.info(f"Selected: **{s['title']}**  \nExpected issue: **{s['expected']}**")

            # Run your existing diagnosis engine (rule-based + optional LLM)
            result = diagnose_disease(s["symptoms"], use_llm=use_llm)

            st.markdown("### Diagnosis Summary")
            st.write(result["summary"])
            st.markdown("### Suggested Actions")
            st.write(result["advice"])

            if st.button("Log this sample diagnosis"):
                log.add_entry(
                    plant_name=s["plant"],
                    action="diagnosis (sample)",
                    notes=f"{s['title']} | Symptoms: {s['symptoms']}",
                )
                st.success("Sample diagnosis logged.")

        with st.form("diagnosis_form"):
            plant_name_d = st.text_input("Plant name (optional)", "")
            symptoms = st.text_area(
                "Describe the symptoms",
                value="Leaves are turning yellow at the bottom and feel soft.",
                height=120,
            )
            submitted_diag = st.form_submit_button("Diagnose")

        if submitted_diag:
            result = diagnose_disease(symptoms, use_llm=use_llm)
            st.markdown("### Diagnosis Summary")
            st.write(result["summary"])
            st.markdown("### Suggested Actions")
            st.write(result["advice"])

            if st.checkbox("Log this diagnosis", value=True, key="log_diag"):
                log.add_entry(
                    plant_name=plant_name_d or "Unknown plant",
                    action="diagnosis",
                    notes=symptoms,
                )
                st.success("Diagnosis logged.")

    # --- Tab 3: Log & Tasks ---
    with tab3:
        st.subheader("Quick Log Entry")

        with st.form("log_form"):
            plant_name_l = st.text_input("Plant name", key="log_plant")
            action = st.text_input("Action (e.g., watered, fertilized, pruned)", key="log_action")
            notes = st.text_area("Notes (optional)", key="log_notes")
            submitted_log = st.form_submit_button("Add to Log")

        if submitted_log:
            next_due = suggest_next_due(action)
            log.add_entry(
                plant_name=plant_name_l,
                action=action,
                notes=notes,
                next_due=next_due,
            )
            if next_due:
                st.success(f"Logged. Suggested next reminder: {next_due.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.success("Logged.")

            # Generate LLM-based upcoming task suggestion
            if use_llm:
                with st.spinner("Analyzing your garden activities..."):
                    upcoming_task = generate_upcoming_task_from_logs(log, use_llm=True)
                    if upcoming_task:
                        st.info(f"💡 **Suggested Upcoming Task**\n\n{upcoming_task}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Recent Log Entries")
            recent = log.get_recent_entries()
            if not recent:
                st.info("No log entries yet.")
            else:
                for e in recent:
                    st.markdown(
                        f"- **{e.plant_name}** • {e.action} • {e.timestamp}"
                        + (f" • _next due: {e.next_due}_" if e.next_due else "")
                    )
                    if e.notes:
                        st.caption(e.notes)

        with col2:
            st.markdown("### Upcoming Tasks")
            upcoming = log.get_upcoming_tasks()
            if not upcoming:
                st.info("No upcoming tasks scheduled.")
            else:
                for e in upcoming:
                    st.markdown(
                        f"- ⏰ **{e.next_due}** • {e.plant_name} • {e.action}"
                    )
                    if e.notes:
                        st.caption(e.notes)


if __name__ == "__main__":
    main()
