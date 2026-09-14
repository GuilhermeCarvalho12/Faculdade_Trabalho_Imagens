import cv2
from ia_classificacao import classificar_frame
from analise_comportamento import RastreadorDeComportamento

frame_anterior = None
rastreador = RastreadorDeComportamento()  # mantém a "memória" dos objetos entre chamadas

def detectar_movimento(frame):
    """
    Retorna a lista de alertas de comportamento incomum encontrados neste frame
    (lista vazia se não houver nenhum).
    """
    global frame_anterior

    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cinza = cv2.GaussianBlur(cinza, (21, 21), 0)  # reduz ruído/falsos positivos

    if frame_anterior is None:
        frame_anterior = cinza
        return []

    diferenca = cv2.absdiff(frame_anterior, cinza)
    _, threshold = cv2.threshold(diferenca, 25, 255, cv2.THRESH_BINARY)
    threshold = cv2.dilate(threshold, None, iterations=2)
    contornos, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    houve_movimento = any(cv2.boundingRect(c)[2] > 30 and cv2.boundingRect(c)[3] > 30for c in contornos)

    alertas = []

    if houve_movimento:
        deteccoes = classificar_frame(frame)

        for nome, confianca, x, y, largura, altura in deteccoes:
            rotulo = f"{nome} ({confianca:.0%})"
            cv2.rectangle(frame, (x, y), (x + largura, y + altura), (0, 255, 0), 2)
            cv2.putText(frame, rotulo, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        alertas = rastreador.atualizar(deteccoes)
        for i, alerta in enumerate(alertas):
            cv2.putText(frame, f"ALERTA: {alerta}", (10, 30 + i * 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if not deteccoes:
            cv2.putText(frame, "Movimento nao identificado", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Threshold", threshold)
    cv2.imshow("Diferenca", diferenca)
    cv2.imshow("Cinza", cinza)

    frame_anterior = cinza

    return alertas
