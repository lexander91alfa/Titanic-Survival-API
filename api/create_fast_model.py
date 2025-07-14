#!/usr/bin/env python3
"""
Cria uma versão otimizada do modelo Titanic
"""

import pandas as pd
import joblib
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import numpy as np

def create_optimized_model():
    """Cria modelo otimizado para performance"""
    print("=== Criando Modelo Otimizado ===")
    
    # Carregar dados
    print("1. Carregando dados do Titanic...")
    df = pd.read_csv("http://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    
    # Preprocessing simples
    print("2. Preprocessando dados...")
    # Usar apenas features mais importantes para modelo mais simples
    features = ['Pclass', 'Age', 'SibSp', 'Parch', 'Fare', 'Sex', 'Embarked']
    
    # Preparar dados
    df_prep = df[features + ['Survived']].copy()
    
    # Tratar valores ausentes
    df_prep['Age'].fillna(df_prep['Age'].median(), inplace=True)
    df_prep['Fare'].fillna(df_prep['Fare'].median(), inplace=True)
    df_prep['Embarked'].fillna(df_prep['Embarked'].mode()[0], inplace=True)
    
    # Encoding
    df_prep = pd.get_dummies(df_prep, columns=['Sex', 'Embarked'], drop_first=True)
    
    # Separar features e target
    X = df_prep.drop('Survived', axis=1)
    y = df_prep['Survived']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("3. Treinando modelos...")
    
    # Modelo 1: RandomForest pequeno
    print("   - RandomForest otimizado...")
    rf_small = RandomForestClassifier(
        n_estimators=10,  # Reduzido de 100 para 10
        max_depth=4,      # Limitado para evitar overfitting
        random_state=42,
        n_jobs=-1
    )
    rf_small.fit(X_train, y_train)
    rf_pred = rf_small.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    rf_auc = roc_auc_score(y_test, rf_small.predict_proba(X_test)[:, 1])
    
    # Modelo 2: Logistic Regression (ainda mais rápido)
    print("   - Logistic Regression...")
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)
    lr_auc = roc_auc_score(y_test, lr.predict_proba(X_test)[:, 1])
    
    print(f"\n4. Performance dos modelos:")
    print(f"   RandomForest (10 est): Acc={rf_acc:.4f}, AUC={rf_auc:.4f}")
    print(f"   Logistic Regression:   Acc={lr_acc:.4f}, AUC={lr_auc:.4f}")
    
    # Escolher modelo baseado na performance
    if abs(rf_auc - lr_auc) < 0.05:  # Se performance similar, usar LR (mais rápido)
        best_model = lr
        model_name = "LogisticRegression"
        print(f"   ✅ Selecionado: Logistic Regression (performance similar, mais rápido)")
    else:
        best_model = rf_small
        model_name = "RandomForest"
        print(f"   ✅ Selecionado: RandomForest (melhor performance)")
    
    # Salvar modelo otimizado
    print(f"\n5. Salvando modelo otimizado...")
    joblib.dump(best_model, 'models/model_fast.joblib')
    with open('models/model_fast.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    
    print(f"   ✅ Modelo salvo como model_fast.*")
    print(f"   📊 Features esperadas: {list(X.columns)}")
    
    # Testar carregamento
    print(f"\n6. Testando carregamento...")
    import time
    
    start_time = time.time()
    model_test = joblib.load('models/model_fast.joblib')
    joblib_time = time.time() - start_time
    
    start_time = time.time()
    with open('models/model_fast.pkl', 'rb') as f:
        model_test = pickle.load(f)
    pickle_time = time.time() - start_time
    
    print(f"   Joblib: {joblib_time:.4f}s")
    print(f"   Pickle: {pickle_time:.4f}s")
    
    # Teste de predição
    test_sample = X.iloc[0:1]
    pred = model_test.predict_proba(test_sample)[0][1]
    print(f"   Teste predição: {pred:.4f}")
    
    return best_model, model_name

if __name__ == "__main__":
    create_optimized_model()
