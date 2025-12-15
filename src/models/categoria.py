"""
Módulo de Categoria - Gerencia categorias de receitas e despesas.
"""

from enum import Enum
from typing import Optional
import uuid


class TipoCategoria(Enum):
    """Enum para tipos de categoria."""
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"


class Categoria:
    """
    Classe que representa uma categoria de lançamento financeiro.
    
    Attributes:
        id: Identificador único da categoria
        nome: Nome da categoria
        tipo: Tipo da categoria (RECEITA ou DESPESA)
        limite_mensal: Limite de gastos mensais (apenas para DESPESA)
        descricao: Descrição opcional da categoria
    """
    
    def __init__(
        self,
        nome: str,
        tipo: TipoCategoria,
        limite_mensal: Optional[float] = None,
        descricao: Optional[str] = None,
        id: Optional[str] = None
    ):
        self._id = id or str(uuid.uuid4())
        self._nome = None
        self._tipo = None
        self._limite_mensal = None
        self._descricao = descricao
        
        # Usar setters para validação
        self.nome = nome
        self.tipo = tipo
        self.limite_mensal = limite_mensal
    
    # ==================== PROPRIEDADES ====================
    
    @property
    def id(self) -> str:
        """Retorna o ID da categoria (somente leitura)."""
        return self._id
    
    @property
    def nome(self) -> str:
        """Retorna o nome da categoria."""
        return self._nome
    
    @nome.setter
    def nome(self, valor: str) -> None:
        """Define o nome da categoria com validação."""
        if not valor or not isinstance(valor, str):
            raise ValueError("Nome da categoria é obrigatório e deve ser uma string.")
        if len(valor.strip()) < 2:
            raise ValueError("Nome da categoria deve ter pelo menos 2 caracteres.")
        self._nome = valor.strip()
    
    @property
    def tipo(self) -> TipoCategoria:
        """Retorna o tipo da categoria."""
        return self._tipo
    
    @tipo.setter
    def tipo(self, valor: TipoCategoria) -> None:
        """Define o tipo da categoria com validação."""
        if not isinstance(valor, TipoCategoria):
            raise TypeError("Tipo deve ser um TipoCategoria válido.")
        self._tipo = valor
    
    @property
    def limite_mensal(self) -> Optional[float]:
        """Retorna o limite mensal da categoria."""
        return self._limite_mensal
    
    @limite_mensal.setter
    def limite_mensal(self, valor: Optional[float]) -> None:
        """Define o limite mensal com validação."""
        if valor is not None:
            # Categorias de receita não podem ter limite
            if self._tipo == TipoCategoria.RECEITA:
                raise ValueError("Categorias de receita não podem ter limite de gastos.")
            if not isinstance(valor, (int, float)):
                raise TypeError("Limite mensal deve ser um número.")
            if valor <= 0:
                raise ValueError("Limite mensal deve ser maior que zero.")
        self._limite_mensal = float(valor) if valor is not None else None
    
    @property
    def descricao(self) -> Optional[str]:
        """Retorna a descrição da categoria."""
        return self._descricao
    
    @descricao.setter
    def descricao(self, valor: Optional[str]) -> None:
        """Define a descrição da categoria."""
        self._descricao = valor.strip() if valor else None
    
    # ==================== MÉTODOS ESPECIAIS ====================
    
    def __str__(self) -> str:
        """Representação amigável da categoria."""
        limite_info = f" (Limite: R${self._limite_mensal:.2f})" if self._limite_mensal else ""
        return f"{self._nome} [{self._tipo.value}]{limite_info}"
    
    def __repr__(self) -> str:
        """Representação técnica da categoria."""
        return (
            f"Categoria(id={self._id!r}, nome={self._nome!r}, "
            f"tipo={self._tipo!r}, limite_mensal={self._limite_mensal!r}, "
            f"descricao={self._descricao!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compara categorias pelo nome e tipo."""
        if not isinstance(other, Categoria):
            return NotImplemented
        return self._nome.lower() == other._nome.lower() and self._tipo == other._tipo
    
    def __hash__(self) -> int:
        """Hash baseado no ID."""
        return hash(self._id)
    
    def __lt__(self, other: "Categoria") -> bool:
        """Ordenação por nome."""
        if not isinstance(other, Categoria):
            return NotImplemented
        return self._nome.lower() < other._nome.lower()
    
    # ==================== MÉTODOS DE SERIALIZAÇÃO ====================
    
    def to_dict(self) -> dict:
        """Converte a categoria para dicionário (serialização)."""
        return {
            "id": self._id,
            "nome": self._nome,
            "tipo": self._tipo.value,
            "limite_mensal": self._limite_mensal,
            "descricao": self._descricao,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Categoria":
        """Cria uma categoria a partir de um dicionário."""
        return cls(
            id=data.get("id"),
            nome=data["nome"],
            tipo=TipoCategoria(data["tipo"]),
            limite_mensal=data.get("limite_mensal"),
            descricao=data.get("descricao"),
        )
