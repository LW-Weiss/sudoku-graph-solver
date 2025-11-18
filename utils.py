from interfaces import IGraph

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

