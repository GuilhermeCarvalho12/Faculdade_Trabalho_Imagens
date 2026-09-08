import cv2
from detectmov import detectar_movimento

# Initialize the camera and verify if it opened successfully
camera =  cv2.VideoCapture(0) 
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
        sucesso, frame = camera.read()
        detectar_movimento(frame)
        if not sucesso:
            print("Error: Could not read frame.")
            break
        cv2.imshow("SafeScreen.AI", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
camera.release()
cv2.destroyAllWindows()