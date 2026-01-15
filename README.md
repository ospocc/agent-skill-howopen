# howopen Skill

This skill allows the agent to perform an "Open Source Health Check" on the current project. It analyzes the technology stack, programming language distribution, and open-source licenses of dependencies.

## When to use
- When the user asks for a project overview or "health check".
- When checking for open-source license compliance.
- When analyzing the tech stack of a new or existing project.

## Instructions
1.  **Run Analysis**: Execute the `analyze_project.py` script located in the same directory as this skill.
    ```powershell
    python .agent/skills/howopen/scripts/analyze_project.py
    ```
2.  **Process Output**: The script will output a JSON object containing:
    - `tech_stack`: A list of identified frameworks and tools.
    - `languages`: A dictionary of languages and their percentage of the codebase.
    - `dependencies`: A list of objects with `name`, `version`, and `license`.
3.  **Generate Report**: Create a Markdown report with the following sections:
    - ### 🛠️ Technology Stack
      A table listing the core frameworks and tools identified.
    - ### 📊 Language Distribution
      A table showing the programming languages used and their percentage (sorted by percentage).
    - ### ⚖️ Open Source License Audit
      A table listing dependencies, their versions, and their licenses. Highlight any "Unknown" or restrictive licenses (like GPL) if relevant.

## Resources
- `scripts/analyze_project.py`: Helper script for technical analysis.
