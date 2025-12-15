# Sistema de Controle de Despesas

Sistema CLI para gerenciar finanças pessoais desenvolvido em Python.
Projeto final da disciplina de Programação Orientada a Objetos – Universidade Federal do Cariri (UFCA)

- Aluna: Maria Welaine Dantas Angelo
- Responsável por toda a integração do sistema

---

## 📋 Sobre o Projeto

Sistema de linha de comando para controle de receitas, despesas e orçamentos pessoais com:
- Cadastro de categorias com limites mensais
- Registro de lançamentos financeiros (receitas e despesas)
- Relatórios automáticos e estatísticas
- Sistema de alertas inteligentes
- Persistência em JSON

---

## 🏗 Arquitetura

```
controle_despesas/
├── src/
│   ├── models/          # Classes de domínio
│   ├── persistence/     # Persistência JSON
│   └── cli/             # Interface CLI
├── tests/               # Testes automatizados
├── data/                # Dados JSON
└── README.md
```

### Diagrama de Classes

```
        Lancamento (ABC)
              ↑
       ┌──────┴──────┐
   Receita        Despesa
                     │
                 Categoria ←── limite mensal
                     │
              OrcamentoMensal
                     │
                  Alerta
```

---

## 🚀 Instalação

```bash
# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar o pacote
pip install -e .
```

---

## 💻 Uso

```bash
# Inicializar sistema
financas inicializar

# Categorias
financas categoria listar
financas categoria criar --nome "Alimentação" --tipo despesa --limite 800

# Adicionar receita
financas adicionar-receita --valor 5000 --categoria "Salário" \
  --data "05/12/2024" --descricao "Salário" --pagamento pix

# Adicionar despesa
financas adicionar-despesa --valor 600 --categoria "Alimentação" \
  --data "10/12/2024" --descricao "Supermercado" --pagamento credito

# Relatório mensal
financas relatorio-mensal --mes 12 --ano 2024

# Ver alertas
financas alertas
```

---

## 🧪 Testes

```bash
pytest tests/ -v
# 78 testes passando ✅
```

---

## 🔔 Sistema de Alertas

| Tipo | Condição |
|------|----------|
| Alto Valor | Despesa > R$500 |
| Limite Excedido | Categoria ultrapassou limite mensal |
| Déficit | Saldo mensal negativo |

---

## 📝 Decisões de Design

| Decisão | Justificativa |
|---------|---------------|
| **Herança** (Lancamento → Receita/Despesa) | Compartilham 90% do código com validações específicas |
| **@property** em todas as classes | Validação centralizada, impossível criar objetos inválidos |
| **JSON** para persistência | Simplicidade e legibilidade para o escopo do projeto |
| **ABC** para Lancamento | Garante contrato - subclasses devem implementar métodos obrigatórios |

---

## 🔧 Tecnologias

- Python 3.12+
- Click (CLI)
- Pytest (Testes)
- JSON (Persistência)

---

## 📄 Licença

MIT License
