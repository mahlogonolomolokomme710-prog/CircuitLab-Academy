"""Release 4.7 — Engineering Analytics and Performance Intelligence.

Analytics are descriptive summaries of lecturer-entered Release 4.6 records.
They are not predictive models, official grades, or independently verified results.
"""
from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import Any

import streamlit as st

from release4_lecturer import validate_workspace


def build_class_analytics(workspace: dict[str, Any], class_id: str) -> dict[str, Any]:
    """Summarise reviewed marks, rubric performance and submission coverage."""
    data = validate_workspace(workspace)
    group = next((c for c in data["classes"] if c["id"] == class_id), None)
    if group is None:
        raise ValueError("Class not found.")
    assignments = [a for a in data["assignments"] if a["class_id"] == class_id]
    students = group["students"]
    assignment_count = len(assignments)
    per_student: dict[str, dict[str, Any]] = {}
    for student in students:
        per_student[student["id"]] = {
            "student_id": student["id"], "name": student["name"],
            "reviewed_marks": [], "reviewed_assignments": 0,
            "records": 0, "received": 0, "late": 0, "not_received": 0,
            "missing_reviews": 0, "criterion_marks": defaultdict(list),
        }
    criterion_totals: dict[str, list[float]] = defaultdict(list)
    assignment_summaries = []
    all_reviewed_percentages = []
    status_counts = {"Not received": 0, "Received": 0, "Late": 0, "Reviewed": 0}
    for assignment in assignments:
        record_map = {r["student_id"]: r for r in assignment["records"]}
        reviewed_scores = []
        for student in students:
            target = per_student[student["id"]]
            record = record_map.get(student["id"])
            if record is None:
                target["not_received"] += 1
                target["missing_reviews"] += 1
                status_counts["Not received"] += 1
                continue
            target["records"] += 1
            status = record["status"]
            status_counts[status] += 1
            if status in ("Received", "Late", "Reviewed"):
                target["received"] += 1
            if status == "Late":
                target["late"] += 1
            if status == "Not received":
                target["not_received"] += 1
            if status != "Reviewed":
                target["missing_reviews"] += 1
                continue
            total = sum(float(record["marks"].get(c["criterion"], 0)) for c in assignment["rubric"])
            percentage = total
            target["reviewed_marks"].append(percentage)
            target["reviewed_assignments"] += 1
            reviewed_scores.append(percentage)
            all_reviewed_percentages.append(percentage)
            for criterion in assignment["rubric"]:
                name = criterion["criterion"]
                maximum = criterion["weight"]
                score = float(record["marks"].get(name, 0))
                normalised = 100 * score / maximum
                target["criterion_marks"][name].append(normalised)
                criterion_totals[name].append(normalised)
        assignment_summaries.append({
            "assignment": assignment["title"], "due_date": assignment["due_date"],
            "students": len(students), "records_received": sum(
                1 for s in students if s["id"] in record_map and
                record_map[s["id"]]["status"] in ("Received", "Late", "Reviewed")),
            "reviewed": len(reviewed_scores),
            "average_reviewed_mark": sum(reviewed_scores) / len(reviewed_scores) if reviewed_scores else None,
        })
    student_rows = []
    for row in per_student.values():
        scores = row["reviewed_marks"]
        average = sum(scores) / len(scores) if scores else None
        coverage = 100 * row["reviewed_assignments"] / assignment_count if assignment_count else None
        student_rows.append({
            "student_id": row["student_id"], "name": row["name"],
            "reviewed_average_percent": round(average, 2) if average is not None else None,
            "assignments_reviewed": row["reviewed_assignments"],
            "assignments_in_class": assignment_count,
            "review_coverage_percent": round(coverage, 2) if coverage is not None else None,
            "records_entered": row["records"], "received_or_late": row["received"],
            "late_records": row["late"], "not_received_or_unrecorded": row["not_received"],
            "awaiting_review": row["missing_reviews"],
            "support_flag": ("Review low average" if average is not None and average < 50
                             else "Review incomplete records" if row["missing_reviews"] else "No flag from available records"),
        })
    criterion_rows = [
        {"criterion": name, "mean_percent_of_criterion": round(sum(values) / len(values), 2),
         "observations": len(values)}
        for name, values in sorted(criterion_totals.items())
    ]
    return {
        "class_name": group["name"], "module": group["module"], "cohort": group["cohort"],
        "student_count": len(students), "assignment_count": assignment_count,
        "reviewed_assessment_count": len(all_reviewed_percentages),
        "overall_reviewed_average": (sum(all_reviewed_percentages) / len(all_reviewed_percentages)
                                     if all_reviewed_percentages else None),
        "status_counts": status_counts, "students": student_rows,
        "assignments": assignment_summaries, "criteria": criterion_rows,
    }


