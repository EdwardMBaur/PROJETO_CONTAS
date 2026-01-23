import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(BASE_DIR, 'golden-pillar-483902-d4-4862974bc3e8.json')

PATH_CREDENTIALS = JSON_PATH 

if not os.path.exists(PATH_CREDENTIALS):
    print(f"ERRO CRÍTICO: Arquivo não encontrado no caminho: {PATH_CREDENTIALS}")

SHEET = "1zayT0T0KhMy2fG1lVtEIaWeTv-nA4HchfkrCkePobgY"