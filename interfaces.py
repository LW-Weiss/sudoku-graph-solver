from abc import ABC, abstractmethod

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