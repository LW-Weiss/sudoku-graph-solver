from interfaces import ISolver, ISolutionCounter, IGraph

class NaiveBacktrackingSolver(ISolver):
    """
    Implementa o algoritmo de backtracking (busca em profundidade) para
    resolver um Sudoku, tratando-o como um problema de coloração de grafos.
    
    Esta classe é "stateless" (sem estado), ela opera nos objetos
    grid e graph fornecidos no método solve().
    """

    def solve(self, grid: list[list[int]], graph: IGraph) -> bool:
        """
        Método público para iniciar a resolução do Sudoku.

        Args:
            grid (list[list[int]]): O tabuleiro 2D (estado atual).
            graph (IGraph): A representação do grafo (regras/adjacência).

        Returns:
            bool: True se uma solução foi encontrada, False caso contrário.
        """
        # Armazena referências temporárias para a execução recursiva
        self.grid = grid
        self.graph = graph
        self.tamanho = len(grid)
        
        # Inicia a recursão
        return self._resolver()

    def _encontrar_proximo_vazio(self) -> tuple[int, int] | None:
        """
        Encontra a próxima célula vazia (valor 0) no grid.
        Na Teoria dos Grafos: "Encontra o próximo vértice não colorido".
        """
        for l in range(self.tamanho):
            for c in range(self.tamanho):
                if self.grid[l][c] == 0:
                    return (l, c)
        return None # Nenhuma célula vazia, o grid está completo.

    def _is_coloracao_valida(self, v: int, cor: int) -> bool:
        """
        Verifica se uma 'cor' (dígito) pode ser colocada no vértice 'v'
        sem conflitar com seus vizinhos já coloridos.
        """
        # Itera por todos os vizinhos (mesma linha, coluna ou bloco)
        for vizinho in self.graph.get_vizinhos(v):
            # Converte o vértice vizinho em coordenadas
            (l_viz, c_viz) = self.graph.vertice_para_grid(vizinho)
            
            # Verifica se o vizinho já tem a cor que estamos tentando usar
            if self.grid[l_viz][c_viz] == cor:
                return False
        
        # Nenhuma colisão encontrada
        return True
    
    def _resolver(self) -> bool:
        """
        O núcleo do algoritmo de backtracking recursivo.
        """
        # 1. Encontrar o próximo vértice a colorir
        celula_vazia = self._encontrar_proximo_vazio()

        # 2. Caso Base (Sucesso):
        # Se não há células vazias, o grid está completo.
        if celula_vazia is None:
            return True # Solução encontrada!

        # 3. Preparar Recursão:
        linha, col = celula_vazia
        v = self.graph.grid_para_vertice(linha, col)

        # 4. Caso Recursivo (Tentar cores de 1 a 9)
        for cor in range(1, self.tamanho + 1):
            
            # 4a. Verificar restrições (Checar vizinhos)
            if self._is_coloracao_valida(v, cor):
                
                # 4b. Tentar (Colorir o vértice)
                self.grid[linha][col] = cor
                
                # 4c. Chamar recursão
                if self._resolver():
                    return True # Sucesso! Propagar a solução para cima.
                
                # 4d. Desfazer (Backtrack)
                # Se a recursão falhou (retornou False), desfazemos a tentativa.
                self.grid[linha][col] = 0
        
        # 5. Caso Base (Falha):
        # Se todas as cores (1-9) falharam para esta célula.
        return False


