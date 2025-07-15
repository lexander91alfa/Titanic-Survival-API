# AWS Lambda SnapStart Implementation

## Visão Geral

Este documento descreve a implementação do AWS Lambda SnapStart na API de Previsão de Sobrevivência do Titanic. O SnapStart reduz significativamente a latência de inicialização a frio das funções Lambda Java, Python e .NET.

## Alterações Implementadas

### 1. Lambda Function (lambda.tf)

#### SnapStart Configuration
```terraform
snap_start {
  apply_on = "PublishedVersions"
}
```

#### Lambda Version
- Criada uma versão específica da Lambda para habilitar o SnapStart
- O SnapStart só funciona com versões publicadas, não com `$LATEST`

#### Lambda Alias
- Criado alias `current` apontando para a versão atual
- O alias facilita o gerenciamento e permite atualizações sem impacto

### 2. API Gateway Integration (apigateway.tf)

#### URI Updates
- Todas as integrações agora apontam para `aws_lambda_alias.prediction_current.invoke_arn`
- Isso garante que o API Gateway use a versão com SnapStart habilitado

#### Permissions
- Adicionada permissão específica para o alias da Lambda
- Mantida a permissão original para compatibilidade

## Benefícios do SnapStart

### Redução de Latência
- **Cold Start**: Redução de até 90% no tempo de inicialização
- **Warm Start**: Performance mantida sem degradação
- **Consistency**: Latência mais previsível entre invocações

### Otimizações Automáticas
- **Pre-initialization**: AWS pré-inicializa o ambiente de execução
- **Memory Snapshot**: Cria snapshot da memória após inicialização
- **Code Optimization**: JIT compilation e otimizações são preservadas

## Considerações de Custo

### SnapStart Pricing
- **Sem custo adicional** para o SnapStart em si
- **Versioning**: Apenas uma versão ativa mantém custos baixos
- **Storage**: Snapshots são gerenciados automaticamente pela AWS

### Cost Control
- Uso do alias `current` evita proliferação de versões
- Lifecycle management automático dos snapshots
- Sem impacto nos custos de execução da Lambda

## Limitações e Considerações

### Compatibilidade
- SnapStart funciona com Python 3.9+ (sua função usa Python 3.12 ✅)
- Arquitetura ARM64 é suportada (sua configuração usa ARM64 ✅)
- Não funciona com funções que usam containers

### Comportamento
- Primeira invocação de uma nova versão pode ter latência ligeiramente maior
- State management deve ser cuidadoso (não persiste entre snapshots)
- Network connections são fechadas durante snapshot

## Deployment

### Terraform Plan
```bash
terraform plan
```

### Terraform Apply
```bash
terraform apply
```

### Verificação
```bash
# Verificar se a função tem SnapStart habilitado
aws lambda get-function --function-name titanic-survival-api-prediction-function

# Verificar alias
aws lambda get-alias --function-name titanic-survival-api-prediction-function --name current
```

## Monitoramento

### CloudWatch Metrics
- `InitDuration`: Tempo de inicialização
- `Duration`: Tempo total de execução
- `RestoreDuration`: Tempo de restauração do snapshot

### Logs
- Logs de inicialização incluem informações sobre SnapStart
- Métricas de performance são automaticamente coletadas

## Best Practices

### Code Optimization
- Minimize operações durante inicialização
- Use lazy loading quando possível
- Evite operações de I/O desnecessárias no startup

### State Management
- Não confie em estado persistente entre invocações
- Reinicialize conexões de rede se necessário
- Use variáveis de ambiente para configuração

## Rollback Plan

Se necessário, para reverter o SnapStart:

1. Remover `snap_start` block da função Lambda
2. Atualizar integrações para usar `aws_lambda_function.prediction.invoke_arn`
3. Remover recursos de versioning e alias
4. Executar `terraform apply`

## Conclusão

A implementação do SnapStart oferece melhorias significativas de performance sem custos adicionais, mantendo apenas uma versão ativa da função Lambda. Esta configuração é ideal para APIs de produção que requerem baixa latência e alta disponibilidade.
