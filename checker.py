"""Educational symptom matching and care-route demonstration.

These hand-authored rules are informed by the references in README.md.
They are not a validated clinical protocol. No probability is computed.
"""
import re
from app import VOCABULARY, RED_FLAGS, is_negated, combination_flags

STOP_WORDS = {'i', 'a', 'an', 'the', 'have', 'has', 'and', 'am', 'my', 'for'}
NEGATION_WORDS = {'no', 'not', 'without', 'never', 'denies'}
# Explicit word-form normalization demonstrates lightweight lemmatization.
LEMMA_MAP = {'coughing': 'cough', 'coughed': 'cough', 'coughs': 'cough',
             'headaches': 'headache', 'fevers': 'fever', 'fatigued': 'fatigue'}
# Each rule needs ALL of its symptoms (a single symptom never picks a
# condition). `self_care_ok` marks patterns that may reach the conditional
# self-care demonstration; every other match goes no lower than primary care.
CONDITION_RULES = [
    {'name': 'Respiratory infection, including influenza (other causes possible)',
     'required': {'fever', 'cough'}, 'self_care_ok': False, 'source': 'CDC: Signs and symptoms of flu'},
    {'name': 'Flu-like illness (other causes possible)',
     'required': {'fever', 'body aches'}, 'self_care_ok': False, 'source': 'CDC: Signs and symptoms of flu'},
    {'name': 'Viral illness such as influenza; fever with headache has other possible causes',
     'required': {'fever', 'headache'}, 'self_care_ok': False, 'source': 'CDC: Signs and symptoms of flu'},
    {'name': 'Throat infection (viral or bacterial, such as strep)',
     'required': {'sore throat', 'fever'}, 'self_care_ok': False, 'source': 'NHS: Sore throat'},
    {'name': 'Common cold or another upper respiratory infection',
     'required': {'cough', 'sore throat'}, 'self_care_ok': True, 'source': 'NHS: Common cold'},
    {'name': 'Common cold or another upper respiratory infection',
     'required': {'runny nose', 'sore throat'}, 'self_care_ok': True, 'source': 'NHS: Common cold'},
    {'name': 'Common cold or another upper respiratory infection',
     'required': {'runny nose', 'cough'}, 'self_care_ok': True, 'source': 'NHS: Common cold'},
    {'name': 'Stomach bug (gastroenteritis) or food poisoning',
     'required': {'vomiting', 'diarrhea'}, 'self_care_ok': True, 'source': 'NHS: Diarrhoea and vomiting'},
    {'name': 'Stomach bug (gastroenteritis) or food poisoning',
     'required': {'nausea', 'vomiting'}, 'self_care_ok': True, 'source': 'NHS: Diarrhoea and vomiting'},
    {'name': 'Inner-ear problem, dehydration, migraine, or other causes of dizziness',
     'required': {'dizziness', 'nausea'}, 'self_care_ok': False, 'source': 'NHS: Dizziness'},
]

UNKNOWN = 'Unknown / not confirmed'
MILD = 'Mild adult symptoms; no warning signs or risk factors; short duration'
PERSISTENT = 'Persistent symptoms; adult; no emergency signs'
SEVERE = 'Severe, worsening, or higher-risk adult'

# Conservative scope checks. These only detect selected expressions, not all
# patient groups or clinically important descriptions. Never infer adult scope
# from the absence of these words.
UNSUPPORTED_GROUP = re.compile(
    r"\b(?:child(?:ren)?|baby|babies|infant|toddler|newborn|pediatric|paediatric|"
    r"pregnan\w*|postpartum|breastfeeding|son|daughter)\b"
    r"|\b(?:[0-9]|1[0-7])\s*(?:years? old|year[- ]old|y/?o)\b")
CONCERNING_DESCRIPTION = re.compile(
    r"\b(?:severe|unbearable|excruciating|worsening|getting worse|"
    r"dehydrat\w*|cannot keep fluids down|can't keep fluids down|"
    r"unable to keep fluids down|blood in (?:my )?stool|bloody stools?)\b")


def unique(items):
    """Remove duplicates while keeping the original order."""
    return list(dict.fromkeys(items))


def process_symptoms(text):
    """Show tokenization, cautious stop-word removal, and normalization.

    This display pipeline is separate from phrase detection so negation,
    source offsets, and multiword phrases remain available to the checker.
    """
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text.lower().replace('’', "'"))
    filtered = [t for t in tokens if t not in STOP_WORDS or t in NEGATION_WORDS]
    return {'tokens': tokens, 'filtered': filtered,
            'lemmas': [LEMMA_MAP.get(t, t) for t in filtered]}

