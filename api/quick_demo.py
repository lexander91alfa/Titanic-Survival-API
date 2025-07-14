#!/usr/bin/env python3
"""
Demonstração FINAL - apenas modelo otimizado
"""

import time
from src.services.predict_service import PredictionService

def quick_demo():
    """Demonstração rápida das melhorias"""
    print("=== SOLUÇÃO PARA CARREGAMENTO LENTO DO MODELO ===\n")
    
    PredictionService.clear_model_cache()
    
    test_data = {
        "Pclass": 1,
        "Sex": "female", 
        "Age": 25.0,
        "SibSp": 0,
        "Parch": 0,
        "Fare": 100.0,
        "Embarked": "S"
    }
    
    print("🎯 PROBLEMA:")
    print("   ❌ Modelo original demorava >30 segundos para carregar")
    print("   ❌ Carregado a cada requisição Lambda")
    
    print("\n🚀 SOLUÇÕES IMPLEMENTADAS:")
    print("   1. Controller global (evita recarga)")
    print("   2. Cache inteligente de modelo")
    print("   3. Lazy loading otimizado")
    print("   4. Modelo mais eficiente")
    print("   5. Fallback automático de formatos")
    
    print("\n📊 TESTE PRÁTICO:")
    
    # Primeiro carregamento
    print("\n1. Cold start (primeiro carregamento):")
    start = time.time()
    service1 = PredictionService(model_name="model_fast", method="pickle")
    pred1 = service1.predict(test_data)
    cold_time = time.time() - start
    print(f"   ⏱️  {cold_time:.4f}s")
    print(f"   🎯 Predição: {pred1:.4f}")
    
    # Cache hit
    print("\n2. Warm start (cache hit):")
    start = time.time()
    service2 = PredictionService(model_name="model_fast", method="pickle")
    pred2 = service2.predict(test_data)
    warm_time = time.time() - start
    print(f"   ⏱️  {warm_time:.4f}s")
    print(f"   🎯 Predição: {pred2:.4f}")
    
    # Reutilização
    print("\n3. Reutilização da instância:")
    start = time.time()
    pred3 = service2.predict(test_data)
    reuse_time = time.time() - start
    print(f"   ⏱️  {reuse_time:.4f}s")
    print(f"   🎯 Predição: {pred3:.4f}")
    
    print("\n" + "="*50)
    print("✅ RESULTADO:")
    print("="*50)
    print(f"🚀 Cold start: {cold_time:.4f}s (vs >30s antes)")
    print(f"⚡ Warm start: {warm_time:.4f}s")
    print(f"💨 Reutilização: {reuse_time:.4f}s")
    
    improvement = ((30 - cold_time) / 30) * 100
    print(f"📈 Melhoria: {improvement:.1f}% mais rápido!")
    
    print(f"\n💡 PARA USAR EM PRODUÇÃO:")
    print(f"   • Substitua 'model' por 'model_fast'")
    print(f"   • Use method='pickle'")
    print(f"   • Controller já está otimizado")
    
    print(f"\n🎉 PROBLEMA RESOLVIDO!")
    print(f"   De >30s para <{cold_time:.1f}s = {improvement:.0f}% mais rápido!")

if __name__ == "__main__":
    quick_demo()
