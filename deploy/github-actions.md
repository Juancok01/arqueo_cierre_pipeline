# GitHub Actions

GitHub despierta el mismo programa cada 15 minutos. No hay una máquina encendida entre corridas, así que no hay un costo mensual de cómputo.

La memoria de qué cierres ya se avisaron vive en `pipeline.cierres_avisados`, dentro de Supabase. El esquema no está expuesto en la API. La primera corrida crea la tabla.

## Secretos

En el repositorio de GitHub: **Settings → Secrets and variables → Actions**.

Secretos:

- `DATABASE_URL`: la URL del Session pooler de Supabase
- `SMTP_USER`
- `SMTP_PASSWORD`: la clave de aplicación de Gmail
- `SMTP_FROM`

Variables:

- `DIAS_ATRAS` = `2`
- `ENVIAR_CORREO` = `false` hasta ver una corrida bien. Luego `true`
- `CORREO_PRUEBA` = correo de pruebas
- `SMTP_HOST` = `smtp.gmail.com`
- `SMTP_PORT` = `587`

## Probarlo

**Actions → Avisar cierres → Run workflow**. Esa pantalla, con el resultado verde, es la captura del automatismo.
