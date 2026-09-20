import cv2

from ia_classificacao import classificar_frame
from analise_comportamento import RastreadorDeComportamento


# -----------------------------------
# VARIÁVEIS DO DETECTOR
# -----------------------------------

frame_anterior = None

rastreador = RastreadorDeComportamento()


# -----------------------------------
# RESETAR ESTADO
# -----------------------------------

def resetar_estado():

    global frame_anterior
    global rastreador

    frame_anterior = None
    rastreador = RastreadorDeComportamento()


# -----------------------------------
# DETECTAR MOVIMENTO
# -----------------------------------

def detectar_movimento(frame):

    global frame_anterior


    # -----------------------------
    # CINZA
    # -----------------------------

    cinza = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # -----------------------------
    # BLUR
    # -----------------------------

    cinza = cv2.GaussianBlur(
        cinza,
        (21, 21),
        0
    )


    # -----------------------------
    # PRIMEIRO FRAME
    # -----------------------------

    if frame_anterior is None:

        frame_anterior = cinza

        threshold = cv2.absdiff(
            cinza,
            cinza
        )

        return [], threshold


    # -----------------------------
    # DIFERENÇA ENTRE FRAMES
    # -----------------------------

    diferenca = cv2.absdiff(
        frame_anterior,
        cinza
    )


    frame_anterior = cinza


    # -----------------------------
    # THRESHOLD
    # -----------------------------

    _, threshold = cv2.threshold(
        diferenca,
        25,
        255,
        cv2.THRESH_BINARY
    )


    # -----------------------------
    # DILATAÇÃO
    # -----------------------------

    threshold = cv2.dilate(
        threshold,
        None,
        iterations=2
    )


    # -----------------------------
    # CONTORNOS
    # -----------------------------

    contornos, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    alertas = []


    # -----------------------------
    # MOVIMENTOS
    # -----------------------------

    for contorno in contornos:

        x, y, largura, altura = cv2.boundingRect(
            contorno
        )


        # Ignorar movimentos muito pequenos

        if largura < 30 or altura < 30:
            continue


        # Desenhar caixa

        cv2.rectangle(
            frame,
            (x, y),
            (x + largura, y + altura),
            (0, 255, 0),
            2
        )


        # --------------------------------
        # CLASSIFICAÇÃO POR IA
        # --------------------------------

        resultado = classificar_frame(
            frame
        )


        # --------------------------------
        # RESULTADOS DA IA
        # --------------------------------

        if resultado:

            for objeto in resultado:

                
                nome, confianca, x, y, largura, altura = objeto


                texto = (
                    f"{nome} "
                    f"{confianca:.2f}"
                )


                cv2.putText(
                    frame,
                    texto,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )


                # Registrar alerta

                alertas.append(
                    nome
                )


    # --------------------------------
    # RETORNO
    # --------------------------------

    return alertas, threshold