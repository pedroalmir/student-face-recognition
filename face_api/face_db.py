# face_api/face_db.py
from . import utils, config
import os, face_recognition, numpy as np, cv2, base64 # type: ignore
from typing import List, Dict, Tuple

# -------- Carga dos rostos conhecidos ---------------------------------
def _load_known_faces() -> Tuple[List[np.ndarray], List[Dict[str, str]]]:
    encs, meta = [], []
    folder = config.STUDENTS_DIR
    if not os.path.isdir(folder):
        raise FileNotFoundError(folder)

    for fname in os.listdir(folder):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        try:
            camel, matric = os.path.splitext(fname)[0].split("-", 1)
        except ValueError:
            print(f"[WARN] nome fora do padrão: {fname}")
            continue

        raw = open(os.path.join(folder, fname), "rb").read()
        rgb = utils.bytes_to_rgb_uint8(raw)
        enc = face_recognition.face_encodings(rgb)
        if enc:
            encs.append(enc[0])
            meta.append({"name": utils.camel_to_words(camel),
                         "matricula": matric})
            print(f"[OK] {camel} ({matric})")
        else:
            print(f"[WARN] nenhum rosto em {fname}")
    if not encs:
        raise RuntimeError("nenhum rosto válido encontrado")
    return encs, meta


# Mantém em memória (carrega uma vez no import)
KNOWN_ENCODINGS, KNOWN_META = _load_known_faces()
print(f"[INFO] {len(KNOWN_ENCODINGS)} rostos no banco.")

# -------- Função principal de reconhecimento --------------------------
def recognize_and_draw(rgb_img: np.ndarray) -> Dict:
    """
    Recebe ndarray RGB uint8, detecta rostos, compara com base,
    devolve dicionário contendo:
       'faces_found', 'unidentified', 'identified', 'annotated' (ndarray RGB)
    """
    locs = face_recognition.face_locations(
        rgb_img, config.UPSAMPLE, model="hog")
    encs = face_recognition.face_encodings(rgb_img, locs)

    identified, unidentified = [], 0
    draw = rgb_img.copy()

    for (top, right, bottom, left), enc in zip(locs, encs):
        matches = face_recognition.compare_faces(
            KNOWN_ENCODINGS, enc, config.TOLERANCE)
        name_txt = "Não identificado"
        color    = (0, 0, 255)  # vermelho BGR depois

        if True in matches:
            dists = face_recognition.face_distance(KNOWN_ENCODINGS, enc)
            idx   = int(np.argmin(dists))
            if matches[idx]:
                meta      = KNOWN_META[idx]
                identified.append(meta)
                name_txt  = meta["name"]
                color     = (0, 255, 0)          # verde
        else:
            unidentified += 1

        # -- Desenho ----------------------------------------------------
        cv2.rectangle(draw, (left, top), (right, bottom),
                      color, config.RECT_THICKNESS)
        font = cv2.FONT_HERSHEY_DUPLEX
        stroke = int(config.RECT_THICKNESS * 1.5)
        # contorno preto
        cv2.putText(draw, name_txt, (left, top - 10),
                    font, config.FONT_SCALE, (0,0,0), stroke, cv2.LINE_AA)
        # preenchimento branco
        cv2.putText(draw, name_txt, (left, top - 10),
                    font, config.FONT_SCALE, (255,255,255),
                    config.RECT_THICKNESS, cv2.LINE_AA)

    return {
        "faces_found": len(locs),
        "unidentified": unidentified,
        "identified": identified,
        "annotated": draw
    }
