import math
import time
from datetime import datetime

# --- Parâmetros ajustáveis (o "conhecimento de negócio" do sistema) ---
DISTANCIA_MAXIMA_PAREAMENTO = 80   # px: o quanto um objeto pode se mover entre frames e ainda ser considerado o mesmo
DISTANCIA_MINIMA_MOVIMENTO = 5      # px: abaixo disso, consideramos que o objeto está "parado"
TEMPO_PARADO_SUSPEITO = 10          # segundos parado no mesmo lugar para disparar alerta
VELOCIDADE_CORRENDO = 300           # px/segundo: acima disso, consideramos que o objeto está "correndo"
HORARIO_ABERTURA = 8
HORARIO_FECHAMENTO = 22


class ObjetoRastreado:
    """Guarda o histórico de um único objeto (pessoa, animal, etc.) ao longo do tempo."""

    def __init__(self, id_objeto, centro, nome_classe):
        self.id = id_objeto
        self.nome_classe = nome_classe
        self.centro_atual = centro
        self.tempo_parado = 0.0
        self.velocidade = 0.0
        self.instante_ultima_atualizacao = time.time()

    def atualizar(self, novo_centro):
        agora = time.time()
        intervalo = max(agora - self.instante_ultima_atualizacao, 1e-6)
        distancia = math.dist(self.centro_atual, novo_centro)

        self.velocidade = distancia / intervalo

        if distancia < DISTANCIA_MINIMA_MOVIMENTO:
            self.tempo_parado += intervalo
        else:
            self.tempo_parado = 0.0  # voltou a se mover, reseta a contagem

        self.centro_atual = novo_centro
        self.instante_ultima_atualizacao = agora


class RastreadorDeComportamento:
    """Recebe as detecções de cada frame e mantém a 'memória' de cada objeto entre frames."""

    def __init__(self):
        self.objetos = {}
        self.proximo_id = 0

    def _centro(self, x, y, largura, altura):
        return (x + largura / 2, y + altura / 2)

    def atualizar(self, deteccoes):
        """
        deteccoes: lista de (nome, confianca, x, y, largura, altura), vinda do classificar_frame.
        Retorna: lista de strings com os alertas de comportamento incomum deste frame.
        """
        alertas = []
        ids_vistos = set()

        for nome, confianca, x, y, largura, altura in deteccoes:
            centro = self._centro(x, y, largura, altura)

            # Procura, entre os objetos já conhecidos da mesma classe, o mais próximo dessa detecção
            id_correspondente = None
            menor_distancia = DISTANCIA_MAXIMA_PAREAMENTO
            for id_objeto, objeto in self.objetos.items():
                if objeto.nome_classe != nome or id_objeto in ids_vistos:
                    continue
                distancia = math.dist(objeto.centro_atual, centro)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    id_correspondente = id_objeto

            if id_correspondente is not None:
                objeto = self.objetos[id_correspondente]
                objeto.atualizar(centro)
            else:
                id_correspondente = self.proximo_id
                self.proximo_id += 1
                objeto = ObjetoRastreado(id_correspondente, centro, nome)
                self.objetos[id_correspondente] = objeto

            ids_vistos.add(id_correspondente)

            # Regra 1: parado no mesmo lugar por tempo demais
            if objeto.tempo_parado >= TEMPO_PARADO_SUSPEITO:
                alertas.append(f"{nome} #{id_correspondente} parado ha {int(objeto.tempo_parado)}s")

            # Regra 2: se movendo rápido demais (correndo)
            if objeto.velocidade > VELOCIDADE_CORRENDO:
                alertas.append(f"{nome} #{id_correspondente} em movimento rapido")

            # Regra 3: pessoa detectada fora do horário comercial
            hora_atual = datetime.now().hour
            if nome == "pessoa" and not (HORARIO_ABERTURA <= hora_atual < HORARIO_FECHAMENTO):
                alertas.append(f"pessoa #{id_correspondente} fora do horario comercial")

        # Objetos que não apareceram neste frame provavelmente saíram de cena - paramos de rastreá-los
        self.objetos = {id_: obj for id_, obj in self.objetos.items() if id_ in ids_vistos}

        return alertas
