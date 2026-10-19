import psycopg

# El id_turno ya existe en Arqueo. Esta tabla solo recuerda cuál se avisó.
_PREPARAR = (
	"create schema if not exists pipeline",
	"""
	create table if not exists pipeline.cierres_avisados (
		id_turno uuid primary key,
		email text not null,
		enviado_at timestamptz not null default now()
	)
	""",
	"revoke all on schema pipeline from public, anon, authenticated",
	"revoke all on table pipeline.cierres_avisados from public, anon, authenticated",
	"alter table pipeline.cierres_avisados enable row level security",
)


def preparar(conn: psycopg.Connection) -> None:
	for orden in _PREPARAR:
		conn.execute(orden)


def ya_avisados(conn: psycopg.Connection) -> set[str]:
	filas = conn.execute("select id_turno::text from pipeline.cierres_avisados").fetchall()
	return {fila[0] for fila in filas}


def marcar_avisado(conn: psycopg.Connection, id_turno: str, email: str) -> None:
	conn.execute(
		"""
		insert into pipeline.cierres_avisados (id_turno, email)
		values (%s, %s)
		on conflict (id_turno) do nothing
		""",
		(id_turno, email),
	)
