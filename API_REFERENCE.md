# 🚀 API Reference - Titanic Survival Prediction

## Base URL
```
https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1
```

## Autenticação
Todas as requisições devem incluir uma API Key no header:
```http
x-api-key: your-api-key-here
```

---

## 📝 Endpoints

### 1. Criar Predição de Sobrevivência

**Endpoint:** `POST /sobreviventes`

Cria uma nova predição de sobrevivência para um ou múltiplos passageiros.

#### Request

**Headers:**
```http
Content-Type: application/json
x-api-key: your-api-key
```

**Body (Passageiro Único):**
```json
{
  "PassengerId": "passenger_001",
  "Pclass": 1,
  "Sex": "female",
  "Age": 29.0,
  "SibSp": 0,
  "Parch": 0,
  "Fare": 211.3375,
  "Embarked": "S"
}
```

**Body (Múltiplos Passageiros):**
```json
[
  {
    "PassengerId": "passenger_001",
    "Pclass": 1,
    "Sex": "female",
    "Age": 29.0,
    "SibSp": 0,
    "Parch": 0,
    "Fare": 211.3375,
    "Embarked": "S"
  },
  {
    "PassengerId": "passenger_002",
    "Pclass": 3,
    "Sex": "male",
    "Age": 22.0,
    "SibSp": 1,
    "Parch": 0,
    "Fare": 7.25,
    "Embarked": "S"
  }
]
```

#### Response

**Status:** `201 Created`

**Body (Passageiro Único):**
```json
{
  "PassengerId": "passenger_001",
  "probability": 0.9124
}
```

**Body (Múltiplos Passageiros):**
```json
[
  {
    "id": "generated-uuid-1",
    "PassengerId": "passenger_001",
    "probability": 0.9124,
    "passenger_data": {
      "Pclass": 1,
      "Sex": "female",
      "Age": 29.0,
      "SibSp": 0,
      "Parch": 0,
      "Fare": 211.3375,
      "Embarked": "S"
    },
    "created_at": "2025-01-14T10:30:00Z"
  },
  {
    "id": "generated-uuid-2",
    "PassengerId": "passenger_002",
    "probability": 0.1234,
    "passenger_data": {
      "Pclass": 3,
      "Sex": "male",
      "Age": 22.0,
      "SibSp": 1,
      "Parch": 0,
      "Fare": 7.25,
      "Embarked": "S"
    },
    "created_at": "2025-01-14T10:30:15Z"
  }
]
```

---

### 2. Listar Todas as Predições

**Endpoint:** `GET /sobreviventes`

Retorna todas as predições armazenadas no sistema.

#### Request

**Headers:**
```http
x-api-key: your-api-key
```

#### Response

**Status:** `200 OK`

**Body:**
```json
[
  {
    "id": "uuid-1234-5678",
    "PassengerId": "passenger_001",
    "probability": 0.9124,
    "passenger_data": {
      "Pclass": 1,
      "Sex": "female",
      "Age": 29.0,
      "SibSp": 0,
      "Parch": 0,
      "Fare": 211.3375,
      "Embarked": "S"
    },
    "created_at": "2025-01-14T10:30:00Z"
  },
  {
    "id": "uuid-9876-5432",
    "PassengerId": "passenger_002",
    "probability": 0.1234,
    "passenger_data": {
      "Pclass": 3,
      "Sex": "male",
      "Age": 22.0,
      "SibSp": 1,
      "Parch": 0,
      "Fare": 7.25,
      "Embarked": "S"
    },
    "created_at": "2025-01-14T10:30:15Z"
  }
]
```

---

### 3. Buscar Predição por ID

**Endpoint:** `GET /sobreviventes/{id}`

Retorna uma predição específica pelo seu ID único.

#### Request

**Headers:**
```http
x-api-key: your-api-key
```

**Path Parameters:**
- `id` (string): ID único da predição

#### Response

**Status:** `200 OK`

**Body:**
```json
{
  "id": "uuid-1234-5678",
  "PassengerId": "passenger_001",
  "probability": 0.9124,
  "passenger_data": {
    "Pclass": 1,
    "Sex": "female",
    "Age": 29.0,
    "SibSp": 0,
    "Parch": 0,
    "Fare": 211.3375,
    "Embarked": "S"
  },
  "created_at": "2025-01-14T10:30:00Z"
}
```

---

### 4. Deletar Predição

**Endpoint:** `DELETE /sobreviventes/{id}`

Remove uma predição específica do sistema.

#### Request

**Headers:**
```http
x-api-key: your-api-key
```

**Path Parameters:**
- `id` (string): ID único da predição

#### Response

**Status:** `200 OK`

**Body:**
```json
{
  "message": "Passageiro deletado com sucesso",
  "deleted_id": "uuid-1234-5678"
}
```

---

### 5. Health Check

**Endpoint:** `GET /health`

Verifica o status de saúde da API e seus componentes.

#### Request

**Headers:**
```http
x-api-key: your-api-key
```

#### Response

**Status:** `200 OK` (Sistema saudável) ou `503 Service Unavailable` (Sistema com problemas)

**Body:**
```json
{
  "overall_status": "healthy",
  "services": {
    "lambda": "healthy",
    "dynamodb": "healthy",
    "ml_model": "healthy"
  },
  "timestamp": "2025-01-14T10:30:00Z",
  "version": "1.0.0"
}
```

---

## 📊 Códigos de Status HTTP

