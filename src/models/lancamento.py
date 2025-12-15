"""
Módulo de Lançamentos - Classes base e especializadas para receitas e despesas.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .categoria import Categoria


class FormaPagamento(Enum):
    """Enum para formas de pagamento."""
    DINHEIRO = "DINHEIRO"
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"
    PIX = "PIX"


class Lancamento(ABC):
    """
    Classe base abstrata para lançamentos financeiros.
    
    Attributes:
        id: Identificador único do lançamento
        valor: Valor do lançamento (deve ser > 0)
        categoria: Categoria associada ao lançamento
        data: Data do lançamento
        descricao: Descrição do lançamento
        forma_pagamento: Forma de pagamento utilizada
    """
    
    def __init__(
        self,
        valor: float,
        categoria: "Categoria",
        data: date,
        descricao: str,
        forma_pagamento: FormaPagamento,
        id: Optional[str] = None
    ):
        self._id = id or str(uuid.uuid4())
        self._valor = None
        self._categoria = None
        self._data = None
        self._descricao = None
        self._forma_pagamento = None
        
        # Usar setters para validação
        self.valor = valor
        self.categoria = categoria
        self.data = data
        self.descricao = descricao
        self.forma_pagamento = forma_pagamento
    
    # ==================== PROPRIEDADES ====================
    
    @property
    def id(self) -> str:
        """Retorna o ID do lançamento (somente leitura)."""
        return self._id
    
    @property
    def valor(self) -> float:
        """Retorna o valor do lançamento."""
        return self._valor
    
    @valor.setter
    def valor(self, valor: float) -> None:
        """Define o valor do lançamento com validação."""
        if not isinstance(valor, (int, float)):
            raise TypeError("Valor deve ser um número.")
        if valor <= 0:
            raise ValueError("Valor do lançamento deve ser maior que zero.")
        self._valor = float(valor)
    
    @property
    def categoria(self) -> "Categoria":
        """Retorna a categoria do lançamento."""
        return self._categoria
    
    @categoria.setter
    def categoria(self, valor: "Categoria") -> None:
        """Define a categoria do lançamento com validação."""
        from .categoria import Categoria
        if not isinstance(valor, Categoria):
            raise TypeError("Categoria deve ser uma instância de Categoria.")
        self._validar_categoria(valor)
        self._categoria = valor
    
    @abstractmethod
    def _validar_categoria(self, categoria: "Categoria") -> None:
        """Valida se a categoria é compatível com o tipo de lançamento."""
        pass
    
    @property
    def data(self) -> date:
        """Retorna a data do lançamento."""
        return self._data
    
    @data.setter
    def data(self, valor: date) -> None:
        """Define a data do lançamento com validação."""
        if isinstance(valor, datetime):
            valor = valor.date()
        if not isinstance(valor, date):
            raise TypeError("Data deve ser uma instância de date ou datetime.")
        self._data = valor
    
    @property
    def descricao(self) -> str:
        """Retorna a descrição do lançamento."""
        return self._descricao
    
    @descricao.setter
    def descricao(self, valor: str) -> None:
        """Define a descrição do lançamento."""
        if not valor or not isinstance(valor, str):
            raise ValueError("Descrição é obrigatória.")
        self._descricao = valor.strip()
    
    @property
    def forma_pagamento(self) -> FormaPagamento:
        """Retorna a forma de pagamento."""
        return self._forma_pagamento
    
    @forma_pagamento.setter
    def forma_pagamento(self, valor: FormaPagamento) -> None:
        """Define a forma de pagamento com validação."""
        if not isinstance(valor, FormaPagamento):
            raise TypeError("Forma de pagamento deve ser um FormaPagamento válido.")
        self._forma_pagamento = valor
    
    @property
    def mes_ano(self) -> tuple[int, int]:
        """Retorna a tupla (mês, ano) do lançamento."""
        return (self._data.month, self._data.year)
    
    @property
    @abstractmethod
    def tipo(self) -> str:
        """Retorna o tipo do lançamento (RECEITA ou DESPESA)."""
        pass
    
    # ==================== MÉTODOS ESPECIAIS ====================
    
    def __str__(self) -> str:
        """Representação amigável do lançamento."""
        return (
            f"{self.tipo}: R${self._valor:.2f} - {self._descricao} "
            f"({self._data.strftime('%d/%m/%Y')}) [{self._categoria.nome}]"
        )
    
    def __repr__(self) -> str:
        """Representação técnica do lançamento."""
        return (
            f"{self.__class__.__name__}(id={self._id!r}, valor={self._valor!r}, "
            f"categoria={self._categoria.nome!r}, data={self._data!r}, "
            f"descricao={self._descricao!r}, forma_pagamento={self._forma_pagamento!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compara lançamentos pelo ID ou pela combinação de data + descrição."""
        if not isinstance(other, Lancamento):
            return NotImplemented
        return self._id == other._id or (
            self._data == other._data and 
            self._descricao.lower() == other._descricao.lower()
        )
    
    def __hash__(self) -> int:
        """Hash baseado no ID."""
        return hash(self._id)
    
    def __lt__(self, other: "Lancamento") -> bool:
        """Ordenação por data (mais antigo primeiro), depois por valor."""
        if not isinstance(other, Lancamento):
            return NotImplemented
        if self._data == other._data:
            return self._valor < other._valor
        return self._data < other._data
    
    def __add__(self, other: "Lancamento") -> float:
        """Soma valores de lançamentos do mesmo tipo."""
        if not isinstance(other, Lancamento):
            return NotImplemented
        if type(self) != type(other):
            raise TypeError("Só é possível somar lançamentos do mesmo tipo.")
        return self._valor + other._valor
    
    # ==================== MÉTODOS DE SERIALIZAÇÃO ====================
    
    def to_dict(self) -> dict:
        """Converte o lançamento para dicionário (serialização)."""
        return {
            "id": self._id,
            "tipo": self.tipo,
            "valor": self._valor,
            "categoria_id": self._categoria.id,
            "data": self._data.isoformat(),
            "descricao": self._descricao,
            "forma_pagamento": self._forma_pagamento.value,
        }


