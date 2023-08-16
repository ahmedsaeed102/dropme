from unittest.mock import patch
from django.test import TestCase
from django.http import Http404
from ..models import Competition
from ..services import competition_get


class CompetitionGetTests(TestCase):
    @patch("competition_api.services.get_object_or_404")
    def test_competition_get_with_given_pk_exists(self, mock_get_object_or_404):
        # Test case 1: Competition with given pk exists
        competition = Competition(pk=1)

        mock_get_object_or_404.return_value = competition

        result = competition_get(pk=1)
        self.assertEqual(result, competition)

    @patch("competition_api.services.get_object_or_404")
    def test_competition_with_given_pk_does_not_exist(self, mock_get_object_or_404):
        # Test case 2: Competition with given pk does not exist
        mock_get_object_or_404.side_effect = Http404()

        self.assertRaises(Http404, competition_get, pk=2)
