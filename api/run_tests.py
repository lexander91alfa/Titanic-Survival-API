#!/usr/bin/env python3
"""
Script para executar todos os testes da aplicação Titanic Survival API.
"""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Executa todos os testes com cobertura."""
    
    # Diretório raiz do projeto
    project_root = Path(__file__).parent
    
    # Comandos de teste
    commands = [
        # Executar testes com cobertura
        [
            "python", "-m", "pytest", 
            "tests/", 
            "-v",
            "--cov=src", 
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--tb=short"
        ],
        
        # Executar apenas testes rápidos (sem cobertura)
        # ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
    ]
    
    print("🧪 Iniciando execução dos testes...\n")
    
    for i, cmd in enumerate(commands, 1):
        print(f"📋 Executando comando {i}/{len(commands)}: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=False,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ Comando {i} executado com sucesso!\n")
            else:
                print(f"❌ Comando {i} falhou com código {result.returncode}\n")
                return result.returncode
                
        except Exception as e:
            print(f"❌ Erro ao executar comando {i}: {e}\n")
            return 1
    
    print("🎉 Todos os testes foram executados!")
    print("📊 Relatório de cobertura gerado em: htmlcov/index.html")
    return 0


def run_specific_test_file(test_file):
    """Executa um arquivo de teste específico."""
    project_root = Path(__file__).parent
    
    cmd = ["python", "-m", "pytest", f"tests/src/{test_file}", "-v"]
    
    print(f"🧪 Executando testes do arquivo: {test_file}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=False,
            text=True,
            check=False
        )
        return result.returncode
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return 1


def show_help():
    """Mostra ajuda sobre como usar o script."""
    print("""
🧪 Script de Testes - Titanic Survival API

Uso:
    python run_tests.py                    # Executa todos os testes
    python run_tests.py <arquivo_teste>    # Executa arquivo específico
    python run_tests.py --help            # Mostra esta ajuda

Exemplos:
    python run_tests.py                           # Todos os testes
    python run_tests.py test_controller.py       # Apenas testes do controller
    python run_tests.py test_predict_service.py  # Apenas testes do predict service

Arquivos de teste disponíveis:
    - test_config.py
    - test_controller.py  
    - test_error_response.py
    - test_handler.py
    - test_health_check.py
    - test_http_adapter.py
    - test_mapper.py
    - test_passenger_request.py
    - test_predict_service.py
    - test_repository.py
""")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Executar todos os testes
        sys.exit(run_tests())
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ["--help", "-h"]:
            show_help()
            sys.exit(0)
        else:
            # Executar arquivo específico
            sys.exit(run_specific_test_file(arg))
    else:
        print("❌ Muitos argumentos. Use --help para ver a ajuda.")
        sys.exit(1)
