# face_api/config.py
STUDENTS_DIR   = "./students_faces"  # pasta com <Nome>-<Matricula>.jpg
TOLERANCE      = 0.5                 # menor → mais estrito
UPSAMPLE       = 1                   # 0=+rápido | 1–2=+preciso
MAX_OUT_WIDTH  = 800                 # px largura máx. da imagem devolvida
RECT_THICKNESS = 4                   # px espessura dos retângulos
FONT_SCALE     = 0.75                # tamanho do texto acima do rosto
JPEG_QUALITY   = 85                  # % qualidade da imagem de saída