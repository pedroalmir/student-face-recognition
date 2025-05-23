# face_api/server.py
import base64, cv2 # type: ignore
from . import face_db, utils, config
from flask import Flask, request, jsonify # type: ignore

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "online"}), 200


@app.route("/recognition", methods=["POST"])
def recognition():
    try:
        raw = request.get_data(cache=False)
        if not raw:
            return jsonify({"status":"falha","motivo":"corpo vazio"}), 400

        rgb = utils.bytes_to_rgb_uint8(raw)
        result = face_db.recognize_and_draw(rgb)

        # Redimensiona imagem de saída, se necessário
        out_img = result["annotated"]
        h, w = out_img.shape[:2]
        if w > config.MAX_OUT_WIDTH:
            new_w = config.MAX_OUT_WIDTH
            new_h = int(h * new_w / w)
            out_img = cv2.resize(out_img, (new_w, new_h),
                                 interpolation=cv2.INTER_AREA)

        # Codifica JPEG
        ok, buf = cv2.imencode(
            ".jpg", cv2.cvtColor(out_img, cv2.COLOR_RGB2BGR),
            [int(cv2.IMWRITE_JPEG_QUALITY), config.JPEG_QUALITY])
        if not ok:
            return jsonify({"status":"falha","motivo":"erro ao codificar"}), 500

        img_b64 = base64.b64encode(buf).decode("utf-8")
        payload = {
            "status": "ok",
            "faces_found": result["faces_found"],
            "unidentified": result["unidentified"],
            "identified": result["identified"],
            "image_b64": img_b64
        }
        return jsonify(payload), 200

    except Exception as exc:
        return jsonify({"status":"falha","motivo": str(exc)}), 500


if __name__ == "__main__":
    # Executar com:  python -m face_api.server
    app.run(host="0.0.0.0", port=5000, debug=True)
