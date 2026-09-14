import csv
import os
from datetime import datetime

PASTA_EVENTOS = "eventos"
CAMINHO_REGISTRO = os.path.join(PASTA_EVENTOS, "registro_eventos.csv")


def _garantir_arquivo_criado():
    os.makedirs(PASTA_EVENTOS, exist_ok=True)
    arquivo_novo = not os.path.exists(CAMINHO_REGISTRO)
    if arquivo_novo:
        with open(CAMINHO_REGISTRO, mode="w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["data_hora", "tipos_de_alerta", "arquivo_video"])


def registrar_evento(caminho_video, alertas):
    """
    Adiciona uma linha no CSV de registro toda vez que um novo evento começa a ser gravado.
    alertas: lista de strings com os motivos do alerta (ex: "pessoa #2 parado ha 12s").
    """
    _garantir_arquivo_criado()

    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tipos = "; ".join(alertas) if alertas else "movimento nao identificado"

    with open(CAMINHO_REGISTRO, mode="a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([data_hora, tipos, caminho_video])

    print(f"[SafeScreen.AI] Evento registrado: {data_hora} - {tipos}")
