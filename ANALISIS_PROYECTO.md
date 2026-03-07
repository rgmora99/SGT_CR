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


## 8) ¿Con qué cambios empezar para lograr un MVP?

### Objetivo MVP (4-6 semanas)
Tener un sistema usable por 1 negocio piloto que permita:
1. Login + onboarding básico.
2. Sincronizar facturas por correo.
3. Registrar y listar gastos.
4. Ver métricas básicas (pendientes/registradas/anuladas).

---

### Fase 1 (Semana 1): estabilizar base técnica
**Meta:** eliminar bloqueadores estructurales para poder construir encima.

- Definir alcance oficial de apps activas para MVP:
  - Activas: `accounts`, `core`, `gastos`.
  - En pausa: `alertas`, `mantenimientos`, `auditoria`, `ventas` (si no aportan al MVP inmediato).
- Corregir inconsistencias de código que pueden romper ejecución:
  - Quitar decoradores de request/auth en funciones de servicio (`sync_facturas` debe ser función de dominio pura).
  - Eliminar duplicidad de métodos (`mark_seen`) en cliente IMAP.
- Estandarizar configuración local:
  - Asegurar entorno Python/Django reproducible (`requirements/dev.txt`, guía de arranque mínima).

**Criterio de salida:** `manage.py check` y arranque local funcionando en ambiente del equipo.

---

### Fase 2 (Semana 2): onboarding y multi-negocio mínimo
**Meta:** asegurar que un usuario nuevo entra y queda operativo.

- Revisar flujo de onboarding end-to-end:
  - Registro → crear negocio → perfil fiscal → home.
- Robustecer middleware de onboarding:
  - Rutas permitidas explícitas y fallback seguro para sesiones sin negocio.
- Añadir validaciones y mensajes de error consistentes en formularios clave.

**Criterio de salida:** flujo completo sin errores manuales para usuario nuevo (happy path + 2 casos inválidos).

---

### Fase 3 (Semana 3-4): gastos punta a punta (núcleo de valor)
**Meta:** cerrar el flujo funcional principal del producto.

- Configuración de correo IMAP por negocio (guardar/probar conexión).
- Sincronización de facturas:
  - deduplicación por `Message-ID`,
  - parseo XML robusto,
  - creación de `FacturaGasto` en estado pendiente.
- Registro de gasto desde factura:
  - pasar de `pendiente` → `en_registro` → `registrada`.
- Listado de gastos con filtros básicos (fecha, categoría, texto).

**Criterio de salida:** demo funcional con 10-20 facturas de prueba y registro exitoso de gastos.

---

### Fase 4 (Semana 5): calidad mínima de producción
**Meta:** reducir riesgo operativo antes de piloto real.

- Seguridad y configuración:
  - mover `SECRET_KEY` y credenciales sensibles a variables de entorno.
- Observabilidad mínima:
  - logging de sincronización (facturas creadas, omitidas, errores).
- Pruebas prioritarias:
  - parseo XML,
  - deduplicación,
  - onboarding middleware,
  - transición de estados de factura/gasto.

**Criterio de salida:** pruebas críticas pasando y checklist de despliegue básico.

---

### Backlog post-MVP (no bloquear salida inicial)
- Reactivar `alertas` con modelo consistente.
- Consolidar `ventas` con modelo de dominio real.
- Evaluar activación de `mantenimientos` según roadmap negocio.

## 9) Priorización sugerida (impacto vs esfuerzo)
1. **Alta / Bajo-Medio:** estabilidad técnica (fase 1).
2. **Alta / Medio:** onboarding sin fricción (fase 2).
3. **Muy alta / Medio-Alto:** flujo de gastos completo (fase 3).
4. **Alta / Medio:** hardening y pruebas críticas (fase 4).

En resumen: si quieres resultados rápidos, empieza por **cerrar el flujo `accounts + gastos`** y congelar temporalmente lo demás.


## 10) Fase 1 ejecutada (ajustes aplicados en código)
Se aplicaron correcciones iniciales de estabilización para reducir deuda técnica inmediata:

- **Servicio de sincronización desacoplado de capa web**
  - `sync_facturas` ya no depende de `@login_required`.
  - Queda utilizable tanto desde vistas como desde command (`sync_facturas_correo`) sin semántica HTTP mezclada.

