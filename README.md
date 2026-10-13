# CareNote: Educational AI Symptom Checker and Triage Tool

**ITAI 1370 Module 03 | Option 1 | Uche Chigozie Achinanya**



## Purpose and method
CareNote accepts fictional adult symptom descriptions and displays preliminary condition possibilities, an educational triage level, and an editable visit note. ChatGPT helped design, implement, test, and document the project. The application uses rule-based NLP rather than a trained LLM. Option 1 is the AI-assisted development choice; the symptom-checker aid supplies the project design.

This is an informational classroom prototype, not a substitute for professional medical advice. Its rules are not clinically validated. Use fictional examples only. It cannot rule out emergencies, diagnose illness, or prescribe treatment. Pediatric, pregnancy, and complex cases require professional assessment.

## Launch
Extract the folder. Install Python 3 with Tkinter, then open a terminal inside CareNote and run:

```bat
py app.py
```

Alternatively use `python app.py`. No pip packages, API key, or network connection are required. On Linux, Tkinter may require python3-tk. Enter fictional symptoms, choose the fictional adult context, and click **Create draft note**. Scroll to inspect the full output. The note remains editable. Clear resets the input, output, and context.

Run checks using `python -m unittest -v`. All 51 synthetic tests passed during final verification. These tests verify software behavior, not diagnostic accuracy. The updated desktop interface has not been independently visually verified in this environment.

## Assignment coverage
| Assignment detail | Implementation |
|---|---|
| Patient-reported symptom input | Desktop text box |
| Tokenization | Regex splits text into words and numbers |
| Stop-word removal | Removes a small filler-word set, preserving negation |
| Stemming/lemmatization | Explicit limited word-form normalization maps coughing/coughed to cough and headaches to headache |
| Keyword/phrase matching | Synonym-aware phrases and all-required-symptom rules |
| Preliminary condition assessment | Ten all-required symptom rules covering influenza-like and other respiratory infections, throat infection, common cold, stomach bug, and causes of dizziness |
| Suggested triage level | Emergency, urgent care, primary care, conditional self-care, or unable to determine |
| Explainability | Matched patterns, source references, processing steps and rationale |
| Commented code | app.py and checker.py |
| Evaluation | test_app.py and test_checker.py |
| Ethics and data | Privacy, bias, uncertainty and data quality below |

## NLP and decision flow
The displayed pipeline shows tokenization, cautious stop-word removal, and limited lemmatization-style normalization. This hand-written mapping is not a full linguistic lemmatizer. Phrase detection runs on the original normalized text to preserve negation and source offsets. Removing no/not before matching would distort the patient's statement.

The small manually authored knowledge base has ten rules, and each needs ALL of its symptoms: for example fever AND cough (influenza-related), fever AND headache (viral illness such as influenza), cough AND sore throat (common cold), vomiting AND diarrhea (stomach bug), or dizziness AND nausea. A single symptom never selects a condition. A match suggests possibilities rather than a confirmed or most-likely diagnosis. Symptoms overlap among illnesses, and testing or clinician assessment may be necessary. No confidence percentage is calculated.

Warning phrases have priority over lower care routes. A stiff neck alone is not treated as a warning, but a stiff neck together with fever or headache is, because that combination can signal meningitis. Self-harm phrases produce crisis-support guidance with 988 in the US and 911 for immediate danger or a medical emergency. Possibly negated warning phrases trigger an uncertain result instead of an automatic downgrade. The absence of a warning phrase never proves safety.

For other recognized symptoms, an explicitly selected severe/worsening or higher-risk adult context demonstrates urgent care. A matched respiratory pattern with persistent symptoms demonstrates primary care. Self-care requires the explicit mild, short-duration, low-risk adult context, a pattern marked as suitable for self-care (cold-like or stomach bug), and no recognized fever. When context is unknown or invalid, the app returns **Unable to determine**, even if a condition pattern matches. Selected severe/worsening expressions in the text override a mild-context selection and produce an urgent professional-review message, including when the symptom itself is outside the vocabulary. Mentions of children, pregnancy, postpartum status, breastfeeding, or selected under-18 age expressions block ordinary adult care-route assignment. Recognized emergency warning phrases and crisis-support messages still take priority. These guards are conservative word matching, not reliable age, severity, or medical-risk assessment. Unmatched wording returns **Unable to determine**. The dropdown supplies fictional context rather than automatically verifying patient facts.

These thresholds and combined rules are student design choices informed by public guidance. The sources do not validate the algorithm. UK guidance informs the care-route concepts; the app uses US 911/988 numbers and mentions local emergency numbers.

## Research rationale
AI-assisted documentation offers a practical healthcare task for a classroom prototype. Wang et al. (2025) describe structured evaluation of ambient digital scribes, including factuality and completeness. This informed retention of the original input and visible review requirements. Lukac et al. (2025) found documentation benefits varied between products, with inaccuracies requiring oversight. These studies concern their evaluated systems and do not establish CareNote's effectiveness.

