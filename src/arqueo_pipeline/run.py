import pandas as pd

from arqueo_pipeline.config import correo_prueba, dias_atras, enviar_de_verdad, entorno
from arqueo_pipeline.emailer import enviar
from arqueo_pipeline.extract import conectar, turnos_cerrados, ventas_de
from arqueo_pipeline.state import marcar_avisado, preparar, ya_avisados
from arqueo_pipeline.transform import mensaje, resumir


def pendientes(resumen: pd.DataFrame, enviados: set[str]) -> pd.DataFrame:
	if resumen.empty:
		return resumen
	nuevos = ~resumen["id_turno"].isin(enviados)
	con_correo = resumen["email"].fillna("").str.contains("@")
	return resumen[nuevos & con_correo].reset_index(drop=True)


def correr() -> int:
	with conectar(entorno("DATABASE_URL")) as conn:
		preparar(conn)
		turnos = turnos_cerrados(conn, dias_atras())
		ventas = ventas_de(conn, turnos["id_turno"].tolist() if not turnos.empty else [])
		resumen = resumir(turnos, ventas)
		por_enviar = pendientes(resumen, ya_avisados(conn))
		if por_enviar.empty:
			print("No hay cierres nuevos.")
			return 0

		real = enviar_de_verdad()
		prueba = correo_prueba()
		for _, fila in por_enviar.iterrows():
			asunto, cuerpo = mensaje(fila)
			destino = prueba or fila["email"]
			if real:
				enviar(destino, asunto, cuerpo)
				marcar_avisado(conn, fila["id_turno"], fila["email"])
				print(f"Enviado a {destino} — {asunto}")
			else:
				nota = f" (la cuenta es {fila['email']})" if prueba else ""
				print(f"--- Simulación para {destino}{nota} ---")
				print(asunto)
				print(cuerpo)
				print("--- No se envió ni se marcó. ENVIAR_CORREO=false ---")
		return len(por_enviar)


def main() -> None:
	correr()


if __name__ == "__main__":
	main()
