"""
Comandos CLI para relatorios e estatisticas.
"""

import click

from .formatadores import get_gerenciador


@click.command("relatorio-mensal")
@click.option("--mes", "-m", required=True, type=int, help="Mes (1-12)")
@click.option("--ano", "-a", required=True, type=int, help="Ano")
def relatorio_mensal(mes: int, ano: int):
    """Gera relatorio de um mes especifico."""
    gerenciador = get_gerenciador()

    if not 1 <= mes <= 12:
        click.echo("[ERRO] Mes deve ser entre 1 e 12.", err=True)
        return

    relatorio = gerenciador.relatorio_mensal(mes, ano)

    click.echo(f"\nRELATORIO MENSAL - {mes:02d}/{ano}")
    click.echo("=" * 50)

    if not relatorio["existe"]:
        click.echo("[INFO] Nenhum dado encontrado para este mes.")
        return

    click.echo(f"\nRESUMO FINANCEIRO:")
    click.echo(f"    Receitas:         R${relatorio['total_receitas']:>12.2f}")
    click.echo(f"    Despesas:         R${relatorio['total_despesas']:>12.2f}")
    click.echo(f"    -----------------------------------")
    click.echo(f"    Saldo:            R${relatorio['saldo']:>12.2f}")

    if relatorio["tem_deficit"]:
        click.echo(f"\n    [!] ATENCAO: Mes em DEFICIT!")

    # Despesas por categoria
    if relatorio["despesas_por_categoria"]:
        click.echo(f"\nDESPESAS POR CATEGORIA:")
        for cat, valor in sorted(relatorio["despesas_por_categoria"].items(), key=lambda x: -x[1]):
            percentual = relatorio["percentual_por_categoria"].get(cat, 0)
            barra = "#" * int(percentual / 5)
            click.echo(f"    {cat:<15} R${valor:>10.2f} ({percentual:>5.1f}%) {barra}")

    # Despesas por forma de pagamento
    if relatorio["despesas_por_forma_pagamento"]:
        click.echo(f"\nDESPESAS POR FORMA DE PAGAMENTO:")
        for forma, valor in sorted(relatorio["despesas_por_forma_pagamento"].items(), key=lambda x: -x[1]):
            click.echo(f"    {forma:<15} R${valor:>10.2f}")

    click.echo()


@click.command("relatorio-comparativo")
@click.option("--meses", "-m", default=3, type=int, help="Numero de meses a comparar")
def relatorio_comparativo(meses: int):
    """Gera relatorio comparativo dos ultimos meses."""
    gerenciador = get_gerenciador()

    relatorios = gerenciador.relatorio_comparativo(meses)

    if not relatorios:
        click.echo("[INFO] Nenhum dado encontrado para comparacao.")
        return

    click.echo(f"\nRELATORIO COMPARATIVO - Ultimos {len(relatorios)} meses")
    click.echo("=" * 70)

    # Cabecalho
    click.echo(f"{'Mes/Ano':<12} {'Receitas':>15} {'Despesas':>15} {'Saldo':>15} {'Status':<12}")
    click.echo("-" * 70)

    for rel in relatorios:
        status = "[!] Deficit" if rel.get("tem_deficit") else "[+] Positivo"
        click.echo(
            f"{rel['mes']:02d}/{rel['ano']:<8} "
            f"R${rel['total_receitas']:>12.2f} "
            f"R${rel['total_despesas']:>12.2f} "
            f"R${rel['saldo']:>12.2f} "
            f"{status}"
        )

    click.echo()


@click.command("estatisticas")
def estatisticas():
    """Mostra estatisticas gerais do sistema."""
    gerenciador = get_gerenciador()

    stats = gerenciador.estatisticas_gerais()
    mes_economico = gerenciador.mes_mais_economico()

    click.echo("\nESTATISTICAS GERAIS")
    click.echo("=" * 50)

    click.echo(f"\n    Categorias cadastradas:    {stats['total_categorias']}")
    click.echo(f"    Lancamentos registrados:   {stats['total_lancamentos']}")
    click.echo(f"    Orcamentos mensais:        {stats['total_orcamentos']}")
    click.echo(f"    Alertas totais:            {stats['total_alertas']}")
    click.echo(f"    Alertas nao lidos:         {stats['alertas_nao_lidos']}")

    click.echo(f"\nTOTAIS ACUMULADOS:")
    click.echo(f"    Receitas: R${stats['total_receitas_geral']:>12.2f}")
    click.echo(f"    Despesas: R${stats['total_despesas_geral']:>12.2f}")
    click.echo(f"    Saldo:    R${stats['saldo_geral']:>12.2f}")

    if mes_economico:
        click.echo(f"\nMES MAIS ECONOMICO:")
        click.echo(f"    {mes_economico['mes']:02d}/{mes_economico['ano']} - Despesas: R${mes_economico['total_despesas']:.2f}")

    click.echo()
