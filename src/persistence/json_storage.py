"""
Módulo de Persistência JSON - Funções para salvar e carregar dados em JSON.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from ..models.categoria import Categoria, TipoCategoria
from ..models.lancamento import Lancamento, Receita, Despesa, FormaPagamento
from ..models.orcamento import OrcamentoMensal
from ..models.alerta import Alerta, TipoAlerta


class JsonStorage:
    """
    Classe responsável pela persistência de dados em arquivos JSON.
    
    Attributes:
        data_dir: Diretório onde os arquivos JSON são armazenados
    """
    
    def __init__(self, data_dir: str = "data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de dados
        self._categorias_file = self._data_dir / "categorias.json"
        self._lancamentos_file = self._data_dir / "lancamentos.json"
        self._orcamentos_file = self._data_dir / "orcamentos.json"
        self._alertas_file = self._data_dir / "alertas.json"
        self._settings_file = self._data_dir / "settings.json"
    
    # ==================== PROPRIEDADES ====================
    
    @property
    def data_dir(self) -> Path:
        """Retorna o diretório de dados."""
        return self._data_dir
    
    # ==================== MÉTODOS DE CATEGORIAS ====================
    
    def salvar_categorias(self, categorias: list[Categoria]) -> None:
        """
        Salva a lista de categorias no arquivo JSON.
        
        Args:
            categorias: Lista de categorias a salvar
        """
        data = [cat.to_dict() for cat in categorias]
        self._escrever_json(self._categorias_file, data)
    
    def carregar_categorias(self) -> list[Categoria]:
        """
        Carrega as categorias do arquivo JSON.
        
        Returns:
            Lista de categorias carregadas
        """
        data = self._ler_json(self._categorias_file)
        if not data:
            return []
        return [Categoria.from_dict(cat_data) for cat_data in data]
    
    def adicionar_categoria(self, categoria: Categoria) -> None:
        """
        Adiciona uma categoria ao arquivo JSON.
        
        Args:
            categoria: Categoria a adicionar
        """
        categorias = self.carregar_categorias()
        
        # Verificar duplicidade
        for cat in categorias:
            if cat == categoria:
                raise ValueError(
                    f"Categoria '{categoria.nome}' do tipo {categoria.tipo.value} já existe."
                )
        
        categorias.append(categoria)
        self.salvar_categorias(categorias)
    
    def atualizar_categoria(self, categoria: Categoria) -> None:
        """
        Atualiza uma categoria existente.
        
        Args:
            categoria: Categoria com dados atualizados
        """
        categorias = self.carregar_categorias()
        
        for i, cat in enumerate(categorias):
            if cat.id == categoria.id:
                categorias[i] = categoria
                self.salvar_categorias(categorias)
                return
        
        raise ValueError(f"Categoria com ID '{categoria.id}' não encontrada.")
    
    def excluir_categoria(self, categoria_id: str) -> Optional[Categoria]:
        """
        Exclui uma categoria pelo ID.
        
        Args:
            categoria_id: ID da categoria a excluir
            
        Returns:
            A categoria excluída, ou None se não encontrada
        """
        categorias = self.carregar_categorias()
        
        for i, cat in enumerate(categorias):
            if cat.id == categoria_id:
                categoria_excluida = categorias.pop(i)
                self.salvar_categorias(categorias)
                return categoria_excluida
        
        return None
    
    def buscar_categoria(self, categoria_id: str) -> Optional[Categoria]:
        """
        Busca uma categoria pelo ID.
        
        Args:
            categoria_id: ID da categoria
            
        Returns:
            A categoria encontrada, ou None
        """
        categorias = self.carregar_categorias()
        for cat in categorias:
            if cat.id == categoria_id:
                return cat
        return None
    
    def buscar_categoria_por_nome(
        self, nome: str, tipo: TipoCategoria
    ) -> Optional[Categoria]:
        """
        Busca uma categoria pelo nome e tipo.
        
        Args:
            nome: Nome da categoria
            tipo: Tipo da categoria
            
        Returns:
            A categoria encontrada, ou None
        """
        categorias = self.carregar_categorias()
        for cat in categorias:
            if cat.nome.lower() == nome.lower() and cat.tipo == tipo:
                return cat
        return None
    
    # ==================== MÉTODOS DE LANÇAMENTOS ====================
    
    def salvar_lancamentos(self, lancamentos: list[Lancamento]) -> None:
        """
        Salva a lista de lançamentos no arquivo JSON.
        
        Args:
            lancamentos: Lista de lançamentos a salvar
        """
        data = [lanc.to_dict() for lanc in lancamentos]
        self._escrever_json(self._lancamentos_file, data)
    
    def carregar_lancamentos(self, categorias: list[Categoria]) -> list[Lancamento]:
        """
        Carrega os lançamentos do arquivo JSON.
        
        Args:
            categorias: Lista de categorias para vincular aos lançamentos
            
        Returns:
            Lista de lançamentos carregados
        """
        data = self._ler_json(self._lancamentos_file)
        if not data:
            return []
        
        # Criar mapa de categorias por ID
        cat_map = {cat.id: cat for cat in categorias}
        
        lancamentos = []
        for lanc_data in data:
            categoria = cat_map.get(lanc_data["categoria_id"])
            if not categoria:
                continue  # Pular lançamentos com categoria inválida
            
            lancamento = self._criar_lancamento_de_dict(lanc_data, categoria)
            if lancamento:
                lancamentos.append(lancamento)
        
        return lancamentos
    
    def _criar_lancamento_de_dict(
        self, data: dict, categoria: Categoria
    ) -> Optional[Lancamento]:
        """Cria um lançamento a partir de dados do dicionário."""
        tipo = data.get("tipo")
        
        kwargs = {
            "id": data.get("id"),
            "valor": data["valor"],
            "categoria": categoria,
            "data": date.fromisoformat(data["data"]),
            "descricao": data["descricao"],
            "forma_pagamento": FormaPagamento(data["forma_pagamento"]),
        }
        
        if tipo == "RECEITA":
            return Receita(**kwargs)
        elif tipo == "DESPESA":
            return Despesa(**kwargs)
        return None
    
    def adicionar_lancamento(
        self, lancamento: Lancamento, categorias: list[Categoria]
    ) -> None:
        """
        Adiciona um lançamento ao arquivo JSON.
        
        Args:
            lancamento: Lançamento a adicionar
            categorias: Lista de categorias para validação
        """
        lancamentos = self.carregar_lancamentos(categorias)
        lancamentos.append(lancamento)
        self.salvar_lancamentos(lancamentos)
    
    def excluir_lancamento(
        self, lancamento_id: str, categorias: list[Categoria]
    ) -> Optional[Lancamento]:
        """
        Exclui um lançamento pelo ID.
        
        Args:
            lancamento_id: ID do lançamento a excluir
            categorias: Lista de categorias para carregar lançamentos
            
        Returns:
            O lançamento excluído, ou None se não encontrado
        """
        lancamentos = self.carregar_lancamentos(categorias)
        
        for i, lanc in enumerate(lancamentos):
            if lanc.id == lancamento_id:
                lancamento_excluido = lancamentos.pop(i)
                self.salvar_lancamentos(lancamentos)
                return lancamento_excluido
        
        return None
    
    # ==================== MÉTODOS DE ORÇAMENTOS ====================
    
    def salvar_orcamentos(self, orcamentos: list[OrcamentoMensal]) -> None:
        """
        Salva a lista de orçamentos no arquivo JSON.
        
        Args:
            orcamentos: Lista de orçamentos a salvar
        """
        data = [orc.to_dict() for orc in orcamentos]
        self._escrever_json(self._orcamentos_file, data)
    
    def carregar_orcamentos(
        self, 
        lancamentos: list[Lancamento],
        alertas: list[Alerta]
    ) -> list[OrcamentoMensal]:
        """
        Carrega os orçamentos do arquivo JSON.
        
        Args:
            lancamentos: Lista de lançamentos para vincular
            alertas: Lista de alertas para vincular
            
        Returns:
            Lista de orçamentos carregados
        """
        data = self._ler_json(self._orcamentos_file)
        if not data:
            return []
        
        # Criar mapas por ID
        lanc_map = {lanc.id: lanc for lanc in lancamentos}
        alerta_map = {alerta.id: alerta for alerta in alertas}
        
        orcamentos = []
        for orc_data in data:
            orcamento = OrcamentoMensal.from_dict(orc_data)
            
            # Vincular lançamentos
            for lanc_id in orc_data.get("lancamentos_ids", []):
                if lanc_id in lanc_map:
                    orcamento._lancamentos.append(lanc_map[lanc_id])
            
            # Vincular alertas
            for alerta_id in orc_data.get("alertas_ids", []):
                if alerta_id in alerta_map:
                    orcamento._alertas.append(alerta_map[alerta_id])
            
            orcamentos.append(orcamento)
        
        return orcamentos
    
    def buscar_orcamento(
        self, mes: int, ano: int, lancamentos: list[Lancamento], alertas: list[Alerta]
    ) -> Optional[OrcamentoMensal]:
        """
        Busca um orçamento por mês/ano.
        
        Args:
            mes: Mês do orçamento
            ano: Ano do orçamento
            lancamentos: Lista de lançamentos
            alertas: Lista de alertas
            
        Returns:
            O orçamento encontrado, ou None
        """
        orcamentos = self.carregar_orcamentos(lancamentos, alertas)
        for orc in orcamentos:
            if orc.mes == mes and orc.ano == ano:
                return orc
        return None
    
    def criar_ou_atualizar_orcamento(
        self, 
        orcamento: OrcamentoMensal,
        lancamentos: list[Lancamento],
        alertas: list[Alerta]
    ) -> None:
        """
        Cria ou atualiza um orçamento.
        
        Args:
            orcamento: Orçamento a salvar
            lancamentos: Lista de lançamentos para carregar
            alertas: Lista de alertas para carregar
        """
        orcamentos = self.carregar_orcamentos(lancamentos, alertas)
        
        # Verificar se já existe
        for i, orc in enumerate(orcamentos):
            if orc.mes_ano == orcamento.mes_ano:
                orcamentos[i] = orcamento
                self.salvar_orcamentos(orcamentos)
                return
        
        # Adicionar novo
        orcamentos.append(orcamento)
        orcamentos.sort()
        self.salvar_orcamentos(orcamentos)
    
    # ==================== MÉTODOS DE ALERTAS ====================
    
    def salvar_alertas(self, alertas: list[Alerta]) -> None:
        """
        Salva a lista de alertas no arquivo JSON.
        
        Args:
            alertas: Lista de alertas a salvar
        """
        data = [alerta.to_dict() for alerta in alertas]
        self._escrever_json(self._alertas_file, data)
    
    def carregar_alertas(self) -> list[Alerta]:
        """
        Carrega os alertas do arquivo JSON.
        
        Returns:
            Lista de alertas carregados
        """
        data = self._ler_json(self._alertas_file)
        if not data:
            return []
        return [Alerta.from_dict(alerta_data) for alerta_data in data]
    
    def adicionar_alerta(self, alerta: Alerta) -> None:
        """
        Adiciona um alerta ao arquivo JSON.
        
        Args:
            alerta: Alerta a adicionar
        """
        alertas = self.carregar_alertas()
        alertas.append(alerta)
        self.salvar_alertas(alertas)
    
    def marcar_alerta_como_lido(self, alerta_id: str) -> bool:
        """
        Marca um alerta como lido.
        
        Args:
            alerta_id: ID do alerta
            
        Returns:
            True se o alerta foi marcado, False se não encontrado
        """
        alertas = self.carregar_alertas()
        
        for alerta in alertas:
            if alerta.id == alerta_id:
                alerta.marcar_como_lido()
                self.salvar_alertas(alertas)
                return True
        
        return False
    
    # ==================== MÉTODOS DE CONFIGURAÇÕES ====================
    
    def carregar_configuracoes(self) -> dict[str, Any]:
        """
        Carrega as configurações do arquivo settings.json.
        
        Returns:
            Dicionário com as configurações
        """
        data = self._ler_json(self._settings_file)
        return data if data else self._configuracoes_padrao()
    
    def salvar_configuracoes(self, config: dict[str, Any]) -> None:
        """
        Salva as configurações no arquivo settings.json.
        
        Args:
            config: Dicionário de configurações
        """
        self._escrever_json(self._settings_file, config)
    
    def _configuracoes_padrao(self) -> dict[str, Any]:
        """Retorna as configurações padrão do sistema."""
        return {
            "valor_minimo_alerta_alto_gasto": 500.0,
            "meses_comparativo": 3,
            "meta_economia_percentual": 20.0,
            "moeda": "BRL",
            "formato_data": "%d/%m/%Y",
        }
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _ler_json(self, filepath: Path) -> Optional[Any]:
        """
        Lê dados de um arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Dados lidos, ou None se o arquivo não existir
        """
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao ler {filepath}: {e}")
            return None
    
    def _escrever_json(self, filepath: Path, data: Any) -> None:
        """
        Escreve dados em um arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo
            data: Dados a escrever
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Erro ao escrever {filepath}: {e}")
            raise
    
    def inicializar_dados(self) -> None:
        """Inicializa os arquivos de dados se não existirem."""
        if not self._categorias_file.exists():
            self._escrever_json(self._categorias_file, [])
        if not self._lancamentos_file.exists():
            self._escrever_json(self._lancamentos_file, [])
        if not self._orcamentos_file.exists():
            self._escrever_json(self._orcamentos_file, [])
        if not self._alertas_file.exists():
            self._escrever_json(self._alertas_file, [])
    
    def limpar_dados(self) -> None:
        """Limpa todos os dados (cuidado!)."""
        self._escrever_json(self._categorias_file, [])
        self._escrever_json(self._lancamentos_file, [])
        self._escrever_json(self._orcamentos_file, [])
        self._escrever_json(self._alertas_file, [])