def student_analytics_csv(analytics: dict[str, Any]) -> str:
    output = io.StringIO()
    rows = analytics["students"]
    fields = list(rows[0]) if rows else [
        "student_id", "name", "reviewed_average_percent", "assignments_reviewed",
        "assignments_in_class", "review_coverage_percent", "records_entered",
        "received_or_late", "late_records", "not_received_or_unrecorded",
        "awaiting_review", "support_flag",
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def analytics_markdown(analytics: dict[str, Any]) -> str:
    average = analytics["overall_reviewed_average"]
    lines = [
        f"# Engineering performance overview — {analytics['class_name']}", "",
        f"**Module:** {analytics['module'] or 'Not supplied'}",
        f"**Cohort:** {analytics['cohort'] or 'Not supplied'}",
        f"**Students:** {analytics['student_count']}",
        f"**Assignments:** {analytics['assignment_count']}",
        f"**Overall mean of reviewed assignment marks:** {'Not available' if average is None else f'{average:.1f}%'}",
        "", "## Submission and review coverage", "",
        "| Status | Count |", "|---|---:|",
    ]
    lines.extend(f"| {status} | {count} |" for status, count in analytics["status_counts"].items())
    lines.extend(["", "## Assignment overview", "",
                  "| Assignment | Due date | Received / late / reviewed | Reviewed | Mean reviewed mark |",
                  "|---|---|---:|---:|---:|"])
    for item in analytics["assignments"]:
        mean = "—" if item["average_reviewed_mark"] is None else f"{item['average_reviewed_mark']:.1f}%"
        lines.append(f"| {item['assignment'].replace('|', '\\|')} | {item['due_date']} | {item['records_received']} | {item['reviewed']} | {mean} |")
    lines.extend(["", "## Rubric criterion performance", "",
                  "| Criterion | Mean percentage of criterion marks | Observations |",
                  "|---|---:|---:|"])
    for item in analytics["criteria"]:
        lines.append(f"| {item['criterion'].replace('|', '\\|')} | {item['mean_percent_of_criterion']:.1f}% | {item['observations']} |")
    lines.extend(["", "## Student-level descriptive overview", "",
                  "| Student ID | Student | Reviewed average | Reviewed / assignments | Review coverage | Review note |",
                  "|---|---|---:|---:|---:|---|"])
    for row in analytics["students"]:
        avg = "—" if row["reviewed_average_percent"] is None else f"{row['reviewed_average_percent']:.1f}%"
        cov = "—" if row["review_coverage_percent"] is None else f"{row['review_coverage_percent']:.1f}%"
        name = row["name"].replace("|", "\\|")
        lines.append(f"| {row['student_id']} | {name} | {avg} | {row['assignments_reviewed']}/{row['assignments_in_class']} | {cov} | {row['support_flag']} |")
    lines.extend([
        "", "## Interpretation and data limitations",
        "These are descriptive summaries of lecturer-entered records only. An assignment mark is included in averages only when its record is marked Reviewed. Missing or unreviewed work is not treated as a zero. Criterion comparisons are normalised to each criterion's own maximum and combine observations across assignments that may use different rubrics; interpret them in context.",
        "The review notes are simple flags for human follow-up, not predictions, diagnoses, automated decisions or student rankings. They do not account for accommodations, assessment difficulty, cohort context or data-entry errors. Verify records and apply institutional policy before any academic decision.",
        "This report is not an official institutional gradebook, verified student record or evidence of competency. Handle student information as confidential.",
    ])
    return "\n".join(lines) + "\n"


def render_performance_analytics() -> None:
    import pandas as pd

    st.markdown("""
    <div style="padding:22px 26px;border-radius:16px;background:linear-gradient(110deg,#14263b,#22566a);color:#f4fbff;margin-bottom:14px">
      <div style="letter-spacing:.15em;font-size:.72rem;color:#72e1d1;font-weight:700">CIRCUITLAB ACADEMY · RELEASE 4.7</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">Engineering Analytics & Performance Intelligence</h2>
      <p style="color:#d0e3eb;margin:0">Understand assessment outcomes, review coverage and topic-level patterns using lecturer-entered records.</p>
    </div>
    """, unsafe_allow_html=True)
    workspace = st.session_state.get("r46_lecturer_workspace")
    if not workspace:
        st.info("Create a class, add students and enter assignment records in Release 4.6 to begin analysing performance.")
        return
    workspace = validate_workspace(workspace)
    if not workspace["classes"]:
        st.info("No class groups are available yet. Create a class in Release 4.6.")
        return
    selected = st.selectbox("Class group to analyse",
        [c["id"] for c in workspace["classes"]],
        format_func=lambda x: next(c["name"] for c in workspace["classes"] if c["id"] == x),
        key="r47_analytics_class")
    analytics = build_class_analytics(workspace, selected)
    st.caption("Descriptive analysis only · Uses records marked Reviewed · Unreviewed or unrecorded assignments are not counted as zero.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students", analytics["student_count"])
    m2.metric("Assignments", analytics["assignment_count"])
    m3.metric("Reviewed records", analytics["reviewed_assessment_count"])
    avg = analytics["overall_reviewed_average"]
    m4.metric("Mean reviewed mark", "—" if avg is None else f"{avg:.1f}%")
    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("#### Submission and review status")
        st.bar_chart(pd.DataFrame([{"Status": k, "Records": v}
                                   for k, v in analytics["status_counts"].items()]).set_index("Status"))
    with right:
        st.markdown("#### Mean mark by assignment")
        assignment_rows = [x for x in analytics["assignments"] if x["average_reviewed_mark"] is not None]
        if assignment_rows:
            st.bar_chart(pd.DataFrame([{"Assignment": x["assignment"],
                                         "Mean reviewed mark (%)": x["average_reviewed_mark"]}
                                        for x in assignment_rows]).set_index("Assignment"))
        else:
            st.info("No reviewed assignment marks are available for this class.")
    st.markdown("#### Rubric criterion patterns")
    if analytics["criteria"]:
        st.bar_chart(pd.DataFrame([{"Criterion": x["criterion"],
                                    "Mean criterion score (%)": x["mean_percent_of_criterion"]}
                                   for x in analytics["criteria"]]).set_index("Criterion"))
        st.caption("Criterion means are normalised to each criterion's maximum. Criteria across different assignments may not be directly comparable.")
    else:
        st.info("No reviewed rubric marks are available yet.")
    st.markdown("#### Student progress overview")
    st.dataframe(pd.DataFrame(analytics["students"]), use_container_width=True, hide_index=True)
    st.caption("Review notes are simple human-follow-up flags: low reviewed average or incomplete records. They are not predictions, grades or automated interventions.")
    st.markdown("#### Assignment-level detail")
    st.dataframe(pd.DataFrame(analytics["assignments"]), use_container_width=True, hide_index=True)
    st.download_button("Download student analytics CSV", student_analytics_csv(analytics),
                       "circuitlab_student_analytics.csv", "text/csv")
    st.download_button("Download class performance report (Markdown)", analytics_markdown(analytics),
                       "circuitlab_class_performance_report.md", "text/markdown")
