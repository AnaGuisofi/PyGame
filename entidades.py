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
        """Permite consultar texto.vivo, sem parênteses, verificando se ainda há tempo de vida."""
        return self.vida > 0

    def desenhar(self, tela, fonte):
        """Renderiza o texto com sombra para leitura nítida."""
        sombra = fonte.render(self.texto, True, (10, 10, 20))
        surf = fonte.render(self.texto, True, self.cor)
        pos = (int(self.x - surf.get_width() / 2), int(self.y))
        tela.blit(sombra, (pos[0] + 2, pos[1] + 2))
        tela.blit(surf, pos)

class Raquete:
    """Plataforma controlada pelo jogador com suporte a buffs, debuffs e choque."""

    def __init__(self, largura_base=RAQUETE_LARGURA_PADRAO):
        """Posiciona a raquete no centro inferior da arena."""
        self.largura_base = largura_base
        self.largura = largura_base
        self.altura = RAQUETE_ALTURA

        # Cria a parte retangular da raquete e centraliza ela perto da parte inferior
        self.rect = pygame.Rect(
            (LARGURA_TELA - self.largura) // 2,
            ALTURA_TELA - RAQUETE_MARGEM_INFERIOR,
            self.largura,
            self.altura,
        )

        # Quanto tempo cada efeito fica ativo
        self.tempo_animacao = 0.0
        self.tempo_expandida = 0.0
        self.tempo_encolhida = 0.0
        self.tempo_invertida = 0.0
        self.tempo_choque = 0.0
        self.tempo_laser = 0.0
        self.recarga_laser = 0.0

    def resetar(self, largura_base=None):
        """Restaura tamanho base e desativa todos os modificadores temporários."""
        if largura_base is not None:
            self.largura_base = largura_base
        self.tempo_expandida = 0.0
        self.tempo_encolhida = 0.0
        self.tempo_invertida = 0.0
        self.tempo_choque = 0.0
        self.tempo_laser = 0.0
        self._recalcular_largura()
        self.rect.centerx = LARGURA_TELA // 2

    def _recalcular_largura(self):
        """Define a largura atual com base nos efeitos ativos."""
        if self.tempo_encolhida > 0:
            nova = RAQUETE_LARGURA_ENCOLHIDA
        elif self.tempo_expandida > 0:
            nova = RAQUETE_LARGURA_EXPANDIDA
        else:
            nova = self.largura_base

        # Guarda o centro para a raquete não pular de posição ao mudar de tamanho
        centro_x = self.rect.centerx
        self.largura = nova
        self.rect.width = nova
        self.rect.centerx = centro_x
        self._limitar_bordas()
    def _limitar_bordas(self):
        """Impede que a raquete ultrapasse as paredes laterais da arena."""
        if self.rect.left < 14:
            self.rect.left = 14
        elif self.rect.right > LARGURA_TELA - 14:
            self.rect.right = LARGURA_TELA - 14

    def ativar_expansao(self, duracao):
        """Expande a raquete e cancela o efeito de encolhimento."""
        self.tempo_encolhida = 0.0
        self.tempo_expandida = duracao
        self._recalcular_largura()

    def ativar_encolhimento(self, duracao):
        """Encolhe a raquete e cancela expansão ativa."""
        self.tempo_expandida = 0.0
        self.tempo_encolhida = duracao
        self._recalcular_largura()

    def ativar_inversao(self, duracao):
        """Inverte os controles horizontais do jogador temporariamente."""
        self.tempo_invertida = duracao

    def ativar_laser(self, duracao):
        """Habilita os canhões laser nas extremidades da raquete."""
        self.tempo_laser = duracao

    def aplicar_choque_chefao(self):
        """Aplica curto-circuito ao ser atingido por disparo do chefão."""
        self.tempo_expandida = 0.0
        self.tempo_laser = 0.0
        self.tempo_encolhida = 4.5
        self.tempo_choque = 0.55
        self._recalcular_largura()
    def mover_teclado(self, direcao, dt):
        """Desloca a raquete via teclado respeitando inversão e paralisia."""
        if self.tempo_choque > 0:
            return
        fator_inv = -1 if self.tempo_invertida > 0 else 1
        self.rect.x += int(direcao * fator_inv * RAQUETE_VELOCIDADE * dt)
        self._limitar_bordas()

    def mover_mouse(self, pos_x):
        """Alinha a raquete ao cursor do mouse (espelhado se invertido)."""
        if self.tempo_choque > 0:
            return
        alvo_x = (LARGURA_TELA - pos_x) if self.tempo_invertida > 0 else pos_x
        self.rect.centerx = alvo_x
        self._limitar_bordas()

    def atualizar(self, dt):
        """Atualiza timers de efeitos e animação dos propulsores."""
        self.tempo_animacao += dt
        if self.recarga_laser > 0:
            self.recarga_laser -= dt
        if self.tempo_choque > 0:
            self.tempo_choque = max(0.0, self.tempo_choque - dt)
        if self.tempo_invertida > 0:
            self.tempo_invertida = max(0.0, self.tempo_invertida - dt)

        precisa_recalcular = False
        if self.tempo_expandida > 0:
            self.tempo_expandida -= dt
            if self.tempo_expandida <= 0:
                precisa_recalcular = True

        if self.tempo_encolhida > 0:
            self.tempo_encolhida -= dt
            if self.tempo_encolhida <= 0:
                precisa_recalcular = True

        if precisa_recalcular:
            self._recalcular_largura()

        if self.tempo_laser > 0:
            self.tempo_laser -= dt

    def desenhar(self, tela):
        """Desenha a raquete com feedback visual para buffs, armadilhas e choque."""
        cor_principal = COR_DESTAQUE_CIANO
        if self.tempo_choque > 0:
            cor_principal = (255, 255, 255) if int(self.tempo_animacao * 30) % 2 == 0 else COR_PERIGO_VERMELHO
        elif self.tempo_invertida > 0:
            cor_principal = COR_PERIGO_ROXO
        elif self.tempo_encolhida > 0:
            cor_principal = COR_PERIGO_VERMELHO
        elif self.tempo_laser > 0:
            cor_principal = COR_DESTAQUE_LARANJA
        elif self.tempo_expandida > 0:
            cor_principal = COR_DESTAQUE_MAGENTA

        pulso = int(4 + 3 * math.sin(self.tempo_animacao * 28))
        pygame.draw.polygon(
            tela,
            COR_DESTAQUE_AMARELO,
            [
                (self.rect.left + 10, self.rect.bottom),
                (self.rect.left + 20, self.rect.bottom),
                (self.rect.left + 15, self.rect.bottom + pulso),
            ],
        )
        pygame.draw.polygon(
            tela,
            COR_DESTAQUE_AMARELO,
            [
                (self.rect.right - 20, self.rect.bottom),
                (self.rect.right - 10, self.rect.bottom),
                (self.rect.right - 15, self.rect.bottom + pulso),
            ],
        )

        pygame.draw.rect(tela, cor_principal, self.rect, border_radius=8)
        nucleo = self.rect.inflate(-14, -8)
        if nucleo.width > 4:
            pygame.draw.rect(tela, (240, 250, 255), nucleo, border_radius=5)

        if self.tempo_laser > 0:
            canhao_esq = pygame.Rect(self.rect.left + 4, self.rect.top - 8, 6, 10)
            canhao_dir = pygame.Rect(self.rect.right - 10, self.rect.top - 8, 6, 10)
            pygame.draw.rect(tela, COR_DESTAQUE_AMARELO, canhao_esq, border_radius=2)
            pygame.draw.rect(tela, COR_DESTAQUE_AMARELO, canhao_dir, border_radius=2)

