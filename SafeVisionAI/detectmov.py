import cv2



frame_anterior = None

def detectar_movimento(frame):
    global frame_anterior

    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if frame_anterior is None:
        frame_anterior = cinza
        return
    
    diferenca = cv2.absdiff(frame_anterior, cinza)
    _, threshold = cv2.threshold(diferenca, 25, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        x, y, largura, altura = cv2.boundingRect(contorno)
        if largura > 30 and altura > 30:
            cv2.rectangle(frame, (x, y), (x + largura, y + altura), (0, 255, 0), 2)
            cv2.putText(frame, "Movimento detectado!", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Threshold", threshold)

    frame_anterior = cinza

    cv2.imshow("Diferenca", diferenca)
    
    cv2.imshow("Cinza", cinza)