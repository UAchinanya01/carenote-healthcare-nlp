"""Rule and pipeline checks use synthetic examples only."""
import unittest
from checker import assess, process_symptoms

MILD = 'Mild adult symptoms; no warning signs or risk factors; short duration'
PERSISTENT = 'Persistent symptoms; adult; no emergency signs'
SEVERE = 'Severe, worsening, or higher-risk adult'

class CheckerTests(unittest.TestCase):
    def test_pipeline(self):
        p = process_symptoms('I have no coughing and headaches.')
        self.assertIn('no', p['filtered'])
        self.assertNotIn('i', p['filtered'])
        self.assertIn('cough', p['lemmas'])
        self.assertIn('headache', p['lemmas'])
    def test_possible_flu(self):
        self.assertIn('influenza', assess('Fever and cough')['possibilities'][0])
    def test_all_required_not_partial(self):
        self.assertEqual(assess('Headache')['possibilities'], [])
    def test_negated_fever(self):
        self.assertFalse(any('influenza' in p for p in assess('No fever but cough')['possibilities']))
    def test_emergency_precedes_mild(self):
        self.assertEqual(assess('Chest pain and cough', MILD)['level'], 'Emergency')
    def test_unknown_context_stays_unknown(self):
        self.assertEqual(assess('Cough and sore throat')['level'], 'Unable to determine')
    def test_aid_example_headache_fever(self):
        r = assess('I have a severe headache and a high fever.')
        self.assertTrue(any('fever with headache' in p for p in r['possibilities']))
        self.assertEqual(r['level'], 'Urgent care')
    def test_stomach_bug_self_care(self):
        self.assertEqual(assess('Vomiting and diarrhea since last night', MILD)['level'], 'Self-care (conditional demonstration)')
    def test_dizziness_nausea_not_self_care(self):
        self.assertEqual(assess('Dizzy and nauseous', MILD)['level'], 'Primary care')
    def test_stiff_neck_fever_is_emergency(self):
        self.assertEqual(assess('Severe headache, stiff neck, fever', MILD)['level'], 'Emergency')
    def test_stiff_neck_alone_is_not_emergency(self):
        self.assertNotEqual(assess('Stiff neck from sleeping badly', MILD)['level'], 'Emergency')
    def test_duplicate_condition_names_merged(self):
        r = assess('Runny nose, cough and sore throat')
        self.assertEqual(len(r['possibilities']), len(set(r['possibilities'])))
    def test_unmatched_is_unknown(self):
        self.assertEqual(assess('Ankle hurts', MILD)['level'], 'Unable to determine')
    def test_negated_flag_blocks_downgrade(self):
        self.assertEqual(assess('No chest pain. Cough and sore throat', MILD)['level'], 'Unable to determine')
    def test_urgent(self):
        self.assertEqual(assess('Cough and fever', SEVERE)['level'], 'Urgent care')
    def test_primary(self):
        self.assertEqual(assess('Cough and sore throat', PERSISTENT)['level'], 'Primary care')
    def test_self_care_requires_context(self):
        self.assertEqual(assess('Mild cough and sore throat', MILD)['level'], 'Self-care (conditional demonstration)')
    def test_fever_not_self_care(self):
        self.assertEqual(assess('Fever and cough', MILD)['level'], 'Primary care')
    def test_self_harm(self):
        r = assess('I want to die', MILD)
        self.assertIn('988', r['reason'])
        self.assertIn('immediate danger', r['reason'])
    def test_empty(self):
        with self.assertRaises(ValueError): assess('')

    def test_severe_unmatched_symptom_overrides_mild(self):
        self.assertEqual(assess('Mild cough and sore throat. Also severe abdominal pain.', MILD)['level'], 'Urgent care')
    def test_severe_unmatched_alone(self):
        self.assertEqual(assess('Severe abdominal pain', MILD)['level'], 'Urgent care')
    def test_child_blocks_self_care(self):
        self.assertEqual(assess('My child has vomiting and diarrhea.', MILD)['level'], 'Unable to determine')
    def test_pregnancy_blocks_self_care(self):
        self.assertEqual(assess('I am pregnant and have cough and sore throat.', MILD)['level'], 'Unable to determine')
    def test_age_blocks_self_care(self):
        self.assertEqual(assess('A 12 year old has vomiting and diarrhea.', MILD)['level'], 'Unable to determine')
    def test_pediatric_emergency_still_shown(self):
        self.assertEqual(assess('My child has trouble breathing.', MILD)['level'], 'Emergency')
    def test_worsening_overrides_mild(self):
        self.assertEqual(assess('Cough and sore throat are getting worse.', MILD)['level'], 'Urgent care')
    def test_invalid_context_stays_unknown(self):
        self.assertEqual(assess('Cough and sore throat', 'invalid')['level'], 'Unable to determine')

if __name__ == '__main__':
    unittest.main()