class Bola:
    """Esfera de energia com rastro animado e proteção contra ângulos rasos."""

    def __init__(self, x, y, presa=True, velocidade=BOLA_VELOCIDADE_INICIAL):
        """Inicializa a bola sobre a raquete ou em movimento livre."""
        self.x = float(x)
        self.y = float(y)
        self.raio = BOLA_RAIO
        self.velocidade = velocidade
        self.vx = 0.0
        self.vy = 0.0
        self.presa = presa
        self.tempo_fogo = 0.0
        self.rastro = []
        self.rect = pygame.Rect(
            int(x - self.raio), int(y - self.raio), self.raio * 2, self.raio * 2
        )

    def lancar(self, angulo_graus=None):
        """Dispara a bola para cima em um ângulo controlado."""
        if angulo_graus is None:
            angulo_graus = random.uniform(-34, 34)
        rad = math.radians(angulo_graus)
        self.vx = self.velocidade * math.sin(rad)
        self.vy = -abs(self.velocidade * math.cos(rad))
        self.presa = False

    def aplicar_turbo(self):
        """Aumenta bruscamente a velocidade da bola (efeito de armadilha)."""
        self.velocidade = min(self.velocidade * 1.28, BOLA_VELOCIDADE_MAXIMA)
        self.normalizar_velocidade()

    def normalizar_velocidade(self):
        """Garante módulo constante da velocidade e evita trajetória quase horizontal."""
        mag = math.hypot(self.vx, self.vy)
        if mag == 0:
            return
        self.vx = (self.vx / mag) * self.velocidade
        self.vy = (self.vy / mag) * self.velocidade

        min_vy = self.velocidade * 0.28
        if abs(self.vy) < min_vy:
            sinal_y = -1.0 if self.vy <= 0 else 1.0
            sinal_x = -1.0 if self.vx < 0 else 1.0
            self.vy = sinal_y * min_vy
            self.vx = sinal_x * math.sqrt(max(1.0, self.velocidade**2 - self.vy**2))

    def atualizar(self, dt, raquete):
        """Atualiza posição e rastro luminoso da bola."""
        if self.tempo_fogo > 0:
            self.tempo_fogo -= dt

        if self.presa:
            self.x = float(raquete.rect.centerx)
            self.y = float(raquete.rect.top - self.raio - 2)
            self.rastro.clear()
        else:
            self.rastro.append((self.x, self.y))
            if len(self.rastro) > BOLA_TAMANHO_RASTRO:
                self.rastro.pop(0)

            self.x += self.vx * dt
            self.y += self.vy * dt

        self.rect.center = (int(self.x), int(self.y))

    def desenhar(self, tela):
        """Desenha o rastro de energia e o núcleo brilhante da bola."""
        em_fogo = self.tempo_fogo > 0
        cor_rastro = COR_DESTAQUE_LARANJA if em_fogo else COR_DESTAQUE_CIANO
        cor_nucleo = COR_DESTAQUE_AMARELO if em_fogo else (255, 255, 255)

        total = len(self.rastro)
        for idx, (rx, ry) in enumerate(self.rastro):
            fator = (idx + 1) / max(1, total)
            raio_rastro = max(2, int(self.raio * fator * 0.85))
            cor_interp = (
                int(cor_rastro[0] * fator),
                int(cor_rastro[1] * fator),
                int(cor_rastro[2] * fator),
            )
            pygame.draw.circle(tela, cor_interp, (int(rx), int(ry)), raio_rastro)

        centro = (int(self.x), int(self.y))
        pygame.draw.circle(tela, cor_rastro, centro, self.raio + 2)
        pygame.draw.circle(tela, cor_nucleo, centro, self.raio - 2)

