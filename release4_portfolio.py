"""Release 4.5 — Student Engineering Portfolio and Progress Tracker.

Session-based portfolio with explicit JSON backup/restore. It is not an
institutional record, authenticated account, or verified competency credential.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date
from typing import Any

import streamlit as st

STATUSES = ("Planning", "In progress", "Completed", "Needs review")
ARTEFACT_TYPES = ("Engineering project", "Simulation", "Practical laboratory",
                  "Assessment", "Design challenge", "Technical report", "Other")


def new_portfolio() -> dict[str, Any]:
    return {"schema_version": 1, "profile": {"student": "", "programme": "", "institution": ""},
            "entries": []}


def validate_portfolio(data: Any) -> dict[str, Any]:
    """Validate and normalise imported portfolio JSON; reject unknown schema."""
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported portfolio file or schema version.")
    profile = data.get("profile", {})
    entries = data.get("entries", [])
    if not isinstance(profile, dict) or not isinstance(entries, list):
        raise ValueError("Portfolio profile or entries have an invalid structure.")
    clean_profile = {key: str(profile.get(key, ""))[:160]
                     for key in ("student", "programme", "institution")}
    clean_entries = []
    allowed = {"id", "title", "kind", "module", "date", "status", "summary",
               "skills", "evidence", "reflection"}
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("Every portfolio entry must be an object.")
        entry = {key: str(item.get(key, ""))[:4000] for key in allowed}
        if not entry["id"] or not entry["title"]:
            raise ValueError("Every entry needs an ID and title.")
        if entry["status"] not in STATUSES or entry["kind"] not in ARTEFACT_TYPES:
            raise ValueError("An entry contains an unrecognised type or status.")
        clean_entries.append(entry)
    if len(clean_entries) > 250:
        raise ValueError("A portfolio can contain at most 250 entries.")
    return {"schema_version": 1, "profile": clean_profile, "entries": clean_entries}


def add_entry(portfolio: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """Return a validated copy with one new entry; never mutate caller input."""
    candidate = {"schema_version": 1, "profile": portfolio.get("profile", {}),
                 "entries": list(portfolio.get("entries", [])) + [entry]}
    return validate_portfolio(candidate)


def portfolio_progress(portfolio: dict[str, Any]) -> dict[str, Any]:
    entries = portfolio["entries"]
    counts = {status: sum(e["status"] == status for e in entries) for status in STATUSES}
    skills = sorted({skill.strip() for e in entries for skill in e["skills"].split(",")
                     if skill.strip()})
    return {"total": len(entries), "status_counts": counts, "skills": skills,
            "completed": counts["Completed"]}


def portfolio_markdown(portfolio: dict[str, Any]) -> str:
    p = portfolio["profile"]
    lines = ["# Student Engineering Portfolio", "",
             f"**Student:** {p['student'] or 'Not supplied'}",
             f"**Programme:** {p['programme'] or 'Not supplied'}",
             f"**Institution:** {p['institution'] or 'Not supplied'}", "",
             "## Portfolio summary"]
    progress = portfolio_progress(portfolio)
    lines.extend([f"- Artefacts recorded: {progress['total']}",
                  f"- Completed: {progress['completed']}",
                  f"- Skills documented: {', '.join(progress['skills']) or 'None recorded'}", ""])
    for index, e in enumerate(portfolio["entries"], 1):
        lines.extend([f"## {index}. {e['title']}", "",
                      f"- Type: {e['kind']}", f"- Module: {e['module'] or 'Not supplied'}",
                      f"- Date: {e['date'] or 'Not supplied'}", f"- Status: {e['status']}",
                      f"- Skills: {e['skills'] or 'Not supplied'}", "",
                      "### Summary", e["summary"] or "Not supplied", "",
                      "### Evidence / references", e["evidence"] or "Not supplied", "",
                      "### Reflection", e["reflection"] or "Not supplied", ""])
    lines.extend(["## Important note", "This is a student-prepared record. Entries, evidence, skills and completion statuses are self-reported and have not been independently verified or accredited."])
    return "\n".join(lines) + "\n"


def portfolio_csv(portfolio: dict[str, Any]) -> str:
    buffer = io.StringIO()
    fields = ["title", "kind", "module", "date", "status", "skills", "summary", "evidence", "reflection"]
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for entry in portfolio["entries"]:
        writer.writerow({key: entry.get(key, "") for key in fields})
    return buffer.getvalue()


def portfolio_json(portfolio: dict[str, Any]) -> str:
    return json.dumps(validate_portfolio(portfolio), indent=2, ensure_ascii=False)


def render_student_portfolio() -> None:
    st.markdown("""
    <div style="padding:22px 26px;border-radius:16px;background:linear-gradient(110deg,#102238,#15515b);color:#f4fbff;margin-bottom:14px">
      <div style="letter-spacing:.15em;font-size:.72rem;color:#72e1d1;font-weight:700">CIRCUITLAB ACADEMY · RELEASE 4.5</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">Student Engineering Portfolio</h2>
      <p style="color:#d0e3eb;margin:0">Capture the projects, practical work, simulations and engineering skills you develop.</p>
    </div>
    """, unsafe_allow_html=True)
    key = "r45_portfolio"
    if key not in st.session_state:
        st.session_state[key] = new_portfolio()
    portfolio = validate_portfolio(st.session_state[key])
    profile = portfolio["profile"]
    with st.expander("Student profile", expanded=not bool(profile["student"])):
        with st.form("r45_profile_form"):
            student = st.text_input("Student name or preferred identifier", profile["student"])
            programme = st.text_input("Programme / qualification", profile["programme"])
            institution = st.text_input("Institution", profile["institution"])
            if st.form_submit_button("Save profile"):
                portfolio["profile"] = {"student": student.strip(), "programme": programme.strip(),
                                        "institution": institution.strip()}
                st.session_state[key] = portfolio
                st.success("Portfolio profile updated.")
                st.rerun()
    overview, add, records, backup = st.tabs(
        ["Progress overview", "Add portfolio entry", "My portfolio", "Backup and restore"])
    with overview:
        progress = portfolio_progress(portfolio)
        a, b, c = st.columns(3)
        a.metric("Total entries", progress["total"])
        b.metric("Completed entries", progress["completed"])
        c.metric("Skills documented", len(progress["skills"]))
        st.markdown("#### Entry status")
        st.dataframe([{"Status": name, "Entries": count}
                      for name, count in progress["status_counts"].items()],
                     use_container_width=True, hide_index=True)
        st.markdown("#### Skills recorded")
        if progress["skills"]:
            st.write(" · ".join(progress["skills"]))
        else:
            st.info("Add portfolio entries and list the skills used to build your skills record.")
        st.caption("Progress is based on entries you record; it is not an independently assessed competency score.")
    with add:
        with st.form("r45_add_entry_form", clear_on_submit=True):
            title = st.text_input("Entry title *", placeholder="e.g. 5 V regulated supply design")
            kind = st.selectbox("Entry type", ARTEFACT_TYPES)
            module = st.text_input("Module / subject")
            entry_date = st.date_input("Date", value=date.today())
            status = st.selectbox("Status", STATUSES)
            skills = st.text_input("Skills (comma-separated)", placeholder="Circuit analysis, soldering, simulation")
            summary = st.text_area("What did you do? What was the engineering objective?")
            evidence = st.text_area("Evidence or references", help="Describe files, schematic names, simulation outputs or report references. Do not paste private credentials.")
            reflection = st.text_area("Reflection: what worked, what did you learn, what would you improve?")
            submitted = st.form_submit_button("Add to portfolio", type="primary")
        if submitted:
            if not title.strip():
                st.error("An entry title is required.")
            else:
                import uuid
                entry = {"id": uuid.uuid4().hex, "title": title.strip(), "kind": kind,
                         "module": module.strip(), "date": entry_date.isoformat(), "status": status,
                         "skills": skills.strip(), "summary": summary.strip(),
                         "evidence": evidence.strip(), "reflection": reflection.strip()}
                st.session_state[key] = add_entry(portfolio, entry)
                st.success("Entry added to your portfolio.")
                st.rerun()
    with records:
        if not portfolio["entries"]:
            st.info("Your portfolio is empty. Add a project, practical, assessment or simulation.")
        for index, entry in enumerate(portfolio["entries"]):
            with st.expander(f"{entry['title']} · {entry['status']}"):
                st.caption(f"{entry['kind']} · {entry['module'] or 'No module'} · {entry['date']}")
                st.write(entry["summary"] or "No summary supplied.")
                st.markdown(f"**Skills:** {entry['skills'] or 'Not supplied'}")
                st.markdown(f"**Evidence:** {entry['evidence'] or 'Not supplied'}")
                st.markdown(f"**Reflection:** {entry['reflection'] or 'Not supplied'}")
                left, right = st.columns(2)
                new_status = left.selectbox("Update status", STATUSES,
                                            index=STATUSES.index(entry["status"]),
                                            key=f"r45_status_{entry['id']}")
                if right.button("Save status", key=f"r45_save_{entry['id']}"):
                    updated = dict(entry)
                    updated["status"] = new_status
                    portfolio["entries"][index] = updated
                    st.session_state[key] = validate_portfolio(portfolio)
                    st.rerun()
                if st.button("Delete this entry", key=f"r45_delete_{entry['id']}"):
                    portfolio["entries"] = [e for e in portfolio["entries"] if e["id"] != entry["id"]]
                    st.session_state[key] = validate_portfolio(portfolio)
                    st.rerun()
    with backup:
        st.write("Your portfolio is stored in the current Streamlit session. Download a JSON backup regularly and restore it when starting a new session.")
        st.download_button("Download complete portfolio backup (JSON)", portfolio_json(portfolio),
                           file_name="circuitlab_student_portfolio.json", mime="application/json")
        st.download_button("Download portfolio report (Markdown)", portfolio_markdown(portfolio),
                           file_name="circuitlab_student_portfolio.md", mime="text/markdown")
        st.download_button("Download entries (CSV)", portfolio_csv(portfolio),
                           file_name="circuitlab_portfolio_entries.csv", mime="text/csv")
        upload = st.file_uploader("Restore a previous JSON portfolio", type=["json"], key="r45_restore")
        if upload is not None and st.button("Validate and restore portfolio", type="primary"):
            try:
                restored = validate_portfolio(json.loads(upload.getvalue().decode("utf-8")))
                st.session_state[key] = restored
                st.success(f"Restored {len(restored['entries'])} portfolio entries.")
                st.rerun()
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                st.error(f"Portfolio was not restored: {exc}")
    st.warning("Portfolio entries and skills are self-reported. This feature does not create a verified qualification, accredited transcript, lecturer gradebook or permanent cloud account. Download your backup before ending the session.")
