"""Release 1 — Engineering Command Center.
A polished project-first home for CircuitLab Academy. Existing learning and simulator
workspaces remain available; this module adds a central command centre without replacing them.
"""
from datetime import datetime
import json
import streamlit as st


PROJECT_TYPES = [
    "Power electronics", "Analogue electronics", "Digital electronics",
    "Embedded systems", "Instrumentation", "Circuit fundamentals", "Other",
]
LEVELS = ["Foundation", "Intermediate", "Advanced", "Final-year project"]
STATUSES = ["Planning", "Designing", "Simulating", "Testing", "Completed"]


def _init_state():
    if "cla_projects" not in st.session_state:
        st.session_state.cla_projects = [
            {
                "id": "CLA-001",
                "name": "5 V regulated DC power supply",
                "project_type": "Power electronics",
                "level": "Intermediate",
                "status": "Designing",
                "objective": "Design and investigate a regulated low-voltage DC supply.",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "notes": "Verify rectifier, ripple, regulator headroom and thermal performance.",
            }
        ]
    if "cla_activity" not in st.session_state:
        st.session_state.cla_activity = [
            {"time": datetime.now().strftime("%d %b %Y"), "event": "Engineering Command Center initialized"}
        ]
    if "cla_selected_project" not in st.session_state:
        st.session_state.cla_selected_project = st.session_state.cla_projects[0]["id"]


def _log(event):
    st.session_state.cla_activity.insert(
        0, {"time": datetime.now().strftime("%d %b %Y · %H:%M"), "event": event}
    )
    st.session_state.cla_activity = st.session_state.cla_activity[:30]