class Tijolo:
    """Bloco da arena com suporte a múltiplos hits, indestrutibilidade e movimento."""

    def __init__(self, x, y, largura, altura, tipo, vx=0.0):
        """Configura resistência, pontuação, velocidade horizontal e aparência."""
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(x, y, largura, altura)
        self.tipo = tipo
        resistencia, pontos, cor, cor_borda = TIPOS_TIJOLO[tipo]
        self.destrutivel = resistencia > 0
        self.vida_max = resistencia
        self.vida = resistencia
        self.pontos = pontos
        self.cor = cor
        self.cor_borda = cor_borda
        self.vx = float(vx)
        self.flash_impacto = 0.0

    def atingir(self, dano=1):
        """
        Aplica dano ao tijolo.

        Returns:
            bool: True se o tijolo foi destruído neste impacto.
        """
        self.flash_impacto = 0.12
        if not self.destrutivel:
            return False
        self.vida -= dano
        return self.vida <= 0

    def atualizar(self, dt):
        """Atualiza brilho de impacto e deslocamento horizontal."""
        if self.flash_impacto > 0:
            self.flash_impacto = max(0.0, self.flash_impacto - dt)
        if self.vx != 0.0:
            self.x += self.vx * dt
            self.rect.x = int(self.x)

    def desenhar(self, tela):
        """Renderiza o tijolo com relevo, ícone especial e rachaduras."""
        cor_atual = (255, 255, 255) if self.flash_impacto > 0 else self.cor
        pygame.draw.rect(tela, cor_atual, self.rect, border_radius=5)
        pygame.draw.rect(tela, self.cor_borda, self.rect, 2, border_radius=5)

        if self.tipo == 7:
            pygame.draw.line(
                tela, self.cor_borda, (self.rect.left + 8, self.rect.top + 6),
                (self.rect.right - 8, self.rect.bottom - 6), 2
            )
            pygame.draw.line(
                tela, self.cor_borda, (self.rect.right - 8, self.rect.top + 6),
                (self.rect.left + 8, self.rect.bottom - 6), 2
            )
            return

        reflexo = pygame.Rect(self.rect.x + 5, self.rect.y + 4, self.rect.width - 10, 4)
        pygame.draw.rect(tela, self.cor_borda, reflexo, border_radius=2)

        if self.tipo == 6:
            cx, cy = self.rect.center
            pygame.draw.circle(tela, COR_DESTAQUE_AMARELO, (cx, cy), 5)

        if self.destrutivel and self.vida < self.vida_max:
            cx, cy = self.rect.center
            pygame.draw.line(tela, (20, 20, 35), (cx - 12, self.rect.top + 3), (cx - 2, cy), 2)
            pygame.draw.line(tela, (20, 20, 35), (cx - 2, cy), (cx + 10, self.rect.bottom - 3), 2)
            