CDC (2024) lists symptoms associated with influenza and warning signs that warrant immediate care. NHS cold and sore-throat guidance supports the distinction between mild symptoms, persistent concerns, and warning signs. These pages inform symptom vocabulary and illustrative care routes; they do not provide a diagnostic training dataset. WHO (2024) highlights governance issues for healthcare AI. CareNote applies transparency and privacy principles at a demonstration scale.

## Demonstration and peer review
| Fictional input | Context | Expected output |
|---|---|---|
| Fever and cough | Unknown / not confirmed | Influenza-related possibility; unable to determine |
| I have a severe headache and a high fever | Unknown / not confirmed | Viral illness such as influenza; urgent care because severe wording overrides missing context |
| Chest pain and trouble breathing | Any | Emergency warning route |
| Cough and fever | Severe, worsening, or higher-risk adult | Urgent care |
| Cough and sore throat | Persistent symptoms; adult; no emergency signs | Primary care |
| Mild cough and sore throat | Mild adult symptoms; no warning signs or risk factors; short duration | Conditional self-care demonstration |
| Vomiting and diarrhea since last night | Mild adult symptoms; no warning signs or risk factors; short duration | Stomach bug; conditional self-care demonstration |
| Severe headache, stiff neck, fever | Any | Emergency warning route (stiff neck with fever) |
| My ankle hurts | Any | No supported condition match; unable to determine |
| No chest pain. Cough and sore throat | Mild context | Uncertain warning phrase; unable to determine |

Additional regression cases: “Mild cough and sore throat. Also severe abdominal pain.” must produce Urgent care even with mild context. “My child has vomiting and diarrhea.” must produce Unable to determine with mild adult context. “My child has trouble breathing.” must still display the Emergency warning route.

Peer reviewers should check the processing steps, care-route priority, negation, unfamiliar wording, editable output, and source preservation. Try “I am not only tired but dizzy” and “Fever for twenty one days.” Explain a limitation and suggest an improvement.

## Data quality, bias, privacy and limits
The knowledge base contains ten hand-authored symptom combinations plus warning phrases and two warning combinations. It has no representative clinical training data and no held-out medical validation set. Rule completeness and language coverage limit reliability. A single partial symptom cannot choose a condition, but even a full match can be misleading.

The app may misunderstand uncertainty, family history, historical symptoms, hypothetical statements, long negated lists, spelling errors, dialects, and other languages. The six-word negation window is approximate. The app can classify another person's or a past symptom as current; humans must verify context. Duration extraction does not attach each duration to a symptom or calculate duration-based thresholds. Structured adult context can be incorrectly selected. Scope and severity guards cover only selected words: other descriptions, negated severity, ages expressed in words, and indirect references may be misread. These guards can generate extra warnings and do not make the system clinically safe. The warning list is incomplete.

No patient text is sent over the network or saved to disk by the app. Inputs remain in memory during use, without names or identifiers being requested. This does not establish HIPAA compliance or protect against other software, screenshots, or clipboard sharing. Use synthetic examples only. A real deployment would require clinical validation, representative evaluation, security controls, governance, and applicable regulatory review.

## References
988 Suicide & Crisis Lifeline. (n.d.). *Contact us*. https://988lifeline.org/contact-us/

Lukac, P. J., Turner, W., Vangala, S., Chin, A. T., Khalili, J., Shih, Y.-C. T., Sarkisian, C., Cheng, E. M., & Mafi, J. N. (2025). Ambient AI scribes in clinical practice: A randomized trial. *NEJM AI, 2*(12), AIoa2501000. https://doi.org/10.1056/AIoa2501000

Wang, H., Yang, R., Alwakeel, M., Kayastha, A., Chowdhury, A., Biro, J. M., Sorrentino, A. D., Handley, J. L., Hantzmon, S., Bessias, S., Economou-Zavlanos, N. J., Bedoya, A., Agrawal, M., Ratwani, R. M., Poon, E. G., Pencina, M. J., Pollak, K. I., & Hong, C. (2025). An evaluation framework for ambient digital scribing tools in clinical applications. *npj Digital Medicine, 8*, Article 358. https://doi.org/10.1038/s41746-025-01622-1

World Health Organization. (2024). *Ethics and governance of artificial intelligence for health: Guidance on large multi-modal models*. https://www.who.int/publications-detail-redirect/9789240084759

Centers for Disease Control and Prevention. (2024, August 26). *Signs and symptoms of flu*. https://www.cdc.gov/flu/signs-symptoms/index.html

NHS. (n.d.). *Common cold*. https://www.nhs.uk/conditions/common-cold/

NHS. (2024, April 8). *Sore throat*. https://www.nhs.uk/symptoms/sore-throat/

NHS. (n.d.). *Diarrhoea and vomiting*. https://www.nhs.uk/conditions/diarrhoea-and-vomiting/

NHS. (n.d.). *Dizziness*. https://www.nhs.uk/symptoms/dizziness/

NHS. (n.d.). *Meningitis*. https://www.nhs.uk/conditions/meningitis/

## GitHub update
Upload app.py, checker.py, test_app.py, test_checker.py, and README.md from this updated package. Replace the old files in the repository. Remove the obsolete screenshot.png if present because it shows an earlier output. Copy the submission text from the separate file and add your actual repository URL.
