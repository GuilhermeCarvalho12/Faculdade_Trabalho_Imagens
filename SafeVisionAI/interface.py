import cv2
import csv
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime

from detectmov import detectar_movimento, resetar_estado
from buffer_eventos import GravadorDeEventos
from registro_eventos import CAMINHO_REGISTRO


class InterfaceSafeScreen:

    

    def __init__(self, janela):

        self.janela = janela
        self.janela.title("SafeScreen.AI")
        self.janela.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        # Modo de visualização
        self.modo_visualizacao = "normal"

        # Modo de segurança
        self.modo_seguranca = True

        # Câmera
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise RuntimeError("Não foi possível abrir a câmera.")

        # FPS da câmera
        fps = self.camera.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            fps = 20

        self.fps = fps

        # Gravador de eventos
        self.gravador = GravadorDeEventos(
            self.fps
        )

        # Montar interface
        self._montar_layout()

        # Iniciar vídeo
        self._loop_video()

    def _verificar_dia_noite(self):

        hora = datetime.now().hour

        if 6 <= hora < 22:
            return "DIA"

        return "NOITE"

    def _montar_layout(self):

        # -----------------------------
        # VÍDEO
        # -----------------------------

        self.label_video = tk.Label(
            self.janela
        )

        self.label_video.pack(
            padx=10,
            pady=10
        )


        # -----------------------------
        # STATUS
        # -----------------------------

        self.label_status = tk.Label(
            self.janela,
            text="Status: Iniciando...",
            font=("Arial", 14)
        )

        self.label_status.pack(
            pady=5
        )


        # -----------------------------
        # EVENTOS RECENTES
        # -----------------------------

        frame_eventos = tk.Frame(
            self.janela
        )

        frame_eventos.pack(
            padx=10,
            pady=10,
            fill="x"
        )


        tk.Label(
            frame_eventos,
            text="Eventos recentes",
            font=("Arial", 12, "bold")
        ).pack(
            anchor="w"
        )


        self.lista_eventos = ttk.Treeview(
            frame_eventos,
            columns=("data", "tipo"),
            show="headings",
            height=8
        )

        self.lista_eventos.heading(
            "data",
            text="Data/Hora"
        )

        self.lista_eventos.heading(
            "tipo",
            text="Evento"
        )

        self.lista_eventos.column(
            "data",
            width=180
        )

        self.lista_eventos.column(
            "tipo",
            width=300
        )

        self.lista_eventos.pack(
            fill="x"
        )


        # -----------------------------
        # BOTÕES
        # -----------------------------

        self.frame_botoes = tk.Frame(
            self.janela
        )

        self.frame_botoes.pack(
            pady=10
        )


        # Botão NORMAL

        self.botao_normal = tk.Button(
            self.frame_botoes,
            text="NORMAL",
            width=15,
            command=self._modo_normal
        )

        self.botao_normal.pack(
            side="left",
            padx=5
        )


        # Botão THRESHOLD

        self.botao_threshold = tk.Button(
            self.frame_botoes,
            text="THRESHOLD",
            width=15,
            command=self._modo_threshold
        )

        self.botao_threshold.pack(
            side="left",
            padx=5
        )


        # Botão SEGURANÇA

        self.botao_seguranca = tk.Button(
            self.frame_botoes,
            text="SEGURANÇA: ATIVA",
            width=18,
            command=self._alternar_seguranca
        )

        self.botao_seguranca.pack(
            side="left",
            padx=5
        )


    # -----------------------------
    # MODO NORMAL
    # -----------------------------

    def _modo_normal(self):

        self.modo_visualizacao = "normal"


    # -----------------------------
    # MODO THRESHOLD
    # -----------------------------

    def _modo_threshold(self):

        self.modo_visualizacao = "threshold"


    # -----------------------------
    # ALTERNAR SEGURANÇA
    # -----------------------------

    def _alternar_seguranca(self):

        self.modo_seguranca = not self.modo_seguranca

        # Limpa o estado anterior do detector
        # para evitar falsos movimentos
        # quando a segurança for reativada.
        resetar_estado()

        if self.modo_seguranca:

            self.botao_seguranca.config(
                text="SEGURANÇA: ATIVA"
            )

            self.label_status.config(
                text="Status: Segurança ativada",
                fg="green"
            )

        else:

            self.botao_seguranca.config(
                text="SEGURANÇA: DESATIVADA"
            )

            self.label_status.config(
                text="Modo câmera normal",
                fg="blue"
            )


    # -----------------------------
    # LOOP DA CÂMERA
    # -----------------------------

    def _loop_video(self):

        sucesso, frame = self.camera.read()

        if not sucesso:

            self.label_status.config(
                text="Erro ao ler câmera",
                fg="red"
            )

            self.janela.after(
                100,
                self._loop_video
            )

            return


        # -----------------------------
        # SEGURANÇA ATIVA
        # -----------------------------

        if self.modo_seguranca:
            
            modo = self._verificar_dia_noite()
            alertas, threshold = detectar_movimento(
                frame
            )

        # -----------------------------
        # SEGURANÇA DESATIVADA
        # -----------------------------

        else:

            alertas = []

            threshold = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )


        # -----------------------------
        # GRAVAÇÃO DE EVENTOS
        # -----------------------------

        self.gravador.atualizar(
            frame,
            alertas
        )


        # -----------------------------
        # STATUS
        # -----------------------------

        if alertas:

            self.label_status.config(
                text="Status: ALERTA!",
                fg="red"
            )

        else:

            if self.modo_seguranca:

                self.label_status.config(
                    text="Status: Tudo normal",
                    fg="green"
                )

            else:

                self.label_status.config(
                    text="Modo câmera normal",
                    fg="blue"
                )


        # -----------------------------
        # ESCOLHER IMAGEM
        # -----------------------------

        if self.modo_visualizacao == "threshold":

            imagem = threshold

            # Threshold é preto e branco
            imagem = cv2.cvtColor(
                imagem,
                cv2.COLOR_GRAY2RGB
            )

        else:

            imagem = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )


        # -----------------------------
        # REDIMENSIONAR
        # -----------------------------

        imagem = cv2.resize(
            imagem,
            (800, 600)
        )


        # -----------------------------
        # CONVERTER PARA TKINTER
        # -----------------------------

        imagem_pil = Image.fromarray(
            imagem
        )

        imagem_tk = ImageTk.PhotoImage(
            imagem_pil
        )


        self.label_video.configure(
            image=imagem_tk
        )

        self.label_video.image = imagem_tk


        # -----------------------------
        # ATUALIZAR EVENTOS
        # -----------------------------

        self._atualizar_lista_eventos()


        # -----------------------------
        # PRÓXIMO FRAME
        # -----------------------------

        self.janela.after(
            15,
            self._loop_video
        )


    # -----------------------------
    # LISTA DE EVENTOS
    # -----------------------------

    def _atualizar_lista_eventos(self):

        if not os.path.exists(
            CAMINHO_REGISTRO
        ):
            return


        try:

            with open(
                CAMINHO_REGISTRO,
                "r",
                encoding="utf-8"
            ) as arquivo:

                leitor = csv.reader(
                    arquivo
                )

                linhas = list(
                    leitor
                )


            # Limpar lista

            for item in self.lista_eventos.get_children():

                self.lista_eventos.delete(
                    item
                )


            # Mostrar últimos 15 eventos

            for linha in linhas[-15:]:

                if len(linha) >= 2:

                    self.lista_eventos.insert(
                        "",
                        "end",
                        values=(
                            linha[0],
                            linha[1]
                        )
                    )

        except Exception:

            pass


    # -----------------------------
    # FECHAR PROGRAMA
    # -----------------------------

    def ao_fechar(self):

        try:

            self.gravador.finalizar()

        except Exception:

            pass


        if self.camera.isOpened():

            self.camera.release()


        self.janela.destroy()


# -----------------------------
# INICIAR INTERFACE
# -----------------------------

def iniciar_interface():

    janela = tk.Tk()

    InterfaceSafeScreen(
        janela
    )

    janela.mainloop()