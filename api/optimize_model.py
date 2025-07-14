#!/usr/bin/env python3
"""
Otimiza o modelo existente para carregamento mais rápido
"""

import joblib
import pickle
import time
import os
from sklearn.ensemble import RandomForestClassifier

def optimize_existing_model():
    """Otimiza o modelo existente"""
    print("=== Otimização do Modelo Existente ===")
    
    # Carregar modelo original
    print("1. Carregando modelo original...")
    original_path = "models/model.joblib"
    
    start_time = time.time()
    try:
        original_model = joblib.load(original_path)
        load_time = time.time() - start_time
        print(f"   ✅ Carregado em {load_time:.4f}s")
        print(f"   Tipo: {type(original_model)}")
        print(f"   N estimators: {getattr(original_model, 'n_estimators', 'N/A')}")
        print(f"   Max depth: {getattr(original_model, 'max_depth', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # Criar versão otimizada
    print("\n2. Criando versão otimizada...")
    
    # Opção 1: Reduzir número de estimadores mantendo performance similar
    if hasattr(original_model, 'n_estimators') and original_model.n_estimators > 50:
        optimized_model = RandomForestClassifier(
            n_estimators=20,  # Reduzir de 100 para 20
            max_depth=original_model.max_depth,
            random_state=42,
            oob_score=True
        )
        
        # Precisaria retreinar com dados, mas vamos salvar uma versão comprimida do original
        print("   Salvando modelo original com compressão...")
        
        # Salvar com compressão
        joblib.dump(original_model, 'models/model_optimized.joblib', compress=3)
        
        # Salvar também versão pickle comprimida
        import gzip
        with gzip.open('models/model_compressed.pkl.gz', 'wb') as f:
            pickle.dump(original_model, f)
        
        print("   ✅ Versões otimizadas salvas")
    
    # Testar carregamento das versões otimizadas
    print("\n3. Testando versões otimizadas...")
    
    # Teste versão comprimida joblib
    print("   Testando joblib comprimido...")
    start_time = time.time()
    model_compressed = joblib.load('models/model_optimized.joblib')
    compressed_time = time.time() - start_time
    print(f"   Tempo: {compressed_time:.4f}s")
    
    # Teste versão gzip+pickle
    print("   Testando gzip+pickle...")
    start_time = time.time()
    import gzip
    with gzip.open('models/model_compressed.pkl.gz', 'rb') as f:
        model_gzip = pickle.load(f)
    gzip_time = time.time() - start_time
    print(f"   Tempo: {gzip_time:.4f}s")
    
    # Comparar tamanhos
    print("\n4. Comparação de tamanhos:")
    files = [
        ('Original joblib', 'models/model.joblib'),
        ('Original pickle', 'models/model.pkl'),
        ('Joblib comprimido', 'models/model_optimized.joblib'),
        ('Gzip+pickle', 'models/model_compressed.pkl.gz')
    ]
    
    for name, path in files:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   {name}: {size:,} bytes ({size/(1024*1024):.2f} MB)")

if __name__ == "__main__":
    optimize_existing_model()
