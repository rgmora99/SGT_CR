from django.test import TestCase

from .forms import ClienteForm
from .models import Cliente, TipoIdentificacion


class ClienteModelTest(TestCase):
    def setUp(self):
        self.tipo = TipoIdentificacion.objects.create(codigo="PASAPORTE", nombre="Pasaporte", patron_regex=r"^[A-Z0-9-]{6,20}$")

    def test_str(self):
        cliente = Cliente(nombre="Acme", tipo_identificacion=self.tipo, identificacion="AB123456")
        self.assertEqual(str(cliente), "Acme (AB123456)")

    def test_formato_identificacion_por_tipo(self):
        form = ClienteForm(
            data={
                "nombre": "Cliente Uno",
                "tipo_identificacion": self.tipo.id,
                "identificacion": "12",
                "correo_electronico": "cliente@correo.com",
                "telefono": "8888-8888",
                "direccion": "San José",
                "estado": Cliente.Estado.ACTIVO,
                "notas": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("identificacion", form.errors)
