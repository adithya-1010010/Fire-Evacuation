"""Web view of the simulation. Streamlit Community Cloud runs this file from the repository root.

Deploy: push the repository to GitHub, then open share.streamlit.io -> Deploy -> point it at
this repository. The app is on https://<name>.streamlit.app. Locally:  streamlit run streamlit_app.py
"""

import copy
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from fire_evacuation.generator import (DIFFICULTIES, MAX_SIZE, MIN_SIZE, generate_environment,
                                       random_environment)
from fire_evacuation.main import HELP_TEXT
from fire_evacuation.scenarios import SCENARIOS
from fire_evacuation.simulation import ESCAPED, FAILED, Simulation, route_text

st.set_page_config(page_title="Fire Evacuation Agent", layout="wide")

WALL, FLOOR, FIRE = "#", ".", "F"
CELL_BIG, CELL_SMALL = 26, 18

COLORS = {
    "wall": "#c9c9c9",
    "floor": "#f8f9fa",
    "seen": "#d0ebff",     # inside the sensing radius
    "known": "#ffe066",    # fire the agent has seen but that is not burning
    "fire": "#e03131",
    "walked": "#0ca678",
    "path": "#ffd43b",
    "agent": "#1971c2",
    "exit": "#2f9e44",
}


# ---------------------------------------------------------------- session state
def start_run(env, title):
    st.session_state.template = copy.deepcopy(env)   # untouched copy, so Restart replays it
    st.session_state.sim = Simulation(env)
    st.session_state.title = title
    st.session_state.view = "Run"


def clear_run():
    for key in ("template", "sim", "title"):
        st.session_state.pop(key, None)
    st.session_state.view = "New Simulation"


st.session_state.setdefault("view", "New Simulation")


# ---------------------------------------------------------------- the map
def grid_html(env, agent):
    """The grid as a small HTML table: one div per cell."""
    walked = agent.walked
    start = walked[0]
    walked_cells = set(walked[1:])
    path_cells = set(agent.path)
    known_fire = agent.known_fire
    burning = env.fire
    cell_px = CELL_BIG if env.cols <= 24 else CELL_SMALL

    parts = [f'<div style="display:grid;grid-template-columns:repeat({env.cols},{cell_px}px);'
             f'grid-auto-rows:{cell_px}px;gap:1px;width:max-content;'
             f'border:1px solid #ced4da;background:#ced4da;">']
    for r in range(env.rows):
        for c in range(env.cols):
            here = (r, c)
            symbol = env.grid[r][c]
            background = COLORS["wall"] if symbol == WALL else COLORS["floor"]
            label = ""
            if here == start:
                label = "S"
            if here in path_cells:
                background = COLORS["path"]
            if here in walked_cells:
                background = COLORS["walked"]
            if here in known_fire and here not in burning:
                background = COLORS["known"]
            if here in burning:
                background = COLORS["fire"]
            if here == env.exit_pos:
                background, label = COLORS["exit"], "E"
            if here == env.agent_pos:
                background, label = COLORS["agent"], "A"
            parts.append(
                f'<div style="background:{background};color:#212529;font:600 11px monospace;'
                f'display:flex;align-items:center;justify-content:center;">{label}</div>')
    parts.append("</div>")
    return "".join(parts)


def legend():
    items = [("Wall", "wall"), ("Floor", "floor"), ("Fire burning", "fire"),
             ("Fire seen (memory)", "known"), ("Route left", "path"),
             ("Walked", "walked"), ("Agent", "agent"), ("Exit", "exit")]
    columns = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
        f'<span style="width:11px;height:11px;background:{COLORS[key]};'
        f'border:1px solid #adb5bd;"></span>{name}</span>'
        for name, key in items)
    st.markdown(columns, unsafe_allow_html=True)


# ---------------------------------------------------------------- the run panel
def show_step(sim):
    step = sim.last_step
    if step is None:
        return
    st.markdown(f"**Step {step['number']}** (tick {step['tick']})")
    st.markdown(
        f"- PERCEIVE: {step['perceive']}\n"
        f"- REASON: {step['reason']}\n"
        f"- DECIDE: {step['decide']}\n"
        f"- ACT: {step['act'] or 'nothing to do'}\n"
        f"- ENVIRONMENT: {step['environment'] or 'quiet'}")


def show_history(sim, limit=25):
    rows = sim.history[-limit:]
    with st.expander(f"Step history ({len(sim.history)} steps)"):
        for number, (kind, summary) in enumerate(rows, start=len(sim.history) - len(rows) + 1):
            st.write(f"{number}. {summary}")


