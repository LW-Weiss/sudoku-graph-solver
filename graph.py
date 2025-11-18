from interfaces import IGraph

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