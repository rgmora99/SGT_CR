from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

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

    def test_identificacion_duplicada_no_valida(self):
        Cliente.objects.create(nombre="Existente", tipo_identificacion=self.tipo, identificacion="AB123456")
        form = ClienteForm(
            data={
                "nombre": "Otro Cliente",
                "tipo_identificacion": self.tipo.id,
                "identificacion": "AB123456",
                "correo_electronico": "otro@correo.com",
                "telefono": "8888-8888",
                "direccion": "Heredia",
                "estado": Cliente.Estado.ACTIVO,
                "notas": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("identificacion", form.errors)


class ClienteValidacionesViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="123")
        self.tipo = TipoIdentificacion.objects.create(codigo="CED", nombre="Cédula física")
        Cliente.objects.create(nombre="Acme", tipo_identificacion=self.tipo, identificacion="111111111")

    def test_validar_identificacion_retorna_duplicado(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("clientes:validar_identificacion"), {"identificacion": "111111111"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["duplicado"], True)

    def test_eliminar_cliente_protegido_muestra_error(self):
        self.client.force_login(self.user)
        cliente = Cliente.objects.create(nombre="Bloqueado", tipo_identificacion=self.tipo, identificacion="222222222")

        with patch("apps.clientes.views.Cliente.delete", side_effect=ProtectedError("x", [])):
            response = self.client.post(reverse("clientes:eliminar", args=[cliente.id]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se puede eliminar el cliente porque tiene movimientos asociados")
