import os
import shutil
import subprocess
import sys
import glob

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

LAYER_BUILD_DIR = os.path.join(PROJECT_ROOT, ".build", "lambda_layer")

PYTHON_DIR = os.path.join(LAYER_BUILD_DIR, "python")

REQUIREMENTS_FILE = os.path.join(PROJECT_ROOT, "api", "requirements.txt")
MODEL_SOURCE_DIR = os.path.join(PROJECT_ROOT, "api", "modelos")

MODEL_DEST_DIR = os.path.join(PYTHON_DIR, "modelos")


def build_layer():
    """
    Executa o processo completo de build da Lambda Layer.
    """
    print("--- Iniciando o build da Lambda Layer ---", flush=True)

    print(">>> 1/4: Limpando diretório de build anterior...", flush=True)
    if os.path.exists(LAYER_BUILD_DIR):
        shutil.rmtree(LAYER_BUILD_DIR)
    os.makedirs(PYTHON_DIR) # Cria a pasta /python
    os.makedirs(MODEL_DEST_DIR) # Cria a pasta /python/modelos

    print(f">>> 2/4: Instalando dependências de '{REQUIREMENTS_FILE}'...", flush=True)
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--platform", "manylinux2014_aarch64", # Para arquitetura arm64
            "--implementation", "cp",
            "--python-version", "3.12",
            "--only-binary=:all:",
            "-r", REQUIREMENTS_FILE,
            "-t", PYTHON_DIR  # O alvo é a pasta 'python', não 'site-packages'
        ], check=True, capture_output=True, text=True)
        print(">>> Dependências instaladas com sucesso.", flush=True)
    except subprocess.CalledProcessError as e:
        print("--- ERRO: Falha ao instalar as dependências. ---", flush=True)
        print(e.stderr, flush=True)
        sys.exit(1)

    print(f">>> 3/4: Copiando todos os modelos de '{MODEL_SOURCE_DIR}'...", flush=True)
    if not os.path.isdir(MODEL_SOURCE_DIR):
        print(f"--- ERRO: Diretório de modelos não encontrado em '{MODEL_SOURCE_DIR}' ---", flush=True)
        sys.exit(1)
    
    models_found = glob.glob(os.path.join(MODEL_SOURCE_DIR, '*'))
    if not models_found:
        print(f"--- AVISO: Nenhum modelo encontrado em '{MODEL_SOURCE_DIR}' ---", flush=True)
    else:
        for model_path in models_found:
            if os.path.isfile(model_path):
                print(f"    - Copiando {os.path.basename(model_path)}...", flush=True)
                shutil.copy2(model_path, MODEL_DEST_DIR)
        print(">>> Modelos copiados com sucesso.", flush=True)


    print(">>> 4/4: Otimizando o tamanho do pacote...", flush=True)
    slim_package(PYTHON_DIR)
    
    print("\n[SUCCESS] Build da camada concluído e otimizado com sucesso!", flush=True)


def slim_package(directory):
    """
    Remove arquivos desnecessários para reduzir o tamanho da layer.
    """
    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.dist-info"
    ]
    print("--- Removendo arquivos de metadados e cache...", flush=True)
    for pattern in patterns_to_remove:
        for path in glob.glob(os.path.join(directory, pattern), recursive=True):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    print("--- Otimizando arquivos binários (.so)...", flush=True)
    try:
        subprocess.run(f"find {directory} -name '*.so' -exec strip {{}} \\;", shell=True, check=True, capture_output=True)
        print(">>> Arquivos binários (.so) otimizados.", flush=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("--- Aviso: Comando 'strip' não encontrado ou falhou. Pulando otimização de binários.")


if __name__ == "__main__":
    build_layer()