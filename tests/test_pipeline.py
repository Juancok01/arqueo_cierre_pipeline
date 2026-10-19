import pandas as pd

from arqueo_pipeline.run import pendientes
from arqueo_pipeline.transform import mensaje, pesos, resumir


def turno(**extra):
	base = {
		"id_turno": "t1",
		"restaurante": "Paladar",
		"email": "dueno@ejemplo.com",
		"cajero": "Ana",
		"fondo": 50_000,
		"abierta_at": "2026-10-19T13:00:00Z",
		"cerrada_at": "2026-10-19T23:00:00Z",
		"efectivo_contado": 80_000,
		"digital_contado": 20_000,
	}
	base.update(extra)
	return pd.DataFrame([base])


def test_esperado_separa_efectivo_y_digital():
	ventas = pd.DataFrame(
		[
			{"id_turno": "t1", "metodo_pago": "efectivo", "total": 30_000},
			{"id_turno": "t1", "metodo_pago": "tarjeta", "total": 20_000},
			{"id_turno": "t1", "metodo_pago": "transferencia", "total": 5_000},
		]
	)
	fila = resumir(turno(), ventas).iloc[0]
	assert fila["esperado_efectivo"] == 80_000
	assert fila["esperado_digital"] == 25_000
	assert fila["diferencia_efectivo"] == 0
	assert fila["diferencia_digital"] == -5_000
	assert fila["tickets"] == 3


def test_sin_conteo_no_inventa_diferencia():
	fila = resumir(turno(efectivo_contado=None, digital_contado=None), pd.DataFrame()).iloc[0]
	assert pd.isna(fila["diferencia_efectivo"])
	assert pesos(fila["efectivo_contado"]) == "sin conteo"


def test_mensaje_nombra_el_negocio():
	asunto, cuerpo = mensaje(resumir(turno(), pd.DataFrame()).iloc[0])
	assert asunto == "Cierre de caja — Paladar"
	assert "Efectivo esperado en cajón: $50.000" in cuerpo
	assert "Efectivo contado: $80.000" in cuerpo


def test_no_reenvia_un_turno_ya_marcado():
	filas = pendientes(resumir(turno(), pd.DataFrame()), {"t1"})
	assert filas.empty


def test_omite_cierre_sin_correo():
	resumen = resumir(turno(email=None), pd.DataFrame())
	assert pendientes(resumen, set()).empty
