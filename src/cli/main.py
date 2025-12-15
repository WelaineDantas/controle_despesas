"""
CLI Principal - Interface de linha de comando para o sistema de finanças.
"""

import click

from .formatadores import get_gerenciador
from .comandos_categoria import categoria_group
from .comandos_lancamento import adicionar_receita, adicionar_despesa, listar_lancamentos
from .comandos_relatorio import relatorio_mensal, relatorio_comparativo, estatisticas
from .comandos_alerta import listar_alertas, marcar_alertas_lidos


@click.group()
@click.version_option(version="1.0.0", prog_name="Controle de Despesas")
def cli():
    """
    💰 Sistema de Controle de Despesas e Receitas.
    
    Gerencie suas finanças pessoais com facilidade!
    """
    pass


# Registrar grupos de comandos
cli.add_command(categoria_group)

# Registrar comandos de lançamentos
cli.add_command(adicionar_receita)
cli.add_command(adicionar_despesa)
cli.add_command(listar_lancamentos)

# Registrar comandos de relatórios
cli.add_command(relatorio_mensal)
cli.add_command(relatorio_comparativo)
cli.add_command(estatisticas)

# Registrar comandos de alertas
cli.add_command(listar_alertas)
cli.add_command(marcar_alertas_lidos)


@cli.command("inicializar")
def inicializar():
    """🚀 Inicializa o sistema com categorias padrão."""
    gerenciador = get_gerenciador()
    
    gerenciador.inicializar_categorias_padrao()
    click.echo("✅ Sistema inicializado com categorias padrão!")
    click.echo("\n💡 Use 'financas categoria listar' para ver as categorias disponíveis.")


if __name__ == "__main__":
    cli()
