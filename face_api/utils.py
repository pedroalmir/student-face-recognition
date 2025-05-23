# face_api/utils.py
import re, cv2, numpy as np # type: ignore

def camel_to_words(txt: str) -> str:
    """Converte CamelCase → 'Camel Case'."""
    return re.sub(r"(?<!^)(?=[A-Z])", " ", txt).strip()

def bytes_to_rgb_uint8(raw: bytes) -> np.ndarray:
    """
    Converte bytes JPG/PNG (até 16-bit, 1/3/4 canais) em ndarray RGB uint8.
    Lança ValueError se não decodificar.
    """
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("imagem inválida")

    if img.dtype != np.uint8:                 # 16-bit → 8-bit
        img = (img / 256).astype(np.uint8)

    if len(img.shape) == 2:                   # Gray  → RGB
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4:                   # BGRA → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    else:                                     # BGR  → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
