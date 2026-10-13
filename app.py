"""CareNote: classroom demonstration of transparent, rule-based NLP.

Run: python app.py. No packages, account, API key, or network required.
Use fictional examples only. This program does not diagnose or assign triage levels. It displays fixed safety guidance.
"""
import re

# A deliberately small vocabulary makes the demonstration easy to audit.
# This vocabulary is an educational design choice, not a medical database.
# Patterns accept common word forms (plurals, -ed, -ing) so "headaches" and
# "coughed" are recognized, plus a few everyday phrasings.
VOCABULARY = {
    'headache': r'\b(?:headaches?|head (?:hurts|aches?|is pounding))\b',
    'cough': r'\b(?:cough(?:s|ed|ing)?)\b',
    'fever': r'\b(?:fevers?|feverish)\b',
    'sore throat': r'\b(?:sore throat|throat (?:hurts|is sore|is scratchy)|scratchy throat)\b',
    'nausea': r'\b(?:nausea|nauseous|nauseated|feel(?:ing)? sick to my stomach)\b',
    'dizziness': r'\b(?:dizzy|dizziness|light-?headed)\b',
    'fatigue': r'\b(?:fatigue|fatigued|tired|exhausted)\b',
}

# Fixed safety notice. These phrases are NOT scored or triaged: if any appears,
# the note opens with the same emergency message. These are keyword-triggered safety messages, not validated triage decisions.
RED_FLAGS = {
    'chest pain or pressure': r'\bchest (?:pains?|pressure|tightness|hurts|is tight)\b|\btight chest\b',
    'trouble breathing': r"\b(?:short(?:ness)? of breath|can'?t breathe|cannot breathe|trouble breathing|difficulty breathing|hard to breathe)\b",
    'face drooping or slurred speech': r'\b(?:face (?:is )?droop(?:s|ing)?|drooping face|slurred speech|slurring)\b',
    'weakness or numbness on one side': r'\b(?:weak|numb)(?:ness)? on one side\b|\bone side (?:is )?(?:weak|numb)\b',
    'sudden severe headache': r'\bworst headache\b|\bsudden severe headache\b',
    'fainting': r'\b(?:fainted|passed out|blacked out)\b',
    'coughing or vomiting blood': r'\b(?:coughing|vomiting|throwing) up blood\b|\b(?:coughing|vomiting) blood\b',
    'thoughts of self-harm': r'\b(?:kill myself|want to die|end my life|suicidal|hurt myself)\b',
}

# Words that switch the following symptom off ("no fever", "didn't have a cough").
NEGATIONS = {
    'no', 'not', 'without', 'never', 'none', 'nor', 'deny', 'denies', 'denied',
    "don't", 'dont', "doesn't", 'doesnt', "didn't", 'didnt', "haven't", 'havent',
    "hasn't", 'hasnt', "isn't", 'isnt', "wasn't", 'wasnt',
}

# How many words before a symptom are checked for a negation word. Six covers
# short lists such as "denies fever, chills, and cough".
NEGATION_WINDOW = 6

# A negation's reach ends at sentence punctuation, at contrast words, or at a
# comma that starts a new clause ("No fever, I have a cough"). A comma inside a
# list ("Denies fever, chills, and cough") does NOT end it.
SCOPE_BREAK = re.compile(
    r"[.!?;]|\b(?:but|however|although|though)\b"
    r"|,\s*(?=(?:i|i'm|im|my|he|she|they|we|it|his|her|their|the patient|just|only)\b)")

# Durations written as numerals or as words ("3 days", "two weeks", "a week").
UNITS = r'(?:one|two|three|four|five|six|seven|eight|nine)'
TENS = r'(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)'
NUMBER_WORDS = rf'(?:\d+|{TENS}(?:[ -]{UNITS})?|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|ten|{UNITS}|a few|several|an|a)'
DURATION = re.compile(rf'\b{NUMBER_WORDS}\s+(?:hours?|days?|weeks?|months?)\b')

MAX_CHARS = 5000


def is_negated(normalized, start):
    """Return True if a negation word appears shortly before position `start`
    in the same clause. Approximate by design; the reviewer checks the source."""
    clause = SCOPE_BREAK.split(normalized[:start])[-1]
    # 'Not only' adds emphasis rather than negating a symptom.
    clause = re.sub(r'\bnot\s+only\b', '', clause)
    words = re.findall(r"[a-z']+", clause)[-NEGATION_WINDOW:]
    return any(w in NEGATIONS for w in words)


