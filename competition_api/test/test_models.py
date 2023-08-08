from django.test import TestCase
from datetime import date, timedelta
from ..models import Competition, CompetitionRanking


class TestCompetitionModel(TestCase):
    def setUp(self):
        self.competition = Competition.objects.create(
            name="test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )

    def test_is_ongoing_is_false(self):
        self.competition.end_date = date.today() - timedelta(days=1)
        self.assertFalse(self.competition.is_ongoing)

    def test_is_ongoing_is_true(self):
        self.assertTrue(self.competition.is_ongoing)

    def test_str_returns_name(self):
        self.assertEqual(str(self.competition), "test")


class TestCompetitionRankingModel(TestCase):
    pass
