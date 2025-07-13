# build_layer.py
import os
import shutil
import subprocess
import sys
import glob

LAYER_BUILD_DIR = "../.build/lambda_layer"
PYTHON_PACKAGE_DIR = os.path.join(LAYER_BUILD_DIR, "python") # Pasta que será compactada
SITE_PACKAGES_DIR = os.path.join(PYTHON_PACKAGE_DIR, "lib/python3.12/site-packages")
REQUIREMENTS_FILE = "../api/requirements.txt"

def clean_and_create_dir():
    """Limpa e recria o diretório de build."""
    print(">>> Limpando o diretório de build anterior...", flush=True)
    if os.path.exists(LAYER_BUILD_DIR):
        shutil.rmtree(LAYER_BUILD_DIR)
    os.makedirs(SITE_PACKAGES_DIR)

def install_dependencies():
    """Instala as dependências de produção na pasta de build."""
    print(f">>> Instalando dependências de '{REQUIREMENTS_FILE}'...", flush=True)
    command = [
        sys.executable, "-m", "pip", "install",
        "--platform", "manylinux2014_aarch64",
        "--implementation", "cp",
        "--python-version", "3.12",
        "--only-binary=:all:",
        "-r", REQUIREMENTS_FILE,
        "-t", SITE_PACKAGES_DIR
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(">>> Instalação de dependências concluída.", flush=True)
    except subprocess.CalledProcessError as e:
        print("--- ERRO: Falha ao instalar as dependências. ---", flush=True)
        print(e.stderr, flush=True)
        sys.exit(1)

def slim_package():
    """
    Remove arquivos e pastas desnecessários para reduzir o tamanho do pacote.
    """
    print(">>> Otimizando o tamanho do pacote...", flush=True)
    total_removed = 0

    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.dist-info",
        "**/tests",
        "**/test"
    ]

    for pattern in patterns_to_remove:
        for path in glob.glob(os.path.join(SITE_PACKAGES_DIR, pattern), recursive=True):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            total_removed += 1
    
    strip_command = f"find {SITE_PACKAGES_DIR} -name '*.so' -exec strip {{}} \\;"
    try:
        subprocess.run(strip_command, shell=True, check=True)
        print(">>> Arquivos binários (.so) otimizados.", flush=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("--- Aviso: Comando 'strip' não encontrado. Pulando a otimização de binários. Isso é comum no Windows.", flush=True)

    print(f">>> Otimização concluída. {total_removed} arquivos/pastas desnecessários removidos.", flush=True)


if __name__ == "__main__":
    clean_and_create_dir()
    install_dependencies()
    slim_package()
    print("\n[SUCCESS] Build da camada concluído e otimizado com sucesso!", flush=True)