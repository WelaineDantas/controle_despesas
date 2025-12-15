"""
Comandos CLI para gerenciamento de categorias.
"""

import click
from typing import Optional

from ..models.categoria import TipoCategoria
from .formatadores import get_gerenciador, parse_tipo_categoria


@click.group("categoria")
def categoria_group():
    """📁 Gerenciar categorias de receitas e despesas."""
    pass


@categoria_group.command("listar")
@click.option("--tipo", "-t", type=click.Choice(["receita", "despesa"]), help="Filtrar por tipo")
def listar_categorias(tipo: Optional[str]):
    """Lista todas as categorias cadastradas."""
    gerenciador = get_gerenciador()
    
    tipo_filtro = parse_tipo_categoria(tipo) if tipo else None
    categorias = gerenciador.listar_categorias(tipo_filtro)
    
    if not categorias:
        click.echo("📭 Nenhuma categoria cadastrada.")
        return
    
    click.echo("\n📁 CATEGORIAS CADASTRADAS")
    click.echo("=" * 60)
    
    # Agrupar por tipo
    receitas = [c for c in categorias if c.tipo == TipoCategoria.RECEITA]
    despesas = [c for c in categorias if c.tipo == TipoCategoria.DESPESA]
    
    if receitas and (not tipo or tipo == "receita"):
        click.echo("\n💚 RECEITAS:")
        for cat in sorted(receitas):
            click.echo(f"   • {cat.nome}")
            if cat.descricao:
                click.echo(f"     {cat.descricao}")
    
    if despesas and (not tipo or tipo == "despesa"):
        click.echo("\n❤️  DESPESAS:")
        for cat in sorted(despesas):
            limite = f" (Limite: R${cat.limite_mensal:.2f})" if cat.limite_mensal else ""
            click.echo(f"   • {cat.nome}{limite}")
            if cat.descricao:
                click.echo(f"     {cat.descricao}")
    
    click.echo()


@categoria_group.command("adicionar")
@click.option("--nome", "-n", required=True, help="Nome da categoria")
@click.option("--tipo", "-t", required=True, type=click.Choice(["receita", "despesa"]), help="Tipo da categoria")
@click.option("--limite", "-l", type=float, help="Limite mensal (apenas para despesas)")
@click.option("--descricao", "-d", help="Descrição da categoria")
def adicionar_categoria(nome: str, tipo: str, limite: Optional[float], descricao: Optional[str]):
    """Adiciona uma nova categoria."""
    gerenciador = get_gerenciador()
    tipo_cat = parse_tipo_categoria(tipo)
    
    try:
        categoria = gerenciador.criar_categoria(
            nome=nome,
            tipo=tipo_cat,
            limite_mensal=limite,
            descricao=descricao
        )
        click.echo(f"✅ Categoria '{categoria.nome}' criada com sucesso!")
    except ValueError as e:
        click.echo(f"❌ Erro: {e}", err=True)


@categoria_group.command("editar")
@click.argument("nome_atual")
@click.option("--tipo", "-t", required=True, type=click.Choice(["receita", "despesa"]), help="Tipo da categoria")
@click.option("--novo-nome", "-n", help="Novo nome")
@click.option("--limite", "-l", type=float, help="Novo limite mensal")
@click.option("--descricao", "-d", help="Nova descrição")
def editar_categoria(nome_atual: str, tipo: str, novo_nome: Optional[str], limite: Optional[float], descricao: Optional[str]):
    """Edita uma categoria existente."""
    gerenciador = get_gerenciador()
    tipo_cat = parse_tipo_categoria(tipo)
    categoria = gerenciador.buscar_categoria_por_nome(nome_atual, tipo_cat)
    
    if not categoria:
        click.echo(f"❌ Categoria '{nome_atual}' não encontrada.", err=True)
        return
    
    try:
        gerenciador.editar_categoria(
            categoria_id=categoria.id,
            nome=novo_nome,
            limite_mensal=limite,
            descricao=descricao
        )
        click.echo(f"✅ Categoria editada com sucesso!")
    except ValueError as e:
        click.echo(f"❌ Erro: {e}", err=True)


@categoria_group.command("excluir")
@click.argument("nome")
@click.option("--tipo", "-t", required=True, type=click.Choice(["receita", "despesa"]), help="Tipo da categoria")
@click.confirmation_option(prompt="Tem certeza que deseja excluir esta categoria?")
def excluir_categoria(nome: str, tipo: str):
    """Exclui uma categoria."""
    gerenciador = get_gerenciador()
    tipo_cat = parse_tipo_categoria(tipo)
    categoria = gerenciador.buscar_categoria_por_nome(nome, tipo_cat)
    
    if not categoria:
        click.echo(f"❌ Categoria '{nome}' não encontrada.", err=True)
        return
    
    try:
        gerenciador.excluir_categoria(categoria.id)
        click.echo(f"✅ Categoria '{nome}' excluída com sucesso!")
    except ValueError as e:
        click.echo(f"❌ Erro: {e}", err=True)
