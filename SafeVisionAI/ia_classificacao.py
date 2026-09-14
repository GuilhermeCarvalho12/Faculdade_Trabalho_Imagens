from ultralytics import YOLO

# Carrega o modelo YOLOv8 "nano" - o mais leve, ótimo para rodar em CPU e em tempo real.
# Na primeira execução ele baixa o arquivo de pesos automaticamente (~6MB).
modelo = YOLO("yolov8n.pt")

# Tradução de algumas classes do dataset COCO (em inglês) para português.
# O modelo reconhece 80 classes no total; aqui traduzimos as mais comuns
# para o contexto do projeto (pessoas, animais, objetos do dia a dia).
TRADUCAO_CLASSES = {
    "person": "pessoa",
    "cat": "gato",
    "dog": "cachorro",
    "bird": "pássaro",
    "horse": "cavalo",
    "cow": "vaca",
    "car": "carro",
    "bicycle": "bicicleta",
    "motorcycle": "moto",
    "bottle": "garrafa",
    "cell phone": "celular",
    "backpack": "mochila",
    "chair": "cadeira",
    "laptop": "notebook",
}


def classificar_frame(frame, confianca_minima=0.4):
    """
    Roda a IA sobre o frame INTEIRO da câmera e retorna todas as detecções
    encontradas, cada uma como:
        (nome_da_classe, confianca, x, y, largura, altura)

    x, y, largura, altura já vêm prontos para desenhar um retângulo com cv2.
    Retorna lista vazia se nada for reconhecido com confiança suficiente.
    """
    resultados = modelo(frame, verbose=False)

    deteccoes = []
    for resultado in resultados:
        for caixa in resultado.boxes:
            confianca = float(caixa.conf[0])
            if confianca < confianca_minima:
                continue

            classe_id = int(caixa.cls[0])
            nome_ingles = modelo.names[classe_id]
            nome_pt = TRADUCAO_CLASSES.get(nome_ingles, nome_ingles)

            # xyxy = coordenadas dos cantos da caixa (canto superior-esq. e inferior-dir.)
            x1, y1, x2, y2 = caixa.xyxy[0]
            x, y = int(x1), int(y1)
            largura, altura = int(x2 - x1), int(y2 - y1)

            deteccoes.append((nome_pt, confianca, x, y, largura, altura))

    return deteccoes
