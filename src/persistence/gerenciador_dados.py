"""
Gerenciador de Dados - Camada de serviço para gerenciar todas as operações de dados.
"""

from datetime import date
from typing import Optional

from ..models.categoria import Categoria, TipoCategoria
from ..models.lancamento import Lancamento, Receita, Despesa, FormaPagamento
from ..models.orcamento import OrcamentoMensal
from ..models.alerta import Alerta, TipoAlerta
from .json_storage import JsonStorage


class GerenciadorDados:
    """
    Classe que gerencia todas as operações de dados do sistema.
    Atua como camada de serviço entre a interface e a persistência.
    
    Attributes:
        storage: Instância do JsonStorage para persistência
    """
    
    def __init__(self, data_dir: str = "data"):
        self._storage = JsonStorage(data_dir)
        self._storage.inicializar_dados()
        
        # Cache de dados
        self._categorias: list[Categoria] = []
        self._lancamentos: list[Lancamento] = []
        self._orcamentos: list[OrcamentoMensal] = []
        self._alertas: list[Alerta] = []
        
        # Carregar dados
        self._carregar_todos_dados()
    
    def _carregar_todos_dados(self) -> None:
        """Carrega todos os dados do armazenamento."""
        self._categorias = self._storage.carregar_categorias()
        self._alertas = self._storage.carregar_alertas()
        self._lancamentos = self._storage.carregar_lancamentos(self._categorias)
        self._orcamentos = self._storage.carregar_orcamentos(
            self._lancamentos, self._alertas
        )
    
    def _salvar_todos_dados(self) -> None:
        """Salva todos os dados no armazenamento."""
        self._storage.salvar_categorias(self._categorias)
        self._storage.salvar_lancamentos(self._lancamentos)
        self._storage.salvar_orcamentos(self._orcamentos)
        self._storage.salvar_alertas(self._alertas)
    
    # ==================== PROPRIEDADES ====================
    
    @property
    def categorias(self) -> list[Categoria]:
        """Retorna a lista de categorias."""
        return self._categorias.copy()
    
    @property
    def lancamentos(self) -> list[Lancamento]:
        """Retorna a lista de lançamentos."""
        return self._lancamentos.copy()
    
    @property
    def orcamentos(self) -> list[OrcamentoMensal]:
        """Retorna a lista de orçamentos."""
        return self._orcamentos.copy()
    
    @property
    def alertas(self) -> list[Alerta]:
        """Retorna a lista de alertas."""
        return self._alertas.copy()
    
    @property
    def alertas_nao_lidos(self) -> list[Alerta]:
        """Retorna a lista de alertas não lidos."""
        return [a for a in self._alertas if not a.lido]
    
    # ==================== OPERAÇÕES DE CATEGORIAS ====================
    
    def criar_categoria(
        self,
        nome: str,
        tipo: TipoCategoria,
        limite_mensal: Optional[float] = None,
        descricao: Optional[str] = None
    ) -> Categoria:
        """
        Cria uma nova categoria.
        
        Args:
            nome: Nome da categoria
            tipo: Tipo da categoria
            limite_mensal: Limite mensal (só para DESPESA)
            descricao: Descrição opcional
            
        Returns:
            A categoria criada
            
        Raises:
            ValueError: Se a categoria já existir
        """
        # Verificar duplicidade
        for cat in self._categorias:
            if cat.nome.lower() == nome.lower() and cat.tipo == tipo:
                raise ValueError(
                    f"Categoria '{nome}' do tipo {tipo.value} já existe."
                )
        
        categoria = Categoria(
            nome=nome,
            tipo=tipo,
            limite_mensal=limite_mensal,
            descricao=descricao
        )
        
        self._categorias.append(categoria)
        self._storage.salvar_categorias(self._categorias)
        
        return categoria
    
    def editar_categoria(
        self,
        categoria_id: str,
        nome: Optional[str] = None,
        limite_mensal: Optional[float] = None,
        descricao: Optional[str] = None
    ) -> Categoria:
        """
        Edita uma categoria existente.
        
        Args:
            categoria_id: ID da categoria a editar
            nome: Novo nome (opcional)
            limite_mensal: Novo limite (opcional)
            descricao: Nova descrição (opcional)
            
        Returns:
            A categoria editada
            
        Raises:
            ValueError: Se a categoria não for encontrada
        """
        categoria = self.buscar_categoria(categoria_id)
        if not categoria:
            raise ValueError(f"Categoria com ID '{categoria_id}' não encontrada.")
        
        if nome:
            # Verificar duplicidade do novo nome
            for cat in self._categorias:
                if cat.id != categoria_id and cat.nome.lower() == nome.lower() and cat.tipo == categoria.tipo:
                    raise ValueError(f"Categoria '{nome}' já existe neste tipo.")
            categoria.nome = nome
        
        if limite_mensal is not None:
            categoria.limite_mensal = limite_mensal
        
        if descricao is not None:
            categoria.descricao = descricao
        
        self._storage.salvar_categorias(self._categorias)
        return categoria
    
    def excluir_categoria(self, categoria_id: str) -> Optional[Categoria]:
        """
        Exclui uma categoria.
        
        Args:
            categoria_id: ID da categoria a excluir
            
        Returns:
            A categoria excluída, ou None se não encontrada
            
        Raises:
            ValueError: Se a categoria tiver lançamentos vinculados
        """
        # Verificar se há lançamentos vinculados
        lancamentos_vinculados = [
            l for l in self._lancamentos if l.categoria.id == categoria_id
        ]
        if lancamentos_vinculados:
            raise ValueError(
                f"Não é possível excluir: categoria possui "
                f"{len(lancamentos_vinculados)} lançamento(s) vinculado(s)."
            )
        
        for i, cat in enumerate(self._categorias):
            if cat.id == categoria_id:
                categoria = self._categorias.pop(i)
                self._storage.salvar_categorias(self._categorias)
                return categoria
        
        return None
    
    def buscar_categoria(self, categoria_id: str) -> Optional[Categoria]:
        """Busca uma categoria pelo ID."""
        for cat in self._categorias:
            if cat.id == categoria_id:
                return cat
        return None
    
    def buscar_categoria_por_nome(
        self, nome: str, tipo: TipoCategoria
    ) -> Optional[Categoria]:
        """Busca uma categoria pelo nome e tipo."""
        for cat in self._categorias:
            if cat.nome.lower() == nome.lower() and cat.tipo == tipo:
                return cat
        return None
    
    def listar_categorias(
        self, tipo: Optional[TipoCategoria] = None
    ) -> list[Categoria]:
        """Lista categorias, opcionalmente filtradas por tipo."""
        if tipo:
            return [c for c in self._categorias if c.tipo == tipo]
        return self._categorias.copy()
    
    def inicializar_categorias_padrao(self) -> None:
        """Inicializa as categorias padrão se não houver nenhuma."""
        if self._categorias:
            return
        
        config = self._storage.carregar_configuracoes()
        categorias_padrao = config.get("categorias_padrao", {})
        
        # Criar categorias de receita
        for cat_data in categorias_padrao.get("receitas", []):
            self.criar_categoria(
                nome=cat_data["nome"],
                tipo=TipoCategoria.RECEITA,
                descricao=cat_data.get("descricao")
            )
        
        # Criar categorias de despesa
        for cat_data in categorias_padrao.get("despesas", []):
            self.criar_categoria(
                nome=cat_data["nome"],
                tipo=TipoCategoria.DESPESA,
                limite_mensal=cat_data.get("limite_mensal"),
                descricao=cat_data.get("descricao")
            )
    
    # ==================== OPERAÇÕES DE LANÇAMENTOS ====================
    
    def adicionar_receita(
        self,
        valor: float,
        categoria_nome: str,
        data_lancamento: date,
        descricao: str,
        forma_pagamento: FormaPagamento = FormaPagamento.PIX
    ) -> tuple[Receita, list[Alerta]]:
        """
        Adiciona uma nova receita.
        
        Args:
            valor: Valor da receita
            categoria_nome: Nome da categoria
            data_lancamento: Data do lançamento
            descricao: Descrição do lançamento
            forma_pagamento: Forma de pagamento
            
        Returns:
            Tupla com a receita criada e lista de alertas gerados
        """
        # Buscar categoria
        categoria = self.buscar_categoria_por_nome(categoria_nome, TipoCategoria.RECEITA)
        if not categoria:
            raise ValueError(f"Categoria de receita '{categoria_nome}' não encontrada.")
        
        # Criar receita
        receita = Receita(
            valor=valor,
            categoria=categoria,
            data=data_lancamento,
            descricao=descricao,
            forma_pagamento=forma_pagamento
        )
        
        # Adicionar ao orçamento do mês
        orcamento = self._obter_ou_criar_orcamento(
            data_lancamento.month, data_lancamento.year
        )
        alertas = orcamento.adicionar_lancamento(receita)
        
        # Atualizar caches
        self._lancamentos.append(receita)
        self._alertas.extend(alertas)
        
        # Salvar
        self._salvar_todos_dados()
        
        return receita, alertas
    
    def adicionar_despesa(
        self,
        valor: float,
        categoria_nome: str,
        data_lancamento: date,
        descricao: str,
        forma_pagamento: FormaPagamento = FormaPagamento.DEBITO
    ) -> tuple[Despesa, list[Alerta]]:
        """
        Adiciona uma nova despesa.
        
        Args:
            valor: Valor da despesa
            categoria_nome: Nome da categoria
            data_lancamento: Data do lançamento
            descricao: Descrição do lançamento
            forma_pagamento: Forma de pagamento
            
        Returns:
            Tupla com a despesa criada e lista de alertas gerados
        """
        # Buscar categoria
        categoria = self.buscar_categoria_por_nome(categoria_nome, TipoCategoria.DESPESA)
        if not categoria:
            raise ValueError(f"Categoria de despesa '{categoria_nome}' não encontrada.")
        
        # Criar despesa
        despesa = Despesa(
            valor=valor,
            categoria=categoria,
            data=data_lancamento,
            descricao=descricao,
            forma_pagamento=forma_pagamento
        )
        
        # Adicionar ao orçamento do mês
        orcamento = self._obter_ou_criar_orcamento(
            data_lancamento.month, data_lancamento.year
        )
        alertas = orcamento.adicionar_lancamento(despesa)
        
        # Atualizar caches
        self._lancamentos.append(despesa)
        self._alertas.extend(alertas)
        
        # Salvar
        self._salvar_todos_dados()
        
        return despesa, alertas
    
    def excluir_lancamento(self, lancamento_id: str) -> Optional[Lancamento]:
        """
        Exclui um lançamento pelo ID.
        
        Args:
            lancamento_id: ID do lançamento
            
        Returns:
            O lançamento excluído, ou None se não encontrado
        """
        for i, lanc in enumerate(self._lancamentos):
            if lanc.id == lancamento_id:
                lancamento = self._lancamentos.pop(i)
                
                # Remover do orçamento correspondente
                for orc in self._orcamentos:
                    orc.remover_lancamento(lancamento_id)
                
                self._salvar_todos_dados()
                return lancamento
        
        return None
    
    def listar_lancamentos(
        self,
        mes: Optional[int] = None,
        ano: Optional[int] = None,
        tipo: Optional[str] = None,
        categoria_nome: Optional[str] = None
    ) -> list[Lancamento]:
        """
        Lista lançamentos com filtros opcionais.
        
        Args:
            mes: Filtrar por mês
            ano: Filtrar por ano
            tipo: Filtrar por tipo (RECEITA ou DESPESA)
            categoria_nome: Filtrar por nome da categoria
            
        Returns:
            Lista de lançamentos filtrados
        """
        resultado = self._lancamentos.copy()
        
        if mes and ano:
            resultado = [l for l in resultado if l.mes_ano == (mes, ano)]
        elif ano:
            resultado = [l for l in resultado if l.data.year == ano]
        
        if tipo:
            resultado = [l for l in resultado if l.tipo == tipo.upper()]
        
        if categoria_nome:
            resultado = [
                l for l in resultado 
                if l.categoria.nome.lower() == categoria_nome.lower()
            ]
        
        return sorted(resultado)
    
    # ==================== OPERAÇÕES DE ORÇAMENTO ====================
    
    def _obter_ou_criar_orcamento(
        self, mes: int, ano: int, receitas_previstas: float = 0.0
    ) -> OrcamentoMensal:
        """
        Obtém um orçamento existente ou cria um novo.
        
        Args:
            mes: Mês do orçamento
            ano: Ano do orçamento
            receitas_previstas: Receitas previstas para o mês
            
        Returns:
            O orçamento obtido ou criado
        """
        # Buscar existente
        for orc in self._orcamentos:
            if orc.mes == mes and orc.ano == ano:
                return orc
        
        # Criar novo
        orcamento = OrcamentoMensal(
            mes=mes,
            ano=ano,
            receitas_previstas=receitas_previstas
        )
        self._orcamentos.append(orcamento)
        self._orcamentos.sort()
        
        return orcamento
    
    def obter_orcamento(self, mes: int, ano: int) -> Optional[OrcamentoMensal]:
        """Obtém um orçamento pelo mês/ano."""
        for orc in self._orcamentos:
            if orc.mes == mes and orc.ano == ano:
                return orc
        return None
    
    def definir_receitas_previstas(
        self, mes: int, ano: int, receitas_previstas: float
    ) -> OrcamentoMensal:
        """
        Define as receitas previstas para um mês.
        
        Args:
            mes: Mês do orçamento
            ano: Ano do orçamento
            receitas_previstas: Valor das receitas previstas
            
        Returns:
            O orçamento atualizado
        """
        orcamento = self._obter_ou_criar_orcamento(mes, ano)
        orcamento.receitas_previstas = receitas_previstas
        self._storage.salvar_orcamentos(self._orcamentos)
        return orcamento
    
    # ==================== RELATÓRIOS ====================
    
    def relatorio_mensal(self, mes: int, ano: int) -> dict:
        """
        Gera relatório de um mês específico.
        
        Args:
            mes: Mês do relatório
            ano: Ano do relatório
            
        Returns:
            Dicionário com dados do relatório
        """
        orcamento = self.obter_orcamento(mes, ano)
        
        if not orcamento:
            return {
                "mes": mes,
                "ano": ano,
                "existe": False,
                "total_receitas": 0.0,
                "total_despesas": 0.0,
                "saldo": 0.0,
            }
        
        return {
            "mes": mes,
            "ano": ano,
            "existe": True,
            "total_receitas": orcamento.total_receitas,
            "total_despesas": orcamento.total_despesas,
            "saldo": orcamento.saldo,
            "receitas_previstas": orcamento.receitas_previstas,
            "saldo_disponivel": orcamento.saldo_disponivel,
            "tem_deficit": orcamento.tem_deficit,
            "despesas_por_categoria": orcamento.despesas_por_categoria(),
            "despesas_por_forma_pagamento": orcamento.despesas_por_forma_pagamento(),
            "percentual_por_categoria": orcamento.percentual_por_categoria(),
            "num_lancamentos": len(orcamento),
            "num_alertas": len(orcamento.alertas),
        }
    
    def relatorio_comparativo(self, meses: int = 3) -> list[dict]:
        """
        Gera relatório comparativo dos últimos meses.
        
        Args:
            meses: Número de meses a comparar
            
        Returns:
            Lista de relatórios mensais ordenados
        """
        # Ordenar orçamentos do mais recente ao mais antigo
        orcamentos_ordenados = sorted(self._orcamentos, reverse=True)
        
        # Pegar os últimos 'meses' orçamentos
        orcamentos_selecionados = orcamentos_ordenados[:meses]
        
        return [
            self.relatorio_mensal(orc.mes, orc.ano)
            for orc in orcamentos_selecionados
        ]
    
    def mes_mais_economico(self) -> Optional[dict]:
        """
        Encontra o mês com menor total de despesas.
        
        Returns:
            Dicionário com dados do mês mais econômico
        """
        if not self._orcamentos:
            return None
        
        orcamento_minimo = min(
            self._orcamentos,
            key=lambda o: o.total_despesas
        )
        
        return {
            "mes": orcamento_minimo.mes,
            "ano": orcamento_minimo.ano,
            "total_despesas": orcamento_minimo.total_despesas,
            "saldo": orcamento_minimo.saldo,
        }
    
    def estatisticas_gerais(self) -> dict:
        """
        Gera estatísticas gerais do sistema.
        
        Returns:
            Dicionário com estatísticas
        """
        total_receitas = sum(orc.total_receitas for orc in self._orcamentos)
        total_despesas = sum(orc.total_despesas for orc in self._orcamentos)
        
        return {
            "total_categorias": len(self._categorias),
            "total_lancamentos": len(self._lancamentos),
            "total_orcamentos": len(self._orcamentos),
            "total_alertas": len(self._alertas),
            "alertas_nao_lidos": len(self.alertas_nao_lidos),
            "total_receitas_geral": total_receitas,
            "total_despesas_geral": total_despesas,
            "saldo_geral": total_receitas - total_despesas,
        }
    
    # ==================== OPERAÇÕES DE ALERTAS ====================
    
    def marcar_alerta_como_lido(self, alerta_id: str) -> bool:
        """Marca um alerta como lido."""
        for alerta in self._alertas:
            if alerta.id == alerta_id:
                alerta.marcar_como_lido()
                self._storage.salvar_alertas(self._alertas)
                return True
        return False
    
    def marcar_todos_alertas_como_lidos(self) -> int:
        """Marca todos os alertas como lidos."""
        count = 0
        for alerta in self._alertas:
            if not alerta.lido:
                alerta.marcar_como_lido()
                count += 1
        self._storage.salvar_alertas(self._alertas)
        return count