| Status Code | Descrição |
|-------------|-----------|
| `200` | OK - Requisição bem-sucedida |
| `201` | Created - Recurso criado com sucesso |
| `400` | Bad Request - Dados inválidos na requisição |
| `401` | Unauthorized - API Key inválida ou ausente |
| `404` | Not Found - Recurso não encontrado |
| `405` | Method Not Allowed - Método HTTP não permitido |
| `429` | Too Many Requests - Rate limit excedido |
| `500` | Internal Server Error - Erro interno do servidor |
| `503` | Service Unavailable - Serviço temporariamente indisponível |

---

## ❌ Tratamento de Erros

### Estrutura de Erro Padrão

```json
{
  "error_type": "validation_error",
  "message": "Dados de entrada inválidos",
  "details": {
    "field": "Age",
    "value": -5,
    "constraint": "must be >= 0"
  },
  "status_code": 400,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

### Tipos de Erro

#### 1. Erro de Validação (400)
```json
{
  "error_type": "validation_error",
  "message": "Classe do Ticket (Pclass) deve ser 1, 2 ou 3.",
  "details": {
    "field": "Pclass",
    "value": 4,
    "constraint": "must be in [1, 2, 3]"
  },
  "status_code": 400,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

#### 2. Erro de Autenticação (401)
```json
{
  "error_type": "authentication_error",
  "message": "API Key inválida ou ausente",
  "details": null,
  "status_code": 401,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

#### 3. Recurso Não Encontrado (404)
```json
{
  "error_type": "not_found_error",
  "message": "Passageiro não encontrado",
  "details": {
    "resource_id": "uuid-1234-5678"
  },
  "status_code": 404,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

#### 4. Erro Interno (500)
```json
{
  "error_type": "internal_error",
  "message": "Erro interno do servidor",
  "details": null,
  "status_code": 500,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

---

## 📝 Validações de Entrada

### Campos Obrigatórios
- `PassengerId`: String não vazia
- `Pclass`: Inteiro (1, 2 ou 3)
- `Sex`: String ("male" ou "female")
- `Age`: Float (0.0 - 120.0)
- `SibSp`: Inteiro (>= 0)
- `Parch`: Inteiro (>= 0)
- `Fare`: Float (>= 0.0)

### Campos Opcionais
- `Embarked`: String ("S", "C", "Q" ou null)

### Regras de Validação
1. **Age**: Deve estar entre 0 e 120 anos
2. **Pclass**: Apenas valores 1 (primeira classe), 2 (segunda classe), 3 (terceira classe)
3. **Sex**: Apenas "male" ou "female"
4. **SibSp/Parch**: Valores não negativos
5. **Fare**: Valor não negativo
6. **Embarked**: S = Southampton, C = Cherbourg, Q = Queenstown

---

## 🔢 Exemplos de Uso

### cURL

#### Criar Predição
```bash
curl -X POST \
  https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1/sobreviventes \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key' \
  -d '{
    "PassengerId": "jack_dawson",
    "Pclass": 3,
    "Sex": "male",
    "Age": 20.0,
    "SibSp": 0,
    "Parch": 0,
    "Fare": 5.0,
    "Embarked": "S"
  }'
```

#### Listar Predições
```bash
curl -X GET \
  https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1/sobreviventes \
  -H 'x-api-key: your-api-key'
```

#### Health Check
```bash
curl -X GET \
  https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1/health \
  -H 'x-api-key: your-api-key'
```

### Python

```python
import requests
import json

# Configuração
BASE_URL = "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1"
API_KEY = "your-api-key"

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# Criar predição
passenger_data = {
    "PassengerId": "rose_dewitt",
    "Pclass": 1,
    "Sex": "female",
    "Age": 17.0,
    "SibSp": 1,
    "Parch": 2,
    "Fare": 512.3292,
    "Embarked": "C"
}

response = requests.post(
    f"{BASE_URL}/sobreviventes",
    headers=headers,
    json=passenger_data
)

if response.status_code == 201:
    result = response.json()
    print(f"Probabilidade de sobrevivência: {result['probability']:.2%}")
else:
    print(f"Erro: {response.status_code} - {response.text}")
```

### JavaScript

```javascript
const BASE_URL = "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1";
const API_KEY = "your-api-key";

const headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
};

// Criar predição
const passengerData = {
    PassengerId: "caledon_hockley",
    Pclass: 1,
    Sex: "male",
    Age: 30.0,
    SibSp: 0,
    Parch: 0,
    Fare: 227.525,
    Embarked: "C"
};

fetch(`${BASE_URL}/sobreviventes`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(passengerData)
})
.then(response => response.json())
.then(data => {
    console.log(`Probabilidade de sobrevivência: ${(data.probability * 100).toFixed(2)}%`);
})
.catch(error => {
    console.error("Erro:", error);
});
```

---

## 📊 Rate Limits

| Endpoint | Limite | Janela |
|----------|---------|---------|
| `POST /sobreviventes` | 100 requests | por minuto |
| `GET /sobreviventes` | 200 requests | por minuto |
| `GET /sobreviventes/{id}` | 500 requests | por minuto |
| `DELETE /sobreviventes/{id}` | 50 requests | por minuto |
| `GET /health` | 1000 requests | por minuto |

Quando o limite é excedido, a API retorna status `429 Too Many Requests`.

---

## 🔐 Segurança

### Boas Práticas
1. **Nunca exponha sua API Key** em código cliente
2. **Use HTTPS** para todas as comunicações
3. **Implemente rate limiting** do lado do cliente
4. **Monitore o uso** da sua API Key
5. **Rotacione as chaves** periodicamente

### CORS
A API está configurada para aceitar requisições de domínios específicos. Para desenvolvimento local, certifique-se de que seu domínio está autorizado.

---

*Documentação da API v1.0.0*
*Última atualização: Janeiro 2025*
