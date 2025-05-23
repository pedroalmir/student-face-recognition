"""
recognition_api.py   –   v1.4  (parâmetros visuais ajustáveis)
────────────────────────────────────────────────────────────────
• GET  /            → {"status": "online"}
• POST /recognition → JSON + imagem anotada em base64
"""

import os, re, base64, cv2, numpy as np, face_recognition
from flask import Flask, request, jsonify
from typing import List, Dict

# ────────── CONFIGURAÇÕES ────────────────────────────────────
STUDENTS_DIR     = "./students_faces"
TOLERANCE        = 0.5           # 0.4–0.6 comum
UPSAMPLE         = 1             # 0 = +rápido | 1–2 = +sensível

MAX_OUT_WIDTH    = 400           # px – largura máx. da imagem devolvida
RECT_THICKNESS   = 6             # px – espessura dos retângulos
FONT_SCALE       = 1.0           # escala da fonte (≈ altura em px/30)

# ────────── FUNÇÕES AUXILIARES ───────────────────────────────
def camel_to_words(txt: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", txt).strip()

def bytes_to_rgb_uint8(raw: bytes) -> np.ndarray:
    """Converte bytes JPG/PNG em ndarray RGB uint8 (h, w, 3)."""
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("imagem inválida")

    if img.dtype != np.uint8:                    # 16-bit → 8-bit
        img = (img / 256).astype(np.uint8)

    if len(img.shape) == 2:                      # Gray  → RGB
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4:                      # BGRA → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    else:                                        # BGR  → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

# ────────── CARREGA ROSTOS CONHECIDOS ────────────────────────
def load_known_faces(folder: str):
    encs, meta = [], []
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

        rgb = bytes_to_rgb_uint8(open(os.path.join(folder, fname), "rb").read())
        enc = face_recognition.face_encodings(rgb)
        if not enc:
            print(f"[WARN] nenhum rosto em {fname}")
            continue

        encs.append(enc[0])
        meta.append({"name": camel_to_words(camel), "matricula": matric})
        print(f"[OK] {camel} ({matric})")

    if not encs:
        raise RuntimeError("nenhum rosto válido encontrado")
    return encs, meta

KNOWN_ENCODINGS, KNOWN_META = load_known_faces(STUDENTS_DIR)
print(f"[INFO] {len(KNOWN_ENCODINGS)} rostos conhecidos carregados.")

# ────────── FLASK APP ───────────────────────────────────────
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "online"}), 200

@app.route("/recognition", methods=["POST"])
def recognition():
    try:
        raw = request.get_data()
        if not raw:
            return jsonify({"status":"falha","motivo":"corpo vazio"}), 400

        rgb = bytes_to_rgb_uint8(raw)

        locs = face_recognition.face_locations(rgb, UPSAMPLE, model="hog")
        encs = face_recognition.face_encodings(rgb, locs)

        identified, unidentified = [], 0
        draw = rgb.copy()

        for (top, right, bottom, left), enc in zip(locs, encs):
            matches = face_recognition.compare_faces(KNOWN_ENCODINGS, enc, TOLERANCE)
            name_txt = "Não identificado"
            color    = (0, 0, 255)                     # vermelho

            if True in matches:
                dists = face_recognition.face_distance(KNOWN_ENCODINGS, enc)
                idx   = int(np.argmin(dists))
                if matches[idx]:
                    meta = KNOWN_META[idx]
                    name_txt = meta["name"]
                    identified.append(meta)
                    color = (0, 255, 0)                # verde
            else:
                unidentified += 1

            # ─── Desenho ────────────────────────────
            cv2.rectangle(draw, (left, top), (right, bottom),
                          color, RECT_THICKNESS)

            font = cv2.FONT_HERSHEY_DUPLEX
            # contorno preto
            cv2.putText(draw, name_txt, (left, top - 10),
                        font, FONT_SCALE, (0,0,0), int(RECT_THICKNESS*1.5),
                        cv2.LINE_AA)
            # preenchimento branco
            cv2.putText(draw, name_txt, (left, top - 10),
                        font, FONT_SCALE, (255,255,255), RECT_THICKNESS,
                        cv2.LINE_AA)

        # ─── Redimensiona saída ─────────────────────
        h, w = draw.shape[:2]
        if w > MAX_OUT_WIDTH:
            new_w = MAX_OUT_WIDTH
            new_h = int(h * new_w / w)
            draw  = cv2.resize(draw, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # codifica JPEG (qualidade 85 %)
        ok, buf = cv2.imencode(".jpg",
                               cv2.cvtColor(draw, cv2.COLOR_RGB2BGR),
                               [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not ok:
            return jsonify({"status":"falha","motivo":"erro ao codificar"}), 500

        img_b64 = base64.b64encode(buf).decode("utf-8")

        return jsonify({
            "status": "ok",
            "faces_found": len(locs),
            "unidentified": unidentified,
            "identified": identified,
            "image_b64": img_b64
        }), 200

    except Exception as exc:
        return jsonify({"status":"falha","motivo": str(exc)}), 500

# ────────── MAIN ────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
