import uuid

from django.contrib.auth.models import User
from django.test import TestCase

from apps.climbers.models import climbers


class ClimberModelTest(TestCase):
    def setUp(self):
        # 1. Создаем уникального пользователя
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(username=unique_username, password="12345")

        # 2. ВАЖНО: Мы НЕ создаем climbers вручную, так как он, вероятно,
        # создается автоматически через сигнал при создании User.
        # Мы просто достаем его из базы.
        self.climber = climbers.objects.get(user=self.user)

        # 3. Дописываем необходимые поля для теста (если их не заполнил сигнал)
        self.climber.first_name = "Ivan"
        self.climber.last_name = "Ivanov"
        self.climber.email = "test@test.com"
        self.climber.sports_category = "3"
        self.climber.schoole = True
        self.climber.test = True
        self.climber.save()

    def test_climber_creation(self):
        """Проверяем, что объект создается и поля сохраняются"""
        self.assertEqual(self.climber.first_name, "Ivan")
        self.assertEqual(self.climber.last_name, "Ivanov")
        self.assertEqual(self.climber.sports_category, "3")
        self.assertTrue(self.climber.schoole)
        self.assertTrue(self.climber.test)

    def test_str_method(self):
        """Проверяем, что метод __str__ возвращает 'Фамилия Имя'"""
        self.assertEqual(str(self.climber), "Ivanov Ivan")