class Receita(Lancamento):
    """
    Classe que representa uma receita (entrada de dinheiro).
    Herda de Lancamento.
    """
    
    def _validar_categoria(self, categoria: "Categoria") -> None:
        """Valida se a categoria é do tipo RECEITA."""
        from .categoria import TipoCategoria
        if categoria.tipo != TipoCategoria.RECEITA:
            raise ValueError("Receitas devem ter categoria do tipo RECEITA.")
    
    @property
    def tipo(self) -> str:
        """Retorna o tipo do lançamento."""
        return "RECEITA"


class Despesa(Lancamento):
    """
    Classe que representa uma despesa (saída de dinheiro).
    Herda de Lancamento.
    
    Attributes:
        alerta_limite: Indica se a despesa excedeu o limite da categoria
    """
    
    def __init__(
        self,
        valor: float,
        categoria: "Categoria",
        data: date,
        descricao: str,
        forma_pagamento: FormaPagamento,
        id: Optional[str] = None
    ):
        super().__init__(valor, categoria, data, descricao, forma_pagamento, id)
        self._alertas: list[str] = []
        self._verificar_alertas()
    
    def _validar_categoria(self, categoria: "Categoria") -> None:
        """Valida se a categoria é do tipo DESPESA."""
        from .categoria import TipoCategoria
        if categoria.tipo != TipoCategoria.DESPESA:
            raise ValueError("Despesas devem ter categoria do tipo DESPESA.")
    
    @property
    def tipo(self) -> str:
        """Retorna o tipo do lançamento."""
        return "DESPESA"
    
    @property
    def alertas(self) -> list[str]:
        """Retorna a lista de alertas associados a esta despesa."""
        return self._alertas.copy()
    
    def _verificar_alertas(self) -> None:
        """Verifica e registra alertas para esta despesa."""
        # Alerta de alto valor (configurável, padrão R$500)
        LIMITE_ALTO_VALOR = 500.0
        if self._valor > LIMITE_ALTO_VALOR:
            self._alertas.append("ALTO_VALOR")
    
    def verificar_limite_categoria(self, total_categoria_mes: float) -> bool:
        """
        Verifica se o total de despesas na categoria excedeu o limite.
        
        Args:
            total_categoria_mes: Total já gasto na categoria no mês
            
        Returns:
            True se excedeu o limite, False caso contrário
        """
        if self._categoria.limite_mensal is not None:
            if total_categoria_mes + self._valor > self._categoria.limite_mensal:
                if "LIMITE_EXCEDIDO" not in self._alertas:
                    self._alertas.append("LIMITE_EXCEDIDO")
                return True
        return False
    
    def to_dict(self) -> dict:
        """Converte a despesa para dicionário (serialização)."""
        data = super().to_dict()
        data["alertas"] = self._alertas
        return data
