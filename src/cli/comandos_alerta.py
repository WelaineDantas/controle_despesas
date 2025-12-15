"""
Comandos CLI para gerenciamento de alertas.
"""

import click

from .formatadores import get_gerenciador


@click.command("alertas")
@click.option("--todos", "-a", is_flag=True, help="Mostrar todos os alertas (incluindo lidos)")
def listar_alertas(todos: bool):
    """🔔 Lista alertas do sistema."""
    gerenciador = get_gerenciador()
    
    if todos:
        alertas = gerenciador.alertas
    else:
        alertas = gerenciador.alertas_nao_lidos
    
    if not alertas:
        click.echo("✅ Nenhum alerta pendente!")
        return
    
    click.echo(f"\n🔔 ALERTAS ({len(alertas)} encontrados)")
    click.echo("=" * 60)
    
    for alerta in sorted(alertas):
        click.echo(f"   {alerta}")
    
    click.echo()


@click.command("marcar-alertas-lidos")
def marcar_alertas_lidos():
    """✅ Marca todos os alertas como lidos."""
    gerenciador = get_gerenciador()
    
    count = gerenciador.marcar_todos_alertas_como_lidos()
    
    if count > 0:
        click.echo(f"✅ {count} alerta(s) marcado(s) como lido(s).")
    else:
        click.echo("📭 Nenhum alerta pendente para marcar.")
