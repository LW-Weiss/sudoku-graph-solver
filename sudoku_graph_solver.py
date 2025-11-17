from abc import ABC, abstractmethod
import time
import copy
import random


# ---------------------------------------------------------------------------- #
#                                   Interface                                  #
# ---------------------------------------------------------------------------- #

class IGraph(ABC):
    """Define o contrato para a topologia do grafo Sudoku."""
    
    @abstractmethod
    def get_vizinhos(self, v: int) -> set:
        """Retorna os vizinhos (vértices adjacentes) do vértice v."""
        pass
        
    @abstractmethod
    def vertice_para_grid(self, v: int) -> tuple[int, int]:
        """Converte um índice de vértice (ex: 0-80) para coordenadas (linha, col)."""
        pass
        
    @abstractmethod
    def grid_para_vertice(self, linha: int, col: int) -> int:
        """Converte coordenadas (linha, col) para um índice de vértice."""
        pass


class ISolver(ABC):
    @abstractmethod
    def solve(self, grid: list[list[int]], graph: IGraph) -> bool:
        pass

class ISolutionCounter(ABC):
    @abstractmethod
    def count_solutions(self) -> int:
        pass


# ---------------------------------------------------------------------------- #
#                                 Dependencias                                 #
# ---------------------------------------------------------------------------- #

