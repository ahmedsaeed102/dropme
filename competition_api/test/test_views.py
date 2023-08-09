import datetime
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Competition

User = get_user_model()


class JoinCompetitionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testpassword"
        )
        self.competition = Competition.objects.create(
            name="test",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=1),
        )
        self.url_name = "competition_join"

    def test_user_should_be_authenticated(self):
        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk})
        )
        self.assertEqual(response.status_code, 401)

    def test_competition_exists(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk})
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse("competition_ranking", kwargs={"pk": self.competition.pk}),
        )

        self.assertTrue(self.user in self.competition.users.all())

    def test_competition_does_not_exist(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk + 1})
        )
        self.assertEqual(response.status_code, 404)

    def test_competition_over(self):
        self.client.force_authenticate(user=self.user)
        self.competition.end_date = datetime.date.today() - datetime.timedelta(days=1)

        self.competition.save()

        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk})
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data["detail"], "Error 400, competition is over")

    def test_user_already_joined(self):
        self.client.force_authenticate(user=self.user)

        self.competition.users.add(self.user.pk)

        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk})
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data["detail"], "You already joined this competition")


class CompetitionDetailTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testpassword"
        )

        self.competition = Competition.objects.create(
            name="Test Competition",
            description="Test Description",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=1),
        )

        self.url_name = "competition_detail"

    def test_competition_detail(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk})
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["name"], "Test Competition")

        self.assertEqual(response.data["description"], "Test Description")

    def test_user_should_be_authenticated(self):
        response = self.client.get(
            reverse(self.url_name, kwargs={"pk": self.competition.pk})
        )
        self.assertEqual(response.status_code, 401)
