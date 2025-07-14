#!/usr/bin/env python3
"""
Script para demonstrar as otimizações implementadas
"""

import time
import os
from src.services.predict_service import PredictionService

def demonstrate_optimizations():
    """
    Demonstra as otimizações implementadas no carregamento do modelo
    """
    print("=== Demonstração das Otimizações ===\n")
    
    # Limpar cache
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
    
    print("🚀 OTIMIZAÇÃO 1: Movendo inicialização para fora da função Lambda")
    print("   ✅ Implementado: PassengerController instanciado globalmente")
    print("   📈 Benefício: Modelo carregado apenas no cold start, não a cada requisição")
    
    print("\n🚀 OTIMIZAÇÃO 2: Lazy Loading + Cache de Modelo")
    print("   ✅ Implementado: Cache em nível de classe para reutilização")
    print("   📈 Benefício: Instâncias subsequentes reutilizam modelo já carregado")
    
    print("\n🚀 OTIMIZAÇÃO 3: Fallback inteligente de formatos")
    print("   ✅ Implementado: Tentativa automática pickle -> joblib")
    print("   📈 Benefício: Usa o formato mais rápido disponível")
    
    print("\n📊 TESTE PRÁTICO:")
    
    # Teste 1: Primeiro carregamento
    print("\n1. Primeiro carregamento (cold start):")
    start_time = time.time()
    service1 = PredictionService(model_name="model", method="pickle")
    prediction1 = service1.predict(test_data)
    first_time = time.time() - start_time
    print(f"   ⏱️  Tempo total: {first_time:.4f}s")
    print(f"   🎯 Predição: {prediction1:.4f}")
    
    # Teste 2: Segundo serviço (cache hit)
    print("\n2. Segunda instância (cache hit):")
    start_time = time.time()
    service2 = PredictionService(model_name="model", method="pickle")
    prediction2 = service2.predict(test_data)
    second_time = time.time() - start_time
    print(f"   ⏱️  Tempo total: {second_time:.4f}s")
    print(f"   🎯 Predição: {prediction2:.4f}")
    
    # Teste 3: Reutilização da mesma instância
    print("\n3. Reutilização da instância:")
    start_time = time.time()
    prediction3 = service2.predict(test_data)
    third_time = time.time() - start_time
    print(f"   ⏱️  Tempo total: {third_time:.4f}s")
    print(f"   🎯 Predição: {prediction3:.4f}")
    
    # Análise
    print(f"\n📈 ANÁLISE DE PERFORMANCE:")
    improvement_cache = ((first_time - second_time) / first_time) * 100
    improvement_reuse = ((first_time - third_time) / first_time) * 100
    
    print(f"   💡 Melhoria com cache: {improvement_cache:.1f}%")
    print(f"   💡 Melhoria com reutilização: {improvement_reuse:.1f}%")
    
    if first_time > 30:
        print("   ⚠️  ALERTA: Primeiro carregamento ainda > 30s")
        print("   💡 RECOMENDAÇÃO: Considere treinar modelo menor ou usar modelo pré-compilado")
    elif first_time > 5:
        print("   ⚠️  ATENÇÃO: Primeiro carregamento > 5s")
        print("   💡 SUGESTÃO: Modelo pode ser otimizado ainda mais")
    else:
        print("   ✅ Performance do primeiro carregamento aceitável")
    
    if second_time < 1:
        print("   ✅ Cache funcionando excelentemente")
    elif second_time < 5:
        print("   ✅ Cache funcionando bem")
    else:
        print("   ⚠️  Cache pode precisar de ajustes")
    
    print(f"\n📋 RESUMO DAS OTIMIZAÇÕES IMPLEMENTADAS:")
    print("   1. ✅ Controller global (evita recarga a cada requisição)")
    print("   2. ✅ Lazy loading (modelo carregado só quando necessário)")
    print("   3. ✅ Cache de classe (reutilização entre instâncias)")
    print("   4. ✅ Fallback inteligente (tenta formato mais rápido primeiro)")
    print("   5. ✅ Logs detalhados (para debugging de performance)")
    
    print(f"\n💡 PARA AMBIENTE LAMBDA:")
    print("   • Cold start: ~{:.2f}s (primeira requisição após deploy)".format(first_time))
    print("   • Warm start: ~{:.2f}s (requisições subsequentes)".format(max(second_time, third_time)))
    print("   • Economia de tempo por requisição: {:.2f}s".format(first_time - min(second_time, third_time)))

if __name__ == "__main__":
    demonstrate_optimizations()
