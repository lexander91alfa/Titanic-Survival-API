# build_layer.py
import os
import shutil
import subprocess
import sys

# --- Configuração ---
# A AWS Lambda procura as bibliotecas neste caminho exato dentro do .zip
LAYER_BUILD_DIR = "../.build/lambda_layer/python/lib/python3.12/site-packages"
REQUIREMENTS_FILE = "../api/requirements.txt"

def build_layer():
    """Cria o pacote da camada com as dependências."""
    print(">>> Iniciando a construção da camada de dependências...")
    
    # Limpa e recria o diretório de build
    if os.path.exists(".build/lambda_layer"):
        shutil.rmtree(".build/lambda_layer")
    os.makedirs(LAYER_BUILD_DIR)
    
    print(f">>> Instalando dependências de '{REQUIREMENTS_FILE}' em '{LAYER_BUILD_DIR}'...")
    
    command = [
        sys.executable,
        "-m", "pip", "install",
        "--platform", "manylinux2014_aarch64", 
        "--implementation", "cp",
        "--python-version", "3.12",
        "--only-binary=:all:",
        "-r", REQUIREMENTS_FILE,
        "-t", LAYER_BUILD_DIR
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(">>> Instalação de dependências para a camada concluída.")
    except subprocess.CalledProcessError as e:
        print("--- ERRO: Falha ao instalar as dependências da camada. ---")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    build_layer()