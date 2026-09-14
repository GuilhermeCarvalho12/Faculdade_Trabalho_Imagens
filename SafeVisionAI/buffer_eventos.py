import cv2
import os
import time
from collections import deque
from datetime import datetime
from registro_eventos import registrar_evento

PASTA_EVENTOS = "eventos"
SEGUNDOS_BUFFER_ANTES = 15    # quanto tempo "antes" do alerta fica guardado em memória
SEGUNDOS_GRAVACAO_DEPOIS = 5  # continua gravando por mais esse tempo após o último alerta


class GravadorDeEventos:
    """
    Mantém um buffer circular com os últimos N segundos de vídeo em memória.
    Quando um evento (alerta) acontece, salva esse buffer + os frames seguintes
    em um arquivo .mp4 e registra o evento no CSV de histórico.
    """

    def __init__(self, fps_estimado=20):
        self.fps = max(int(fps_estimado), 1)
        self.buffer = deque(maxlen=self.fps * SEGUNDOS_BUFFER_ANTES)
        self.gravando = False
        self.writer = None
        self.instante_ultimo_alerta = None
        os.makedirs(PASTA_EVENTOS, exist_ok=True)

    def atualizar(self, frame, alertas):
        """
        Chame isso a cada frame do loop principal.
        alertas: lista de strings retornada por detectar_movimento (vazia se não houver nenhum).
        """
        self.buffer.append(frame.copy())

        agora = time.time()
        houve_alerta = bool(alertas)

        if houve_alerta:
            self.instante_ultimo_alerta = agora
            if not self.gravando:
                self._iniciar_gravacao(frame, alertas)

        if self.gravando:
            self.writer.write(frame)

            if agora - self.instante_ultimo_alerta > SEGUNDOS_GRAVACAO_DEPOIS:
                self._encerrar_gravacao()

    def _iniciar_gravacao(self, frame_atual, alertas):
        altura, largura = frame_atual.shape[:2]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = os.path.join(PASTA_EVENTOS, f"evento_{timestamp}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(caminho, fourcc, self.fps, (largura, altura))

        for frame_anterior in self.buffer:
            self.writer.write(frame_anterior)

        self.gravando = True
        registrar_evento(caminho, alertas)

    def _encerrar_gravacao(self):
        self.writer.release()
        self.writer = None
        self.gravando = False
        print("[SafeScreen.AI] Gravacao do evento encerrada.")

    def finalizar(self):
        """Chame ao encerrar o programa, caso ainda esteja gravando algo."""
        if self.gravando:
            self._encerrar_gravacao()
