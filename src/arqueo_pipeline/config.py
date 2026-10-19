import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")


def entorno(nombre: str, defecto: str = "") -> str:
	valor = os.getenv(nombre, defecto).strip()
	if not valor and not defecto:
		raise RuntimeError(f"Falta {nombre}")
	return valor


def enviar_de_verdad() -> bool:
	return os.getenv("ENVIAR_CORREO", "false").strip().lower() in {"1", "true", "si", "sí", "yes"}


def dias_atras() -> int:
	valor = os.getenv("DIAS_ATRAS", "2").strip()
	return int(valor or "2")


def correo_prueba() -> str:
	"""Si tiene valor, todos los avisos salen a este correo y no al del cliente."""
	return os.getenv("CORREO_PRUEBA", "").strip()
