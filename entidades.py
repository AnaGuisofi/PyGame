import math
import random
import pygame
from config import (
    ALTURA_TELA,
    BOLA_RAIO,
    BOLA_TAMANHO_RASTRO,
    BOLA_VELOCIDADE_INICIAL,
    BOLA_VELOCIDADE_MAXIMA,
    CAPSULA_VELOCIDADE_QUEDA,
    COR_BORDA_NEON,
    COR_DESTAQUE_AMARELO,
    COR_DESTAQUE_CIANO,
    COR_DESTAQUE_LARANJA,
    COR_DESTAQUE_MAGENTA,
    COR_GRADE,
    COR_GRADE_BRILHO,
    COR_PERIGO_ROXO,
    COR_PERIGO_VERMELHO,
    LARGURA_TELA,
    RAQUETE_ALTURA,
    RAQUETE_LARGURA_ENCOLHIDA,
    RAQUETE_LARGURA_EXPANDIDA,
    RAQUETE_LARGURA_PADRAO,
    RAQUETE_MARGEM_INFERIOR,
    RAQUETE_VELOCIDADE,
    TIPOS_ARMADILHA,
    TIPOS_POWERUP,
    TIPOS_TIJOLO,
)


class FundoAnimado:
    """Renderiza o cenário synthwave com estrelas em paralaxe e grade móvel."""

    def __init__(self):
        """Inicializa as estrelas e o deslocamento da grade de fundo."""
        self.estrelas = [
            [
                random.uniform(20, LARGURA_TELA - 20),
                random.uniform(20, ALTURA_TELA - 20),
                random.uniform(15.0, 55.0),
                random.randint(1, 3),
            ]
            for _ in range(65)
        ]
        self.offset_grade = 0.0
        self.tempo = 0.0

    def atualizar(self, dt):
        """Atualiza a posição das estrelas e da grade animada."""
        self.tempo += dt
        self.offset_grade = (self.offset_grade + 38.0 * dt) % 48
        for estrela in self.estrelas:
            estrela[1] += estrela[2] * dt
            if estrela[1] > ALTURA_TELA - 15:
                estrela[1] = 15
                estrela[0] = random.uniform(20, LARGURA_TELA - 20)

    def desenhar(self, tela):
        """Desenha a grade neon, estrelas e moldura energética da arena."""
        espaco = 48
        for x in range(espaco, LARGURA_TELA, espaco):
            pygame.draw.line(tela, COR_GRADE, (x, 0), (x, ALTURA_TELA), 1)

        y = int(self.offset_grade)
        while y < ALTURA_TELA:
            cor_linha = COR_GRADE_BRILHO if (y // espaco) % 3 == 0 else COR_GRADE
            pygame.draw.line(tela, cor_linha, (0, y), (LARGURA_TELA, y), 1)
            y += espaco

        for x, y_est, _, raio in self.estrelas:
            brilho = int(160 + 95 * math.sin(self.tempo * 3.0 + x))
            cor = (brilho, brilho, 255)
            pygame.draw.circle(tela, cor, (int(x), int(y_est)), raio)

        pygame.draw.rect(
            tela,
            COR_BORDA_NEON,
            (8, 56, LARGURA_TELA - 16, ALTURA_TELA - 64),
            2,
            border_radius=8,
        )


class OndaChoque:
    """Anel luminoso expansivo exibido em explosões e derrotadas de inimigos."""

    def __init__(self, x, y, cor, raio_max=135):
        """Inicializa a onda de choque no epicentro do impacto."""
        self.x = int(x)
        self.y = int(y)
        self.cor = cor
        self.raio = 10.0
        self.raio_max = float(raio_max)
        self.velocidade = raio_max / 0.34

    def atualizar(self, dt):
        """Expande o raio do anel ao longo do tempo."""
        self.raio += self.velocidade * dt

    @property
    def viva(self):
        """Retorna True enquanto o anel não atingir seu raio máximo."""
        return self.raio < self.raio_max

    def desenhar(self, tela):
        """Renderiza o anel afinando a espessura conforme se dissipa."""
        progresso = self.raio / self.raio_max
        espessura = max(1, int(4 * (1.0 - progresso)))
        pygame.draw.circle(tela, self.cor, (self.x, self.y), int(self.raio), espessura)


class Particula:
    """Representa um fragmento animado gerado em colisões e explosões."""

    def __init__(self, x, y, cor):
        """Cria uma partícula com velocidade e tempo de vida aleatórios."""
        angulo = random.uniform(0, 2 * math.pi)
        velocidade = random.uniform(70, 300)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angulo) * velocidade
        self.vy = math.sin(angulo) * velocidade
        self.cor = cor
        self.vida_max = random.uniform(0.28, 0.58)
        self.vida = self.vida_max
        self.tamanho = random.uniform(3.0, 6.5)

    def atualizar(self, dt):
        """Aplica movimento, gravidade leve e decaimento de vida."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 320.0 * dt
        self.vida -= dt

    @property
    def viva(self):
        """Indica se a partícula ainda deve ser renderizada."""
        return self.vida > 0

    def desenhar(self, tela):
        """Desenha a partícula reduzindo seu tamanho conforme expira."""
        fator = max(0.0, self.vida / self.vida_max)
        lado = max(1, int(self.tamanho * fator))
        rect = pygame.Rect(int(self.x - lado / 2), int(self.y - lado / 2), lado, lado)
        pygame.draw.rect(tela, self.cor, rect)


class TextoFlutuante:
    """Exibe indicadores animados de pontuação, combos e alertas na tela."""

    def __init__(self, x, y, texto, cor):
        """Inicializa o texto flutuante na posição do impacto."""
        self.x = float(x)
        self.y = float(y)
        self.texto = texto
        self.cor = cor
        self.vida = 0.85

    def atualizar(self, dt):
        """Move o texto suavemente para cima."""
        self.y -= 50.0 * dt
        self.vida -= dt

    @property
    def vivo(self):
        """Retorna True enquanto o texto estiver visível."""
        return self.vida > 0

    def desenhar(self, tela, fonte):
        """Renderiza o texto com sombra para leitura nítida."""
        sombra = fonte.render(self.texto, True, (10, 10, 20))
        surf = fonte.render(self.texto, True, self.cor)
        pos = (int(self.x - surf.get_width() / 2), int(self.y))
        tela.blit(sombra, (pos[0] + 2, pos[1] + 2))
        tela.blit(surf, pos)
