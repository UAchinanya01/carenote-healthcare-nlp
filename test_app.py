"""Synthetic checks verify software behavior, not medical accuracy."""
import unittest
from app import analyze


class CareNoteTests(unittest.TestCase):
    # --- original checks ---
    def test_synonym(self):
        self.assertIn('cough: mentioned', analyze('I am coughing.'))
    def test_negation(self):
        self.assertIn('fever: possibly negated', analyze('No fever.'))
    def test_contrast(self):
        self.assertIn('headache: mentioned', analyze('No fever but headache.'))
    def test_duration(self):
        self.assertIn('3 days', analyze('Cough for 3 days.'))
    def test_unknown_preserved(self):
        self.assertIn('My ankle hurts', analyze('My ankle hurts'))
        self.assertIn('No vocabulary match', analyze('My ankle hurts'))
    def test_empty(self):
        with self.assertRaises(ValueError): analyze(' ')
    def test_limit(self):
        with self.assertRaises(ValueError): analyze('x' * 5001)
    def test_no_diagnosis(self):
        self.assertNotIn('Possible flu', analyze('Headache and fever'))

    # --- added checks ---
    def test_contraction_negation(self):
        self.assertIn('fever: possibly negated', analyze("I didn't have a fever."))
        self.assertIn('headache: possibly negated', analyze('I never had a headache.'))
    def test_negated_list(self):
        self.assertIn('cough: possibly negated', analyze('Denies fever, chills, and cough.'))
    def test_new_clause_ends_negation(self):
        self.assertIn('cough: mentioned', analyze('No fever, I have a cough.'))
    def test_word_forms(self):
        out = analyze('I have headaches, I coughed all night and my throat is sore.')
        for label in ('headache: mentioned', 'cough: mentioned', 'sore throat: mentioned'):
            self.assertIn(label, out)
    def test_word_durations(self):
        out = analyze('Fever for two days and a week of fatigue.')
        self.assertIn('two days', out)
        self.assertIn('a week', out)
    def test_red_flag_notice(self):
        out = analyze('I have chest pain and cannot breathe.')
        self.assertIn('SAFETY NOTICE', out)
        self.assertIn('call 911', out)
    def test_self_harm_shows_988(self):
        self.assertIn('988', analyze('Sometimes I want to die.'))
    def test_just_after_comma_ends_negation(self):
        self.assertIn('headache: mentioned', analyze('No chest pain, just a headache.'))
    def test_988_only_for_self_harm(self):
        self.assertNotIn('988', analyze('I have chest pain.'))
    def test_no_notice_for_routine_symptoms(self):
        self.assertNotIn('SAFETY NOTICE', analyze('I have been coughing for 3 days.'))


    def test_not_only_is_not_negation(self):
        self.assertIn('fatigue: mentioned', analyze('I am not only tired but dizzy.'))

    def test_compound_duration(self):
        self.assertIn('twenty one days', analyze('Fever for twenty one days.'))
        self.assertIn('twenty-one days', analyze('Fever for twenty-one days.'))

    def test_self_harm_emergency_is_conditional(self):
        out = analyze('I want to die.')
        self.assertIn('call or text 988', out)
        self.assertIn('If there is immediate danger', out)
        self.assertNotIn('If a listed physical symptom', out)

    def test_negated_flag_is_uncertain(self):
        self.assertIn('possibly negated; confirm', analyze('No chest pain.'))

if __name__ == '__main__':
    unittest.main()
