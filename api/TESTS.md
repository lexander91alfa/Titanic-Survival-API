# 🧪 Documentação dos Testes - Titanic Survival API

## 📋 Visão Geral

Esta documentação descreve a estratégia e implementação dos testes para a API de Predição de Sobrevivência do Titanic. Os testes foram criados seguindo as melhores práticas de teste unitário e cobertura de código.

## 🗂️ Estrutura dos Testes

```
tests/
├── conftest.py                 # Fixtures e configuração
├── src/
│   ├── test_config.py          # Testes de configuração
│   ├── test_controller.py      # Testes do controller
│   ├── test_error_response.py  # Testes de resposta de erro
│   ├── test_handler.py         # Testes do lambda handler
│   ├── test_health_check.py    # Testes de health check
│   ├── test_http_adapter.py    # Testes do adapter HTTP
│   ├── test_mapper.py          # Testes do mapper
│   ├── test_passenger_request.py # Testes do modelo de request
│   ├── test_predict_service.py # Testes do serviço de predição
│   └── test_repository.py      # Testes do repositório
└── __init__.py
```

## 🎯 Tipos de Testes Implementados

### 1. **Testes Unitários**
- Testam componentes individuais em isolamento
- Usam mocks para dependências externas
- Focam na lógica de negócio específica

### 2. **Testes de Integração**
- Testam interação entre componentes
- Validam fluxos completos de dados
- Incluem testes do lambda handler

### 3. **Testes de Validação**
- Testam validação de entrada usando Pydantic
- Cobrem casos de sucesso e falha
- Verificam mensagens de erro apropriadas

### 4. **Testes de Configuração**
- Testam carregamento de variáveis de ambiente
- Validam valores padrão
- Verificam diferentes ambientes (dev/prod)

## 📊 Cobertura de Testes por Módulo

### `test_config.py` - Configuração da Aplicação
- **Cobertura**: Configuração de ambiente
- **Cenários Testados**:
  - ✅ Carregamento de variáveis de ambiente
  - ✅ Valores padrão quando variáveis ausentes
  - ✅ Detecção de ambiente (dev/prod)
  - ✅ Configurações específicas por ambiente

### `test_passenger_request.py` - Modelo de Dados
- **Cobertura**: Validação de entrada
- **Cenários Testados**:
  - ✅ Requisições válidas completas
  - ✅ Campos opcionais ausentes
  - ✅ Validação de tipos de dados
  - ✅ Valores limite (boundary tests)
  - ✅ Valores inválidos e mensagens de erro
  - ✅ Validadores customizados

### `test_predict_service.py` - Serviço de Predição
- **Cobertura**: Lógica de ML e preprocessing
- **Cenários Testados**:
  - ✅ Carregamento de modelo (joblib/pickle)
  - ✅ Preprocessamento de dados
  - ✅ Predições com dados completos/incompletos
  - ✅ Tratamento de erros de modelo
  - ✅ Validação de probabilidades
  - ✅ Valores padrão para campos faltantes

### `test_controller.py` - Lógica de Negócio
- **Cobertura**: Orquestração de serviços
- **Cenários Testados**:
  - ✅ Salvamento de passageiros (único/múltiplos)
  - ✅ Conversão para Decimal (DynamoDB)
  - ✅ Busca de passageiros (todos/por ID)
  - ✅ Exclusão de passageiros
  - ✅ Tratamento de erros de validação/negócio
  - ✅ Logging de erros
  - ✅ Integração com mapper

### `test_repository.py` - Acesso a Dados
- **Cobertura**: Operações de banco de dados
- **Cenários Testados**:
  - ✅ Operações CRUD no DynamoDB
  - ✅ Tratamento de erros de conexão
  - ✅ Mocking do AWS DynamoDB
  - ✅ Configuração de ambiente

### `test_handler.py` - Ponto de Entrada da API
- **Cobertura**: Endpoints e HTTP
- **Cenários Testados**:
  - ✅ POST - Criação de predições
  - ✅ GET - Listagem e busca por ID
  - ✅ DELETE - Remoção de passageiros
  - ✅ Health check endpoint
  - ✅ Tratamento de erros HTTP
  - ✅ Validação de parâmetros
  - ✅ Métodos não suportados

### `test_http_adapter.py` - Adaptador HTTP
- **Cobertura**: Parsing e resposta HTTP
- **Cenários Testados**:
  - ✅ Parsing de eventos do API Gateway
  - ✅ Extração de parâmetros e body
  - ✅ Construção de respostas
  - ✅ Headers CORS
  - ✅ Serialização de modelos Pydantic
  - ✅ Tratamento de JSON inválido

