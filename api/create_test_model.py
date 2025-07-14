#!/usr/bin/env python3
"""
Cria um modelo de teste menor para comparação
"""

import joblib
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

def create_test_model():
    """Cria um modelo menor para comparação"""
    print("=== Criando Modelo de Teste ===")
    
    # Dados sintéticos simples
    X, y = make_classification(n_samples=100, n_features=8, random_state=42)
    
    # Modelo pequeno
    rf_small = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=42)
    rf_small.fit(X, y)
    
    # Salvar
    joblib.dump(rf_small, 'models/test_model.joblib')
    with open('models/test_model.pkl', 'wb') as f:
        pickle.dump(rf_small, f)
    
    print("✅ Modelo de teste criado")
    
    # Testar carregamento
    import time
    
    print("\n=== Teste de Carregamento do Modelo Pequeno ===")
    
    start_time = time.time()
    test_model = joblib.load('models/test_model.joblib')
    load_time = time.time() - start_time
    print(f"Joblib: {load_time:.4f}s")
    
    start_time = time.time()
    with open('models/test_model.pkl', 'rb') as f:
        test_model = pickle.load(f)
    load_time = time.time() - start_time
    print(f"Pickle: {load_time:.4f}s")

if __name__ == "__main__":
    create_test_model()
