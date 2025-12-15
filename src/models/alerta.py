"""
Módulo de Alertas - Sistema de notificações do sistema financeiro.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class TipoAlerta(Enum):
    """Enum para tipos de alerta."""
    ALTO_VALOR = "ALTO_VALOR"
    LIMITE_EXCEDIDO = "LIMITE_EXCEDIDO"
    DEFICIT_ORCAMENTARIO = "DEFICIT_ORCAMENTARIO"
    SALDO_NEGATIVO = "SALDO_NEGATIVO"
    META_NAO_ATINGIDA = "META_NAO_ATINGIDA"


class Alerta:
    """
    Classe que representa um alerta do sistema.
    
    Attributes:
        id: Identificador único do alerta
        tipo: Tipo do alerta
        mensagem: Mensagem descritiva do alerta
        data_criacao: Data/hora de criação do alerta
        lancamento_id: ID do lançamento associado (se houver)
        categoria_id: ID da categoria associada (se houver)
        mes_ano: Mês/ano de referência (se aplicável)
        lido: Indica se o alerta foi lido/visualizado
    """
    
    def __init__(
        self,
        tipo: TipoAlerta,
        mensagem: str,
        lancamento_id: Optional[str] = None,
        categoria_id: Optional[str] = None,
        mes_ano: Optional[tuple[int, int]] = None,
        id: Optional[str] = None,
        data_criacao: Optional[datetime] = None,
        lido: bool = False
    ):
        self._id = id or str(uuid.uuid4())
        self._tipo = None
        self._mensagem = None
        self._data_criacao = data_criacao or datetime.now()
        self._lancamento_id = lancamento_id
        self._categoria_id = categoria_id
        self._mes_ano = mes_ano
        self._lido = lido
        
        # Usar setters para validação
        self.tipo = tipo
        self.mensagem = mensagem
    
    # ==================== PROPRIEDADES ====================
    
    @property
    def id(self) -> str:
        """Retorna o ID do alerta (somente leitura)."""
        return self._id
    
    @property
    def tipo(self) -> TipoAlerta:
        """Retorna o tipo do alerta."""
        return self._tipo
    
    @tipo.setter
    def tipo(self, valor: TipoAlerta) -> None:
        """Define o tipo do alerta com validação."""
        if not isinstance(valor, TipoAlerta):
            raise TypeError("Tipo deve ser um TipoAlerta válido.")
        self._tipo = valor
    
    @property
    def mensagem(self) -> str:
        """Retorna a mensagem do alerta."""
        return self._mensagem
    
    @mensagem.setter
    def mensagem(self, valor: str) -> None:
        """Define a mensagem do alerta."""
        if not valor or not isinstance(valor, str):
            raise ValueError("Mensagem do alerta é obrigatória.")
        self._mensagem = valor.strip()
    
    @property
    def data_criacao(self) -> datetime:
        """Retorna a data de criação do alerta."""
        return self._data_criacao
    
    @property
    def lancamento_id(self) -> Optional[str]:
        """Retorna o ID do lançamento associado."""
        return self._lancamento_id
    
    @property
    def categoria_id(self) -> Optional[str]:
        """Retorna o ID da categoria associada."""
        return self._categoria_id
    
    @property
    def mes_ano(self) -> Optional[tuple[int, int]]:
        """Retorna o mês/ano de referência."""
        return self._mes_ano
    
    @property
    def lido(self) -> bool:
        """Retorna se o alerta foi lido."""
        return self._lido
    
    @lido.setter
    def lido(self, valor: bool) -> None:
        """Define se o alerta foi lido."""
        self._lido = bool(valor)
    
    # ==================== MÉTODOS ====================
    
    def marcar_como_lido(self) -> None:
        """Marca o alerta como lido."""
        self._lido = True
    
    @property
    def nivel_severidade(self) -> int:
        """
        Retorna o nível de severidade do alerta (1-3).
        
        Returns:
            1: Informativo
            2: Atenção
            3: Crítico
        """
        severidades = {
            TipoAlerta.ALTO_VALOR: 1,
            TipoAlerta.META_NAO_ATINGIDA: 2,
            TipoAlerta.LIMITE_EXCEDIDO: 2,
            TipoAlerta.SALDO_NEGATIVO: 3,
            TipoAlerta.DEFICIT_ORCAMENTARIO: 3,
        }
        return severidades.get(self._tipo, 1)
    
    # ==================== MÉTODOS ESPECIAIS ====================
    
    def __str__(self) -> str:
        """Representação amigável do alerta."""
        status = "✓" if self._lido else "●"
        return f"[{status}] {self._tipo.value}: {self._mensagem}"
    
    def __repr__(self) -> str:
        """Representação técnica do alerta."""
        return (
            f"Alerta(id={self._id!r}, tipo={self._tipo!r}, "
            f"mensagem={self._mensagem!r}, lido={self._lido!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compara alertas pelo ID."""
        if not isinstance(other, Alerta):
            return NotImplemented
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash baseado no ID."""
        return hash(self._id)
    
    def __lt__(self, other: "Alerta") -> bool:
        """Ordenação por severidade (mais severo primeiro), depois por data."""
        if not isinstance(other, Alerta):
            return NotImplemented
        if self.nivel_severidade != other.nivel_severidade:
            return self.nivel_severidade > other.nivel_severidade
        return self._data_criacao > other._data_criacao
    
    # ==================== MÉTODOS DE SERIALIZAÇÃO ====================
    
    def to_dict(self) -> dict:
        """Converte o alerta para dicionário (serialização)."""
        return {
            "id": self._id,
            "tipo": self._tipo.value,
            "mensagem": self._mensagem,
            "data_criacao": self._data_criacao.isoformat(),
            "lancamento_id": self._lancamento_id,
            "categoria_id": self._categoria_id,
            "mes_ano": list(self._mes_ano) if self._mes_ano else None,
            "lido": self._lido,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Alerta":
        """Cria um alerta a partir de um dicionário."""
        mes_ano = tuple(data["mes_ano"]) if data.get("mes_ano") else None
        return cls(
            id=data.get("id"),
            tipo=TipoAlerta(data["tipo"]),
            mensagem=data["mensagem"],
            data_criacao=datetime.fromisoformat(data["data_criacao"]) if data.get("data_criacao") else None,
            lancamento_id=data.get("lancamento_id"),
            categoria_id=data.get("categoria_id"),
            mes_ano=mes_ano,
            lido=data.get("lido", False),
        )
    
    # ==================== FACTORY METHODS ====================
    
    @classmethod
    def criar_alerta_alto_valor(cls, lancamento_id: str, valor: float) -> "Alerta":
        """Cria um alerta de alto valor."""
        return cls(
            tipo=TipoAlerta.ALTO_VALOR,
            mensagem=f"Despesa de alto valor registrada: R${valor:.2f}",
            lancamento_id=lancamento_id,
        )
    
    @classmethod
    def criar_alerta_limite_excedido(
        cls, 
        categoria_id: str, 
        categoria_nome: str,
        limite: float,
        total: float
    ) -> "Alerta":
        """Cria um alerta de limite de categoria excedido."""
        return cls(
            tipo=TipoAlerta.LIMITE_EXCEDIDO,
            mensagem=(
                f"Limite da categoria '{categoria_nome}' excedido! "
                f"Limite: R${limite:.2f}, Total: R${total:.2f}"
            ),
            categoria_id=categoria_id,
        )
    
    @classmethod
    def criar_alerta_deficit(cls, mes: int, ano: int, saldo: float) -> "Alerta":
        """Cria um alerta de déficit orçamentário."""
        return cls(
            tipo=TipoAlerta.DEFICIT_ORCAMENTARIO,
            mensagem=f"Déficit orçamentário em {mes:02d}/{ano}: R${abs(saldo):.2f}",
            mes_ano=(mes, ano),
        )
    
    @classmethod
    def criar_alerta_saldo_negativo(cls, mes: int, ano: int, saldo: float) -> "Alerta":
        """Cria um alerta de saldo negativo."""
        return cls(
            tipo=TipoAlerta.SALDO_NEGATIVO,
            mensagem=f"Saldo negativo em {mes:02d}/{ano}: R${saldo:.2f}",
            mes_ano=(mes, ano),
        )
