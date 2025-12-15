"""
Testes para a classe Categoria.
"""

import pytest
from src.models.categoria import Categoria, TipoCategoria


class TestCategoria:
    """Testes para a classe Categoria."""
    
    def test_criar_categoria_receita(self):
        """Testa criação de categoria de receita."""
        categoria = Categoria(
            nome="Salário",
            tipo=TipoCategoria.RECEITA,
            descricao="Renda principal"
        )
        
        assert categoria.nome == "Salário"
        assert categoria.tipo == TipoCategoria.RECEITA
        assert categoria.descricao == "Renda principal"
        assert categoria.limite_mensal is None
        assert categoria.id is not None
    
    def test_criar_categoria_despesa_com_limite(self):
        """Testa criação de categoria de despesa com limite."""
        categoria = Categoria(
            nome="Alimentação",
            tipo=TipoCategoria.DESPESA,
            limite_mensal=500.0
        )
        
        assert categoria.nome == "Alimentação"
        assert categoria.tipo == TipoCategoria.DESPESA
        assert categoria.limite_mensal == 500.0
    
    def test_categoria_receita_nao_pode_ter_limite(self):
        """Testa que categorias de receita não podem ter limite."""
        with pytest.raises(ValueError, match="Categorias de receita não podem ter limite"):
            Categoria(
                nome="Salário",
                tipo=TipoCategoria.RECEITA,
                limite_mensal=1000.0
            )
    
    def test_nome_categoria_obrigatorio(self):
        """Testa que nome é obrigatório."""
        with pytest.raises(ValueError, match="Nome da categoria é obrigatório"):
            Categoria(nome="", tipo=TipoCategoria.RECEITA)
    
    def test_nome_categoria_minimo_2_caracteres(self):
        """Testa que nome deve ter pelo menos 2 caracteres."""
        with pytest.raises(ValueError, match="pelo menos 2 caracteres"):
            Categoria(nome="A", tipo=TipoCategoria.RECEITA)
    
    def test_limite_mensal_deve_ser_positivo(self):
        """Testa que limite deve ser maior que zero."""
        with pytest.raises(ValueError, match="maior que zero"):
            Categoria(
                nome="Alimentação",
                tipo=TipoCategoria.DESPESA,
                limite_mensal=-100.0
            )
    
    def test_limite_mensal_zero_invalido(self):
        """Testa que limite zero é inválido."""
        with pytest.raises(ValueError, match="maior que zero"):
            Categoria(
                nome="Alimentação",
                tipo=TipoCategoria.DESPESA,
                limite_mensal=0
            )
    
    def test_tipo_invalido(self):
        """Testa que tipo inválido gera erro."""
        with pytest.raises(TypeError, match="TipoCategoria válido"):
            Categoria(nome="Teste", tipo="INVALIDO")
    
    def test_str_categoria(self):
        """Testa representação string."""
        categoria = Categoria(
            nome="Alimentação",
            tipo=TipoCategoria.DESPESA,
            limite_mensal=500.0
        )
        
        resultado = str(categoria)
        assert "Alimentação" in resultado
        assert "DESPESA" in resultado
        assert "500.00" in resultado
    
    def test_repr_categoria(self):
        """Testa representação técnica."""
        categoria = Categoria(
            nome="Alimentação",
            tipo=TipoCategoria.DESPESA
        )
        
        resultado = repr(categoria)
        assert "Categoria(" in resultado
        assert "nome='Alimentação'" in resultado
    
    def test_eq_categorias_iguais(self):
        """Testa comparação de categorias iguais."""
        cat1 = Categoria(nome="Alimentação", tipo=TipoCategoria.DESPESA)
        cat2 = Categoria(nome="alimentação", tipo=TipoCategoria.DESPESA)
        
        assert cat1 == cat2
    
    def test_eq_categorias_diferentes_tipo(self):
        """Testa que categorias com mesmo nome mas tipo diferente são diferentes."""
        cat1 = Categoria(nome="Outros", tipo=TipoCategoria.RECEITA)
        cat2 = Categoria(nome="Outros", tipo=TipoCategoria.DESPESA)
        
        assert cat1 != cat2
    
    def test_lt_ordenacao_por_nome(self):
        """Testa ordenação por nome."""
        cat1 = Categoria(nome="Alimentação", tipo=TipoCategoria.DESPESA)
        cat2 = Categoria(nome="Transporte", tipo=TipoCategoria.DESPESA)
        
        assert cat1 < cat2
    
    def test_hash_categoria(self):
        """Testa que categorias podem ser usadas em sets."""
        cat1 = Categoria(nome="Alimentação", tipo=TipoCategoria.DESPESA)
        cat2 = Categoria(nome="Transporte", tipo=TipoCategoria.DESPESA)
        
        categorias = {cat1, cat2}
        assert len(categorias) == 2
    
    def test_to_dict(self):
        """Testa serialização para dicionário."""
        categoria = Categoria(
            nome="Alimentação",
            tipo=TipoCategoria.DESPESA,
            limite_mensal=500.0,
            descricao="Gastos com comida"
        )
        
        dados = categoria.to_dict()
        
        assert dados["nome"] == "Alimentação"
        assert dados["tipo"] == "DESPESA"
        assert dados["limite_mensal"] == 500.0
        assert dados["descricao"] == "Gastos com comida"
        assert "id" in dados
    
    def test_from_dict(self):
        """Testa desserialização de dicionário."""
        dados = {
            "id": "123",
            "nome": "Alimentação",
            "tipo": "DESPESA",
            "limite_mensal": 500.0,
            "descricao": "Gastos com comida"
        }
        
        categoria = Categoria.from_dict(dados)
        
        assert categoria.id == "123"
        assert categoria.nome == "Alimentação"
        assert categoria.tipo == TipoCategoria.DESPESA
        assert categoria.limite_mensal == 500.0
