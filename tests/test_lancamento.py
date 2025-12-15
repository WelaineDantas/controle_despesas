"""
Testes para as classes Lancamento, Receita e Despesa.
"""

import pytest
from datetime import date
from src.models.categoria import Categoria, TipoCategoria
from src.models.lancamento import Lancamento, Receita, Despesa, FormaPagamento


@pytest.fixture
def categoria_receita():
    """Fixture para categoria de receita."""
    return Categoria(nome="Salário", tipo=TipoCategoria.RECEITA)


@pytest.fixture
def categoria_despesa():
    """Fixture para categoria de despesa."""
    return Categoria(
        nome="Alimentação",
        tipo=TipoCategoria.DESPESA,
        limite_mensal=500.0
    )


@pytest.fixture
def categoria_despesa_sem_limite():
    """Fixture para categoria de despesa sem limite."""
    return Categoria(nome="Outros", tipo=TipoCategoria.DESPESA)


class TestReceita:
    """Testes para a classe Receita."""
    
    def test_criar_receita(self, categoria_receita):
        """Testa criação de receita válida."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário de dezembro",
            forma_pagamento=FormaPagamento.PIX
        )
        
        assert receita.valor == 1000.0
        assert receita.categoria == categoria_receita
        assert receita.data == date(2024, 12, 1)
        assert receita.descricao == "Salário de dezembro"
        assert receita.forma_pagamento == FormaPagamento.PIX
        assert receita.tipo == "RECEITA"
        assert receita.id is not None
    
    def test_receita_valor_zero_invalido(self, categoria_receita):
        """Testa que receita com valor zero é inválida."""
        with pytest.raises(ValueError, match="maior que zero"):
            Receita(
                valor=0,
                categoria=categoria_receita,
                data=date(2024, 12, 1),
                descricao="Teste",
                forma_pagamento=FormaPagamento.PIX
            )
    
    def test_receita_valor_negativo_invalido(self, categoria_receita):
        """Testa que receita com valor negativo é inválida."""
        with pytest.raises(ValueError, match="maior que zero"):
            Receita(
                valor=-100.0,
                categoria=categoria_receita,
                data=date(2024, 12, 1),
                descricao="Teste",
                forma_pagamento=FormaPagamento.PIX
            )
    
    def test_receita_categoria_incorreta(self, categoria_despesa):
        """Testa que receita não pode usar categoria de despesa."""
        with pytest.raises(ValueError, match="tipo RECEITA"):
            Receita(
                valor=1000.0,
                categoria=categoria_despesa,
                data=date(2024, 12, 1),
                descricao="Teste",
                forma_pagamento=FormaPagamento.PIX
            )
    
    def test_receita_mes_ano(self, categoria_receita):
        """Testa propriedade mes_ano."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 15),
            descricao="Teste",
            forma_pagamento=FormaPagamento.PIX
        )
        
        assert receita.mes_ano == (12, 2024)


class TestDespesa:
    """Testes para a classe Despesa."""
    
    def test_criar_despesa(self, categoria_despesa):
        """Testa criação de despesa válida."""
        despesa = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 5),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        assert despesa.valor == 100.0
        assert despesa.categoria == categoria_despesa
        assert despesa.tipo == "DESPESA"
    
    def test_despesa_valor_zero_invalido(self, categoria_despesa):
        """Testa que despesa com valor zero é inválida."""
        with pytest.raises(ValueError, match="maior que zero"):
            Despesa(
                valor=0,
                categoria=categoria_despesa,
                data=date(2024, 12, 1),
                descricao="Teste",
                forma_pagamento=FormaPagamento.DEBITO
            )
    
    def test_despesa_valor_negativo_invalido(self, categoria_despesa):
        """Testa que despesa com valor negativo é inválida."""
        with pytest.raises(ValueError, match="maior que zero"):
            Despesa(
                valor=-50.0,
                categoria=categoria_despesa,
                data=date(2024, 12, 1),
                descricao="Teste",
                forma_pagamento=FormaPagamento.DEBITO
            )
    
    def test_despesa_categoria_incorreta(self, categoria_receita):
        """Testa que despesa não pode usar categoria de receita."""
        with pytest.raises(ValueError, match="tipo DESPESA"):
            Despesa(
                valor=100.0,
                categoria=categoria_receita,
                data=date(2024, 12, 1),
                descricao="Teste",
                forma_pagamento=FormaPagamento.DEBITO
            )
    
    def test_despesa_alerta_alto_valor(self, categoria_despesa):
        """Testa alerta para despesa de alto valor (> R$500)."""
        despesa = Despesa(
            valor=600.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 1),
            descricao="Compra grande",
            forma_pagamento=FormaPagamento.CREDITO
        )
        
        assert "ALTO_VALOR" in despesa.alertas
    
    def test_despesa_sem_alerta_alto_valor(self, categoria_despesa):
        """Testa que despesa menor não gera alerta."""
        despesa = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 1),
            descricao="Compra normal",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        assert "ALTO_VALOR" not in despesa.alertas
    
    def test_verificar_limite_categoria(self, categoria_despesa):
        """Testa verificação de limite da categoria."""
        despesa = Despesa(
            valor=200.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 1),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        # Total já gasto: 400, nova despesa: 200, limite: 500
        excedeu = despesa.verificar_limite_categoria(400.0)
        
        assert excedeu is True
        assert "LIMITE_EXCEDIDO" in despesa.alertas
    
    def test_nao_excede_limite_categoria(self, categoria_despesa):
        """Testa quando não excede limite da categoria."""
        despesa = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 1),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        # Total já gasto: 200, nova despesa: 100, limite: 500
        excedeu = despesa.verificar_limite_categoria(200.0)
        
        assert excedeu is False
        assert "LIMITE_EXCEDIDO" not in despesa.alertas


