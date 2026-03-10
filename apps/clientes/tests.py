from django.test import TestCase

from .models import Cliente


class ClienteModelTest(TestCase):
    def test_str(self):
        cliente = Cliente(nombre="Acme", identificacion="3-101-222")
        self.assertEqual(str(cliente), "Acme (3-101-222)")
