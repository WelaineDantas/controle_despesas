"""
Funções auxiliares de formatação e parsing para a CLI.
"""

import click
from datetime import datetime, date
from typing import Optional

from ..models.categoria import TipoCategoria
from ..models.lancamento import FormaPagamento
from ..persistence.gerenciador_dados import GerenciadorDados


# Instância global do gerenciador
_gerenciador: Optional[GerenciadorDados] = None


def get_gerenciador() -> GerenciadorDados:
    """Obtém ou cria a instância do gerenciador."""
    global _gerenciador
    if _gerenciador is None:
        _gerenciador = GerenciadorDados()
        _gerenciador.inicializar_categorias_padrao()
    return _gerenciador


def parse_data(data_str: str) -> date:
    """Converte string para data."""
    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    raise click.BadParameter(f"Data inválida: {data_str}. Use DD/MM/YYYY")


def parse_forma_pagamento(forma: str) -> FormaPagamento:
    """Converte string para FormaPagamento."""
    mapa = {
        "dinheiro": FormaPagamento.DINHEIRO,
        "debito": FormaPagamento.DEBITO,
        "credito": FormaPagamento.CREDITO,
        "pix": FormaPagamento.PIX,
    }
    forma_lower = forma.lower()
    if forma_lower not in mapa:
        raise click.BadParameter(
            f"Forma de pagamento inválida: {forma}. "
            f"Use: {', '.join(mapa.keys())}"
        )
    return mapa[forma_lower]


def parse_tipo_categoria(tipo: str) -> TipoCategoria:
    """Converte string para TipoCategoria."""
    return TipoCategoria.RECEITA if tipo == "receita" else TipoCategoria.DESPESA


def formatar_valor(valor: float) -> str:
    """Formata valor monetário."""
    return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
