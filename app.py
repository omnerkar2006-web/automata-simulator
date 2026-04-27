import streamlit as st
import google.generativeai as genai
from graphviz import Digraph
import re
import json

# Setup Gemini API
genai.configure(api_key="Your_API_Key")
model = genai.GenerativeModel("gemini-flash-latest")

SYSTEM_PROMPT = """
Convert user input into STRICT JSON.

Output ONLY JSON:
{
  "type": "DFA or NFA",
  "states": [],
  "alphabet": [],
  "start": "",
  "final": [],
  "transitions": {
    "state,symbol": ["next_state"]
  }
}

No explanation. No markdown formatting blocks like ```json. Just the raw JSON string.
"""

def generate_automaton(prompt):
    response = model.generate_content(
        SYSTEM_PROMPT + "\nUser Input: " + prompt,
        generation_config={"temperature": 0.2}
    )
    return response.text

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

def validate(automaton):
    required_keys = {"type", "states", "alphabet", "start", "final", "transitions"}
    if not all(k in automaton for k in required_keys):
        return False
        
    states = set(automaton["states"])
    if automaton["start"] not in states: return False
    for f in automaton["final"]:
        if f not in states: return False
    for key, vals in automaton["transitions"].items():
        if "," not in key: return False
        s, sym = key.split(",", 1)
        if s not in states: return False
        for v in vals:
            if v not in states: return False
    return True

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    .stApp {
        background-color: #0a0e17;
        color: #e2e8f0;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6, p, span {
        color: #e2e8f0 !important;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stTextArea textarea, .stTextInput input {
        background-color: #0f1523 !important;
        border: 1px solid #1e293b !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        padding: 12px !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0284c7 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 10px 20px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #0369a1 0%, #075985 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
    }
    
    .section-title {
        color: #38bdf8 !important;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    .section-divider {
        border-top: 1px solid #1e293b;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    
    .formal-def-container, .transition-table-container {
        background-color: transparent;
        padding: 0px;
        margin-bottom: 20px;
    }
    
    .def-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    
    .def-label {
        color: #f8fafc;
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    
    .def-box {
        background-color: #0f1523;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        color: #e2e8f0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }
    
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace;
        background-color: transparent;
        border: 1px solid #1e293b;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .custom-table th, .custom-table td {
        padding: 14px 16px;
        text-align: left;
        border: 1px solid #1e293b;
    }
    
    .custom-table th {
        color: #38bdf8;
        font-weight: 700;
        background-color: #0f1523;
    }
    
    .custom-table td {
        color: #e2e8f0;
        background-color: #0a0e17;
    }
    
    .state-start-final { color: #f43f5e; font-weight: 700; }
    .state-start { color: #f43f5e; font-weight: 700; }
    .state-final { color: #10b981; font-weight: 700; }
    .state-normal { color: #38bdf8; font-weight: 700; }
    
    .stCodeBlock {
        background-color: #0f1523 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px;
    }
    
    /* Graphviz background */
    .stGraphVizChart > div > div {
        background-color: #e2e8f0 !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_formal_definition(automaton):
    states = ", ".join(automaton.get("states", []))
    alphabet = ", ".join(automaton.get("alphabet", []))
    start_state = automaton.get("start", "")
    final_states = ", ".join(automaton.get("final", []))
    
    transitions = automaton.get("transitions", {})
    trans_list = []
    
    sorted_keys = sorted(transitions.keys())
    
    for key in sorted_keys:
        vals = transitions[key]
        if "," in key:
            s, sym = key.split(",", 1)
            display_sym = sym if sym else "ε"
            if len(vals) == 1:
                trans_list.append(f"δ({s}, {display_sym}) = {vals[0]}")
            else:
                trans_list.append(f"δ({s}, {display_sym}) = {{ {', '.join(vals)} }}")
                
    if trans_list:
        trans_str = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px;'>"
        for t in trans_list:
            trans_str += f"<div>{t}</div>"
        trans_str += "</div>"
    else:
        trans_str = "None"

    html = f"""<div class="formal-def-container">
<div class="def-grid">
<div class="def-item">
<div class="def-label">Q — All States</div>
<div class="def-box">{{ {states} }}</div>
</div>
<div class="def-item">
<div class="def-label">q₀ — Start State</div>
<div class="def-box">{start_state}</div>
</div>
<div class="def-item">
<div class="def-label">Σ — Alphabet</div>
<div class="def-box">{{ {alphabet} }}</div>
</div>
<div class="def-item">
<div class="def-label">F — Accept States</div>
<div class="def-box">{{ {final_states} }}</div>
</div>
</div>
<div class="def-item" style="margin-top: 20px;">
<div class="def-label">δ — Transition Function</div>
<div class="def-box" style="line-height: 1.6;">
{trans_str}
</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_transition_table(automaton):
    states = automaton.get("states", [])
    alphabet = automaton.get("alphabet", [])
    transitions = automaton.get("transitions", {})
    
    html = f"""<div class="transition-table-container">
<table class="custom-table">
<thead>
<tr>
<th>State</th>"""
    for sym in alphabet:
        display_sym = sym if sym else "ε"
        html += f"<th>{display_sym}</th>"
    html += """</tr>
</thead>
<tbody>"""
    
    for state in states:
        is_start = state == automaton.get("start")
        is_final = state in automaton.get("final", [])
        
        if is_start and is_final:
            prefix = "→ * "
            state_disp = f'<span class="state-start-final">{prefix}{state}</span>'
        elif is_start:
            prefix = "→ "
            state_disp = f'<span class="state-start">{prefix}{state}</span>'
        elif is_final:
            prefix = "* "
            state_disp = f'<span class="state-final">{prefix}{state}</span>'
        else:
            state_disp = f'<span class="state-normal">{state}</span>'
            
        html += f"<tr><td>{state_disp}</td>"
        
        for symbol in alphabet:
            key = f"{state},{symbol}"
            next_states = transitions.get(key, [])
            if not next_states:
                val = "-"
            elif len(next_states) == 1:
                val = next_states[0]
            else:
                val = "{" + ", ".join(next_states) + "}"
            html += f"<td>{val}</td>"
            
        html += "</tr>"
        
    html += """</tbody>
</table>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

def simulate(automaton, input_string):
    current_states = {automaton["start"]}

    for symbol in input_string:
        next_states = set()

        for state in current_states:
            key = f"{state},{symbol}"
            if key in automaton["transitions"]:
                next_states.update(automaton["transitions"][key])
            
        current_states = next_states

    return any(s in automaton["final"] for s in current_states)

def draw(automaton):
    dot = Digraph()
    dot.attr(rankdir='LR', size='8,5')
    dot.attr('node', fontname='Space Grotesk')
    dot.attr('edge', fontname='Space Grotesk')

    dot.node('start_indicator', shape='point')
    dot.edge('start_indicator', automaton["start"])

    for s in automaton["states"]:
        if s in automaton["final"]:
            dot.node(s, shape="doublecircle", style="filled", fillcolor="#38bdf8", color="#0284c7")
        else:
            dot.node(s, shape="circle", style="filled", fillcolor="#e2e8f0", color="#64748b")

    for key, vals in automaton["transitions"].items():
        if "," in key:
            s, sym = key.split(",", 1)
            label_sym = sym if sym else "ε"
            for v in vals:
                dot.edge(s, v, label=label_sym)

    return dot

# --- Streamlit UI ---
st.set_page_config(page_title="Automata Simulator Pro", page_icon="⚙️", layout="wide")
inject_custom_css()

st.markdown("<h1 style='text-align: center; color: #38bdf8 !important; margin-bottom: 0px;'>⚙️ Automata Simulator Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8 !important; font-size: 1.1rem; margin-bottom: 40px;'>Design, visualize, and simulate finite state machines using text descriptions.</p>", unsafe_allow_html=True)

# Input Section
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='section-title'>1. Define Automaton</div><hr class='section-divider'>", unsafe_allow_html=True)
    prompt = st.text_area(
        "Enter automaton description", 
        placeholder="e.g. A DFA over alphabet {0, 1} that accepts strings containing '010'.",
        height=120,
        label_visibility="collapsed"
    )

with col_right:
    st.markdown("<div class='section-title'>2. Test Simulation</div><hr class='section-divider'>", unsafe_allow_html=True)
    input_string = st.text_input("Enter input string to test", placeholder="e.g. 100101", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("Generate & Run Simulation", type="primary", use_container_width=True)

if generate_btn:
    if not prompt:
        st.warning("Please enter a prompt first.")
    else:
        with st.spinner("Compiling Automaton Architecture..."):
            raw = generate_automaton(prompt)
            
        with st.expander("System Logs (Raw JSON)", expanded=False):
            st.code(raw, language="json")

        automaton = extract_json(raw)

        if automaton:
            if validate(automaton):
                st.success(f"System successfully compiled a valid {automaton.get('type', 'Automaton')}.")
                
                # Section 1: Formal Definition
                st.markdown("<div class='section-title' style='margin-top: 30px;'>1. FORMAL DEFINITION M = (Q, Σ, Δ, q₀, F)</div><hr class='section-divider'>", unsafe_allow_html=True)
                render_formal_definition(automaton)
                
                # Section 2: Automaton Visualization
                st.markdown("<div class='section-title' style='margin-top: 30px;'>2. AUTOMATON VISUALIZATION</div><hr class='section-divider'>", unsafe_allow_html=True)
                st.graphviz_chart(draw(automaton))
                
                # Section 3: Truth Table & Simulation
                st.markdown("<div class='section-title' style='margin-top: 30px;'>3. TRUTH TABLE & SIMULATION RESULTS</div><hr class='section-divider'>", unsafe_allow_html=True)
                col_table, col_sim = st.columns([2, 1])
                with col_table:
                    render_transition_table(automaton)
                    
                with col_sim:
                    if input_string != "":
                        result = simulate(automaton, input_string)
                        st.markdown(f"<div style='background-color: #0f1523; border: 1px solid #1e293b; border-radius: 8px; padding: 20px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #94a3b8 !important; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;'>Input String</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-family: monospace; font-size: 1.5rem; color: #f8fafc !important; margin-bottom: 20px;'>{input_string}</p>", unsafe_allow_html=True)
                        
                        if result:
                            st.markdown(f"<div style='background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); padding: 10px; border-radius: 6px; font-weight: 700; font-size: 1.2rem;'>ACCEPTED ✓</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='background-color: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.2); padding: 10px; border-radius: 6px; font-weight: 700; font-size: 1.2rem;'>REJECTED ✗</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("No input string provided for simulation.")
            else:
                st.error("Generated JSON failed validation checks.")
        else:
            st.error("Failed to parse output from language model.")