class TestLancamentoMetodosEspeciais:
    """Testes para métodos especiais da classe Lancamento."""
    
    def test_str_lancamento(self, categoria_receita):
        """Testa representação string."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        resultado = str(receita)
        assert "RECEITA" in resultado
        assert "1000.00" in resultado
        assert "Salário" in resultado
    
    def test_repr_lancamento(self, categoria_receita):
        """Testa representação técnica."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        resultado = repr(receita)
        assert "Receita(" in resultado
        assert "valor=1000.0" in resultado
    
    def test_eq_lancamentos_mesmo_id(self, categoria_receita):
        """Testa igualdade por ID."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        assert receita == receita
    
    def test_eq_lancamentos_data_descricao(self, categoria_receita):
        """Testa igualdade por data + descrição."""
        receita1 = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        receita2 = Receita(
            valor=2000.0,  # valor diferente
            categoria=categoria_receita,
            data=date(2024, 12, 1),  # mesma data
            descricao="salário",  # mesma descrição (case insensitive)
            forma_pagamento=FormaPagamento.PIX
        )
        
        assert receita1 == receita2
    
    def test_lt_ordenacao_por_data(self, categoria_receita):
        """Testa ordenação por data."""
        receita1 = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Primeiro",
            forma_pagamento=FormaPagamento.PIX
        )
        
        receita2 = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 15),
            descricao="Segundo",
            forma_pagamento=FormaPagamento.PIX
        )
        
        assert receita1 < receita2
    
    def test_lt_ordenacao_por_valor_mesma_data(self, categoria_receita):
        """Testa ordenação por valor quando data é igual."""
        receita1 = Receita(
            valor=500.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Menor",
            forma_pagamento=FormaPagamento.PIX
        )
        
        receita2 = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Maior",
            forma_pagamento=FormaPagamento.PIX
        )
        
        assert receita1 < receita2
    
    def test_add_lancamentos_mesmo_tipo(self, categoria_receita):
        """Testa soma de lançamentos do mesmo tipo."""
        receita1 = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        receita2 = Receita(
            valor=500.0,
            categoria=categoria_receita,
            data=date(2024, 12, 15),
            descricao="Bonus",
            forma_pagamento=FormaPagamento.PIX
        )
        
        total = receita1 + receita2
        assert total == 1500.0
    
    def test_add_lancamentos_tipos_diferentes_erro(self, categoria_receita, categoria_despesa):
        """Testa que soma de tipos diferentes gera erro."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        despesa = Despesa(
            valor=100.0,
            categoria=categoria_despesa,
            data=date(2024, 12, 1),
            descricao="Compra",
            forma_pagamento=FormaPagamento.DEBITO
        )
        
        with pytest.raises(TypeError, match="mesmo tipo"):
            receita + despesa
    
    def test_hash_lancamento(self, categoria_receita):
        """Testa que lançamentos podem ser usados em sets."""
        receita1 = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        receita2 = Receita(
            valor=500.0,
            categoria=categoria_receita,
            data=date(2024, 12, 15),
            descricao="Bonus",
            forma_pagamento=FormaPagamento.PIX
        )
        
        lancamentos = {receita1, receita2}
        assert len(lancamentos) == 2
    
    def test_to_dict_receita(self, categoria_receita):
        """Testa serialização de receita."""
        receita = Receita(
            valor=1000.0,
            categoria=categoria_receita,
            data=date(2024, 12, 1),
            descricao="Salário",
            forma_pagamento=FormaPagamento.PIX
        )
        
        dados = receita.to_dict()
        
        assert dados["tipo"] == "RECEITA"
        assert dados["valor"] == 1000.0
        assert dados["data"] == "2024-12-01"
        assert dados["forma_pagamento"] == "PIX"
    
    def test_to_dict_despesa(self, categoria_despesa):
        """Testa serialização de despesa."""
        despesa = Despesa(
            valor=600.0,  # > 500 para gerar alerta
            categoria=categoria_despesa,
            data=date(2024, 12, 1),
            descricao="Supermercado",
            forma_pagamento=FormaPagamento.CREDITO
        )
        
        dados = despesa.to_dict()
        
        assert dados["tipo"] == "DESPESA"
        assert "alertas" in dados
        assert "ALTO_VALOR" in dados["alertas"]