class Capsula:
    """Cápsula que cai dos tijolos, podendo ser Power-up positivo ou Armadilha."""

    def __init__(self, x, y, tipo, eh_armadilha=False):
        """Inicializa a cápsula com visual diferenciado para bônus ou perigo."""
        self.tipo = tipo
        self.eh_armadilha = eh_armadilha
        tabela = TIPOS_ARMADILHA if eh_armadilha else TIPOS_POWERUP
        self.sigla, self.cor = tabela[tipo]
        self.rect = pygame.Rect(int(x - 25), int(y - 12), 50, 24)
        self.tempo = 0.0

    def atualizar(self, dt):
        """Move a cápsula para baixo e atualiza sua animação pulsante."""
        self.rect.y += int(CAPSULA_VELOCIDADE_QUEDA * dt)
        self.tempo += dt

    def desenhar(self, tela, fonte):
        """Desenha cápsula arredondada (bônus) ou angular de alerta (armadilha)."""
        escala = int(2 * math.sin(self.tempo * 12))
        rect_anim = self.rect.inflate(escala, escala)
        fundo = (48, 12, 24) if self.eh_armadilha else (18, 26, 52)
        raio_borda = 3 if self.eh_armadilha else 11

        pygame.draw.rect(tela, fundo, rect_anim, border_radius=raio_borda)
        pygame.draw.rect(tela, self.cor, rect_anim, 2, border_radius=raio_borda)

        label = fonte.render(self.sigla, True, self.cor)
        tela.blit(label, label.get_rect(center=rect_anim.center))


