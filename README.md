# Cierre de caja — pipeline de Arqueo

Cuando un negocio cierra la caja en Arqueo, este pipeline arma el resumen del turno y se lo envía al correo de la cuenta.

Este repositorio es el proyecto de ingeniería de datos: lee la base, transforma el cierre y entrega un aviso.

## Qué problema resuelve

El cajero cuenta el dinero y cierra el turno en la app. El dueño no siempre está en el local. El pipeline detecta ese cierre y le manda:

- horario y cajero
- tickets y ventas
- efectivo esperado contra efectivo contado
- digital esperado contra digital contado

## Las tres etapas

| Etapa | Descripción |
|---|---|
| Extraer | Postgres de Supabase: `turnos_caja`, `pedidos`, correo de la cuenta |
| Transformar | Un renglón por cierre, con diferencias |
| Entregar| Correo al dueño |

El correo sale de `accesos.email`. Si esa fila no existe, usa el correo de `auth.users`, que es el de la cuenta con la que entra el cliente.

## Dónde corre

GitHub Actions ejecuta `arqueo-cierres` cada 15 minutos y se apaga al terminar. Cada corrida:

1. Trae los cierres de los últimos días.
2. Descarta los que ya están en `pipeline.cierres_avisados`.
3. Arma el correo y lo envía.
4. Anota el `id_turno`, para no repetirlo.



