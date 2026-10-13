# CareNote: AI-assisted healthcare visit preparation

**Module 03 | Option 1 | Uche Chigozie Achinanya**



## Run the application
Install Python 3 with Tkinter (included in most Windows Python installations).
Extract this folder, open a terminal inside it, and run:

```bash
python app.py
```

Click **Create draft note**, review the output, and edit it directly in the output box. The Clear button clears both boxes. No API key or third-party Python packages are needed. On Linux, the window may require the operating system's python3-tk package.

Run the software checks with:

```bash
python -m unittest -v
```

The checks do not need Tkinter, so they run on any computer with Python 3.

## Project purpose
CareNote addresses a small healthcare task: organizing a patient's written concerns before a visit. It recognizes a limited set of symptom expressions, marks possible negation, and extracts duration phrases. The original description stays visible in the draft so a reviewer can catch omissions. It offers clarification questions without making a diagnosis, prescribing treatment, or assigning a triage level. It also displays limited keyword-triggered safety guidance.

Descriptions containing selected physical warning phrases trigger a fixed, conditional emergency notice. Self-harm language triggers US 988 support information, with 911 reserved in the wording for immediate danger, an attempt in progress, or a medical emergency. These keyword-triggered messages are not clinically validated triage decisions. A missing notice does not establish that a situation is safe. The wording follows the distinction described by the 988 Lifeline (n.d.).

## How this satisfies Option 1
ChatGPT helped design, code, test, and document this application. Option 1 describes the AI tool used to build the app. The runtime method is transparent, rule-based natural language processing, which the assignment permits. CareNote does not call an LLM or claim to be a trained clinical model. Its editable draft supports human review.

## Research and innovation
The broader innovation is AI-assisted clinical documentation, particularly ambient AI scribes. Such systems can turn clinician-patient conversations into draft visit notes. CareNote adapts the documentation idea to a smaller, typed-input classroom prototype. It does not record conversations or reproduce a commercial scribe's capabilities.

A 2025 evaluation study tested an ambient digital scribing system on 40 clinical recordings. It found strengths in readability alongside weaknesses in factual accuracy and capturing new medications. The authors propose evaluation combining simulation, computational metrics, and human review (Wang et al., 2025). This informed CareNote's source preservation and visible review instructions. Readable output alone does not prove that a note is complete or correct.

A randomized trial of ambient AI scribes reported modest improvements in some documentation and physician outcomes, with differences between systems (Lukac et al., 2025). These results concern the evaluated products and clinical setting. They do not establish that CareNote saves time or improves care.

WHO's guidance describes ethical and governance concerns for large multimodal models in healthcare (World Health Organization, 2024). Although CareNote uses rules rather than a multimodal model, privacy, transparency, and human oversight remain relevant design considerations.

## How the NLP works
1. Normalize case and apostrophes while retaining the original text.
2. Match whole words, common word forms (plurals, -ed, -ing) and a few synonym phrases using regular expressions. For example, "headaches", "coughed" and "my throat is sore" are recognized.
3. Check up to six preceding words in the same clause for a negation word, including contractions such as "didn't" and "isn't". A negation reaches across a short list ("Denies fever, chills, and cough") but stops at a contrast word ("but") or a comma that starts a new clause ("No fever, I have a cough").
4. Extract duration expressions written as numerals or words ("3 days", "two weeks", "a week", "twenty one days"), without assuming which symptom they describe.
5. Scan for red-flag phrases and, if any appear, place conditional safety guidance at the top of the note. Red flags are shown even when they look negated, because the negation rules are approximate and missing an emergency costs more than an extra warning.
6. Build a reviewable note with source snippets and clarification questions.

The code keeps words such as "no" and "not" because deleting them would change meaning. The vocabulary is manually authored demonstration data. No patient records were used for training or testing.

## Demonstration
Input: `I have been coughing for 3 days. No fever, but my throat hurts.`

Expected extraction: cough mentioned, fever possibly negated, sore throat mentioned, and duration phrase 3 days. These are text mentions rather than verified clinical findings.

