# ⚙️ Automata Simulator Pro

**Automata Simulator Pro** is a modern, premium web application built with Streamlit that allows you to design, visualize, and simulate finite state machines (DFA, NFA) using text descriptions. Powered by Google's Gemini LLM, it translates descriptions into formal mathematical models and interactive visualizations.

## Features

- **Natural Language Parsing**: Describe an automaton in plain text (e.g. "A DFA that accepts strings ending with '01'").
- **Formal Definition Generation**: Automatically generates the formal definition $M = (Q, \Sigma, \Delta, q_0, F)$.
- **State Machine Visualization**: Generates a beautiful Graphviz node diagram to visualize your state machine.
- **Transition Table**: Outputs a detailed transition table denoting start states, final states, and transition paths.
- **Interactive Simulation**: Test strings against your generated automaton to verify acceptance or rejection.
- **Premium UI**: Designed with a modern dark theme ("cyber slate"), custom CSS grid layouts, and readable Google Fonts (Space Grotesk & JetBrains Mono).

## Prerequisites

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [Graphviz](https://graphviz.org/) (Ensure it's installed on your system and added to your PATH)
- [google-generativeai](https://pypi.org/project/google-generativeai/)

## Installation

1. Clone or download the repository to your local machine.
2. Install the required python packages using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Graphviz is installed on your OS.

## Usage

Start the Streamlit application by running the following command in your terminal:
```bash
python -m streamlit run app.py
```
*(Alternatively, just run `streamlit run app.py` if Streamlit is in your PATH.)*

## Environment Configuration

The app uses Google's Gemini API. In the current setup, an API key is hardcoded. **For production or sharing, please remove the hardcoded API key and replace it with environment variables (`os.environ.get("GEMINI_API_KEY")`) or Streamlit secrets!**

## Technologies Used
- **Streamlit**: Web Framework & UI
- **Google Gemini API**: Generative AI / Text-to-JSON
- **Graphviz**: Visualization Engine
- **Custom HTML/CSS**: UI Styling

## License
[MIT License](LICENSE)
