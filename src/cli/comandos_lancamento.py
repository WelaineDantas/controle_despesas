"""
Comandos CLI para gerenciamento de lançamentos (receitas e despesas).
"""

import click
from typing import Optional

from .formatadores import get_gerenciador, parse_data, parse_forma_pagamento


@click.command("adicionar-receita")
@click.option("--valor", "-v", required=True, type=float, help="Valor da receita")
@click.option("--categoria", "-c", required=True, help="Nome da categoria")
@click.option("--data", "-d", required=True, help="Data (DD/MM/YYYY)")
@click.option("--descricao", "-D", required=True, help="Descrição")
@click.option("--pagamento", "-p", default="pix", help="Forma de pagamento (dinheiro/debito/credito/pix)")
def adicionar_receita(valor: float, categoria: str, data: str, descricao: str, pagamento: str):
    """💚 Adiciona uma nova receita."""
    gerenciador = get_gerenciador()
    
    try:
        data_lancamento = parse_data(data)
        forma_pagamento = parse_forma_pagamento(pagamento)
        
        receita, alertas = gerenciador.adicionar_receita(
            valor=valor,
            categoria_nome=categoria,
            data_lancamento=data_lancamento,
            descricao=descricao,
            forma_pagamento=forma_pagamento
        )
        
        click.echo(f"✅ Receita adicionada com sucesso!")
        click.echo(f"   💰 Valor: R${valor:.2f}")
        click.echo(f"   📁 Categoria: {categoria}")
        click.echo(f"   📅 Data: {data_lancamento.strftime('%d/%m/%Y')}")
        
    except ValueError as e:
        click.echo(f"❌ Erro: {e}", err=True)


@click.command("adicionar-despesa")
@click.option("--valor", "-v", required=True, type=float, help="Valor da despesa")
@click.option("--categoria", "-c", required=True, help="Nome da categoria")
@click.option("--data", "-d", required=True, help="Data (DD/MM/YYYY)")
@click.option("--descricao", "-D", required=True, help="Descrição")
@click.option("--pagamento", "-p", default="debito", help="Forma de pagamento (dinheiro/debito/credito/pix)")
def adicionar_despesa(valor: float, categoria: str, data: str, descricao: str, pagamento: str):
    """❤️  Adiciona uma nova despesa."""
    gerenciador = get_gerenciador()
    
    try:
        data_lancamento = parse_data(data)
        forma_pagamento = parse_forma_pagamento(pagamento)
        
        despesa, alertas = gerenciador.adicionar_despesa(
            valor=valor,
            categoria_nome=categoria,
            data_lancamento=data_lancamento,
            descricao=descricao,
            forma_pagamento=forma_pagamento
        )
        
        click.echo(f"✅ Despesa adicionada com sucesso!")
        click.echo(f"   💸 Valor: R${valor:.2f}")
        click.echo(f"   📁 Categoria: {categoria}")
        click.echo(f"   📅 Data: {data_lancamento.strftime('%d/%m/%Y')}")
        
        # Mostrar alertas se houver
        if alertas:
            click.echo("\n⚠️  ALERTAS:")
            for alerta in alertas:
                click.echo(f"   {alerta}")
        
    except ValueError as e:
        click.echo(f"❌ Erro: {e}", err=True)


@click.command("listar-lancamentos")
@click.option("--mes", "-m", type=int, help="Filtrar por mês (1-12)")
@click.option("--ano", "-a", type=int, help="Filtrar por ano")
@click.option("--tipo", "-t", type=click.Choice(["receita", "despesa"]), help="Filtrar por tipo")
@click.option("--categoria", "-c", help="Filtrar por categoria")
def listar_lancamentos(mes: Optional[int], ano: Optional[int], tipo: Optional[str], categoria: Optional[str]):
    """📋 Lista lançamentos com filtros opcionais."""
    gerenciador = get_gerenciador()
    
    lancamentos = gerenciador.listar_lancamentos(
        mes=mes,
        ano=ano,
        tipo=tipo,
        categoria_nome=categoria
    )
    
    if not lancamentos:
        click.echo("📭 Nenhum lançamento encontrado.")
        return
    
    click.echo(f"\n📋 LANÇAMENTOS ({len(lancamentos)} encontrados)")
    click.echo("=" * 70)
    
    total_receitas = 0.0
    total_despesas = 0.0
    
    for lanc in lancamentos:
        icone = "💚" if lanc.tipo == "RECEITA" else "❤️ "
        click.echo(
            f"{icone} {lanc.data.strftime('%d/%m/%Y')} | "
            f"R${lanc.valor:>10.2f} | "
            f"{lanc.categoria.nome:<15} | "
            f"{lanc.descricao}"
        )
        
        if lanc.tipo == "RECEITA":
            total_receitas += lanc.valor
        else:
            total_despesas += lanc.valor
    
    click.echo("=" * 70)
    click.echo(f"💚 Total Receitas: R${total_receitas:.2f}")
    click.echo(f"❤️  Total Despesas: R${total_despesas:.2f}")
    click.echo(f"💰 Saldo: R${total_receitas - total_despesas:.2f}")
    click.echo()