class ProjetilLaser:
    """Disparo vertical emitido pela raquete quando o power-up Laser está ativo."""

    def __init__(self, x, y):
        """Cria um feixe de laser na posição do canhão."""
        self.rect = pygame.Rect(int(x - 2), int(y - 14), 4, 16)
        self.velocidade = 800.0

    def atualizar(self, dt):
        """Desloca o laser verticalmente para o topo da tela."""
        self.rect.y -= int(self.velocidade * dt)

    def desenhar(self, tela):
        """Renderiza o feixe energético."""
        pygame.draw.rect(tela, COR_DESTAQUE_AMARELO, self.rect, border_radius=2)


class ProjetilInimigo:
    """Rajada de plasma disparada pelo chefão contra a raquete do jogador."""

    def __init__(self, x, y, vx=0.0, vy=330.0):
        """Inicializa o projétil inimigo."""
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.rect = pygame.Rect(int(x - 5), int(y - 9), 10, 18)

    def atualizar(self, dt):
        """Move o projétil em direção à parte inferior da arena."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))

    def desenhar(self, tela):
        """Renderiza o disparo de plasma vermelho/amarelo."""
        pygame.draw.ellipse(tela, COR_PERIGO_VERMELHO, self.rect)
        interno = self.rect.inflate(-4, -6)
        pygame.draw.ellipse(tela, COR_DESTAQUE_AMARELO, interno)


class DroneInimigo:
    """Drone de patrulha que cruza a arena e desvia a trajetória da bola."""

    def __init__(self, x, y, velocidade):
        """Inicializa o drone com movimento horizontal e oscilação vertical."""
        self.x = float(x)
        self.y_base = float(y)
        self.y = float(y)
        self.vx = float(velocidade)
        self.rect = pygame.Rect(int(x - 24), int(y - 12), 48, 24)
        self.tempo = random.uniform(0, 6.28)
        self.cooldown_rebate = 0.0

    def atualizar(self, dt):
        """Movimenta o drone entre as paredes laterais da arena."""
        self.tempo += dt
        if self.cooldown_rebate > 0:
            self.cooldown_rebate = max(0.0, self.cooldown_rebate - dt)

        self.x += self.vx * dt
        if self.x - 24 <= 18:
            self.x = 42
            self.vx = abs(self.vx)
        elif self.x + 24 >= LARGURA_TELA - 18:
            self.x = LARGURA_TELA - 42
            self.vx = -abs(self.vx)

        self.y = self.y_base + math.sin(self.tempo * 4.5) * 8.0
        self.rect.center = (int(self.x), int(self.y))

    def desenhar(self, tela):
        """Desenha o drone cibernético com visor pulsante e escudo."""
        pygame.draw.rect(tela, (45, 22, 75), self.rect, border_radius=10)
        pygame.draw.rect(tela, COR_PERIGO_ROXO, self.rect, 2, border_radius=10)

        olho_x = self.rect.centerx + int(math.sin(self.tempo * 6) * 8)
        pygame.draw.circle(tela, COR_PERIGO_VERMELHO, (olho_x, self.rect.centery), 5)
        pygame.draw.circle(tela, (255, 220, 220), (olho_x, self.rect.centery), 2)


class ChefaoCore:
    """Chefão final da Fase 4 que patrulha o topo e dispara rajadas de plasma."""

    def __init__(self, vida_maxima):
        """Configura posição, vida e cadência de ataques do chefão."""
        self.vida_max = vida_maxima
        self.vida = vida_maxima
        self.x = float(LARGURA_TELA // 2)
        self.y = 112.0
        self.vx = 145.0
        self.rect = pygame.Rect(int(self.x - 75), int(self.y - 24), 150, 48)
        self.tempo = 0.0
        self.timer_ataque = 2.2
        self.carregando_tiro = 0.0
        self.flash_dano = 0.0
        self.invulneravel = 0.0

    @property
    def vivo(self):
        """Retorna True enquanto o chefão possuir pontos de vida."""
        return self.vida > 0

    def atingir(self, dano=1):
        """
        Aplica dano ao chefão respeitando breve janela de invulnerabilidade.

        Returns:
            bool: True se o dano foi efetivamente contabilizado.
        """
        if self.invulneravel > 0 or not self.vivo:
            return False
        self.vida = max(0, self.vida - dano)
        self.flash_dano = 0.14
        self.invulneravel = 0.14
        return True

    def atualizar(self, dt, alvo_x):
        """
        Atualiza movimento, animação e dispara rajadas quando o timer zera.

        Returns:
            list[ProjetilInimigo]: Lista de novos projéteis disparados neste frame.
        """
        self.tempo += dt
        if self.flash_dano > 0:
            self.flash_dano = max(0.0, self.flash_dano - dt)
        if self.invulneravel > 0:
            self.invulneravel = max(0.0, self.invulneravel - dt)

        fator_furia = 1.45 if self.vida <= self.vida_max // 2 else 1.0
        self.x += self.vx * fator_furia * dt
        if self.x - 75 <= 24:
            self.x = 99
            self.vx = abs(self.vx)
        elif self.x + 75 >= LARGURA_TELA - 24:
            self.x = LARGURA_TELA - 99
            self.vx = -abs(self.vx)

        self.rect.center = (int(self.x), int(self.y))

        novos_tiros = []
        self.timer_ataque -= dt * fator_furia
        if self.timer_ataque <= 0.65:
            self.carregando_tiro = max(0.0, self.timer_ataque)

        if self.timer_ataque <= 0:
            self.timer_ataque = 2.4
            self.carregando_tiro = 0.0
            dx = alvo_x - self.x
            vx_mirado = max(-160.0, min(160.0, dx * 0.45))
            novos_tiros.append(ProjetilInimigo(self.x - 36, self.rect.bottom, vx=0.0, vy=320.0))
            novos_tiros.append(ProjetilInimigo(self.x + 36, self.rect.bottom, vx=0.0, vy=320.0))
            if self.vida <= self.vida_max // 2:
                novos_tiros.append(ProjetilInimigo(self.x, self.rect.bottom, vx=vx_mirado, vy=360.0))

        return novos_tiros

    def desenhar(self, tela):
        """Renderiza a estrutura blindada e o núcleo energético do chefão."""
        cor_casco = (255, 255, 255) if self.flash_dano > 0 else (38, 22, 65)
        cor_borda = COR_DESTAQUE_AMARELO if self.carregando_tiro > 0 else COR_DESTAQUE_MAGENTA

        pygame.draw.rect(tela, cor_casco, self.rect, border_radius=14)
        pygame.draw.rect(tela, cor_borda, self.rect, 3, border_radius=14)

        canhao_esq = pygame.Rect(self.rect.left + 28, self.rect.bottom - 4, 14, 10)
        canhao_dir = pygame.Rect(self.rect.right - 42, self.rect.bottom - 4, 14, 10)
        pygame.draw.rect(tela, COR_PERIGO_VERMELHO, canhao_esq, border_radius=3)
        pygame.draw.rect(tela, COR_PERIGO_VERMELHO, canhao_dir, border_radius=3)

        raio_nucleo = int(14 + 3 * math.sin(self.tempo * 8))
        cor_nucleo = COR_DESTAQUE_AMARELO if self.carregando_tiro > 0 else COR_PERIGO_VERMELHO
        pygame.draw.circle(tela, cor_nucleo, self.rect.center, raio_nucleo)
        pygame.draw.circle(tela, (255, 255, 255), self.rect.center, max(4, raio_nucleo // 2))