### `test_mapper.py` - Mapeamento de Dados
- **Cobertura**: Transformação de dados
- **Cenários Testados**:
  - ✅ Mapeamento completo de request para DynamoDB
  - ✅ Campos opcionais ausentes
  - ✅ Conversão de tipos
  - ✅ Preservação de dados
  - ✅ Todos os valores possíveis de enum

### `test_error_response.py` - Tratamento de Erros
- **Cobertura**: Padronização de erros
- **Cenários Testados**:
  - ✅ Criação de respostas de erro padronizadas
  - ✅ Erros de validação com detalhes
  - ✅ Erros de negócio
  - ✅ Erros internos do servidor
  - ✅ Serialização de erros

### `test_health_check.py` - Monitoramento
- **Cobertura**: Status do sistema
- **Cenários Testados**:
  - ✅ Verificação de saúde do modelo
  - ✅ Verificação de conexão com DB
  - ✅ Status geral do sistema
  - ✅ Ambiente de desenvolvimento vs produção
  - ✅ Tratamento de componentes não saudáveis

## 🚀 Como Executar os Testes

### Executar Todos os Testes
```bash
# Com cobertura
python run_tests.py

# Ou usando pytest diretamente
python -m pytest tests/ -v --cov=src --cov-report=html
```

### Executar Testes Específicos
```bash
# Arquivo específico
python run_tests.py test_controller.py

# Classe específica
python -m pytest tests/src/test_controller.py::TestPassengerController -v

# Teste específico
python -m pytest tests/src/test_controller.py::TestPassengerController::test_save_passenger -v
```

### Executar com Diferentes Níveis de Verbosidade
```bash
# Modo silencioso
python -m pytest tests/ -q

# Modo verbose
python -m pytest tests/ -v

# Modo extra verbose
python -m pytest tests/ -vv
```

## 📋 Fixtures Disponíveis

### `conftest.py` - Fixtures Globais
- `aws_credentials`: Credenciais AWS mockadas
- `dynamodb_table`: Tabela DynamoDB mockada
- `passenger_repository`: Instância do repositório
- `passenger_controller`: Instância do controller
- `mock_prediction_service`: Mock do serviço de predição
- `sample_passenger_data`: Dados de exemplo
- `sample_api_gateway_event`: Evento de exemplo do API Gateway

## 🔧 Configuração de Ambiente para Testes

### Variáveis de Ambiente Automáticas
```python
DYNAMODB_TABLE_NAME=titanic-survival-api-passengers
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_REGION=us-east-1
```

### Dependências de Teste
```
pytest==8.4.1
pytest-cov==6.2.1
moto==5.1.8  # Mock AWS services
```

## 📈 Métricas de Qualidade

### Objetivos de Cobertura
- **Meta**: > 90% de cobertura de código
- **Linhas críticas**: 100% cobertura em lógica de negócio
- **Branches**: Cobertura de todos os caminhos de execução

### Tipos de Teste por Categoria
- **Testes de Sucesso**: ~60%
- **Testes de Erro**: ~30%
- **Testes de Edge Cases**: ~10%

## 🐛 Debugging de Testes

### Executar com Debugging
```bash
# Com breakpoints
python -m pytest tests/ -s --pdb

# Com output completo
python -m pytest tests/ -s -vv --tb=long

# Parar no primeiro erro
python -m pytest tests/ -x
```

### Logs Durante Testes
```bash
# Capturar logs
python -m pytest tests/ --log-cli-level=DEBUG
```

## 🔄 Integração Contínua

### Comandos para CI/CD
```bash
# Instalação de dependências
pip install -r requirements_test.txt

# Execução de testes
python -m pytest tests/ --cov=src --cov-report=xml --cov-fail-under=90

# Verificação de qualidade
python -m pytest tests/ --tb=short --strict-markers
```

## 📝 Convenções de Teste

### Nomenclatura
- **Arquivos**: `test_<module>.py`
- **Classes**: `Test<ClassName>`
- **Métodos**: `test_<action>_<expected_result>`

### Estrutura de Teste (AAA Pattern)
```python
def test_something():
    # Arrange - Configuração
    data = {...}
    
    # Act - Ação
    result = function_under_test(data)
    
    # Assert - Verificação
    assert result == expected
```

### Mocking Strategy
- Mock dependências externas (AWS, arquivos, rede)
- Usar `patch` para substituir comportamentos
- Manter mocks simples e focados

## 🎯 Próximos Passos

1. **Testes de Performance**: Adicionar testes de carga
2. **Testes de Segurança**: Validar inputs maliciosos
3. **Testes de Contrato**: API contract testing
4. **Testes E2E**: Testes end-to-end completos
5. **Mutation Testing**: Testar qualidade dos testes
