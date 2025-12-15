"""
Testes para a classe OrcamentoMensal.
"""

import pytest
from datetime import date
from src.models.categoria import Categoria, TipoCategoria
from src.models.lancamento import Receita, Despesa, FormaPagamento
from src.models.orcamento import OrcamentoMensal
from src.models.alerta import TipoAlerta


@pytest.fixture
def categoria_receita():
    """Fixture para categoria de receita."""
    return Categoria(nome="Salário", tipo=TipoCategoria.RECEITA)


@pytest.fixture
def categoria_despesa():
    """Fixture para categoria de despesa com limite."""
    return Categoria(
        nome="Alimentação",
        tipo=TipoCategoria.DESPESA,
        limite_mensal=500.0
    )


@pytest.fixture
def categoria_despesa_transporte():
    """Fixture para segunda categoria de despesa."""
    return Categoria(
        nome="Transporte",
        tipo=TipoCategoria.DESPESA,
        limite_mensal=300.0
    )


@pytest.fixture
def orcamento_dezembro():
    """Fixture para orçamento de dezembro/2024."""
    return OrcamentoMensal(mes=12, ano=2024, receitas_previstas=5000.0)


class TestOrcamentoMensal:
    """Testes para a classe OrcamentoMensal."""
    
    def test_criar_orcamento(self):
        """Testa criação de orçamento."""
        orcamento = OrcamentoMensal(mes=12, ano=2024, receitas_previstas=5000.0)
        
        assert orcamento.mes == 12
        assert orcamento.ano == 2024
        assert orcamento.receitas_previstas == 5000.0
        assert orcamento.id is not None
        assert len(orcamento) == 0
    
    def test_mes_invalido(self):
        """Testa que mês inválido gera erro."""
        with pytest.raises(ValueError, match="entre 1 e 12"):
            OrcamentoMensal(mes=13, ano=2024)
    
    def test_mes_zero_invalido(self):
        """Testa que mês zero é inválido."""
        with pytest.raises(ValueError, match="entre 1 e 12"):
            OrcamentoMensal(mes=0, ano=2024)
    
    def test_receitas_previstas_negativa(self):
        """Testa que receitas previstas negativas são inválidas."""
        with pytest.raises(ValueError, match="não pode ser negativo"):
            OrcamentoMensal(mes=12, ano=2024, receitas_previstas=-1000.0)
    
    def test_adicionar_receita(self, orcamento_dezembro, categoria_receita):
        """Testa adição de receita."""
        receita = Receita(
            valor=3000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        alertas = orcamento_dezembro.adicionar_lancamento(receita)
        
        assert len(orcamento_dezembro) == 1
        assert orcamento_dezembro.total_receitas == 3000.0
        assert receita in orcamento_dezembro
    
    def test_adicionar_despesa(self, orcamento_dezembro, categoria_despesa):
        """Testa adição de despesa."""
        despesa = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        alertas = orcamento_dezembro.adicionar_lancamento(despesa)
        
        assert len(orcamento_dezembro) == 1
        assert orcamento_dezembro.total_despesas == 100.0
    
    def test_lancamento_mes_diferente_erro(self, orcamento_dezembro, categoria_receita):
        """Testa que lançamento de outro mês é rejeitado."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 11, 5),  # novembro, não dezembro
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        with pytest.raises(ValueError, match="não pertence"):
            orcamento_dezembro.adicionar_lancamento(receita)
    
    def test_calcular_saldo(self, orcamento_dezembro, categoria_receita, categoria_despesa):
        """Testa cálculo de saldo."""
        receita = Receita(
            valor=3000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa = Despesa(
            valor=500.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        orcamento_dezembro.adicionar_lancamento(receita)
        orcamento_dezembro.adicionar_lancamento(despesa)
        
        assert orcamento_dezembro.total_receitas == 3000.0
        assert orcamento_dezembro.total_despesas == 500.0
        assert orcamento_dezembro.saldo == 2500.0
    
    def test_saldo_negativo_deficit(self, orcamento_dezembro, categoria_receita, categoria_despesa):
        """Testa detecção de déficit."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário parcial",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa = Despesa(
            valor=400.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Compra 1",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        despesa2 = Despesa(
            valor=700.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 15),
            descricao="Compra 2",
            forma_pagamento=FormaPagamento.CREDITO
        )
        
        orcamento_dezembro.adicionar_lancamento(receita)
        orcamento_dezembro.adicionar_lancamento(despesa)
        alertas = orcamento_dezembro.adicionar_lancamento(despesa2)
        
        assert orcamento_dezembro.saldo == -100.0
        assert orcamento_dezembro.tem_deficit is True
        
        # Deve ter gerado alerta de déficit
        alertas_deficit = [a for a in alertas if a.tipo == TipoAlerta.DEFICIT_ORCAMENTARIO]
        assert len(alertas_deficit) == 1
    
    def test_alerta_limite_categoria_excedido(self, orcamento_dezembro, categoria_despesa):
        """Testa alerta quando limite da categoria é excedido."""
        despesa1 = Despesa(
            valor=400.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 5),
            descricao="Compra 1",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        despesa2 = Despesa(
            valor=200.0,  # Vai exceder limite de 500
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Compra 2",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        orcamento_dezembro.adicionar_lancamento(despesa1)
        alertas = orcamento_dezembro.adicionar_lancamento(despesa2)
        
        # Deve ter gerado alerta de limite excedido
        alertas_limite = [a for a in alertas if a.tipo == TipoAlerta.LIMITE_EXCEDIDO]
        assert len(alertas_limite) == 1
        assert "Alimentação" in alertas_limite[0].mensagem
    
    def test_alerta_alto_valor(self, orcamento_dezembro, categoria_despesa):
        """Testa alerta para despesa de alto valor."""
        despesa = Despesa(
            valor=600.0,  # > R$500 = alto valor
            categoria=categoria_despesa,
            data=date(2024, 12, 5),
            descricao="Compra grande",
            forma_pagamento=FormaPagamento.CREDITO
        )
        
        alertas = orcamento_dezembro.adicionar_lancamento(despesa)
        
        # Deve ter gerado alerta de alto valor
        alertas_alto = [a for a in alertas if a.tipo == TipoAlerta.ALTO_VALOR]
        assert len(alertas_alto) == 1
    
    def test_despesas_por_categoria(
        self, orcamento_dezembro, categoria_despesa, categoria_despesa_transporte
    ):
        """Testa agrupamento de despesas por categoria."""
        despesa1 = Despesa(
            valor=200.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 5),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        despesa2 = Despesa(
            valor=100.0,
            categoria=categoria_despesa_transporte,
            data=date(2024, 12, 10),
            descricao="Uber",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa3 = Despesa(
            valor=150.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 15),
            descricao="Restaurante",
            forma_pagamento=FormaPagamento.CREDITO
        )
        
        orcamento_dezembro.adicionar_lancamento(despesa1)
        orcamento_dezembro.adicionar_lancamento(despesa2)
        orcamento_dezembro.adicionar_lancamento(despesa3)
        
        por_categoria = orcamento_dezembro.despesas_por_categoria()
        
        assert por_categoria["Alimentação"] == 350.0
        assert por_categoria["Transporte"] == 100.0
    
    def test_despesas_por_forma_pagamento(self, orcamento_dezembro, categoria_despesa):
        """Testa agrupamento de despesas por forma de pagamento."""
        despesa1 = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 5),
            descricao="Compra 1",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        despesa2 = Despesa(
            valor=200.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Compra 2",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa3 = Despesa(
            valor=50.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 15),
            descricao="Compra 3",
            forma_pagamento=FormaPagamento.PIX
        )
        
        orcamento_dezembro.adicionar_lancamento(despesa1)
        orcamento_dezembro.adicionar_lancamento(despesa2)
        orcamento_dezembro.adicionar_lancamento(despesa3)
        
        por_pagamento = orcamento_dezembro.despesas_por_forma_pagamento()
        
        assert por_pagamento["DEBITO"] == 100.0
        assert por_pagamento["PIX"] == 250.0
    
    def test_percentual_por_categoria(
        self, orcamento_dezembro, categoria_despesa, categoria_despesa_transporte
    ):
        """Testa cálculo de percentual por categoria."""
        despesa1 = Despesa(
            valor=300.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 5),
            descricao="Alimentação",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        despesa2 = Despesa(
            valor=100.0,
            categoria=categoria_despesa_transporte,
            data=date(2024, 12, 10),
            descricao="Transporte",
            forma_pagamento=FormaPagamento.PIX
        )
        
        orcamento_dezembro.adicionar_lancamento(despesa1)
        orcamento_dezembro.adicionar_lancamento(despesa2)
        
        percentuais = orcamento_dezembro.percentual_por_categoria()
        
        # Total: 400. Alimentação: 300/400 = 75%. Transporte: 100/400 = 25%
        assert percentuais["Alimentação"] == 75.0
        assert percentuais["Transporte"] == 25.0
    
    def test_remover_lancamento(self, orcamento_dezembro, categoria_receita):
        """Testa remoção de lançamento."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        orcamento_dezembro.adicionar_lancamento(receita)
        assert len(orcamento_dezembro) == 1
        
        removido = orcamento_dezembro.remover_lancamento(receita.id)
        
        assert removido == receita
        assert len(orcamento_dezembro) == 0
    
    def test_iteracao_orcamento(self, orcamento_dezembro, categoria_receita, categoria_despesa):
        """Testa iteração sobre lançamentos do orçamento."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Compra",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        orcamento_dezembro.adicionar_lancamento(receita)
        orcamento_dezembro.adicionar_lancamento(despesa)
        
        lancamentos = list(orcamento_dezembro)
        assert len(lancamentos) == 2
    
    def test_str_orcamento(self, orcamento_dezembro, categoria_receita, categoria_despesa):
        """Testa representação string do orçamento."""
        receita = Receita(
            valor=3000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa = Despesa(
            valor=500.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Compra",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        orcamento_dezembro.adicionar_lancamento(receita)
        orcamento_dezembro.adicionar_lancamento(despesa)
        
        resultado = str(orcamento_dezembro)
        
        assert "12/2024" in resultado
        assert "3000.00" in resultado
        assert "500.00" in resultado
        assert "2500.00" in resultado
    
    def test_eq_orcamentos(self):
        """Testa comparação de orçamentos por mês/ano."""
        orc1 = OrcamentoMensal(mes=12, ano=2024)
        orc2 = OrcamentoMensal(mes=12, ano=2024)
        orc3 = OrcamentoMensal(mes=11, ano=2024)
        
        assert orc1 == orc2
        assert orc1 != orc3
    
    def test_lt_ordenacao_orcamentos(self):
        """Testa ordenação de orçamentos."""
        orc_dez = OrcamentoMensal(mes=12, ano=2024)
        orc_nov = OrcamentoMensal(mes=11, ano=2024)
        orc_jan_25 = OrcamentoMensal(mes=1, ano=2025)
        
        orcamentos = [orc_dez, orc_jan_25, orc_nov]
        orcamentos_ordenados = sorted(orcamentos)
        
        assert orcamentos_ordenados[0] == orc_nov
        assert orcamentos_ordenados[1] == orc_dez
        assert orcamentos_ordenados[2] == orc_jan_25
    
    def test_add_saldos_orcamentos(self, categoria_receita, categoria_despesa):
        """Testa soma de saldos de orçamentos."""
        orc1 = OrcamentoMensal(mes=11, ano=2024)
        orc2 = OrcamentoMensal(mes=12, ano=2024)
        
        receita1 = Receita(
            valor=3000.0,
            categoria=categoria_receita,
            data=date(2024, 11, 5),
            descricao="Salário nov",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa1 = Despesa(
            valor=500.0,
            categoria=categoria_despesa,
            data=date(2024, 11, 10),
            descricao="Compra nov",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        receita2 = Receita(
            valor=4000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 5),
            descricao="Salário dez",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa2 = Despesa(
            valor=1000.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 10),
            descricao="Compra dez",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        orc1.adicionar_lancamento(receita1)
        orc1.adicionar_lancamento(despesa1)
        orc2.adicionar_lancamento(receita2)
        orc2.adicionar_lancamento(despesa2)
        
        # Nov: 3000 - 500 = 2500
        # Dez: 4000 - 1000 = 3000
        # Total: 5500
        
        total = orc1 + orc2
        assert total == 5500.0