Try `My ankle hurts.` The vocabulary misses ankle pain, but the complete description remains in the note and the app displays "No vocabulary match." This shows why a reviewer must inspect the source rather than relying only on recognized terms.

Try `I have chest pain and cannot breathe.` Neither phrase is in the symptom vocabulary, but the note opens with the safety notice.

## Testing and limits
Twenty-two automated checks passed during final verification:
- **Original eight:** synonym recognition, basic negation, contrast handling, duration extraction, preservation of unfamiliar input, empty input rejection, length limit, and absence of a sample diagnosis phrase.
- **Negation:** contractions ("didn't", "never"), negated lists, and new clauses after a comma ("No fever, I have a cough"; "No chest pain, just a headache").
- **Recognition:** word forms ("headaches", "coughed", "throat is sore") and durations written as words.
- **Safety notice:** shown for red flags, includes 988 only for self-harm language, and is absent for routine symptoms.

Four additional checks cover “not only” wording, compound number durations, conditional emergency wording for self-harm, and uncertain negated warning phrases. These checks verify selected software behaviors, not medical performance. The final desktop interface has not been independently visually verified in this environment.

Negation is approximate. For example, "I am not sure whether I have a fever" is marked possibly negated even though the statement expresses uncertainty. The app also cannot reliably distinguish family history ("My mom has a fever" is recorded as a mention), hypothetical descriptions, or complex timelines. Its small English vocabulary may perform poorly for dialects, spelling variations, and other languages. The red-flag list is short and also misses wording it does not contain. No clinical accuracy percentage is claimed.

The app makes no network requests and writes no patient text to disk. Text exists in memory during use. This does not establish HIPAA compliance or protect against screenshots, clipboard sharing, or other software on the computer. Use fictional examples only.

## Peer-review checklist
- Does the app launch and produce an editable note?
- Does the supplied example show negation and duration correctly?
- Can you identify a sentence that the rules misread?
- Is the original input preserved for review?
- Does a red-flag phrase produce the safety notice?
- Are privacy boundaries and limitations clear?
- What vocabulary or evaluation improvement would you recommend?

## Submission and demonstration
Upload app.py, test_app.py, and README.md to a GitHub repository named `carenote-healthcare-nlp`. Add SUBMISSION.txt if desired. Copy the repository URL from your browser and include it in the assignment submission. The repository must be accessible to your instructor and peer reviewers. Do not submit a placeholder URL.

Launch the app with `python app.py`, click Create draft note, and review the default sample. Then try `I am not only tired but dizzy.` and `Fever for twenty one days.` Explain that preserving the source helps a reviewer identify extraction errors. Test the Clear button and edit the output directly before submitting. A short recording can supplement the code submission.

## References
988 Suicide & Crisis Lifeline. (n.d.). *Contact us*. https://988lifeline.org/contact-us/

Lukac, P. J., Turner, W., Vangala, S., Chin, A. T., Khalili, J., Shih, Y.-C. T., Sarkisian, C., Cheng, E. M., & Mafi, J. N. (2025). Ambient AI scribes in clinical practice: A randomized trial. *NEJM AI, 2*(12), AIoa2501000. https://doi.org/10.1056/AIoa2501000

Wang, H., Yang, R., Alwakeel, M., Kayastha, A., Chowdhury, A., Biro, J. M., Sorrentino, A. D., Handley, J. L., Hantzmon, S., Bessias, S., Economou-Zavlanos, N. J., Bedoya, A., Agrawal, M., Ratwani, R. M., Poon, E. G., Pencina, M. J., Pollak, K. I., & Hong, C. (2025). An evaluation framework for ambient digital scribing tools in clinical applications. *npj Digital Medicine, 8*, Article 358. https://doi.org/10.1038/s41746-025-01622-1

World Health Organization. (2024). *Ethics and governance of artificial intelligence for health: Guidance on large multi-modal models*. https://www.who.int/publications-detail-redirect/9789240084759
