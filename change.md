# Agentic Coaching & Evaluation Platform (ACEP) Plan

## 1. Data Ingestion & Customer Simulation
*   **Text Simulator (PoC):** CS Agents practice using a Google Gem configured to randomly roleplay SD-CS-01 scenarios. Agents export the session to Google Docs or paste the text directly into the system.
*   **Voice Simulator (Phase 2):** A lightweight WebRTC browser interface connected via WebSockets to the Gemini Multimodal Live API. This provides ultra-low latency, native speech-to-speech simulation without the cost of telephony APIs like Twilio.
*   **Real Operations (3CX):** Ingesting real customer calls. This requires a Data Sanitization/PII Redaction pipeline to mask sensitive data before it hits the LLM, ensuring strict PDPA compliance.

## 2. The Evaluation Engine (Backend API)
*   **Tech Stack:** Python, FastAPI, and the `google-genai` SDK (`gemini-3.6-flash`).
*   **Core Logic:** The API evaluates the transcript against the SD-CS-01 rules.
*   **Structured Output:** Enforces strict JSON formatting using Pydantic schemas. The API outputs a mathematical score (0-100), a granular pass/fail checklist, direct quotes as evidence, and the AI's reasoning.

## 3. Persistent Data Layer (Storage & PDCA)
*   **Current Prototype:** Local SQLite database handling evaluation records.
*   **Production Target:** Relational database (PostgreSQL). The schema will implement temporal versioning (e.g., `Rubric_Version_ID`) to ensure historical scores remain accurate when CS policies are updated, allowing management to track long-term trends and drive continuous improvement.

## 4. User Interface (Streamlit Dashboard)
*   **Role-Based Access:** A unified frontend with a role selector.
*   **CS Agent Portal:** A self-evaluation screen where agents can submit text logs or upload 3CX audio files (which are transcribed to text using Gemini).
*   **QA Manager Inbox:** An actionable dashboard filtering for failed or flagged evaluations. It features a side-by-side layout displaying the AI's detailed scorecard next to the raw transcript, allowing supervisors to verify AI decisions and quickly coach agents.
