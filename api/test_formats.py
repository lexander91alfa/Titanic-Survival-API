#!/usr/bin/env python3
"""
Teste de comparação entre joblib e pickle
"""

import time
import joblib
import pickle
import os

def test_both_formats():
    """Testa ambos os formatos"""
    print("=== Comparação Joblib vs Pickle ===")
    
    model_path = os.path.join("models", "model")
    
    # Teste joblib
    print("1. Testando Joblib...")
    joblib_path = f"{model_path}.joblib"
    if os.path.exists(joblib_path):
        size = os.path.getsize(joblib_path)
        print(f"   Tamanho: {size:,} bytes")
        
        start_time = time.time()
        try:
            with open(joblib_path, "rb") as f:
                model_joblib = joblib.load(f)
            joblib_time = time.time() - start_time
            print(f"   ✅ Carregado em {joblib_time:.4f}s")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            joblib_time = None
    else:
        print("   ❌ Arquivo não encontrado")
        joblib_time = None
    
    # Teste pickle
    print("\n2. Testando Pickle...")
    pickle_path = f"{model_path}.pkl"
    if os.path.exists(pickle_path):
        size = os.path.getsize(pickle_path)
        print(f"   Tamanho: {size:,} bytes")
        
        start_time = time.time()
        try:
            with open(pickle_path, "rb") as f:
                model_pickle = pickle.load(f)
            pickle_time = time.time() - start_time
            print(f"   ✅ Carregado em {pickle_time:.4f}s")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            pickle_time = None
    else:
        print("   ❌ Arquivo não encontrado")
        pickle_time = None
    
    # Comparação
    if joblib_time and pickle_time:
        print(f"\n3. Comparação:")
        faster = "Pickle" if pickle_time < joblib_time else "Joblib"
        difference = abs(joblib_time - pickle_time)
        print(f"   {faster} é mais rápido por {difference:.4f}s")
        
        if min(joblib_time, pickle_time) > 30:
            print("   ⚠️  PROBLEMA: Ambos são muito lentos (>30s)")
        elif min(joblib_time, pickle_time) > 5:
            print("   ⚠️  Ambos são lentos (>5s)")
        else:
            print("   ✅ Pelo menos um é rápido")

if __name__ == "__main__":
    test_both_formats()