def assess(text, context=UNKNOWN):
    """Return explainable classroom outputs, with uncertainty as a fallback.

    Context values are explicit user selections, not inferred patient facts.
    Adult scope only. Keyword absence never proves safety.
    """
    if not text.strip():
        raise ValueError('Enter a fictional symptom description.')
    if len(text) > 5000:
        raise ValueError('Maximum input length is 5,000 characters.')
    n = text.lower().replace('’', "'")
    active = set()
    for label, pattern in VOCABULARY.items():
        if any(not is_negated(n, m.start()) for m in re.finditer(pattern, n)):
            active.add(label)
    flags = []
    uncertain_flags = []
    self_harm = False
    for label, pattern in RED_FLAGS.items():
        for m in re.finditer(pattern, n):
            if is_negated(n, m.start()):
                uncertain_flags.append(label)
            elif label == 'thoughts of self-harm':
                self_harm = True
            else:
                flags.append(label)
    # Warning combinations such as stiff neck + fever count like warning phrases.
    flags += combination_flags(active)
    matched = [r for r in CONDITION_RULES if r['required'] <= active]
    possibilities = unique(r['name'] for r in matched)
    evidence = unique(r['source'] for r in matched)
    level = 'Unable to determine'
    reason = 'Insufficient information. Ask a qualified healthcare professional; no match does not mean non-urgent.'
    if flags:
        level = 'Emergency'
        reason = 'Warning phrase detected: ' + ', '.join(sorted(set(flags))) + '. If happening now, seek emergency help (911 in the US). Rules cannot establish timing or who has the symptom.'
    elif self_harm:
        level = 'Urgent care / crisis support'
        reason = 'Call or text 988 in the US for crisis support. Call 911 for immediate danger, an attempt in progress, or a medical emergency.'
    elif uncertain_flags:
        reason = 'A warning phrase may be negated or uncertain. Confirm the description with a clinician; this prototype cannot safely assign a lower route.'
    elif UNSUPPORTED_GROUP.search(n):
        reason = ('The text mentions a patient group outside this adult demonstration. '
                  'Seek individualized professional assessment; the selected adult context cannot override this scope restriction.')
    elif CONCERNING_DESCRIPTION.search(n):
        level = 'Urgent care'
        reason = ('The text contains severe, worsening, or other concerning wording. '
                  'Seek prompt professional assessment. A mild-context selection cannot override this warning. '
                  'If this may be a medical emergency, seek emergency help.')
    elif context not in {MILD, PERSISTENT, SEVERE}:
        reason = ('Severity, duration, risk factors, and adult scope are not confirmed. '
                  'A condition-pattern match cannot establish a safe care route. Obtain professional guidance.')
    elif active and context == SEVERE:
        level = 'Urgent care'
        reason = 'The user selected severe/worsening symptoms or higher risk. Contact a healthcare professional promptly for individualized advice.'
    elif possibilities and context == MILD:
        # Self-care only when every matched pattern allows it and there is no fever.
        if all(r['self_care_ok'] for r in matched) and 'fever' not in active:
            level = 'Self-care (conditional demonstration)'
            reason = 'Mild pattern plus explicit low-risk adult context. Monitor symptoms and obtain professional advice if they worsen or persist. Missing keywords do not rule out serious illness.'
        else:
            level = 'Primary care'
            reason = 'A symptom pattern matched that should be discussed with a primary-care professional; testing may be needed to identify the cause.'
    elif possibilities and context == PERSISTENT:
        level = 'Primary care'
        reason = 'The user reports persistent symptoms. Arrange professional review. Duration thresholds vary by symptom and are not modeled here.'
    return {'level': level, 'reason': reason, 'possibilities': possibilities,
            'evidence': evidence, 'active': sorted(active), 'nlp': process_symptoms(text)}

def format_assessment(result):
    p = result['nlp']
    return '\n'.join([
        'CLASSROOM SYMPTOM CHECKER: NOT CLINICALLY VALIDATED',
        'Preliminary possibilities (not diagnoses):',
        *(['- ' + x for x in result['possibilities']] or ['- No supported pattern matched; condition undetermined.']),
        'Suggested triage level (educational): ' + result['level'],
        'Reason: ' + result['reason'],
        'Rule sources: ' + ('; '.join(result['evidence']) or 'Safety/fallback rules; see README.'),
        '', 'NLP demonstration:', 'Tokens: ' + ', '.join(p['tokens']),
        'After stop-word removal: ' + ', '.join(p['filtered']),
        'After word-form normalization: ' + ', '.join(p['lemmas']),
        '', 'For information only, not a substitute for professional medical advice.',
        'Use fictional adult examples. No medications or treatment doses are recommended.',
        'Unknown, pediatric, pregnancy, and complex contexts need professional assessment.',
        ''
    ])
