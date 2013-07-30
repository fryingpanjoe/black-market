from unittest import TestCase
from collections import defaultdict

from blackmarket.shared.utility import weighted_choice


class WeightedChoiceTest(TestCase):
    def test_weighted_choice_always(self):
        for i in range(100):
            self.assertEquals(
                'always', weighted_choice([(0, 'never'), (1, 'always')]))

    def test_weighted_choice_prob(self):
        seq = [(1, 'rare'), (10, 'common')]
        count = defaultdict(int)
        for i in range(1000):
            count[weighted_choice(seq)] += 1
        self.assertTrue(count['rare'] < count['common'])

    def test_weighted_choice_uniform(self):
        seq = [(1, 'eq1'), (1, 'eq2'), (1, 'eq3')]
        count = defaultdict(int)
        for i in range(1000):
            count[weighted_choice(seq)] += 1
        for _, elem in seq:
            self.assertTrue(200 < count[elem] < 400)
