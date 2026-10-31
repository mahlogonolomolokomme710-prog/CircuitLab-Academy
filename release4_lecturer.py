"""Release 4.6 — Lecturer and Classroom Management Workspace.

A session-based teaching workspace for class rosters, assignment briefs, rubrics,
and lecturer-entered submission/mark records. It is not a multi-user LMS,
student submission portal, institutional gradebook, or permanent database.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date
from typing import Any

import streamlit as st

SCHEMA_VERSION = 1
SUBMISSION_STATUSES = ("Not received", "Received", "Late", "Reviewed")
MAX_CLASSES = 50
MAX_STUDENTS_PER_CLASS = 500
MAX_ASSIGNMENTS = 200


def new_workspace() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "classes": [], "assignments": []}


def _clean_text(value: Any, limit: int = 4000) -> str:
    return str(value if value is not None else "").strip()[:limit]


def validate_rubric(rubric: Any) -> list[dict[str, Any]]:
    if not isinstance(rubric, list) or not rubric:
        raise ValueError("An assignment needs at least one rubric criterion.")
    clean = []
    names = set()
    for item in rubric:
        if not isinstance(item, dict):
            raise ValueError("Each rubric criterion must be an object.")
        name = _clean_text(item.get("criterion"), 160)
        try:
            weight = int(item.get("weight"))
        except (TypeError, ValueError):
            raise ValueError("Rubric weights must be whole numbers.")
        if not name or name.casefold() in names:
            raise ValueError("Rubric criteria must have unique, non-empty names.")
        if weight <= 0 or weight > 100:
            raise ValueError("Each rubric weight must be between 1 and 100.")
        names.add(name.casefold())
        clean.append({"criterion": name, "weight": weight})
    if sum(x["weight"] for x in clean) != 100:
        raise ValueError("Rubric weights must add up to exactly 100.")
    return clean


def validate_workspace(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported workspace file or schema version.")
    classes = data.get("classes", [])
    assignments = data.get("assignments", [])
    if not isinstance(classes, list) or not isinstance(assignments, list):
        raise ValueError("Classes and assignments must be lists.")
    if len(classes) > MAX_CLASSES or len(assignments) > MAX_ASSIGNMENTS:
        raise ValueError("Workspace exceeds the supported class or assignment limit.")
    clean_classes = []
    class_ids = set()
    for raw in classes:
        if not isinstance(raw, dict):
            raise ValueError("Each class must be an object.")
        cid = _clean_text(raw.get("id"), 80)
        name = _clean_text(raw.get("name"), 160)
        if not cid or not name or cid in class_ids:
            raise ValueError("Each class needs a unique ID and name.")
        class_ids.add(cid)
        raw_students = raw.get("students", [])
        if not isinstance(raw_students, list) or len(raw_students) > MAX_STUDENTS_PER_CLASS:
            raise ValueError("A class roster must be a list of at most 500 students.")
        students, student_ids = [], set()
        for student in raw_students:
            if not isinstance(student, dict):
                raise ValueError("Each student record must be an object.")
            sid = _clean_text(student.get("id"), 120)
            student_name = _clean_text(student.get("name"), 160)
            if not sid or not student_name or sid.casefold() in student_ids:
                raise ValueError("Every student needs a unique identifier and name within the class.")
            student_ids.add(sid.casefold())
            students.append({"id": sid, "name": student_name,
                             "email": _clean_text(student.get("email"), 254)})
        clean_classes.append({"id": cid, "name": name,
                              "module": _clean_text(raw.get("module"), 160),
                              "cohort": _clean_text(raw.get("cohort"), 120),
                              "students": students})
    clean_assignments = []
    assignment_ids = set()
    for raw in assignments:
        if not isinstance(raw, dict):
            raise ValueError("Each assignment must be an object.")
        aid = _clean_text(raw.get("id"), 80)
        cid = _clean_text(raw.get("class_id"), 80)
        title = _clean_text(raw.get("title"), 200)
        if not aid or aid in assignment_ids or cid not in class_ids or not title:
            raise ValueError("Each assignment needs a unique ID, valid class and title.")
        assignment_ids.add(aid)
        try:
            due = date.fromisoformat(_clean_text(raw.get("due_date"), 10)).isoformat()
        except ValueError:
            raise ValueError("Assignment due dates must use YYYY-MM-DD.")
        rubric = validate_rubric(raw.get("rubric"))
        student_ids = {s["id"] for c in clean_classes if c["id"] == cid for s in c["students"]}
        raw_records = raw.get("records", [])
        if not isinstance(raw_records, list):
            raise ValueError("Assignment records must be a list.")
        records, recorded_students = [], set()
        for record in raw_records:
            if not isinstance(record, dict):
                raise ValueError("Each submission record must be an object.")
            sid = _clean_text(record.get("student_id"), 120)
            status = _clean_text(record.get("status"), 30)
            if sid not in student_ids or sid in recorded_students or status not in SUBMISSION_STATUSES:
                raise ValueError("A submission record has an unknown student, duplicate student or invalid status.")
            recorded_students.add(sid)
            marks_raw = record.get("marks", {})
            if not isinstance(marks_raw, dict):
                raise ValueError("Marks must be stored by rubric criterion.")
            marks = {}
            for criterion in rubric:
                value = marks_raw.get(criterion["criterion"], 0)
                try:
                    score = float(value)
                except (TypeError, ValueError):
                    raise ValueError("Marks must be numeric.")
                if score < 0 or score > criterion["weight"]:
                    raise ValueError(f"Marks for {criterion['criterion']} must be between 0 and {criterion['weight']}.")
                marks[criterion["criterion"]] = score
            submitted_on = _clean_text(record.get("submitted_on"), 10)
            if submitted_on:
                try:
                    submitted_on = date.fromisoformat(submitted_on).isoformat()
                except ValueError:
                    raise ValueError("Submission dates must use YYYY-MM-DD.")
            records.append({"student_id": sid, "status": status, "submitted_on": submitted_on,
                            "marks": marks, "feedback": _clean_text(record.get("feedback"), 4000)})
        clean_assignments.append({"id": aid, "class_id": cid, "title": title,
                                  "brief": _clean_text(raw.get("brief"), 8000),
                                  "due_date": due, "rubric": rubric, "records": records})
    return {"schema_version": SCHEMA_VERSION, "classes": clean_classes,
            "assignments": clean_assignments}


def add_class(workspace: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    candidate = dict(workspace)
    candidate["classes"] = list(workspace.get("classes", [])) + [item]
    return validate_workspace(candidate)


def add_student(workspace: dict[str, Any], class_id: str, student: dict[str, Any]) -> dict[str, Any]:
    candidate = json.loads(json.dumps(workspace))
    group = next((c for c in candidate["classes"] if c["id"] == class_id), None)
    if group is None:
        raise ValueError("Class not found.")
    group["students"].append(student)
    return validate_workspace(candidate)


def import_roster_csv(workspace: dict[str, Any], class_id: str, content: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not {"student_id", "name"}.issubset(
            {str(x).strip().lower() for x in reader.fieldnames}):
        raise ValueError("CSV must contain student_id and name columns; email is optional.")
    rows = []
    for row in reader:
        normal = {str(k).strip().lower(): v for k, v in row.items() if k is not None}
        if _clean_text(normal.get("student_id")) or _clean_text(normal.get("name")):
            rows.append({"id": _clean_text(normal.get("student_id"), 120),
                         "name": _clean_text(normal.get("name"), 160),
                         "email": _clean_text(normal.get("email"), 254)})
    candidate = json.loads(json.dumps(workspace))
    group = next((c for c in candidate["classes"] if c["id"] == class_id), None)
    if group is None:
        raise ValueError("Class not found.")
    group["students"].extend(rows)
    return validate_workspace(candidate)


def add_assignment(workspace: dict[str, Any], assignment: dict[str, Any]) -> dict[str, Any]:
    candidate = json.loads(json.dumps(workspace))
    candidate["assignments"].append(assignment)
    return validate_workspace(candidate)


def record_submission(workspace: dict[str, Any], assignment_id: str, record: dict[str, Any]) -> dict[str, Any]:
    candidate = json.loads(json.dumps(workspace))
    assignment = next((a for a in candidate["assignments"] if a["id"] == assignment_id), None)
    if assignment is None:
        raise ValueError("Assignment not found.")
    sid = _clean_text(record.get("student_id"), 120)
    assignment["records"] = [r for r in assignment["records"] if r["student_id"] != sid]
    assignment["records"].append(record)
    return validate_workspace(candidate)


def assignment_summary(workspace: dict[str, Any], assignment_id: str) -> dict[str, Any]:
    assignment = next((a for a in workspace["assignments"] if a["id"] == assignment_id), None)
    if assignment is None:
        raise ValueError("Assignment not found.")
    group = next(c for c in workspace["classes"] if c["id"] == assignment["class_id"])
    records = {r["student_id"]: r for r in assignment["records"]}
    rows = []
    for student in group["students"]:
        record = records.get(student["id"], {})
        total = sum(float(v) for v in record.get("marks", {}).values())
        has_marks = bool(record.get("marks")) and record.get("status") == "Reviewed"
        rows.append({"student_id": student["id"], "name": student["name"],
                     "status": record.get("status", "Not received"),
                     "submitted_on": record.get("submitted_on", ""),
                     "marks": total if has_marks else None,
                     "percentage": 100 * total / 100 if has_marks else None,
                     "feedback": record.get("feedback", "")})
    reviewed = [r for r in rows if r["status"] == "Reviewed" and r["marks"] is not None]
    return {"rows": rows, "class_size": len(rows), "received": sum(r["status"] in ("Received", "Late", "Reviewed") for r in rows),
            "reviewed": len(reviewed),
            "average_percentage": sum(r["percentage"] for r in reviewed) / len(reviewed) if reviewed else None}


def assignment_csv(workspace: dict[str, Any], assignment_id: str) -> str:
    summary = assignment_summary(workspace, assignment_id)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["student_id", "name", "status", "submitted_on", "marks", "percentage", "feedback"])
    writer.writeheader()
    writer.writerows(summary["rows"])
    return out.getvalue()


def assignment_markdown(workspace: dict[str, Any], assignment_id: str) -> str:
    assignment = next(a for a in workspace["assignments"] if a["id"] == assignment_id)
    group = next(c for c in workspace["classes"] if c["id"] == assignment["class_id"])
    summary = assignment_summary(workspace, assignment_id)
    lines = [f"# {assignment['title']}", "", f"**Class:** {group['name']}",
             f"**Module:** {group['module'] or 'Not supplied'}",
             f"**Due date:** {assignment['due_date']}", "", "## Assignment brief",
             assignment["brief"], "", "## Rubric"]
    lines.extend([f"- {x['criterion']}: {x['weight']} marks" for x in assignment["rubric"]])
    lines.extend(["", "## Lecturer-entered class record", "",
                  "| Student ID | Student | Status | Submitted | Mark | Feedback |",
                  "|---|---|---|---|---:|---|"])
    for row in summary["rows"]:
        mark = "" if row["marks"] is None else f"{row['marks']:g}/100"
        safe = [str(row[k]).replace("|", "\\|").replace("\n", " ") for k in ("student_id", "name", "status", "submitted_on", "feedback")]
        lines.append("| " + " | ".join(safe[:4] + [mark, safe[4]]) + " |")
    lines.extend(["", "## Data and assessment notice",
                  "Submission statuses, marks and feedback are records manually entered by the lecturer. This workspace does not receive files from students, authenticate users, verify identities, or constitute an official institutional gradebook."])
    return "\n".join(lines) + "\n"


def workspace_json(workspace: dict[str, Any]) -> str:
    return json.dumps(validate_workspace(workspace), indent=2, ensure_ascii=False)


def parse_rubric_text(value: str) -> list[dict[str, Any]]:
    rubric = []
    for line in value.splitlines():
        if not line.strip():
            continue
        parts = line.rsplit("|", 1)
        if len(parts) != 2:
            raise ValueError("Use one rubric criterion per line in the format: Criterion | Weight")
        try:
            weight = int(parts[1].strip())
        except ValueError:
            raise ValueError("Rubric weights must be whole numbers.")
        rubric.append({"criterion": parts[0].strip(), "weight": weight})
    return validate_rubric(rubric)


def render_lecturer_workspace() -> None:
    import uuid
    import pandas as pd

    st.markdown("""
    <div style="padding:22px 26px;border-radius:16px;background:linear-gradient(110deg,#102238,#15515b);color:#f4fbff;margin-bottom:14px">
      <div style="letter-spacing:.15em;font-size:.72rem;color:#72e1d1;font-weight:700">CIRCUITLAB ACADEMY · RELEASE 4.6</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">Lecturer & Classroom Management</h2>
      <p style="color:#d0e3eb;margin:0">Organise class rosters, publish assignment briefs, apply transparent rubrics and maintain a lecturer-entered markbook.</p>
    </div>
    """, unsafe_allow_html=True)
    key = "r46_lecturer_workspace"
    if key not in st.session_state:
        st.session_state[key] = new_workspace()
    workspace = validate_workspace(st.session_state[key])
    classes = workspace["classes"]
    assignments = workspace["assignments"]
    overview, class_tab, assignment_tab, markbook, backup = st.tabs(
        ["Overview", "Classes & rosters", "Assignment builder", "Markbook & feedback", "Backup & exports"])
    with overview:
        a, b, c, d = st.columns(4)
        a.metric("Class groups", len(classes))
        b.metric("Students on rosters", sum(len(x["students"]) for x in classes))
        c.metric("Assignments", len(assignments))
        d.metric("Records reviewed", sum(1 for x in assignments for r in x["records"] if r["status"] == "Reviewed"))
        st.caption("All records are local to this Streamlit session until exported as a JSON backup.")
        if assignments:
            st.markdown("#### Assignment activity")
            st.dataframe([{"Assignment": x["title"], "Class": next(c["name"] for c in classes if c["id"] == x["class_id"]),
                           "Due date": x["due_date"], "Rubric criteria": len(x["rubric"]),
                           "Records entered": len(x["records"])} for x in assignments],
                         use_container_width=True, hide_index=True)
        else:
            st.info("Create a class group, add its roster, then build an assignment.")
    with class_tab:
        st.markdown("#### Create a class group")
        with st.form("r46_class_form", clear_on_submit=True):
            class_name = st.text_input("Class name *", placeholder="e.g. Electronics 1 · Group A")
            module = st.text_input("Module / subject")
            cohort = st.text_input("Academic year / cohort")
            create = st.form_submit_button("Create class")
        if create:
            if not class_name.strip():
                st.error("A class name is required.")
            else:
                try:
                    item = {"id": uuid.uuid4().hex, "name": class_name.strip(), "module": module.strip(),
                            "cohort": cohort.strip(), "students": []}
                    st.session_state[key] = add_class(workspace, item)
                    st.success("Class group created.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        if classes:
            selected_class = st.selectbox("Select class group", [c["id"] for c in classes],
                                          format_func=lambda x: next(c["name"] for c in classes if c["id"] == x),
                                          key="r46_roster_class")
            group = next(c for c in classes if c["id"] == selected_class)
            st.caption(f"{group['module'] or 'Module not set'} · {group['cohort'] or 'Cohort not set'} · {len(group['students'])} students")
            with st.form("r46_student_form", clear_on_submit=True):
                sid = st.text_input("Student number / unique ID *")
                sname = st.text_input("Student name *")
                email = st.text_input("Email (optional)")
                add = st.form_submit_button("Add student")
            if add:
                try:
                    st.session_state[key] = add_student(workspace, selected_class,
                        {"id": sid, "name": sname, "email": email})
                    st.success("Student added to the roster.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            template = "student_id,name,email\nSTU001,Example Student,student@example.com\n"
            st.download_button("Download roster CSV template", template, "circuitlab_roster_template.csv", "text/csv")
            roster_file = st.file_uploader("Import roster CSV", type=["csv"], key="r46_roster_upload")
            if roster_file is not None and st.button("Validate and import roster", key="r46_import_roster"):
                try:
                    decoded = roster_file.getvalue().decode("utf-8-sig")
                    st.session_state[key] = import_roster_csv(workspace, selected_class, decoded)
                    st.success("Roster imported and validated.")
                    st.rerun()
                except (UnicodeDecodeError, csv.Error, ValueError) as exc:
                    st.error(f"Roster was not imported: {exc}")
            st.dataframe(pd.DataFrame(group["students"], columns=["id", "name", "email"]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Create a class group to begin building a roster.")
    with assignment_tab:
        if not classes:
            st.info("Create a class group before building an assignment.")
        else:
            with st.form("r46_assignment_form", clear_on_submit=True):
                class_id = st.selectbox("Class group", [c["id"] for c in classes],
                                        format_func=lambda x: next(c["name"] for c in classes if c["id"] == x))
                title = st.text_input("Assignment title *")
                brief = st.text_area("Assignment instructions / learning outcomes", height=140)
                due = st.date_input("Due date", value=date.today())
                rubric_text = st.text_area("Rubric (one criterion per line: Criterion | Weight)",
                    value="Engineering theory and calculations | 25\nCircuit design and schematic | 25\nSimulation / practical evidence | 25\nTechnical discussion and report | 25",
                    height=140)
                create_assignment = st.form_submit_button("Create assignment")
            if create_assignment:
                try:
                    rubric = parse_rubric_text(rubric_text)
                    item = {"id": uuid.uuid4().hex, "class_id": class_id, "title": title,
                            "brief": brief, "due_date": due.isoformat(), "rubric": rubric, "records": []}
                    st.session_state[key] = add_assignment(workspace, item)
                    st.success("Assignment and 100-mark rubric created.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            st.markdown("#### Assignment briefs")
            for item in assignments:
                group = next(c for c in classes if c["id"] == item["class_id"])
                with st.expander(f"{item['title']} · {group['name']} · due {item['due_date']}"):
                    st.write(item["brief"] or "No brief supplied.")
                    st.dataframe(pd.DataFrame(item["rubric"]), use_container_width=True, hide_index=True)
                    st.download_button("Download assignment and rubric",
                        assignment_markdown(workspace, item["id"]),
                        file_name=f"circuitlab_assignment_{item['id'][:8]}.md",
                        mime="text/markdown", key=f"r46_brief_{item['id']}")
    with markbook:
        if not assignments:
            st.info("Create an assignment before entering submission records or marks.")
        else:
            aid = st.selectbox("Assignment", [a["id"] for a in assignments],
                               format_func=lambda x: next(a["title"] for a in assignments if a["id"] == x),
                               key="r46_markbook_assignment")
            assignment = next(a for a in assignments if a["id"] == aid)
            group = next(c for c in classes if c["id"] == assignment["class_id"])
            summary = assignment_summary(workspace, aid)
            a, b, c = st.columns(3)
            a.metric("Received / late / reviewed", summary["received"])
            b.metric("Reviewed", summary["reviewed"])
            c.metric("Class average", "—" if summary["average_percentage"] is None else f"{summary['average_percentage']:.1f}%")
            student_id = st.selectbox("Student", [s["id"] for s in group["students"]],
                                      format_func=lambda x: next(s["name"] + " · " + s["id"] for s in group["students"] if s["id"] == x),
                                      key=f"r46_record_student_{aid}") if group["students"] else None
            if student_id:
                existing = next((r for r in assignment["records"] if r["student_id"] == student_id), {})
                with st.form(f"r46_record_form_{aid}_{student_id}"):
                    status = st.selectbox("Submission status", SUBMISSION_STATUSES,
                                          index=SUBMISSION_STATUSES.index(existing.get("status", "Not received")))
                    submitted_on = st.date_input("Date received", value=date.fromisoformat(existing["submitted_on"]) if existing.get("submitted_on") else date.today())
                    st.markdown("**Rubric marks**")
                    marks = {}
                    for index, criterion in enumerate(assignment["rubric"]):
                        marks[criterion["criterion"]] = st.number_input(
                            f"{criterion['criterion']} (maximum {criterion['weight']})",
                            min_value=0.0, max_value=float(criterion["weight"]), step=1.0,
                            value=float(existing.get("marks", {}).get(criterion["criterion"], 0)),
                            key=f"r46_mark_{aid}_{student_id}_{index}")
                    feedback = st.text_area("Lecturer feedback", value=existing.get("feedback", ""), height=120)
                    save_record = st.form_submit_button("Save submission record and marks")
                if save_record:
                    record = {"student_id": student_id, "status": status,
                              "submitted_on": submitted_on.isoformat(), "marks": marks,
                              "feedback": feedback}
                    try:
                        st.session_state[key] = record_submission(workspace, aid, record)
                        st.success("Lecturer-entered record saved.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            st.markdown("#### Class markbook")
            st.dataframe(pd.DataFrame(summary["rows"]), use_container_width=True, hide_index=True)
            st.download_button("Export markbook CSV", assignment_csv(workspace, aid),
                               file_name=f"circuitlab_markbook_{aid[:8]}.csv", mime="text/csv")
            st.download_button("Export assignment record", assignment_markdown(workspace, aid),
                               file_name=f"circuitlab_assignment_record_{aid[:8]}.md", mime="text/markdown")
            st.caption("A percentage appears only for records marked Reviewed. Marks are manually entered by the lecturer and are not independently verified.")
    with backup:
        st.write("Download a JSON backup regularly. Restore it in a later session to continue working with the same class and assignment records.")
        st.download_button("Download complete lecturer workspace (JSON)", workspace_json(workspace),
                           "circuitlab_lecturer_workspace.json", "application/json")
        upload = st.file_uploader("Restore lecturer workspace JSON", type=["json"], key="r46_workspace_restore")
        if upload is not None and st.button("Validate and restore workspace", type="primary"):
            try:
                restored = validate_workspace(json.loads(upload.getvalue().decode("utf-8")))
                st.session_state[key] = restored
                st.success(f"Restored {len(restored['classes'])} classes and {len(restored['assignments'])} assignments.")
                st.rerun()
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                st.error(f"Workspace was not restored: {exc}")
        st.warning("This workspace is session-based. It has no lecturer/student login, student upload portal, cloud database, automatic notifications, moderation workflow or official TUT/NHLS/LMS integration. Only enter information you are authorised to process. Protect downloaded roster and markbook files as confidential student records.")
