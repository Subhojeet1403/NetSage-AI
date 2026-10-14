# NetSage AI

NetSage AI is a Cisco network troubleshooting case library. It pairs structured incident evidence (IOS show command output) with a deterministic checker and an LLM diagnostic prompt, and it keeps a log of human review decisions.

## Files

- cases.csv: the diagnostic case library. Each row has a symptom, topology note, show command output, expected fault, OSI layer and severity.
- checker.py: a rule-based verifier. It reads cases.csv and flags three fault types: administratively down interfaces (Layer 1), trunking failures (Layer 2) and missing routing table entries (Layer 3). It does not run any Cisco commands.
- diagnose_prompt.md: the system prompt for the NetSage AI diagnostic agent. It tells the model to treat command output as evidence and to separate observed facts, inferences and recommended actions.
- cisco_lab_commands.txt: the lab setup and configuration commands used to build the test scenarios.
- responsible_ai_log.json: examples of AI diagnosis errors and the corrections made during human review.

## Usage

Requires Python 3.

    python checker.py
    python checker.py path/to/cases.csv

## Responsible AI

Human review is required for security-sensitive, ambiguous or low-confidence diagnoses. The audit log shows cases where the AI output was rejected and corrected.

## Author

Subhojeet Ghosh
