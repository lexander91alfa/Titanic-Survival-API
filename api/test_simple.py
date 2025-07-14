#!/usr/bin/env python3
"""
Teste simples de carregamento do modelo
"""

import time
import joblib
import os

def test_simple_load():
    """Teste simples de carregamento direto"""
    print("=== Teste Simples de Carregamento ===")
    
    model_path = os.path.join("models", "model")
    
    print(f"1. Testando carregamento direto com joblib...")
    print(f"   Caminho: {model_path}.joblib")
    
    start_time = time.time()
    try:
        with open(f"{model_path}.joblib", "rb") as f:
            model = joblib.load(f)
        load_time = time.time() - start_time
        print(f"   ✅ Sucesso! Tempo: {load_time:.4f} segundos")
        print(f"   Tipo do modelo: {type(model)}")
        print(f"   Tem predict_proba: {hasattr(model, 'predict_proba')}")
        
        # Teste rápido de predição
        if hasattr(model, 'predict_proba'):
            # Dados de teste baseados no preprocessing
            import numpy as np
            test_features = np.array([[1, 25.0, 0, 0, 100.0, 0, 0, 1]])  # Pclass=1, Age=25, etc.
            pred_time_start = time.time()
            prediction = model.predict_proba(test_features)
            pred_time = time.time() - pred_time_start
            print(f"   Predição: {prediction[0][1]:.4f} (tempo: {pred_time:.4f}s)")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        
    print(f"\n2. Informações do arquivo:")
    file_path = f"{model_path}.joblib"
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"   Tamanho: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    else:
        print(f"   ❌ Arquivo não encontrado: {file_path}")

if __name__ == "__main__":
    test_simple_load()
