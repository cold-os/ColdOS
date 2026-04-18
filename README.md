<div align="center">
    
[English](README.md) | [中文](README.zh.md)

</div>

<div align="center">

# ColdOS: A Formally-Motivated Operating System for AI Agents (Conceptual Prototype)

</div>

<div align="center">

[![Status](https://img.shields.io/badge/Status-Pre--Alpha--Prototype-orange)](https://github.com/cold-os/ColdOS)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![arXiv](https://img.shields.io/badge/arXiv-2512.08740-brightgreen.svg)](https://arxiv.org/abs/2512.08740)
[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31696846-blueviolet.svg)](https://doi.org/10.6084/m9.figshare.31696846)

</div>

---

## ⚠️ Experimental Conceptual Prototype

> **This project is currently in an extremely early proof-of-concept stage. All code is a pre-alpha prototype, extremely rough, and intended solely for academic exploration and demonstration.**
> **The code is under review and refactoring.** The entire project has been **heavily assisted by AI tools**; the human author is responsible for the core ideas, architectural design, and final review. **Use in any production environment, real-world decision-making, or safety-critical scenario is strictly prohibited.**
>
> ColdOS will undergo **continuous iteration**, and its current form does not represent the final architecture. The researcher welcomes all forms of critique, suggestions, and collaboration.

---

## 🧊 Core Positioning: Runtime Belief Monitoring

**ColdOS is not a traditional operating system.** It does not manage CPU, memory, or I/O devices. It manages an agent's **belief state and behavioral consistency**.

In mainstream AI agent frameworks, safety monitoring typically focuses on "behavior"—what the model outputs, what tools it calls. **ColdOS takes an additional step forward**: it requires the agent to first report its internal "beliefs" (certain, speculative, unknown) in a structured format before acting, and then continuously verifies at runtime:

1. **Belief Legality**: Whether the reported beliefs fall within the legal bounds defined by the deductive alignment rulebase (CEAL).
2. **Behavioral Self-Consistency**: Whether the planned behavior (`action_type` and `output_text`) is internally logically consistent.
3. **Behavior-Belief Consistency**: Whether the planned behavior logically contradicts the reported beliefs.

Through this three-tier verification, ColdOS aims to provide a set of **auditable, quantifiable, and model-claim-independent** runtime safety constraints for agents. This is the core of the "formal operating system" concept: **incorporating an agent's "inner state" and "words/deeds" into a verifiable runtime kernel**.

<div align="center">

Frontend Interaction Demo

</div>

![演示动图](assets/demonstration.gif)

The right-hand dashboard shows ColdReasoner’s real-time belief verification outcomes for each AI dialogue round.

---

## 📦 Components Overview

ColdOS is an integration project that assembles the following independent components into a demonstrable prototype:

| Component | Responsibility | Current Status |
| :--- | :--- | :--- |
| **ColdReasoner** | Three-tier consistency verification kernel (Report - Self-Consistency - Behavior-Belief Consistency) | Under code review |
| **CEAL** | Deductive alignment rulebase, providing legal belief bounds and inconsistency axioms | Experimental prototype |
| **CAGE** | Token gateway and audit logging, isolating the agent from the external world | Proof-of-Concept |

> **Important**: The current integrated prototype is solely for demonstrating the concept of "runtime belief monitoring." Verification logic is based on an **axiomatic rulebase** (CEAL-style) for intent symbolization and logical contradiction detection, but remains an early proof-of-concept and **falls far short of any formal guarantee**. Rulebase coverage is limited, and the token/isolation mechanisms are simulated. **Use in any production or safety-critical scenario is strictly prohibited.**

---

## 🚀 Quick Start

**An extremely rough demo version, intended only for experiencing the concept.**

This demo requires calling the Qwen API to generate belief reports and behavior proposals. You **must** set the API key as a system environment variable (do **not** hardcode it in source files).

1.  Visit the [Alibaba Cloud Bailian Console](https://bailian.console.aliyun.com/), activate the model service, and obtain your API Key.

2.  Set the environment variable `DASHSCOPE_API_KEY` on your system:

    **macOS / Linux (Zsh/Bash):**
    ```bash
    export DASHSCOPE_API_KEY="your-qwen-api-key"
    ```

    **Windows (Command Prompt):**
    ```cmd
    set DASHSCOPE_API_KEY=your-qwen-api-key
    ```

    **Windows (PowerShell):**
    ```powershell
    $env:DASHSCOPE_API_KEY="your-qwen-api-key"
    ```

3.  Clone the repository, install dependencies, and run the Streamlit dashboard:

    ```bash
    # Clone the flagship repository
    git clone https://github.com/cold-os/ColdOS.git
    cd ColdOS

    # Install dependencies (Python 3.8+ recommended)
    pip install -r requirements.txt

    # Run the Streamlit-based monitoring dashboard
    streamlit run streamlit_app.py
    ```

Open the local URL in your browser to see a chat interface. As you converse freely with the AI, the dashboard on the right will display the real-time verification results from ColdReasoner for each turn—such as belief legality pressure and behavior-belief consistency deviation.

---

## ⚙️ Limitations & Roadmap

**The core architecture has been refactored with the CEAL-style approach, but this remains an early proof-of-concept prototype. Key known limitations:**

- **No rigorous formal verification**: Although the three-tier verification now uses an axiomatic rulebase, it has not undergone machine-checkable formal proof (e.g., via TLA⁺ or Coq).
- **Limited rulebase coverage**: The axioms defined in `cold_os_rules.yaml` are sufficient for demo scenarios only and have not been exhaustively validated against large-scale real-world dialogues.
- **Simulated token and isolation**: The CAGE token gateway and ColdMirror sandbox are conceptual mock-ups and do not provide real permission isolation or cryptographic audit trails.

**Recently Completed (✅ Implemented):**

- ✅ Upgraded ColdReasoner's behavioral self-consistency check to a CEAL-style "intent symbolization + axiomatic rulebase."
- ✅ Introduced logical contradiction axioms for belief-behavior consistency, complementing numerical deviation checks in a dual verification mechanism.
- ✅ Built a real-time Streamlit visualization dashboard, featuring multi-turn belief drift trends, radar charts, and risk scoring.

**Next Steps (Continuous Iteration):**

- [ ] Expand the rulebase and validate its completeness/robustness through adversarial testing and real-world dialogue data.
- [ ] Develop a lightweight formal model (e.g., in TLA⁺) for key safety properties of the ColdReasoner kernel.
- [ ] Integrate ColdOS as a pluggable middleware with real agent frameworks such as LangChain for validation.

---

## 🤝 Contributing

This is an open, transparent academic exploration project. The researcher welcomes:

- Critiques and corrections on the architecture, code, and documentation.
- Suggestions for improving verification rules, contradiction axioms, and visualization approaches.
- Any form of interdisciplinary collaboration.

Please contact the author via GitHub Issues or Discussions. **All contributors will be acknowledged in the `CONTRIBUTORS` file following open-source conventions.**
