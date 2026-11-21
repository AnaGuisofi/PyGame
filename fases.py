"""
Módulo de definição e construção das fases do jogo.

Organiza os mapas de blocos, fileiras móveis, drones de patrulha e o
chefão final em 4 estágios com progressão de dificuldade.
"""

from config import (
    LARGURA_TELA,
    TIJOLO_ALTURA,
    TIJOLO_COLUNAS,
    TIJOLO_ESPACAMENTO,
    TIJOLO_LARGURA,
    TIJOLO_MARGEM_SUPERIOR,
)
from entidades import ChefaoCore, DroneInimigo, Tijolo


class GerenciadorFases:
    """Armazena os layouts das fases e instancia entidades de cada nível."""

    def __init__(self):
        """Define as matrizes de design, fileiras móveis e inimigos das 4 fases."""
        self.fases = [
            {
                "nome": "FASE 1: HORIZONTE NEON",
                "subtitulo": "Desvie das armadilhas vermelhas e domine os combos",
                "linhas_moveis": {},
                "drones": [],
                "tem_chefao": False,
                "mapa": [
                    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
                    [3, 3, 3, 3, 3, 6, 3, 3, 3, 3, 3],
                    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                ],
            },
            {
                "nome": "FASE 2: FORTALEZA BLINDADA",
                "subtitulo": "Blocos indestrutiveis, fileira movel e drone de patrulha",
                "linhas_moveis": {4: 85.0},
                "drones": [(LARGURA_TELA // 2, 330)],
                "tem_chefao": False,
                "mapa": [
                    [0, 5, 4, 4, 5, 6, 5, 4, 4, 5, 0],
                    [4, 4, 3, 3, 3, 3, 3, 3, 3, 4, 4],
                    [3, 6, 7, 5, 2, 2, 2, 5, 7, 6, 3],
                    [2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2],
                    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                ],
            },
            {
                "nome": "FASE 3: PIRÂMIDE SOLAR",
                "subtitulo": "Duas fileiras moveis e patrulha dupla na arena",
                "linhas_moveis": {1: -95.0, 5: 105.0},
                "drones": [(260, 325), (700, 365)],
                "tem_chefao": False,
                "mapa": [
                    [0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 4, 6, 4, 0, 0, 0, 0],
                    [0, 0, 0, 4, 3, 5, 3, 4, 0, 0, 0],
                    [0, 0, 7, 3, 6, 2, 6, 3, 7, 0, 0],
                    [0, 2, 2, 4, 2, 2, 2, 4, 2, 2, 0],
                    [0, 1, 5, 1, 1, 0, 1, 1, 5, 1, 0],
                ],
            },
            {
                "nome": "FASE 4: NUCLEO ATARI FINAL",
                "subtitulo": "Destrua o Chefao Core e suas defesas!",
                "linhas_moveis": {4: 115.0},
                "drones": [(280, 355), (680, 355)],
                "tem_chefao": True,
                "mapa": [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [5, 0, 7, 4, 6, 5, 6, 4, 7, 0, 5],
                    [4, 3, 3, 2, 2, 2, 2, 2, 3, 3, 4],
                    [0, 2, 4, 2, 0, 6, 0, 2, 4, 2, 0],
                ],
            },
        ]

    @property
    def total_fases(self):
        """Retorna a quantidade total de fases disponíveis."""
        return len(self.fases)

    def obter_info_fase(self, indice):
        """Retorna o dicionário de metadados da fase solicitada."""
        return self.fases[indice]

    def construir_fase(self, indice, vel_inimigo, vida_chefao):
        """
        Instancia tijolos, drones e o chefão (se houver) da fase informada.

        Args:
            indice (int): Índice da fase (0 a total_fases - 1).
            vel_inimigo (float): Velocidade base dos drones conforme dificuldade.
            vida_chefao (int): Pontos de vida do chefão final conforme dificuldade.

        Returns:
            tuple[list[Tijolo], list[DroneInimigo], ChefaoCore | None]: Entidades da fase.
        """
        info = self.fases[indice]
        mapa = info["mapa"]
        linhas_moveis = info["linhas_moveis"]

        largura_total = (
            TIJOLO_COLUNAS * TIJOLO_LARGURA + (TIJOLO_COLUNAS - 1) * TIJOLO_ESPACAMENTO
        )
        inicio_x = (LARGURA_TELA - largura_total) // 2

        tijolos = []
        for linha_idx, linha in enumerate(mapa):
            vx_linha = linhas_moveis.get(linha_idx, 0.0)
            for col_idx, tipo in enumerate(linha):
                if tipo == 0:
                    continue
                x = inicio_x + col_idx * (TIJOLO_LARGURA + TIJOLO_ESPACAMENTO)
                y = TIJOLO_MARGEM_SUPERIOR + linha_idx * (TIJOLO_ALTURA + TIJOLO_ESPACAMENTO)
                tijolo = Tijolo(x, y, TIJOLO_LARGURA, TIJOLO_ALTURA, tipo, vx=vx_linha)
                tijolo.linha_id = linha_idx
                tijolos.append(tijolo)

        drones = []
        for idx, (dx, dy) in enumerate(info["drones"]):
            direcao = 1 if idx % 2 == 0 else -1
            drones.append(DroneInimigo(dx, dy, vel_inimigo * direcao))

        chefao = ChefaoCore(vida_chefao) if info["tem_chefao"] else None
        return tijolos, drones, chefao