def show_report(sim):
    agent = sim.agent
    metrics = sim.get_metrics()
    escaped = sim.status == ESCAPED
    (st.success if escaped else st.error)(
        "AGENT ESCAPED" if escaped else f"AGENT FAILED - {sim.failure_reason}")

    left, right = st.columns(2)
    with left:
        st.write(f"- Steps: **{metrics['steps']}**")
        st.write(f"- Replans: **{metrics['replans']}**")
        st.write(f"- Fire seen: **{len(agent.known_fire)}**")
        st.write(f"- First route length: **{metrics['initial_path_length']}**")
    with right:
        st.write(f"- Ticks: **{metrics['ticks']}**")
        st.write(f"- A* nodes explored: **{metrics['nodes_explored_total']}**")
        st.write(f"- A* time: **{metrics['astar_time_ms']} ms**")
        st.write(f"- Cells walked: **{len(agent.walked) - 1}**")

    with st.expander("Route the agent took", expanded=True):
        st.code(" -> ".join(f"({r},{c})" for r, c in agent.walked) or "(no moves)")
    if metrics["initial_path_length"] is not None and escaped:
        with st.expander("The first route A* found"):
            st.code(f"{metrics['initial_path_length']} moves")


def show_run():
    menu_col, restart_col, step_col, run_col = st.columns(4)
    go_menu = menu_col.button("Menu", use_container_width=True)
    do_restart = restart_col.button("Restart", use_container_width=True)
    if go_menu:
        clear_run()
        return
    if do_restart:
        start_run(copy.deepcopy(st.session_state.template), st.session_state.title)
        return

    sim = st.session_state.sim
    agent = sim.agent
    if step_col.button("Step", type="primary", use_container_width=True, disabled=not sim.is_running()):
        sim.step()
    if run_col.button("Run to end", use_container_width=True, disabled=not sim.is_running()):
        sim.run()
    agent = sim.agent

    left, right = st.columns([1, 1])
    with left:
        st.subheader(st.session_state.title)
        st.markdown(grid_html(sim.env, agent), unsafe_allow_html=True)
        legend()
    with right:
        badge = {"EVACUATING": st.info, ESCAPED: st.success, FAILED: st.error}[sim.status]
        badge(f"Status: {sim.status}")
        a, b, c, d, e = st.columns(5)
        a.metric("Steps", sim.steps)
        b.metric("Replans", agent.replans)
        c.metric("Fire known", len(agent.known_fire))
        d.metric("Route left", len(agent.path))
        e.metric("Clock", sim.env.tick)
        show_step(sim)
        if not sim.is_running():
            show_report(sim)
        show_history(sim)


# ---------------------------------------------------------------- the menu
st.title("Intelligent Fire Evacuation Agent")
st.caption("Classical AI only: rule-based reasoning, A* with the Manhattan heuristic, memory of "
           "seen fire, and replanning. No machine learning.")

VIEWS = ["New Simulation", "Preset Scenarios", "Run", "Help"]
if st.session_state.view not in VIEWS:
    st.session_state.view = "New Simulation"

menu = st.radio("View", VIEWS, horizontal=True, index=VIEWS.index(st.session_state.view))
st.session_state.view = menu

if menu == "New Simulation":
    st.subheader("New Simulation")
    mode = st.radio("Mode", ["Random", "Custom"], horizontal=True)
    if mode == "Random":
        st.write("The program picks the size (10-20) and the difficulty.")
        if st.button("Run random simulation", type="primary"):
            start_run(random_environment(), "Random Simulation")
    else:
        c1, c2, c3 = st.columns(3)
        rows = c1.number_input("Rows", MIN_SIZE, MAX_SIZE, value=12, step=1)
        cols = c2.number_input("Columns", MIN_SIZE, MAX_SIZE, value=12, step=1)
        difficulty = c3.selectbox("Difficulty", list(DIFFICULTIES))
        st.caption(f"Easy: {DIFFICULTIES['Easy']['fire_count']} fires, first at tick "
                   f"{DIFFICULTIES['Easy']['first_tick']}. Medium: "
                   f"{DIFFICULTIES['Medium']['fire_count']} fires, first at tick "
                   f"{DIFFICULTIES['Medium']['first_tick']}. Hard: "
                   f"{DIFFICULTIES['Hard']['fire_count']} fires, first at tick "
                   f"{DIFFICULTIES['Hard']['first_tick']}.")
        if st.button("Run custom simulation", type="primary"):
            env = generate_environment(int(rows), int(cols), difficulty)
            start_run(env, env.name)

elif menu == "Preset Scenarios":
    st.subheader("Preset Scenarios")
    for build in SCENARIOS:
        st.write(f"**{build.__name__.replace('_', ' ').title()}** - {(build.__doc__ or '').strip()}")
        if st.button("Run it", key=build.__name__):
            start_run(build(), build.__name__.replace("_", " ").title())

elif menu == "Help":
    st.subheader("Help")
    st.code(HELP_TEXT.strip())
    st.markdown("This page runs the same simulation as the terminal version (`python run.py`) "
                "and the Pygame version (`python main.py`).")

if st.session_state.view == "Run":
    st.divider()
    if "sim" in st.session_state:
        show_run()
    else:
        st.info("No simulation yet. Start one from New Simulation or Preset Scenarios.")