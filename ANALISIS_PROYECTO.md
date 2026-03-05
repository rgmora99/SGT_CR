# Análisis del proyecto SGT_CR

## 1) Visión general
- Proyecto **Django** modular con configuración por entorno (`base`, `dev`, `prod`) y estructura por apps de dominio.
- Funcionalmente, el foco actual está en:
  - **Cuentas/onboarding multi-negocio** (`apps.accounts`)
  - **Gastos con ingestión de facturas por correo IMAP + XML** (`apps.gastos`)
  - **Ventas** (estructura mínima inicial)
  - **Core** (home y navegación base)
- Existen módulos adicionales/legado (`mantenimientos`, `auditoria`, `alertas`) con distinto nivel de madurez e integración.

## 2) Arquitectura técnica

### Backend
- Framework principal: Django.
- DB: PostgreSQL con `search_path=cnt` en settings base.
- Auth:
  - Backend LDAP personalizado + backend local de Django.
  - Middleware de onboarding que fuerza completar negocio y perfil fiscal.

### Frontend
- Templates server-side (`templates/`) + estáticos (`static/css`, `static/js`).
- No se observa framework SPA; patrón clásico Django MVT.

## 3) Estructura por módulos (apps)

### `apps.accounts`
Responsable de autenticación y contexto empresarial:
- Registro/login/logout.
- Onboarding en pasos (negocio + configuración fiscal).
- Relación usuario ↔ negocio (`TB_USUARIO_NEGOCIO`) y negocio activo en sesión.
- Modelo de configuración fiscal por negocio.

### `apps.gastos`
Módulo más robusto actualmente:
- Configuración de buzón IMAP por negocio.
- Sincronización de correos y extracción de adjuntos XML/PDF.
- Parseo de XML de factura electrónica (campos fiscales y montos).
- Creación de `FacturaGasto` con deduplicación por `Message-ID`.
- Flujo de registro de gasto (`FacturaGasto` → `Gasto`).
- Reglas de gastos fijos (`GastoFijo`) para clasificación/automatización.

### `apps.ventas`
- Endpoints base (`listar`, `crear`) y plantillas.
- Aún sin modelos ni lógica de dominio persistente.

### `apps.core`
- Home protegido por login.

### Módulos parcialmente integrados
- `apps.alertas`: vistas y rutas presentes, pero `models.py` vacío actualmente.
- `apps.mantenimientos`: dominio de contratos, prorrogas, garantías, órdenes y documentos (no instalado en `INSTALLED_APPS`).
- `apps.auditoria`: modelo simple de auditoría, también fuera del flujo principal de URLs.

## 4) Flujo funcional principal detectado

1. Usuario se autentica (LDAP o local).
2. Middleware valida onboarding:
   - Si no tiene negocio, redirige a crear negocio.
   - Si no tiene config fiscal, redirige a completar perfil fiscal.
3. Con negocio activo en sesión, el usuario accede a módulos operativos.
4. En gastos:
   - Configura correo IMAP.
   - Ejecuta sincronización (AJAX o comando management).
   - Sistema parsea correos y XML, crea facturas pendientes.
   - Usuario registra/anula/edita gastos derivados.

## 5) Hallazgos importantes
- Hay señales de código en evolución:
  - `apps/ventas/models.py` está vacío.
  - `apps/alertas/models.py` está vacío aunque existen vistas que importan modelos.
  - `apps/gastos/services/imap_client.py` define `mark_seen` dos veces.
  - En `sync_facturas`, hay decorador `@login_required` en una función de servicio reutilizada por comando management.
- Existen apps y rutas comentadas en settings/urls (posible migración gradual o backlog técnico).
- Repositorio incluye `venv/` y `media/` con muchos archivos binarios; conviene verificar estrategia de versionado y `.gitignore`.

## 6) Recomendaciones priorizadas
1. **Consolidar estado de módulos activos/inactivos**
   - Definir oficialmente qué apps están en producción y cuáles en refactor.
2. **Corregir inconsistencias de dominio**
   - Restaurar o eliminar `alertas`/`ventas` incompletas para evitar imports rotos.
3. **Separar capas con mayor claridad**
   - Quitar decoradores HTTP/auth de funciones de servicio reutilizadas por CLI.
4. **Endurecer seguridad/configuración**
   - Evitar secretos hardcodeados en settings base.
5. **Mejorar observabilidad y pruebas**
   - Agregar pruebas de parseo XML, deduplicación y onboarding middleware.

## 7) Conclusión
El proyecto tiene una base sólida de Django modular y un módulo de **gastos** bastante avanzado que ya resuelve un problema real (captura y registro de facturas desde correo). La oportunidad principal está en **limpieza arquitectónica**, **alineación de módulos activos** y **fortalecimiento de calidad (tests + hardening)** para escalar de forma más segura.
