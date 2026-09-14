import cv2
from detectmov import detectar_movimento
from buffer_eventos import GravadorDeEventos

# Initialize the camera and verify if it opened successfully
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

# Algumas webcams não informam o FPS corretamente (retornam 0) - usamos 20 como padrão nesse caso
fps_camera = camera.get(cv2.CAP_PROP_FPS)
if not fps_camera or fps_camera <= 1:
    fps_camera = 20

gravador = GravadorDeEventos(fps_estimado=fps_camera)

while True:
        sucesso, frame = camera.read()
        if not sucesso:
            print("Error: Could not read frame.")
            break

        alertas = detectar_movimento(frame)
        gravador.atualizar(frame, alertas)

        cv2.imshow("SafeScreen.AI", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

gravador.finalizar()
camera.release()
cv2.destroyAllWindows()