def _metric_card(label, value, detail, accent="#36B7C8"):
    st.markdown(
        f"""
        <div class="cla-metric">
          <div class="cla-metric-top"><span>{label}</span><i style="background:{accent}"></i></div>
          <div class="cla-metric-value">{value}</div>
          <div class="cla-metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render():
    _init_state()
    st.markdown(
        """
        <style>
        .block-container {max-width: 1500px; padding-top: 1.35rem; padding-bottom: 3rem;}
        [data-testid="stSidebar"] {border-right: 1px solid rgba(120,145,165,.18);}
        .cla-hero {
          padding: 30px 32px; border-radius: 20px; color: #F4FAFF;
          background: radial-gradient(circle at 82% 15%, rgba(54,183,200,.27), transparent 32%),
                      linear-gradient(115deg,#0A1929 0%,#102D43 55%,#124A5A 100%);
          border: 1px solid rgba(95,190,205,.22); margin-bottom: 18px;
        }
        .cla-eyebrow {font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#72D4DE;font-weight:750;}
        .cla-hero h1 {font-size:2.35rem;line-height:1.12;margin:.55rem 0 .55rem;color:#F4FAFF;font-weight:780;}
        .cla-hero p {font-size:1rem;line-height:1.55;color:#C3D5E1;max-width:760px;margin:0;}
        .cla-hero-foot {display:flex;gap:9px;flex-wrap:wrap;margin-top:20px;}
        .cla-chip {font-size:.73rem;border:1px solid rgba(151,211,220,.3);color:#D6F3F5;border-radius:99px;padding:6px 10px;background:rgba(255,255,255,.055);}
        .cla-section {font-size:1.02rem;font-weight:750;color:var(--text-color);margin:8px 0 4px;}
        .cla-muted {color:var(--text-color);opacity:.66;font-size:.85rem;}
        .cla-metric {border:1px solid rgba(125,150,170,.23);background:linear-gradient(145deg,rgba(125,150,170,.09),rgba(125,150,170,.025));border-radius:15px;padding:15px 16px;min-height:112px;}
        .cla-metric-top {display:flex;justify-content:space-between;align-items:center;color:var(--text-color);opacity:.7;font-size:.75rem;font-weight:650;letter-spacing:.04em;text-transform:uppercase;}
        .cla-metric-top i {width:7px;height:7px;border-radius:50%;display:inline-block;}
        .cla-metric-value {font-size:1.85rem;line-height:1.3;font-weight:800;color:var(--text-color);margin-top:7px;}
        .cla-metric-detail {font-size:.76rem;color:var(--text-color);opacity:.62;margin-top:2px;}
        .cla-project {border:1px solid rgba(125,150,170,.25);border-radius:15px;padding:16px;background:rgba(125,150,170,.045);margin-bottom:10px;}
        .cla-project-title {font-size:1.02rem;font-weight:750;margin-bottom:5px;}
        .cla-project-meta {font-size:.78rem;opacity:.68;}
        .cla-status {display:inline-block;border-radius:99px;padding:4px 9px;font-size:.7rem;font-weight:700;background:rgba(54,183,200,.13);color:#28A9B9;}
        .cla-step {border-left:2px solid #36B7C8;padding:2px 0 12px 14px;margin-left:5px;}
        div[data-testid="stForm"] {border-color:rgba(125,150,170,.25);border-radius:14px;}
        div.stButton > button[kind="primary"] {background:#087F91;border-color:#087F91;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    projects = st.session_state.cla_projects
    active = [p for p in projects if p["status"] != "Completed"]
    completed = [p for p in projects if p["status"] == "Completed"]

    st.markdown(
        """
        <div class="cla-hero">
          <div class="cla-eyebrow">CircuitLab Academy · Release 1</div>
          <h1>Your engineering command center.</h1>
          <p>One workspace to plan engineering projects, organize design work, launch simulations
          and build evidence of what you understand — from first principles to verified decisions.</p>
          <div class="cla-hero-foot">
            <span class="cla-chip">PROJECT-FIRST WORKFLOW</span>
            <span class="cla-chip">SIMULATION-READY</span>
            <span class="cla-chip">ENGINEERING EVIDENCE</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        _metric_card("All projects", str(len(projects)), "Your engineering work")
    with m2:
        _metric_card("In progress", str(len(active)), "Projects still underway", "#36B7C8")
    with m3:
        _metric_card("Completed", str(len(completed)), "Finished project records", "#72B58B")
    with m4:
        _metric_card("Workspace", "READY", "Simulator and learning tools", "#D8A34D")

    st.write("")
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown('<div class="cla-section">Your project workspace</div>', unsafe_allow_html=True)
        st.markdown('<div class="cla-muted">Pick up an existing design or create a new engineering challenge.</div>', unsafe_allow_html=True)
        if projects:
            for project in projects[:4]:
                status = project["status"]
                st.markdown(
                    f'<div class="cla-project"><div class="cla-project-title">{project["name"]}</div>'
                    f'<div class="cla-project-meta">{project["id"]} &nbsp;·&nbsp; {project["project_type"]} &nbsp;·&nbsp; {project["level"]}</div>'
                    f'<div style="margin-top:10px"><span class="cla-status">{status}</span></div>'
                    f'<div class="cla-muted" style="margin-top:9px">{project["objective"]}</div></div>',
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns([1, 5])
                with c1:
                    if st.button("Open project", key=f"open_{project['id']}"):
                        st.session_state.cla_selected_project = project["id"]
                        st.session_state.cla_active_tab = "Projects"
                        st.rerun()
        else:
            st.info("No projects yet. Create your first engineering project.")
    with right:
        st.markdown('<div class="cla-section">Engineering workflow</div>', unsafe_allow_html=True)
        st.markdown('<div class="cla-muted">A consistent process for every design challenge.</div>', unsafe_allow_html=True)
        for title, desc in [
            ("01 · Define", "Translate the brief into measurable requirements."),
            ("02 · Design", "Choose a topology and justify component values."),
            ("03 · Simulate", "Test predictions and inspect circuit behaviour."),
            ("04 · Verify", "Check limits, tolerances and design weaknesses."),
            ("05 · Document", "Capture evidence and communicate decisions."),
        ]:
            st.markdown(
                f'<div class="cla-step"><b>{title}</b><div class="cla-muted">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    overview_tab, projects_tab, launch_tab, activity_tab = st.tabs(
        ["Overview", "Project manager", "Launch a workspace", "Activity"]
    )

    with overview_tab:
        a, b = st.columns([1.2, 1], gap="large")
        with a:
            st.markdown("#### Start with an engineering challenge")
            st.write("Create a project around a real design problem. Your project brief becomes the anchor for calculations, simulation, testing and reporting.")
            if st.button("＋ Create a project", type="primary", key="overview_create"):
                st.session_state.cla_active_tab = "Projects"
                st.info("Open the **Project manager** tab to create and organize your project.")
            st.markdown("#### Your tools, connected by the project")
            st.write("Use the existing simulator, guided build, design calculations and component references as part of one engineering workflow.")
        with b:
            st.markdown("#### Release 1 foundations")
            for item in [
                "Central engineering dashboard",
                "Project creation and status tracking",
                "One-click access to existing workspaces",
                "Exportable project register",
                "Stable legacy tools retained",
            ]:
                st.markdown(f"✓ {item}")

    with projects_tab:
        st.markdown("#### Project manager")
        st.caption("Create and organize engineering projects. Release 1 stores these records in the current Streamlit session; persistent accounts and cloud sync are planned for a later release.")
        with st.form("cla_new_project_form", clear_on_submit=True):
            name = st.text_input("Project name", placeholder="e.g. Adjustable bench power supply")
            objective = st.text_area("Engineering objective", placeholder="What must the circuit or system achieve?")
            x, y = st.columns(2)
            with x:
                project_type = st.selectbox("Engineering domain", PROJECT_TYPES)
            with y:
                level = st.selectbox("Project level", LEVELS)
            submitted = st.form_submit_button("Create engineering project", type="primary")
        if submitted:
            if not name.strip() or not objective.strip():
                st.error("Enter a project name and engineering objective.")
            else:
                project_id = f"CLA-{len(projects) + 1:03d}-{datetime.now().strftime('%H%M%S')}"
                new_project = {
                    "id": project_id, "name": name.strip(), "objective": objective.strip(),
                    "project_type": project_type, "level": level, "status": "Planning",
                    "created": datetime.now().strftime("%Y-%m-%d"), "notes": "",
                }
                st.session_state.cla_projects.append(new_project)
                st.session_state.cla_selected_project = project_id
                _log(f"Created project: {name.strip()}")
                st.success(f"Project {project_id} created.")
                st.rerun()

        if projects:
            options = {f'{p["name"]} · {p["id"]}': p["id"] for p in projects}
            selected_label = next((k for k, v in options.items() if v == st.session_state.cla_selected_project), next(iter(options)))
            selected_label = st.selectbox("Select a project to manage", list(options), index=list(options).index(selected_label))
            selected_id = options[selected_label]
            selected = next(p for p in projects if p["id"] == selected_id)
            st.session_state.cla_selected_project = selected_id
            with st.form(f"cla_edit_{selected_id}"):
                new_status = st.selectbox("Project status", STATUSES, index=STATUSES.index(selected["status"]))
                new_notes = st.text_area("Engineering notes", value=selected.get("notes", ""))
                save = st.form_submit_button("Save project updates", type="primary")
            if save:
                selected["status"] = new_status
                selected["notes"] = new_notes
                _log(f"Updated project: {selected['name']} → {new_status}")
                st.success("Project updated.")
                st.rerun()
            st.markdown("**Project brief**")
            st.write(selected["objective"])
            st.caption(f"Created: {selected['created']} · Domain: {selected['project_type']} · Level: {selected['level']}")
            export = json.dumps(selected, indent=2, ensure_ascii=False)
            st.download_button("Download selected project (JSON)", export, file_name=f"{selected_id.lower()}_project.json", mime="application/json")
            with st.expander("Remove this project"):
                st.warning("This removes the project from this session. Download a copy first if you need to keep it.")
                if st.button("Delete selected project", key=f"delete_{selected_id}"):
                    st.session_state.cla_projects = [p for p in projects if p["id"] != selected_id]
                    st.session_state.cla_selected_project = st.session_state.cla_projects[0]["id"] if st.session_state.cla_projects else ""
                    _log(f"Deleted project: {selected['name']}")
                    st.rerun()

    with launch_tab:
        st.markdown("#### Open an engineering workspace")
        st.write("The existing tools remain available from the main navigation. Choose the workspace that best fits the next step in your project.")
        shortcuts = [
            ("Circuit Simulator", "Open a live CircuitJS simulation.", "Circuit Simulator"),
            ("Prepared Circuit Library", "Start from an editable teaching example.", "Prepared Circuit Library"),
            ("Circuit Workspace", "Explore the guided power-supply schematic.", "Circuit Workspace"),
            ("Design Bench", "Calculate first-pass component values.", "Design Bench"),
            ("Component Library", "Review component roles and specifications.", "Component Library"),
            ("Fault Detective", "Practise systematic troubleshooting.", "Fault Detective"),
            ("Guided Build", "Follow a staged practical workflow.", "Guided Build"),
            ("Project Report", "Prepare a structured engineering report.", "Project Report"),
        ]
        cols = st.columns(2)
        for i, (title, description, destination) in enumerate(shortcuts):
            with cols[i % 2]:
                st.markdown(f"**{title}**")
                st.caption(description)
                if st.button(f"Open {title}", key=f"shortcut_{i}", use_container_width=True):
                    st.session_state["cla_navigation_target"] = destination
                    st.info(f"Select **{destination}** in the left navigation. Your project workspace remains available.")
        st.info("The command center is the new home screen; specialist tools are intentionally retained as dedicated workspaces.")

    with activity_tab:
        st.markdown("#### Recent activity")
        if st.session_state.cla_activity:
            st.dataframe(st.session_state.cla_activity, use_container_width=True, hide_index=True)
        else:
            st.caption("Your project activity will appear here.")
        full_register = {
            "application": "CircuitLab Academy",
            "release": "1.0 — Engineering Interface",
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "projects": projects,
            "activity": st.session_state.cla_activity,
        }
        st.download_button(
            "Export project register and activity (JSON)",
            json.dumps(full_register, indent=2, ensure_ascii=False),
            file_name="circuitlab_academy_project_register.json",
            mime="application/json",
            type="primary",
        )

    st.caption("Release 1 · Engineering Interface. Project data is session-based in this release; export your register before ending the session.")
