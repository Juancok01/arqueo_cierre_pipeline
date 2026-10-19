import pandas as pd
import psycopg


def _tabla(conn: psycopg.Connection, sql: str, params: dict) -> pd.DataFrame:
	with conn.cursor() as cur:
		cur.execute(sql, params)
		columnas = [col.name for col in cur.description]
		return pd.DataFrame(cur.fetchall(), columns=columnas)

TURNOS = """
select
    t.id_turno::text as id_turno,
    r.nombre as restaurante,
    coalesce(a.email, u.email) as email,
    e.nombre as cajero,
    t.fondo,
    t.abierta_at,
    t.cerrada_at,
    t.efectivo_contado,
    t.digital_contado
from public.turnos_caja t
join public.restaurantes r on r.id_restaurante = t.id_restaurante
left join public.empleados e on e.id_empleado = t.id_empleado
left join public.accesos a on a.id_usuario = r.id_usuario
left join auth.users u on u.id = r.id_usuario
where t.cerrada_at is not null
  and t.cerrada_at >= now() - make_interval(days => %(dias)s)
order by t.cerrada_at
"""

VENTAS = """
select
    p.id_turno::text as id_turno,
    p.metodo_pago,
    p.total
from public.pedidos p
where p.estado = 'cerrado'
  and p.id_turno = any(%(ids)s::uuid[])
"""


def conectar(url: str) -> psycopg.Connection:
	return psycopg.connect(url)


def turnos_cerrados(conn: psycopg.Connection, dias: int) -> pd.DataFrame:
	return _tabla(conn, TURNOS, {"dias": dias})


def ventas_de(conn: psycopg.Connection, ids: list[str]) -> pd.DataFrame:
	if not ids:
		return pd.DataFrame(columns=["id_turno", "metodo_pago", "total"])
	return _tabla(conn, VENTAS, {"ids": ids})
