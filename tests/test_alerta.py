"""
Testes para a classe Alerta.
"""

from datetime import datetime
from src.models.alerta import Alerta, TipoAlerta


class TestAlerta:
    """Testes para a classe Alerta."""
    
    def test_criar_alerta(self):
        """Testa criação de alerta."""
        alerta = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Despesa de alto valor registrada"
        )
        
        assert alerta.tipo == TipoAlerta.ALTO_VALOR
        assert alerta.mensagem == "Despesa de alto valor registrada"
        assert alerta.lido is False
        assert alerta.id is not None
        assert alerta.data_criacao is not None
    
    def test_alerta_com_lancamento_id(self):
        """Testa alerta com ID de lançamento."""
        alerta = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Teste",
            lancamento_id="lanc-123"
        )
        
        assert alerta.lancamento_id == "lanc-123"
    
    def test_alerta_com_categoria_id(self):
        """Testa alerta com ID de categoria."""
        alerta = Alerta(
            tipo=TipoAlerta.LIMITE_EXCEDIDO,
            mensagem="Limite excedido",
            categoria_id="cat-456"
        )
        
        assert alerta.categoria_id == "cat-456"
    
    def test_alerta_com_mes_ano(self):
        """Testa alerta com mês/ano."""
        alerta = Alerta(
            tipo=TipoAlerta.DEFICIT_ORCAMENTARIO,
            mensagem="Déficit em dezembro",
            mes_ano=(12, 2024)
        )
        
        assert alerta.mes_ano == (12, 2024)
    
    def test_marcar_como_lido(self):
        """Testa marcação de alerta como lido."""
        alerta = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Teste"
        )
        
        assert alerta.lido is False
        
        alerta.marcar_como_lido()
        
        assert alerta.lido is True
    
    def test_nivel_severidade_alto_valor(self):
        """Testa nível de severidade para alto valor."""
        alerta = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Teste"
        )
        
        assert alerta.nivel_severidade == 1
    
    def test_nivel_severidade_limite_excedido(self):
        """Testa nível de severidade para limite excedido."""
        alerta = Alerta(
            tipo=TipoAlerta.LIMITE_EXCEDIDO,
            mensagem="Teste"
        )
        
        assert alerta.nivel_severidade == 2
    
    def test_nivel_severidade_deficit(self):
        """Testa nível de severidade para déficit."""
        alerta = Alerta(
            tipo=TipoAlerta.DEFICIT_ORCAMENTARIO,
            mensagem="Teste"
        )
        
        assert alerta.nivel_severidade == 3
    
    def test_str_alerta_nao_lido(self):
        """Testa representação string de alerta não lido."""
        alerta = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Despesa alta"
        )
        
        resultado = str(alerta)
        assert "●" in resultado
        assert "ALTO_VALOR" in resultado
        assert "Despesa alta" in resultado
    
    def test_str_alerta_lido(self):
        """Testa representação string de alerta lido."""
        alerta = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Despesa alta"
        )
        alerta.marcar_como_lido()
        
        resultado = str(alerta)
        assert "✓" in resultado
    
    def test_eq_alertas(self):
        """Testa comparação de alertas por ID."""
        alerta1 = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Teste"
        )
        
        alerta2 = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem="Teste"
        )
        
        assert alerta1 != alerta2  # IDs diferentes
        assert alerta1 == alerta1  # Mesmo objeto
    
    def test_lt_ordenacao_por_severidade(self):
        """Testa ordenação por severidade (mais severo primeiro)."""
        alerta_leve = Alerta(
            tipo=TipoAlerta.ALTO_VALOR,  # severidade 1
            mensagem="Leve"
        )
        
        alerta_critico = Alerta(
            tipo=TipoAlerta.DEFICIT_ORCAMENTARIO,  # severidade 3
            mensagem="Crítico"
        )
        
        alertas = [alerta_leve, alerta_critico]
        alertas_ordenados = sorted(alertas)
        
        # Mais severo primeiro
        assert alertas_ordenados[0].tipo == TipoAlerta.DEFICIT_ORCAMENTARIO
        assert alertas_ordenados[1].tipo == TipoAlerta.ALTO_VALOR
    
    def test_to_dict(self):
        """Testa serialização para dicionário."""
        alerta = Alerta(
            tipo=TipoAlerta.LIMITE_EXCEDIDO,
            mensagem="Limite excedido na categoria Alimentação",
            categoria_id="cat-123",
            mes_ano=(12, 2024)
        )
        
        dados = alerta.to_dict()
        
        assert dados["tipo"] == "LIMITE_EXCEDIDO"
        assert dados["mensagem"] == "Limite excedido na categoria Alimentação"
        assert dados["categoria_id"] == "cat-123"
        assert dados["mes_ano"] == [12, 2024]
        assert dados["lido"] is False
    
    def test_from_dict(self):
        """Testa desserialização de dicionário."""
        dados = {
            "id": "alerta-123",
            "tipo": "ALTO_VALOR",
            "mensagem": "Despesa alta",
            "data_criacao": "2024-12-14T10:30:00",
            "lancamento_id": "lanc-456",
            "categoria_id": None,
            "mes_ano": None,
            "lido": True
        }
        
        alerta = Alerta.from_dict(dados)
        
        assert alerta.id == "alerta-123"
        assert alerta.tipo == TipoAlerta.ALTO_VALOR
        assert alerta.mensagem == "Despesa alta"
        assert alerta.lancamento_id == "lanc-456"
        assert alerta.lido is True
    
    def test_factory_criar_alerta_alto_valor(self):
        """Testa factory method para alerta de alto valor."""
        alerta = Alerta.criar_alerta_alto_valor("lanc-123", 750.0)
        
        assert alerta.tipo == TipoAlerta.ALTO_VALOR
        assert alerta.lancamento_id == "lanc-123"
        assert "750.00" in alerta.mensagem
    
    def test_factory_criar_alerta_limite_excedido(self):
        """Testa factory method para alerta de limite excedido."""
        alerta = Alerta.criar_alerta_limite_excedido(
            categoria_id="cat-123",
            categoria_nome="Alimentação",
            limite=500.0,
            total=650.0
        )
        
        assert alerta.tipo == TipoAlerta.LIMITE_EXCEDIDO
        assert alerta.categoria_id == "cat-123"
        assert "Alimentação" in alerta.mensagem
        assert "500.00" in alerta.mensagem
        assert "650.00" in alerta.mensagem
    
    def test_factory_criar_alerta_deficit(self):
        """Testa factory method para alerta de déficit."""
        alerta = Alerta.criar_alerta_deficit(12, 2024, -250.0)
        
        assert alerta.tipo == TipoAlerta.DEFICIT_ORCAMENTARIO
        assert alerta.mes_ano == (12, 2024)
        assert "12/2024" in alerta.mensagem
        assert "250.00" in alerta.mensagem
    
    def test_factory_criar_alerta_saldo_negativo(self):
        """Testa factory method para alerta de saldo negativo."""
        alerta = Alerta.criar_alerta_saldo_negativo(12, 2024, -500.0)
        
        assert alerta.tipo == TipoAlerta.SALDO_NEGATIVO
        assert alerta.mes_ano == (12, 2024)
