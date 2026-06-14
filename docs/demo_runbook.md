# Demo Runbook

## Objective

Show how the workflow helps a customer trust or GRC team reduce repetitive diligence work while controlling customer-facing security, privacy, regional, customer-specific architecture, and compliance claims.

## Setup

Start backend:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Start frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

## Demo script

1. Click **Load Demo Requests**.
2. Point out the metrics: total requests, open, escalated, high priority, and region routed.
3. Use filters to show **Questionnaires**, **Trust Center**, **Unsupported Claims**, **Region Routed**, **Japan / APAC**, **EU / EEA**, and **US Financial Services**.
4. Open the Japan/APAC enterprise request.
5. Show how the workflow front-loads regional needs such as localized documentation, data residency language, subprocessors, cross-border transfer language, and dedicated storage review.
6. Open the EU/EEA request.
7. Explain how the workflow anticipates DPA, SCC, subprocessor, retention, deletion, and AI/data-use boundary questions and routes them to Legal, Privacy, Product, and Security review.
8. Open the large bank questionnaire request.
9. Explain how the workflow separates standard answer-bank content from items requiring Security, Privacy, Product, Field Security, Customer Success, or regional review.
10. Open the stakeholder review matrix and show required, conditional, and informational reviewers.
11. Explain that this mirrors real escalation judgment: answer directly from approved content, consult the right stakeholder, or block unsupported claims.
12. Add analyst notes describing approved evidence, regional playbook fit, or missing context.
13. Escalate the unsupported external claim example.
14. Show the audit trail, including stakeholder review matrix generation and escalation events.
15. Close by explaining that the system supports humans rather than automatically approving customer-facing claims.

## Talking points

- This mirrors real customer trust work: questionnaires, Trust Center content, customer calls, public policy language, and deal support.
- Different customer regions tend to produce different diligence patterns, so the workflow helps teams prepare the right evidence before the request becomes a blocker.
- The strongest control is not speed alone; it is speed with claim accuracy.
- The stakeholder review matrix makes escalation judgment explicit: required reviewers, conditional reviewers, informational stakeholders, review triggers, and suggested next steps.
- The workflow helps GTM teams move faster while keeping Legal, Privacy, Security, Product, Field Security, Customer Success, and regional review in the loop.
- Reusable artifacts such as CAIQ, SOC 2 Type 2, ISO 27001 evidence paths, regional playbooks, and approved FAQs reduce one-off work.