class SmartBacktrackingSolver(ISolver):
    """
    Implementa Backtracking com otimizações:
    1. Forward Checking (calcula possibilidades antes de tentar).
    2. Heurística MRV (escolhe a célula com menos opções).
    """

    def solve(self, grid: list[list[int]], graph: IGraph) -> bool:
        self.grid = grid
        self.graph = graph
        self.tamanho = len(grid)
        
        return self._resolver()
    
    def _calcular_possibilidades(self, linha: int, col: int) -> set[int]:
        """
        Retorna um conjunto (set) com todas as cores válidas para esta célula,
        baseado nas cores já preenchidas nos vizinhos.
        """
        # 1. Pega o vértice no grafo
        v = self.graph.grid_para_vertice(linha, col)
        
        # 2. Começa assumindo que TUDO é possível (ex: {1, 2, ..., 9})
        possiveis = set(range(1, self.tamanho + 1))
        
        # 3. Remove as cores usadas pelos vizinhos
        for vizinho in self.graph.get_vizinhos(v):
            (l_viz, c_viz) = self.graph.vertice_para_grid(vizinho)
            val_vizinho = self.grid[l_viz][c_viz]
            
            if val_vizinho != 0: # Se o vizinho já tem cor
                possiveis.discard(val_vizinho) # Remove essa opção
                
        return possiveis

    def _encontrar_melhor_celula(self):
        """
        Encontra a célula vazia com o MENOR número de possibilidades (MRV).
        Retorna:
            - (linha, col): A melhor célula para preencher.
            - None: Se não houver células vazias (Sucesso!).
            - "FALHA": Se houver uma célula vazia com 0 possibilidades (Beco sem saída).
        """
        melhor_celula = None
        min_opcoes = self.tamanho + 1 # Valor inicial alto para comparação
        
        tem_vazio = False # Flag para saber se o tabuleiro já está cheio

        for l in range(self.tamanho):
            for c in range(self.tamanho):
                if self.grid[l][c] == 0:
                    tem_vazio = True
                    
                    # Calcula quantas opções essa célula tem
                    opcoes = self._calcular_possibilidades(l, c)
                    qtd = len(opcoes)
                    
                    # PODA IMEDIATA: Se achamos uma célula sem opções, 
                    # o tabuleiro atual é inválido.
                    if qtd == 0:
                        return "FALHA"
                    
                    # Atualiza a melhor célula se essa tiver menos opções
                    if qtd < min_opcoes:
                        min_opcoes = qtd
                        melhor_celula = (l, c)
                        
                        # Otimização extra: Se só tem 1 opção, é impossível ser melhor.
                        # Retorna logo para economizar tempo.
                        if min_opcoes == 1:
                            return melhor_celula

        if not tem_vazio:
            return None # Tabuleiro completo!
            
        return melhor_celula
    
    def _resolver(self) -> bool:
        # 1. Pergunta para o Seletor qual a próxima célula
        resultado = self._encontrar_melhor_celula()
        
        # Caso Base 1: Beco sem saída detectado antecipadamente
        if resultado == "FALHA":
            return False
            
        # Caso Base 2: Sucesso (não há mais vazios)
        if resultado is None:
            return True
            
        # Preparação
        linha, col = resultado
        
        # 2. Busca apenas as cores VÁLIDAS (otimização do loop)
        cores_validas = self._calcular_possibilidades(linha, col)
        
        for cor in cores_validas:
            # Tentar
            self.grid[linha][col] = cor
            
            # Recursão
            if self._resolver():
                return True
            
            # Backtrack (Desfazer)
            self.grid[linha][col] = 0
            
        return False


class BacktrackingCounter(ISolutionCounter):
    def count_solutions(self, grid, graph) -> int:
        self.grid = grid
        self.graph = graph
        self.tamanho = len(grid)
        self.contador_solucoes = 0

        self._contar_recursivo()

        return self.contador_solucoes
    
    def _contar_recursivo(self):
            # 1. Encontra o próximo vértice a colorir
            celula_vazia = self._encontrar_proximo_vazio()

            # 2. Caso Base (Sucesso):
            # Se não há células vazias, uma solução completa foi encontrada.
            if celula_vazia is None:
                self.contador_solucoes += 1 # Incrementa o contador
                return False # Retorna False para FORÇAR a continuação da busca

            # 3. Preparar Recursão:
            linha, col = celula_vazia
            v = self.graph.grid_para_vertice(linha, col)

            # 4. Caso Recursivo (Tentar cores de 1 a 9)
            for cor in range(1, self.tamanho + 1):
                
                # 4a. Verificar restrições (Checar vizinhos)
                if self._is_coloracao_valida(v, cor):
                    
                    # 4b. Tentar (Colorir o vértice)
                    self.grid[linha][col] = cor
                    
                    # 4c. Chamar recursão
                    #    Note que NÃO retornamos True aqui.
                    #    Nós apenas chamamos a função para continuar a busca.
                    self._contar_recursivo()
                    
                    # 4d. Desfazer (Backtrack)
                    # O backtrack acontece IMEDIATAMENTE após a chamada recursiva,
                    # para que o loop 'for' possa tentar a próxima cor.
                    self.grid[linha][col] = 0
            
            # 5. Caso Base (Falha):
            # Se todas as cores (1-9) falharam para esta célula.
            return False

    def _encontrar_proximo_vazio(self) -> tuple[int, int] | None:
        """
        Encontra a próxima célula vazia (valor 0) no grid.
        Na Teoria dos Grafos: "Encontra o próximo vértice não colorido".
        """
        for l in range(self.tamanho):
            for c in range(self.tamanho):
                if self.grid[l][c] == 0:
                    return (l, c)
        return None # Nenhuma célula vazia, o grid está completo.

    def _is_coloracao_valida(self, v: int, cor: int) -> bool:
        """
        Verifica se uma 'cor' (dígito) pode ser colocada no vértice 'v'
        sem conflitar com seus vizinhos já coloridos.
        """
        # Itera por todos os vizinhos (mesma linha, coluna ou bloco)
        for vizinho in self.graph.get_vizinhos(v):
            # Converte o vértice vizinho em coordenadas
            (l_viz, c_viz) = self.graph.vertice_para_grid(vizinho)
            
            # Verifica se o vizinho já tem a cor que estamos tentando usar
            if self.grid[l_viz][c_viz] == cor:
                return False
        
        # Nenhuma colisão encontrada
        return True
        