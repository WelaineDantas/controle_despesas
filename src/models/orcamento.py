"""
Módulo de Orçamento Mensal - Gerencia o orçamento e lançamentos de um mês.
"""

from datetime import date
from typing import Optional, Iterator
from collections import defaultdict
import uuid

from .lancamento import Lancamento, Receita, Despesa, FormaPagamento
from .categoria import Categoria, TipoCategoria
from .alerta import Alerta, TipoAlerta


class OrcamentoMensal:
    """
    Classe que representa o orçamento de um mês específico.
    Agrupa todos os lançamentos do mês e calcula saldos.
    
    Attributes:
        id: Identificador único do orçamento
        mes: Mês de referência (1-12)
        ano: Ano de referência
        receitas_previstas: Total de receitas previstas para o mês
        lancamentos: Lista de lançamentos do mês
        alertas: Lista de alertas gerados
    """
    
    def __init__(
        self,
        mes: int,
        ano: int,
        receitas_previstas: float = 0.0,
        id: Optional[str] = None
    ):
        self._id = id or str(uuid.uuid4())
        self._mes = None
        self._ano = None
        self._receitas_previstas = None
        self._lancamentos: list[Lancamento] = []
        self._alertas: list[Alerta] = []
        
        # Usar setters para validação
        self.mes = mes
        self.ano = ano
        self.receitas_previstas = receitas_previstas
    
    # ==================== PROPRIEDADES ====================
    
    @property
    def id(self) -> str:
        """Retorna o ID do orçamento (somente leitura)."""
        return self._id
    
    @property
    def mes(self) -> int:
        """Retorna o mês do orçamento."""
        return self._mes
    
    @mes.setter
    def mes(self, valor: int) -> None:
        """Define o mês com validação."""
        if not isinstance(valor, int) or not 1 <= valor <= 12:
            raise ValueError("Mês deve ser um inteiro entre 1 e 12.")
        self._mes = valor
    
    @property
    def ano(self) -> int:
        """Retorna o ano do orçamento."""
        return self._ano
    
    @ano.setter
    def ano(self, valor: int) -> None:
        """Define o ano com validação."""
        if not isinstance(valor, int) or valor < 1900 or valor > 2100:
            raise ValueError("Ano deve ser um inteiro válido (1900-2100).")
        self._ano = valor
    
    @property
    def receitas_previstas(self) -> float:
        """Retorna as receitas previstas."""
        return self._receitas_previstas
    
    @receitas_previstas.setter
    def receitas_previstas(self, valor: float) -> None:
        """Define as receitas previstas com validação."""
        if not isinstance(valor, (int, float)):
            raise TypeError("Receitas previstas deve ser um número.")
        if valor < 0:
            raise ValueError("Receitas previstas não pode ser negativo.")
        self._receitas_previstas = float(valor)
    
    @property
    def lancamentos(self) -> list[Lancamento]:
        """Retorna a lista de lançamentos (cópia)."""
        return self._lancamentos.copy()
    
    @property
    def alertas(self) -> list[Alerta]:
        """Retorna a lista de alertas (cópia)."""
        return self._alertas.copy()
    
    @property
    def mes_ano(self) -> tuple[int, int]:
        """Retorna a tupla (mês, ano)."""
        return (self._mes, self._ano)
    
    # ==================== PROPRIEDADES CALCULADAS ====================
    
    @property
    def total_receitas(self) -> float:
        """Calcula o total de receitas do mês."""
        return sum(
            lanc.valor for lanc in self._lancamentos 
            if isinstance(lanc, Receita)
        )
    
    @property
    def total_despesas(self) -> float:
        """Calcula o total de despesas do mês."""
        return sum(
            lanc.valor for lanc in self._lancamentos 
            if isinstance(lanc, Despesa)
        )
    
    @property
    def saldo(self) -> float:
        """Calcula o saldo do mês (receitas - despesas)."""
        return self.total_receitas - self.total_despesas
    
    @property
    def saldo_disponivel(self) -> float:
        """Calcula o saldo disponível considerando receitas previstas."""
        return self._receitas_previstas - self.total_despesas
    
    @property
    def tem_deficit(self) -> bool:
        """Verifica se o mês está em déficit."""
        return self.saldo < 0
    
    @property
    def receitas(self) -> list[Receita]:
        """Retorna apenas as receitas do mês."""
        return [lanc for lanc in self._lancamentos if isinstance(lanc, Receita)]
    
    @property
    def despesas(self) -> list[Despesa]:
        """Retorna apenas as despesas do mês."""
        return [lanc for lanc in self._lancamentos if isinstance(lanc, Despesa)]
    
    # ==================== MÉTODOS DE GERENCIAMENTO ====================
    
    def adicionar_lancamento(self, lancamento: Lancamento) -> list[Alerta]:
        """
        Adiciona um lançamento ao orçamento.
        
        Args:
            lancamento: O lançamento a ser adicionado
            
        Returns:
            Lista de alertas gerados pelo lançamento
            
        Raises:
            ValueError: Se o lançamento não pertence a este mês
        """
        # Validar mês/ano do lançamento
        if lancamento.mes_ano != self.mes_ano:
            raise ValueError(
                f"Lançamento de {lancamento.data.strftime('%m/%Y')} não pertence "
                f"ao orçamento de {self._mes:02d}/{self._ano}."
            )
        
        # Verificar duplicidade
        if lancamento in self._lancamentos:
            raise ValueError("Lançamento já existe neste orçamento.")
        
        alertas_gerados: list[Alerta] = []
        
        # Para despesas, verificar limites e gerar alertas
        if isinstance(lancamento, Despesa):
            # Verificar alerta de alto valor
            if "ALTO_VALOR" in lancamento.alertas:
                alerta = Alerta.criar_alerta_alto_valor(lancamento.id, lancamento.valor)
                alertas_gerados.append(alerta)
            
            # Verificar limite da categoria
            total_categoria = self.total_por_categoria(lancamento.categoria)
            if lancamento.verificar_limite_categoria(total_categoria):
                alerta = Alerta.criar_alerta_limite_excedido(
                    lancamento.categoria.id,
                    lancamento.categoria.nome,
                    lancamento.categoria.limite_mensal,
                    total_categoria + lancamento.valor
                )
                alertas_gerados.append(alerta)
        
        # Adicionar lançamento
        self._lancamentos.append(lancamento)
        self._lancamentos.sort()  # Manter ordenado por data
        
        # Registrar alertas
        self._alertas.extend(alertas_gerados)
        
        # Verificar déficit após adicionar
        if self.tem_deficit:
            # Verificar se já existe alerta de déficit para este mês
            deficit_existente = any(
                a.tipo == TipoAlerta.DEFICIT_ORCAMENTARIO and a.mes_ano == self.mes_ano
                for a in self._alertas
            )
            if not deficit_existente:
                alerta_deficit = Alerta.criar_alerta_deficit(
                    self._mes, self._ano, self.saldo
                )
                alertas_gerados.append(alerta_deficit)
                self._alertas.append(alerta_deficit)
        
        return alertas_gerados
    
    def remover_lancamento(self, lancamento_id: str) -> Optional[Lancamento]:
        """
        Remove um lançamento pelo ID.
        
        Args:
            lancamento_id: ID do lançamento a remover
            
        Returns:
            O lançamento removido, ou None se não encontrado
        """
        for i, lanc in enumerate(self._lancamentos):
            if lanc.id == lancamento_id:
                return self._lancamentos.pop(i)
        return None
    
    def buscar_lancamento(self, lancamento_id: str) -> Optional[Lancamento]:
        """Busca um lançamento pelo ID."""
        for lanc in self._lancamentos:
            if lanc.id == lancamento_id:
                return lanc
        return None
    
    # ==================== MÉTODOS DE RELATÓRIO ====================
    
    def total_por_categoria(self, categoria: Categoria) -> float:
        """Calcula o total de lançamentos de uma categoria."""
        return sum(
            lanc.valor for lanc in self._lancamentos
            if lanc.categoria == categoria
        )
    
    def despesas_por_categoria(self) -> dict[str, float]:
        """Retorna o total de despesas agrupado por categoria."""
        totais: dict[str, float] = defaultdict(float)
        for lanc in self._lancamentos:
            if isinstance(lanc, Despesa):
                totais[lanc.categoria.nome] += lanc.valor
        return dict(totais)
    
    def despesas_por_forma_pagamento(self) -> dict[str, float]:
        """Retorna o total de despesas agrupado por forma de pagamento."""
        totais: dict[str, float] = defaultdict(float)
        for lanc in self._lancamentos:
            if isinstance(lanc, Despesa):
                totais[lanc.forma_pagamento.value] += lanc.valor
        return dict(totais)
    
    def percentual_por_categoria(self) -> dict[str, float]:
        """Retorna o percentual de cada categoria em relação ao total de despesas."""
        total = self.total_despesas
        if total == 0:
            return {}
        
        despesas_cat = self.despesas_por_categoria()
        return {
            cat: (valor / total) * 100 
            for cat, valor in despesas_cat.items()
        }
    
    def saldo_por_dia(self) -> dict[date, float]:
        """Calcula o saldo acumulado por dia do mês."""
        saldos: dict[date, float] = {}
        acumulado = 0.0
        
        for lanc in sorted(self._lancamentos, key=lambda x: x.data):
            if isinstance(lanc, Receita):
                acumulado += lanc.valor
            else:
                acumulado -= lanc.valor
            saldos[lanc.data] = acumulado
        
        return saldos
    
    # ==================== MÉTODOS ESPECIAIS ====================
    
    def __str__(self) -> str:
        """Representação amigável do orçamento."""
        return (
            f"Orçamento {self._mes:02d}/{self._ano} - "
            f"Receitas: R${self.total_receitas:.2f} | "
            f"Despesas: R${self.total_despesas:.2f} | "
            f"Saldo: R${self.saldo:.2f}"
        )
    
    def __repr__(self) -> str:
        """Representação técnica do orçamento."""
        return (
            f"OrcamentoMensal(id={self._id!r}, mes={self._mes!r}, "
            f"ano={self._ano!r}, lancamentos={len(self._lancamentos)})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compara orçamentos pelo mês/ano."""
        if not isinstance(other, OrcamentoMensal):
            return NotImplemented
        return self.mes_ano == other.mes_ano
    
    def __hash__(self) -> int:
        """Hash baseado no mês/ano."""
        return hash(self.mes_ano)
    
    def __lt__(self, other: "OrcamentoMensal") -> bool:
        """Ordenação por data (mais antigo primeiro)."""
        if not isinstance(other, OrcamentoMensal):
            return NotImplemented
        if self._ano != other._ano:
            return self._ano < other._ano
        return self._mes < other._mes
    
    def __len__(self) -> int:
        """Retorna o número de lançamentos."""
        return len(self._lancamentos)
    
    def __iter__(self) -> Iterator[Lancamento]:
        """Permite iterar sobre os lançamentos."""
        return iter(self._lancamentos)
    
    def __contains__(self, item: Lancamento) -> bool:
        """Verifica se um lançamento está no orçamento."""
        return item in self._lancamentos
    
    def __add__(self, other: "OrcamentoMensal") -> float:
        """Soma os saldos de dois orçamentos."""
        if not isinstance(other, OrcamentoMensal):
            return NotImplemented
        return self.saldo + other.saldo
    
    # ==================== MÉTODOS DE SERIALIZAÇÃO ====================
    
    def to_dict(self) -> dict:
        """Converte o orçamento para dicionário (serialização)."""
        return {
            "id": self._id,
            "mes": self._mes,
            "ano": self._ano,
            "receitas_previstas": self._receitas_previstas,
            "lancamentos_ids": [lanc.id for lanc in self._lancamentos],
            "alertas_ids": [alerta.id for alerta in self._alertas],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OrcamentoMensal":
        """Cria um orçamento a partir de um dicionário (sem lançamentos)."""
        return cls(
            id=data.get("id"),
            mes=data["mes"],
            ano=data["ano"],
            receitas_previstas=data.get("receitas_previstas", 0.0),
        )
