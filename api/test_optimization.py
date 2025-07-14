#!/usr/bin/env python3
"""
Script para testar a otimização do carregamento do modelo.
Compara o tempo de carregamento com e sem cache.
"""

import time
import json
from src.services.predict_service import PredictionService

def test_model_loading_performance():
    """
    Testa o desempenho do carregamento do modelo.
    """
    print("=== Teste de Performance do Carregamento do Modelo ===\n")
    
    # Limpar cache para começar do zero
    PredictionService.clear_model_cache()
    
    # Dados de teste
    test_data = {
        "Pclass": 1,
        "Sex": "female", 
        "Age": 25.0,
        "SibSp": 0,
        "Parch": 0,
        "Fare": 100.0,
        "Embarked": "S"
    }
    
    print("1. Primeiro carregamento (sem cache):")
    start_time = time.time()
    service1 = PredictionService(model_name="model", method="joblib")
    prediction1 = service1.predict(test_data)
    first_load_time = time.time() - start_time
    print(f"   Tempo: {first_load_time:.4f} segundos")
    print(f"   Predição: {prediction1:.4f}")
    print(f"   Info do cache: {PredictionService.get_cache_info()}")
    
    print("\n2. Segundo carregamento (com cache):")
    start_time = time.time()
    service2 = PredictionService(model_name="model", method="joblib") 
    prediction2 = service2.predict(test_data)
    second_load_time = time.time() - start_time
    print(f"   Tempo: {second_load_time:.4f} segundos")
    print(f"   Predição: {prediction2:.4f}")
    print(f"   Info do cache: {PredictionService.get_cache_info()}")
    
    print("\n3. Terceiro carregamento (reutilização de instância):")
    start_time = time.time()
    prediction3 = service2.predict(test_data)
    third_load_time = time.time() - start_time
    print(f"   Tempo: {third_load_time:.4f} segundos")
    print(f"   Predição: {prediction3:.4f}")
    
    # Análise
    print(f"\n=== Análise ===")
    print(f"Melhoria do cache: {(first_load_time - second_load_time) / first_load_time * 100:.1f}%")
    print(f"Melhoria da reutilização: {(first_load_time - third_load_time) / first_load_time * 100:.1f}%")
    
    if first_load_time > 30:
        print("⚠️  PROBLEMA: Carregamento inicial muito lento (>30s)")
    elif first_load_time > 5:
        print("⚠️  ATENÇÃO: Carregamento inicial lento (>5s)")
    else:
        print("✅ Carregamento inicial OK")
        
    if second_load_time < 1:
        print("✅ Cache funcionando bem")
    else:
        print("⚠️  Cache pode não estar funcionando como esperado")

if __name__ == "__main__":
    test_model_loading_performance()