class SudokuGraph(IGraph):
    def __init__(self, n=3):
        self.n = n
        self.tamanho = n**2
        self.num_vertices = n**4

        self.construir_grafo()

    def vertice_para_grid(self, v: int) -> tuple[int, int]:
        linha = v // self.tamanho
        col = v % self.tamanho

        return (linha, col)
    
    def grid_para_vertice(self, linha: int, col: int) -> int:
        v = linha * self.tamanho + col

        return v
    
    def construir_grafo(self):
        adj = {}
        for i in range(0, self.num_vertices):
            adj[i] = set()
            linha, coluna = self.vertice_para_grid(i)

            for col_vizinha in range(0, self.tamanho):
                if coluna != col_vizinha:
                    adj[i].add(self.grid_para_vertice(linha, col_vizinha))

            for linha_vizinha in range(0, self.tamanho):
                if linha != linha_vizinha:
                    adj[i].add(self.grid_para_vertice(linha_vizinha, coluna))

            # 1. Encontra o canto superior esquerdo do bloco
            inicio_linha = (linha // self.n) * self.n
            inicio_col = (coluna // self.n) * self.n

            # 2. Itera por todas as células dentro desse bloco
            for i_bloco in range(self.n):
                for j_bloco in range(self.n):
                    
                    # Encontra a coordenada absoluta do vizinho no grid
                    linha_vizinha = inicio_linha + i_bloco
                    coluna_vizinha = inicio_col + j_bloco
                    
                    # Converte a coordenada para o índice do vértice
                    v_vizinho = self.grid_para_vertice(linha_vizinha, coluna_vizinha)
                    
                    # Adiciona o vizinho, se não for o próprio vértice 'i'
                    # O set() cuida automaticamente das duplicatas (vizinhas de linha/coluna)
                    if i != v_vizinho:
                        adj[i].add(v_vizinho)

        self.grafo_adj = adj
        return adj
    
    def get_vizinhos(self, v):
        return self.grafo_adj[v]
    

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
        

class PuzzleGenerator:
    """
    Responsável por gerar novos puzzles de Sudoku.
    Usa a Injeção de Dependência para desacoplar-se dos algoritmos
    específicos de resolução e contagem.
    """

    def __init__(self, solver: ISolver, counter: ISolutionCounter):
        """
        Inicializa o gerador com as 'ferramentas' necessárias.

        Args:
            solver: Um objeto que implementa ISolver (para criar a solução inicial).
            counter: Um objeto que implementa ISolutionCounter (para verificar a unicidade).
        """
        self.solver = solver
        self.counter = counter

    def gerar_puzzle(self, n: int) -> tuple[list[list[int]], list[list[int]]]:
        """
        Gera um novo puzzle de Sudoku com garantia de solução única.

        Args:
            n: O tamanho do bloco (ex: 3 para 9x9).

        Returns:
            Uma tupla contendo (puzzle, solucao)
        """
        
        # --- Passo 1: Criar a base (Grid e Grafo) ---
        graph = SudokuGraph(n=n)
        grid_vazio = [[0] * graph.tamanho for _ in range(graph.tamanho)]
        
        # --- Passo 2: Gerar uma solução completa ---
        # (Idealmente, você adicionaria aleatoriedade aqui, 
        # mas para este projeto, resolver um grid vazio funciona)
        print("Gerando solução base...")
        self.solver.solve(grid_vazio, graph)
        # Agora, 'grid_vazio' não está mais vazio, contém a solução.
        solucao_completa = copy.deepcopy(grid_vazio)
        
        # Este é o grid que vamos "cavar" para criar o puzzle
        puzzle_grid = copy.deepcopy(solucao_completa)
        
        # --- Passo 3: Preparar a Remoção (Poda) ---
        # Cria uma lista de todos os vértices (0 a 80) e a embaralha
        vertices = list(range(graph.num_vertices))
        random.shuffle(vertices)
        
        print(f"Iniciando a 'cavação' de {len(vertices)} células...")
        
        # --- Passo 4: Loop de Remoção e Verificação ---
        for v in vertices:
            (linha, col) = graph.vertice_para_grid(v)
            
            # Guarda o valor caso precisemos desfazer
            valor_removido = puzzle_grid[linha][col]
            
            # Pula se a célula já foi removida (ex: em um puzzle simétrico)
            if valor_removido == 0:
                continue

            # 4a. Tenta remover a pista
            puzzle_grid[linha][col] = 0
            
            # 4b. Verifica a Unicidade
            # É CRUCIAL usar uma cópia, pois o contador modifica o grid!
            grid_para_teste = copy.deepcopy(puzzle_grid)
            
            num_solucoes = self.counter.count_solutions(grid_para_teste, graph)
            
            # 4c. Decide
            if num_solucoes > 1:
                # Se tiver mais de uma solução, a remoção foi inválida.
                # Desfaz a remoção (coloca o número de volta).
                puzzle_grid[linha][col] = valor_removido
            # else:
                # Se num_solucoes == 1, a remoção foi válida! 
                # Deixa a célula como 0 e continua o loop.
        
        print("Geração concluída.")
        return (puzzle_grid, solucao_completa)

# ---------------------------------------------------------------------------- #
#                              Funções Auxiliares                              #
# ---------------------------------------------------------------------------- #

def imprimir_grid(grid: list[list[int]], n: int):
    """Imprime o grid de Sudoku formatado."""
    tamanho = n * n
    separador_horizontal = "-" * (tamanho * 2 + n * 2 - 1)
    
    for i in range(tamanho):
        if i % n == 0 and i != 0:
            print(separador_horizontal)
        
        for j in range(tamanho):
            if j % n == 0 and j != 0:
                print("| ", end="")
            
            val = grid[i][j]
            print(f"{val} " if val != 0 else ". ", end="")
        print() # Nova linha no final da linha do grid

def validar_grid_inicial(grid: list[list[int]], graph: IGraph) -> bool:
    """
    Verifica se as pistas iniciais (não-zero) do grid são válidas
    de acordo com as regras do grafo.
    """
    tamanho = len(grid)
    for l in range(tamanho):
        for c in range(tamanho):
            valor = grid[l][c]
            
            # Se for uma pista (um número já preenchido)
            if valor != 0:
                v = graph.grid_para_vertice(l, c)
                
                # Verificamos seus vizinhos
                for vizinho in graph.get_vizinhos(v):
                    l_viz, c_viz = graph.vertice_para_grid(vizinho)
                    
                    # Se um vizinho tiver o MESMO valor da pista, o puzzle é inválido
                    if grid[l_viz][c_viz] == valor:
                        print(f"  [Erro de Validação] Conflito encontrado na célula ({l}, {c})")
                        return False
    return True

def adicionar_sudoku_nsxns(n: int)-> list[list]:

    print("Coloque os números do sudoku e aperte enter 0 p/ vazio e -1 se quiser voltar")
    i = 0
    sudoku_list = [["x"] * n**2 for _ in range(n**2)]
    imprimir_grid(sudoku_list, n)
    while i < n**2:
        j = 0
        while j < n**2:
            try:
                num_to_add = int(input())
            except:
                print(f"[Error] Adicione um número de 1 a {n**2} (0 se for vazio) e -1 se quiser voltar")
                continue

            if num_to_add > n**2 or num_to_add < -1:
                print(f"[Error] Adicione um número de 1 a {n**2} (0 se for vazio) e -1 se quiser voltar")
                continue

            if num_to_add == -1:
                print("Voltando um número")
                if j == 0:
                    j = n**2 -1
                    i-=1
                    sudoku_list[i][j] = "x"
                    imprimir_grid(sudoku_list, n)
                    continue
                j-=1
                sudoku_list[i][j] = "x"
                imprimir_grid(sudoku_list, n)
                continue

            sudoku_list[i][j] = num_to_add
            
            imprimir_grid(sudoku_list, n)
            j+=1
        i+=1

    return sudoku_list


# ---------------------------------------------------------------------------- #
#                                  Driver Code                                 #
# ---------------------------------------------------------------------------- #

# # --- 1. Definição do Problema ---
# N_VALOR = 3

# # Renomeie para guardar o original
# meu_puzzle_original = [
#     [8, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 3, 6, 0, 0, 0, 0, 0],
#     [0, 7, 0, 0, 9, 0, 2, 0, 0],
#     [0, 5, 0, 0, 0, 7, 0, 0, 0],
#     [0, 0, 0, 0, 4, 5, 7, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 3, 0],
#     [0, 0, 1, 0, 0, 0, 0, 6, 8],
#     [0, 0, 8, 5, 0, 0, 0, 1, 0],
#     [0, 9, 0, 0, 0, 0, 4, 0, 0]
# ]


# # --- 2. Instanciação dos Componentes ---
# print(f"Iniciando setup para Sudoku {N_VALOR**2}x{N_VALOR**2}...")
# graph: IGraph = SudokuGraph(n=N_VALOR)
# print("Modelo do Grafo (G=(V,E)) construído com sucesso.")

# # --- 3. Validação Inicial ---
# print("\n--- Puzzle Inicial ---")
# imprimir_grid(meu_puzzle_original, N_VALOR)

# print("\nValidando pistas iniciais...")
# if not validar_grid_inicial(meu_puzzle_original, graph):
#     print("ERRO: O puzzle inicial é inválido e não pode ser resolvido.")
#     exit()  # Para o programa
# else:
#     print("Puzzle inicial é válido.")


# # --- 4. Execução e Teste com o Naive ---

# # Crie uma CÓPIA para o solver Naive
# puzzle_para_naive = copy.deepcopy(meu_puzzle_original)

# try:
#     solver_naive: ISolver = NaiveBacktrackingSolver()
#     print("\nAlgoritmo de Resolução (NaiveBacktrackingSolver) instanciado.")
    
#     print("Resolvendo com o Naive...")
#     start_time_naive = time.time()
#     sucesso_naive = solver_naive.solve(puzzle_para_naive, graph) # Resolve a cópia
#     end_time_naive = time.time()
#     tempo_total_naive = end_time_naive - start_time_naive

# except Exception as e:
#     print(f"Erro ao instanciar ou rodar NaiveBacktrackingSolver: {e}")
#     sucesso_naive = False


# # --- 5. Execução e Teste com o Smart ---

# # Crie uma SEGUNDA CÓPIA para o solver Smart
# puzzle_para_smart = copy.deepcopy(meu_puzzle_original)

# try:
#     solver_smart: ISolver = SmartBacktrackingSolver()
#     print("\nAlgoritmo de Resolução (SmartBacktrackingSolver) instanciado.")
    
#     print("Resolvendo com o Smart...")
#     start_time_smart = time.time()
#     sucesso_smart = solver_smart.solve(puzzle_para_smart, graph) # Resolve a outra cópia
#     end_time_smart = time.time()
#     tempo_total_smart = end_time_smart - start_time_smart

# except Exception as e:
#     print(f"Erro ao instanciar ou rodar SmartBacktrackingSolver: {e}")
#     sucesso_smart = False


# # --- 6. Resultados ---

# if sucesso_naive:
#     print(f"\n--- Solução Naive --- (em {tempo_total_naive:.4f} segundos)")
#     imprimir_grid(puzzle_para_naive, N_VALOR)
# else:
#     print(f"\n--- Naive não encontrou solução --- (verificado em {tempo_total_naive:.4f} segundos)")

# if sucesso_smart:
#     print(f"\n--- Solução Smart --- (em {tempo_total_smart:.8f} segundos)")
#     imprimir_grid(puzzle_para_smart, N_VALOR)
# else:
#     print(f"\n--- Smart não encontrou solução --- (verificado em {tempo_total_smart:.8f} segundos)")

# # Comparação de tempo
# if sucesso_naive and sucesso_smart:
#     if tempo_total_smart < tempo_total_naive:
#         # Evita divisão por zero se o tempo for muito rápido
#         if tempo_total_smart > 0:
#             fator = tempo_total_naive / tempo_total_smart
#             print(f"\n O Smart foi {fator:.1f}x mais rápido!")
#         else:
#             print(f"\n O Smart foi instantâneo (Naive levou {tempo_total_naive:.4f}s)")
#     else:
#         if tempo_total_naive > 0:
#             fator = tempo_total_smart / tempo_total_naive
#             print(f"\n O Naive foi {fator:.1f}x mais rápido (Smart foi mais lento).")
#         else:
#              print(f"\n O Naive foi instantâneo (Smart levou {tempo_total_smart:.8f}s).")


    
# --- 1. Definição do Problema ---
N_VALOR = 4

# --- 2. Instanciação dos Componentes ---
print(f"Iniciando setup para Geração de Sudoku {N_VALOR**2}x{N_VALOR**2}...")

graph: IGraph = SudokuGraph(n=N_VALOR)
solver: ISolver = NaiveBacktrackingSolver()
counter: ISolutionCounter = BacktrackingCounter()

# Instancia o Gerador e injeta as ferramentas
generator = PuzzleGenerator(solver, counter)

print("Componentes instanciados.")

# --- 3. Execução da Geração ---
start_time = time.time()

(novo_puzzle, solucao) = generator.gerar_puzzle(N_VALOR)

end_time = time.time()
tempo_total = end_time - start_time

# --- 4. Resultados ---
print(f"\n--- Puzzle Gerado com Sucesso! --- (em {tempo_total:.2f} segundos)\n")
imprimir_grid(novo_puzzle, N_VALOR)

print("\n--- Solução Única Correspondente --- \n")
imprimir_grid(solucao, N_VALOR)

# --- 5. (Opcional) Validar o puzzle gerado ---
print("\nValidando o puzzle gerado...")
num_solucoes = counter.count_solutions(novo_puzzle, graph)
print(f"O puzzle gerado tem {num_solucoes} solução(ões). (Deve ser 1)")