- **Cliente IMAP saneado**
  - Se eliminó la duplicidad de `mark_seen`.
  - Se añadieron validaciones de conexión (`self.conn`) antes de operaciones IMAP para errores más claros.

- **Sincronización AJAX alineada con su contrato**
  - `sync_facturas_ajax` ahora ejecuta con `solo_unread=True` para respetar el comportamiento descrito.

- **Hardening de configuración base**
  - `SECRET_KEY` y `DEBUG` pasan a depender de variables de entorno (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`) con fallback seguro de desarrollo.

### Resultado esperado tras estos cambios
1. Menor acoplamiento entre vistas y servicios.
2. Menos riesgo de errores silenciosos en IMAP.
3. Comportamiento consistente entre documentación y ejecución.
4. Primer paso hacia configuración segura para entornos no locales.

## 11) Lectura funcional en dos perfiles: contador y usuario final

### 11.1 Perspectiva de un contador
**¿Qué valor aporta?**
- El sistema está orientado a centralizar la evidencia fiscal del negocio (facturas de gasto con XML/PDF), con estados operativos que permiten seguimiento contable (`pendiente`, `en_registro`, `registrada`, `rechazada`).
- Existe estructura de configuración fiscal por negocio (identificación, régimen IVA, porcentaje IVA, periodicidad, declaración de renta), útil para parametrizar la lógica tributaria por cliente.
- La arquitectura multi-negocio permite atender varios negocios sin mezclar datos, clave para despacho contable o asesor externo.

**Fortalezas contables observadas**
1. **Trazabilidad documental:** se conserva origen de correo, `message_id`, archivos XML/PDF y estado de procesamiento.
2. **Control de duplicados:** restricción única por `negocio + email_message_id`, importante para evitar doble registro.
3. **Flujo de formalización:** la factura detectada pasa a gasto registrado con categoría, fecha y método de pago.
4. **KPIs operativos iniciales:** la bandeja y listados muestran pendientes/registrados/anulados para control diario.

**Riesgos o vacíos desde contabilidad**
- No se observa aún conciliación avanzada (bancos, cuentas contables, asientos dobles).
- El dashboard inicial tiene indicadores demo/estáticos en la portada.
- El módulo de ventas está en etapa temprana, por lo que la visión completa ingreso-egreso todavía es parcial.

### 11.2 Perspectiva de usuario final (dueño/administrador pyme)
**Experiencia principal esperada**
1. Crear cuenta e iniciar sesión.
2. Completar onboarding (crear negocio + datos fiscales).
3. Configurar correo para lectura de facturas.
4. Sincronizar y revisar facturas en bandeja.
5. Registrar gasto en pocos clics y consultar histórico.

**Lo que sí resuelve hoy para usuario final**
- Reduce trabajo manual al capturar facturas desde correo.
- Organiza el proceso con estados claros y acciones concretas (registrar/rechazar/continuar).
- Permite filtrar y consultar gastos por proveedor, categoría, método de pago y fechas.

**Puntos de fricción probables para usuario no técnico**
- La configuración IMAP puede ser sensible (credenciales, carpeta, puertos).
- Algunos módulos visibles en navegación parecen no estar completos todavía.
- La portada promete funciones de reportes/IVA que en parte todavía se perciben en desarrollo.

### 11.3 Concepto del sistema (síntesis)
El concepto central de SGT_CR es ser un **asistente operativo contable-fiscal para pymes**, priorizando primero el frente de **gastos con soporte documental electrónico**, y construyendo alrededor un marco multi-negocio con onboarding fiscal guiado. Es un enfoque pragmático: primero ordenar la captura y registro de evidencia tributaria, luego escalar hacia analítica y cumplimiento más avanzado.

### 11.4 Recomendación estratégica por perfil
- **Para contador:** posicionarlo como “hub de documentación fiscal + precontabilidad”, evitando venderlo aún como ERP completo.
- **Para usuario final:** enfatizar beneficios inmediatos (menos papeleo, mayor orden, visibilidad de pendientes).
- **Para producto:** cerrar totalmente el ciclo gastos + tablero real (KPIs dinámicos) antes de expandir ventas/reportes avanzados.
