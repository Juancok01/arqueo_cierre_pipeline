from zoneinfo import ZoneInfo

import pandas as pd

BOGOTA = ZoneInfo("America/Bogota")
DIGITAL = {"digital", "tarjeta", "transferencia"}


def resumir(turnos: pd.DataFrame, ventas: pd.DataFrame) -> pd.DataFrame:
	"""Misma cuenta que la pantalla de cierres: fondo + efectivo, y digital aparte."""
	if turnos.empty:
		return turnos.copy()

	ventas = ventas.copy()
	if ventas.empty:
		ventas = pd.DataFrame(columns=["id_turno", "metodo_pago", "total"])
	ventas["total"] = pd.to_numeric(ventas["total"], errors="coerce").fillna(0)
	ventas["metodo_pago"] = ventas["metodo_pago"].fillna("")

	efectivo = ventas[ventas["metodo_pago"].eq("efectivo")].groupby("id_turno")["total"].sum()
	digital = ventas[ventas["metodo_pago"].isin(DIGITAL)].groupby("id_turno")["total"].sum()
	tickets = ventas.groupby("id_turno").size()

	out = turnos.copy()
	for columna in ("fondo", "efectivo_contado", "digital_contado"):
		out[columna] = pd.to_numeric(out[columna], errors="coerce")
	out["fondo"] = out["fondo"].fillna(0)
	out["ventas_efectivo"] = out["id_turno"].map(efectivo).fillna(0)
	out["ventas_digital"] = out["id_turno"].map(digital).fillna(0)
	out["tickets"] = out["id_turno"].map(tickets).fillna(0).astype(int)
	out["esperado_efectivo"] = out["fondo"] + out["ventas_efectivo"]
	out["esperado_digital"] = out["ventas_digital"]
	out["diferencia_efectivo"] = out["efectivo_contado"] - out["esperado_efectivo"]
	out["diferencia_digital"] = out["digital_contado"] - out["esperado_digital"]
	return out


def pesos(valor: object) -> str:
	numero = pd.to_numeric(valor, errors="coerce")
	if pd.isna(numero):
		return "sin conteo"
	return f"${numero:,.0f}".replace(",", ".")


def hora(valor: object) -> str:
	if valor is None or (isinstance(valor, float) and pd.isna(valor)):
		return "—"
	marca = pd.to_datetime(valor, utc=True).tz_convert(BOGOTA)
	if pd.isna(marca):
		return "—"
	return marca.strftime("%d/%m/%Y %H:%M")


def _texto(valor: object, defecto: str) -> str:
	if valor is None or pd.isna(valor) or str(valor).strip() == "":
		return defecto
	return str(valor)


def mensaje(fila: pd.Series) -> tuple[str, str]:
	restaurante = _texto(fila.get("restaurante"), "tu negocio")
	asunto = f"Cierre de caja — {restaurante}"
	cuerpo = "\n".join(
		[
			f"Hola, la caja de {restaurante} ya cerró.",
			"",
			f"Cajero: {_texto(fila.get('cajero'), 'Administrador')}",
			f"Abrió: {hora(fila.get('abierta_at'))}",
			f"Cerró: {hora(fila.get('cerrada_at'))}",
			f"Tickets: {int(fila.get('tickets') or 0)}",
			"",
			f"Fondo inicial: {pesos(fila.get('fondo'))}",
			f"Ventas en efectivo: {pesos(fila.get('ventas_efectivo'))}",
			f"Efectivo esperado en cajón: {pesos(fila.get('esperado_efectivo'))}",
			f"Efectivo contado: {pesos(fila.get('efectivo_contado'))}",
			f"Diferencia de efectivo: {pesos(fila.get('diferencia_efectivo'))}",
			"",
			f"Ventas digitales: {pesos(fila.get('ventas_digital'))}",
			f"Digital contado: {pesos(fila.get('digital_contado'))}",
			f"Diferencia digital: {pesos(fila.get('diferencia_digital'))}",
		]
	)
	return asunto, cuerpo