def analyze(text):
    """Extract symptom mentions and durations; preserve the complete source.

    Negation scope is intentionally limited to preceding words in the same
    clause. Complex sentences remain uncertain and require human review.
    Do not remove stop words: removing 'no' would change the meaning.
    """
    if not text.strip():
        raise ValueError('Enter a fictional patient description first.')
    if len(text) > MAX_CHARS:
        raise ValueError(f'Please keep the description to {MAX_CHARS:,} characters or fewer.')
    normalized = text.lower().replace('’', "'")

    mentions = []
    for label, pattern in VOCABULARY.items():
        for match in re.finditer(pattern, normalized):
            status = 'possibly negated' if is_negated(normalized, match.start()) else 'mentioned'
            mentions.append((label, status, text[match.start():match.end()]))

    # Red-flag phrases are reported even when they look negated, because the
    # negation rules are approximate and missing an emergency costs more.
    flags = []
    self_harm = False
    for label, pattern in RED_FLAGS.items():
        match = re.search(pattern, normalized)
        if match:
            note = ' (possibly negated; confirm with the patient)' if is_negated(normalized, match.start()) else ''
            flags.append(f'- {label}{note}')
            self_harm = self_harm or label == 'thoughts of self-harm'

    # Durations are listed separately rather than assigned to the wrong symptom.
    durations = [m.group(0) for m in DURATION.finditer(normalized)]

    lines = ['CARENOTE: DRAFT FOR HUMAN REVIEW', '']
    if flags:
        lines += ['SAFETY NOTICE: the description mentions:', *flags]
        if any(not flag.startswith('- thoughts of self-harm') for flag in flags):
            lines += ['If a listed physical symptom is happening now and may be a medical emergency, call 911 (or your local emergency number).']
        if self_harm:
            lines += ['For thoughts of self-harm or emotional distress in the US, call or text 988 (Suicide & Crisis Lifeline).',
                      'If there is immediate danger, an attempt in progress, or a medical emergency, call 911 (or your local emergency number).']
        lines += ['']
    lines += ['Original description:', text, '', 'Recognized mentions (not confirmed findings):']
    lines += [f'- {label}: {status} [source: {source}]'
              for label, status, source in mentions] or ['- No vocabulary match.']
    lines += ['', 'Duration phrases (association unverified):',
              ', '.join(durations) or 'Not recognized.', '', 'Questions to clarify:',
              '- When did each concern start?', '- What changed or made it worse?',
              '- What medicines or allergies should the clinician know about?', '',
              'Review all extracted details against the original text.',
              'Limited English vocabulary and negation rules can miss or misread details.',
              'Educational prototype. No diagnosis, treatment, or triage level. Safety messages use limited keyword rules.']
    return '\n'.join(lines)


def main():
    """Small desktop interface. Text stays in memory until the app closes."""
    # Tkinter is imported here, not at the top of the file, so analyze() and
    # the tests work on computers where Tkinter is not installed.
    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title('CareNote | Healthcare NLP classroom demo')
    root.geometry('850x750')
    ttk.Label(root, text='CareNote', font=('Arial', 24, 'bold')).pack(pady=10)
    ttk.Label(root, text='Prepare an editable visit note from a fictional description.').pack()
    ttk.Label(root, text='Use synthetic data only. This app does not provide medical advice.').pack(pady=8)
    source = tk.Text(root, height=7, wrap='word', font=('Arial', 12))
    source.pack(fill='x', padx=20)
    sample = 'I have been coughing for 3 days. No fever, but my throat hurts.'
    source.insert('1.0', sample)
    output = tk.Text(root, height=24, wrap='word', font=('Arial', 11))

    def generate():
        try:
            result = analyze(source.get('1.0', 'end-1c'))
            output.delete('1.0', 'end')
            output.insert('1.0', result)
        except ValueError as error:
            messagebox.showinfo('Check input', str(error))

    def clear():
        source.delete('1.0', 'end')
        output.delete('1.0', 'end')

    bar = ttk.Frame(root)
    bar.pack(pady=10)
    ttk.Button(bar, text='Create draft note', command=generate).pack(side='left', padx=5)
    ttk.Button(bar, text='Clear', command=clear).pack(side='left', padx=5)
    output.pack(fill='both', expand=True, padx=20, pady=10)
    root.mainloop()


if __name__ == '__main__':
    main()
