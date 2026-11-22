"""
Módulo controlador principal do jogo Breakout.

Gerencia o modo tela cheia, seletor de dificuldade, entrada do nome do jogador,
exibição das pontuações da sessão, máquina de estados das telas, física de
colisões, inimigos e chefão final.
"""

import math
import random
import pygame
from audio import GerenciadorAudio
from config import (
    ALTURA_TELA,
    BOLA_VELOCIDADE_MAXIMA,
    CADENCIA_LASER,
    COR_DESTAQUE_AMARELO,
    COR_DESTAQUE_CIANO,
    COR_DESTAQUE_LARANJA,
    COR_DESTAQUE_MAGENTA,
    COR_DESTAQUE_VERDE,
    COR_FUNDO,
    COR_PERIGO_ROXO,
    COR_PERIGO_VERMELHO,
    COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO,
    DIFICULDADES,
    FPS,
    LARGURA_TELA,
    ORDEM_DIFICULDADES,
    TELA_CHEIA_INICIAL,
    TIPOS_ARMADILHA,
    TIPOS_POWERUP,
    TITULO_JOGO,
    VIDAS_INICIAIS,
    VIDAS_MAXIMAS,
)
from entidades import (
    Bola,
    Capsula,
    FundoAnimado,
    OndaChoque,
    Particula,
    ProjetilLaser,
    Raquete,
    TextoFlutuante,
)
from fases import GerenciadorFases


class JogoBreakout:
    """Orquestra o loop principal, eventos, regras e renderização do jogo."""

    def __init__(self):
        """Inicializa PyGame em tela cheia, fontes, áudio e estado inicial."""
        pygame.init()
        self.tela_cheia = TELA_CHEIA_INICIAL
        self.tela = self._configurar_janela(self.tela_cheia)
        pygame.display.set_caption(TITULO_JOGO)
        self.relogio = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont("consolas", 50, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_hud = pygame.font.SysFont("consolas", 19, bold=True)
        self.fonte_texto = pygame.font.SysFont("consolas", 17)
        self.fonte_pequena = pygame.font.SysFont("consolas", 14, bold=True)

        self.audio = GerenciadorAudio()
        self.gerenciador_fases = GerenciadorFases()
        self.fundo = FundoAnimado()

        self.indice_dificuldade = 0
        self.estado = "MENU"
        self.nome_jogador = ""
        self.pontuacao = 0
        self.historico_partidas = []
        self.vidas = VIDAS_INICIAIS
        self.fase_atual = 0
        self.combo = 0
        self.vitoria_final = False
        self.tremor_tela = 0.0
        self.tempo_global = 0.0

        self.raquete = Raquete()
        self.bolas = []
        self.tijolos = []
        self.drones = []
        self.chefao = None
        self.capsulas = []
        self.lasers = []
        self.tiros_inimigos = []
        self.particulas = []
        self.ondas_choque = []
        self.textos_flutuantes = []

        self.audio.iniciar_musica()

    def _configurar_janela(self, ativar_tela_cheia):
        """Cria ou alterna a janela entre tela cheia escalonada e modo janela."""
        flags = (pygame.FULLSCREEN | pygame.SCALED) if ativar_tela_cheia else pygame.SCALED
        return pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), flags)

    def alternar_tela_cheia(self):
        """Alterna dinamicamente entre tela cheia e modo janela."""
        self.tela_cheia = not self.tela_cheia
        self.tela = self._configurar_janela(self.tela_cheia)

    @property
    def cfg_dificuldade(self):
        """Retorna o dicionário de parâmetros da dificuldade selecionada."""
        chave = ORDEM_DIFICULDADES[self.indice_dificuldade]
        return DIFICULDADES[chave]

    def _mudar_dificuldade(self, delta):
        """Altera o nível de dificuldade selecionado no menu."""
        self.indice_dificuldade = (self.indice_dificuldade + delta) % len(ORDEM_DIFICULDADES)
        self.audio.tocar("menu_select")

    def iniciar_novo_jogo(self):
        """Reseta placar, vidas e carrega a primeira fase na dificuldade escolhida."""
        if not self.nome_jogador.strip():
            self.nome_jogador = "JOGADOR"
        self.pontuacao = 0
        self.vidas = VIDAS_INICIAIS
        self.fase_atual = 0
        self.combo = 0
        self.vitoria_final = False
        self._carregar_fase(0)
        self.estado = "JOGANDO"

    def _finalizar_partida(self, venceu):
        """Registra a pontuação do jogador no histórico da sessão e encerra."""
        self.vitoria_final = venceu
        self.historico_partidas.insert(
            0,
            {
                "nome": self.nome_jogador,
                "pontos": self.pontuacao,
                "dificuldade": self.cfg_dificuldade["rotulo"],
            },
        )
        self.historico_partidas = self.historico_partidas[:4]
        self.estado = "FIM_DE_JOGO"

    def _carregar_fase(self, indice):
        """Prepara blocos, inimigos, chefão e reposiciona raquete e bola."""
        cfg = self.cfg_dificuldade
        self.fase_atual = indice
        self.tijolos, self.drones, self.chefao = self.gerenciador_fases.construir_fase(
            indice, cfg["vel_inimigo"], cfg["vida_chefao"]
        )
        self.capsulas.clear()
        self.lasers.clear()
        self.tiros_inimigos.clear()
        self.particulas.clear()
        self.ondas_choque.clear()
        self.textos_flutuantes.clear()
        self.raquete.resetar(largura_base=cfg["largura_raquete"])
        self._criar_bola_presa()

    def _criar_bola_presa(self):
        """Cria uma bola inicial posicionada sobre a raquete."""
        vel_base = self.cfg_dificuldade["vel_bola"] + self.fase_atual * 24.0
        bola = Bola(
            self.raquete.rect.centerx,
            self.raquete.rect.top - 12,
            presa=True,
            velocidade=vel_base,
        )
        self.bolas = [bola]

    def _disparar_acao_principal(self):
        """Lança bolas presas ou dispara lasers quando o power-up está ativo."""
        lancou = False
        for bola in self.bolas:
            if bola.presa:
                bola.lancar()
                lancou = True

        if lancou:
            self.audio.tocar("raquete")
            return

        if (
            self.raquete.tempo_laser > 0
            and self.raquete.recarga_laser <= 0
            and self.raquete.tempo_choque <= 0
        ):
            self.lasers.append(ProjetilLaser(self.raquete.rect.left + 7, self.raquete.rect.top))
            self.lasers.append(ProjetilLaser(self.raquete.rect.right - 7, self.raquete.rect.top))
            self.raquete.recarga_laser = CADENCIA_LASER
            self.audio.tocar("laser")

    def _processar_digitacao_nome(self, evento):
        """Trata a digitação do nome do jogador antes de iniciar a partida."""
        if evento.key == pygame.K_ESCAPE:
            self.audio.tocar("menu_select")
            self.estado = "MENU"
        elif evento.key == pygame.K_RETURN:
            self.audio.tocar("menu_select")
            self.iniciar_novo_jogo()
        elif evento.key == pygame.K_BACKSPACE:
            self.nome_jogador = self.nome_jogador[:-1]
        elif evento.unicode and evento.unicode.isprintable():
            if len(self.nome_jogador) < 16:
                self.nome_jogador += evento.unicode.upper()

    def _processar_eventos(self):
        """Trata entradas de teclado, mouse e fechamento da janela."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEMOTION and self.estado == "JOGANDO":
                self.raquete.mover_mouse(evento.pos[0])

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.estado == "JOGANDO":
                    self._disparar_acao_principal()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    self.alternar_tela_cheia()
                    continue

                if self.estado == "NOME_JOGADOR":
                    self._processar_digitacao_nome(evento)
                    continue

                if evento.key == pygame.K_m:
                    self.audio.alternar_mudo()

                if self.estado == "MENU":
                    if evento.key in (pygame.K_LEFT, pygame.K_a):
                        self._mudar_dificuldade(-1)
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        self._mudar_dificuldade(1)
                    elif evento.key == pygame.K_1:
                        self.indice_dificuldade = 0
                        self.audio.tocar("menu_select")
                    elif evento.key == pygame.K_2:
                        self.indice_dificuldade = 1
                        self.audio.tocar("menu_select")
                    elif evento.key == pygame.K_3:
                        self.indice_dificuldade = 2
                        self.audio.tocar("menu_select")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.tocar("menu_select")
                        self.estado = "NOME_JOGADOR"
                    elif evento.key == pygame.K_i:
                        self.audio.tocar("menu_select")
                        self.estado = "INSTRUCOES"
                    elif evento.key == pygame.K_ESCAPE:
                        return False

                elif self.estado == "INSTRUCOES":
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_i):
                        self.audio.tocar("menu_select")
                        self.estado = "MENU"

                elif self.estado == "JOGANDO":
                    if evento.key == pygame.K_SPACE:
                        self._disparar_acao_principal()
                    elif evento.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.estado = "PAUSADO"

                elif self.estado == "PAUSADO":
                    if evento.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN):
                        self.estado = "JOGANDO"
                    elif evento.key == pygame.K_q:
                        self.estado = "MENU"

                elif self.estado == "TRANSICAO_FASE":
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.tocar("menu_select")
                        self._carregar_fase(self.fase_atual + 1)
                        self.estado = "JOGANDO"

                elif self.estado == "FIM_DE_JOGO":
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.tocar("menu_select")
                        self.iniciar_novo_jogo()
                    elif evento.key == pygame.K_n:
                        self.audio.tocar("menu_select")
                        self.nome_jogador = ""
                        self.estado = "NOME_JOGADOR"
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU"

        return True

    def _atualizar_tijolos_moveis(self, dt):
        """Atualiza tijolos e inverte a direção sincronizada das fileiras móveis."""
        for tijolo in self.tijolos:
            tijolo.atualizar(dt)

        linhas_reverter = set()
        for tijolo in self.tijolos:
            if tijolo.vx < 0 and tijolo.rect.left <= 18:
                linhas_reverter.add(tijolo.linha_id)
            elif tijolo.vx > 0 and tijolo.rect.right >= LARGURA_TELA - 18:
                linhas_reverter.add(tijolo.linha_id)

        if linhas_reverter:
            for tijolo in self.tijolos:
                if tijolo.linha_id in linhas_reverter:
                    tijolo.vx = -tijolo.vx

    def _atualizar_jogando(self, dt):
        """Executa a física, colisões, armadilhas, inimigos e chefão em tempo real."""
        teclas = pygame.key.get_pressed()
        direcao = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            direcao -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            direcao += 1
        if direcao != 0:
            self.raquete.mover_teclado(direcao, dt)

        self.raquete.atualizar(dt)
        self._atualizar_tijolos_moveis(dt)

        for drone in self.drones:
            drone.atualizar(dt)

        if self.chefao and self.chefao.vivo:
            novos_tiros = self.chefao.atualizar(dt, self.raquete.rect.centerx)
            if novos_tiros:
                self.tiros_inimigos.extend(novos_tiros)
                self.audio.tocar("chefao_tiro")

        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if p.viva]

        for onda in self.ondas_choque:
            onda.atualizar(dt)
        self.ondas_choque = [o for o in self.ondas_choque if o.viva]

        for txt in self.textos_flutuantes:
            txt.atualizar(dt)
        self.textos_flutuantes = [t for t in self.textos_flutuantes if t.vivo]

        # Atualiza projéteis inimigos do chefão
        for tiro in self.tiros_inimigos[:]:
            tiro.atualizar(dt)
            if tiro.rect.top > ALTURA_TELA:
                self.tiros_inimigos.remove(tiro)
            elif tiro.rect.colliderect(self.raquete.rect):
                self.tiros_inimigos.remove(tiro)
                self.raquete.aplicar_choque_chefao()
                self.combo = 0
                self.tremor_tela = 0.24
                self.audio.tocar("choque")
                self.ondas_choque.append(
                    OndaChoque(self.raquete.rect.centerx, self.raquete.rect.top, COR_PERIGO_VERMELHO, 95)
                )
                self.textos_flutuantes.append(
                    TextoFlutuante(self.raquete.rect.centerx, self.raquete.rect.top - 14, "CURTO-CIRCUITO!", COR_PERIGO_VERMELHO)
                )
                for _ in range(14):
                    self.particulas.append(Particula(self.raquete.rect.centerx, self.raquete.rect.top, COR_PERIGO_VERMELHO))

        # Atualiza projéteis de laser do jogador
        for laser in self.lasers[:]:
            laser.atualizar(dt)
            if laser.rect.bottom < 60:
                self.lasers.remove(laser)
                continue

            atingiu = False
            if self.chefao and self.chefao.vivo and laser.rect.colliderect(self.chefao.rect):
                if self.chefao.atingir(1):
                    self._processar_dano_chefao(laser.rect.centerx, laser.rect.top)
                atingiu = True

            if not atingiu:
                for drone in self.drones[:]:
                    if laser.rect.colliderect(drone.rect):
                        self._destruir_drone(drone)
                        atingiu = True
                        break

            if not atingiu:
                for tijolo in self.tijolos[:]:
                    if laser.rect.colliderect(tijolo.rect):
                        self._atingir_tijolo(tijolo, dano=1)
                        atingiu = True
                        break

            if atingiu and laser in self.lasers:
                self.lasers.remove(laser)

        # Atualiza cápsulas (power-ups e armadilhas)
        for cap in self.capsulas[:]:
            cap.atualizar(dt)
            if cap.rect.colliderect(self.raquete.rect):
                self._aplicar_capsula(cap)
                self.capsulas.remove(cap)
            elif cap.rect.top > ALTURA_TELA:
                self.capsulas.remove(cap)

        # Atualiza bolas e colisões
        for bola in self.bolas[:]:
            bola.atualizar(dt, self.raquete)
            if bola.presa:
                continue

            if bola.rect.left <= 12:
                bola.x = 12 + bola.raio
                bola.vx = abs(bola.vx)
                self.audio.tocar("parede")
            elif bola.rect.right >= LARGURA_TELA - 12:
                bola.x = LARGURA_TELA - 12 - bola.raio
                bola.vx = -abs(bola.vx)
                self.audio.tocar("parede")

            if bola.rect.top <= 58:
                bola.y = 58 + bola.raio
                bola.vy = abs(bola.vy)
                self.audio.tocar("parede")

            if bola.vy > 0 and bola.rect.colliderect(self.raquete.rect):
                deslocamento = (bola.x - self.raquete.rect.centerx) / (
                    self.raquete.rect.width / 2.0
                )
                deslocamento = max(-0.92, min(0.92, deslocamento))
                angulo = deslocamento * math.radians(62)
                bola.velocidade = min(bola.velocidade * 1.02, BOLA_VELOCIDADE_MAXIMA)
                bola.vx = bola.velocidade * math.sin(angulo)
                bola.vy = -abs(bola.velocidade * math.cos(angulo))
                bola.normalizar_velocidade()
                bola.y = self.raquete.rect.top - bola.raio - 1
                self.combo = 0
                self.audio.tocar("raquete")

            if self.chefao and self.chefao.vivo and bola.rect.colliderect(self.chefao.rect):
                self._rebater_bola_retangulo(bola, self.chefao.rect)
                dano_boss = 2 if bola.tempo_fogo > 0 else 1
                if self.chefao.atingir(dano_boss):
                    self._processar_dano_chefao(bola.x, bola.y)

            for drone in self.drones[:]:
                if bola.rect.colliderect(drone.rect):
                    if bola.tempo_fogo > 0:
                        self._destruir_drone(drone)
                    elif drone.cooldown_rebate <= 0:
                        self._rebater_bola_retangulo(bola, drone.rect)
                        bola.vx += random.uniform(-90, 90)
                        bola.normalizar_velocidade()
                        drone.cooldown_rebate = 0.12
                        self.audio.tocar("drone")
                        for _ in range(8):
                            self.particulas.append(Particula(drone.x, drone.y, COR_PERIGO_ROXO))
                    break

            for tijolo in self.tijolos[:]:
                if bola.rect.colliderect(tijolo.rect):
                    if bola.tempo_fogo <= 0 or not tijolo.destrutivel:
                        self._rebater_bola_retangulo(bola, tijolo.rect)
                    dano = 2 if (bola.tempo_fogo > 0 and tijolo.destrutivel) else 1
                    self._atingir_tijolo(tijolo, dano=dano)
                    break

            if bola.rect.top > ALTURA_TELA + 10:
                self.bolas.remove(bola)

        if not self.bolas:
            self.vidas -= 1
            self.combo = 0
            self.tremor_tela = 0.25
            self.audio.tocar("perder_vida")
            if self.vidas <= 0:
                self._finalizar_partida(venceu=False)
            else:
                self.raquete.resetar()
                self._criar_bola_presa()

        restam_blocos = any(t.destrutivel for t in self.tijolos)
        chefao_vivo = self.chefao is not None and self.chefao.vivo
        if not restam_blocos and not chefao_vivo and self.estado == "JOGANDO":
            bonus_vidas = self.vidas * 300
            self.pontuacao += bonus_vidas
            self.audio.tocar("vitoria_fase")
            if self.fase_atual + 1 >= self.gerenciador_fases.total_fases:
                self._finalizar_partida(venceu=True)
            else:
                self.estado = "TRANSICAO_FASE"

    def _rebater_bola_retangulo(self, bola, rect):
        """Reflete a bola pelo eixo de menor penetração e reposiciona fora do alvo."""
        sobre_esq = bola.rect.right - rect.left
        sobre_dir = rect.right - bola.rect.left
        sobre_topo = bola.rect.bottom - rect.top
        sobre_base = rect.bottom - bola.rect.top

        menor_x = min(sobre_esq, sobre_dir)
        menor_y = min(sobre_topo, sobre_base)

        if menor_x < menor_y:
            if sobre_esq < sobre_dir:
                bola.x = rect.left - bola.raio - 1
                bola.vx = -abs(bola.vx)
            else:
                bola.x = rect.right + bola.raio + 1
                bola.vx = abs(bola.vx)
        else:
            if sobre_topo < sobre_base:
                bola.y = rect.top - bola.raio - 1
                bola.vy = -abs(bola.vy)
            else:
                bola.y = rect.bottom + bola.raio + 1
                bola.vy = abs(bola.vy)

        bola.normalizar_velocidade()
        bola.rect.center = (int(bola.x), int(bola.y))
    def _destruir_drone(self, drone):
        """Destrói um drone inimigo com explosão, onda de choque e bônus."""
        if drone in self.drones:
            self.drones.remove(drone)
        self.pontuacao += 350
        self.audio.tocar("explosao")
        self.ondas_choque.append(OndaChoque(drone.x, drone.y, COR_PERIGO_ROXO, 110))
        self.textos_flutuantes.append(
            TextoFlutuante(drone.x, drone.y, "+350 DRONE!", COR_PERIGO_ROXO)
        )
        for _ in range(18):
            self.particulas.append(Particula(drone.x, drone.y, COR_PERIGO_ROXO))

    def _processar_dano_chefao(self, x, y):
        """Contabiliza pontos, partículas e explosão final ao atingir o chefão."""
        self.pontuacao += 200
        self.audio.tocar("chefao_hit")
        self.tremor_tela = 0.16
        for _ in range(12):
            self.particulas.append(Particula(x, y, COR_DESTAQUE_MAGENTA))

        if self.chefao and not self.chefao.vivo:
            self.pontuacao += 2000
            self.tremor_tela = 0.45
            self.audio.tocar("explosao")
            self.tiros_inimigos.clear()
            self.ondas_choque.append(OndaChoque(self.chefao.x, self.chefao.y, COR_DESTAQUE_AMARELO, 220))
            self.textos_flutuantes.append(
                TextoFlutuante(self.chefao.x, self.chefao.y, "+2000 CORE DESTRUIDO!", COR_DESTAQUE_AMARELO)
            )
            for _ in range(45):
                self.particulas.append(Particula(self.chefao.x, self.chefao.y, COR_DESTAQUE_AMARELO))

    def _atingir_tijolo(self, tijolo, dano=1):
        """Processa dano, partículas, combos, explosões e queda de cápsulas."""
        if tijolo not in self.tijolos:
            return

        destruido = tijolo.atingir(dano)
        if not destruido:
            self.audio.tocar("metal")
            for _ in range(5):
                self.particulas.append(
                    Particula(tijolo.rect.centerx, tijolo.rect.centery, tijolo.cor_borda)
                )
            return

        self.tijolos.remove(tijolo)
        self.combo += 1
        multiplicador = 1 + (self.combo - 1) // 3
        ganho = tijolo.pontos * multiplicador
        self.pontuacao += ganho

        label = f"+{ganho}" if multiplicador == 1 else f"+{ganho} (x{multiplicador})"
        self.textos_flutuantes.append(
            TextoFlutuante(tijolo.rect.centerx, tijolo.rect.centery, label, tijolo.cor_borda)
        )

        for _ in range(14):
            self.particulas.append(Particula(tijolo.rect.centerx, tijolo.rect.centery, tijolo.cor))

        if tijolo.tipo == 6:
            self.audio.tocar("explosao")
            self.tremor_tela = 0.22
            self.ondas_choque.append(
                OndaChoque(tijolo.rect.centerx, tijolo.rect.centery, COR_DESTAQUE_LARANJA, 130)
            )
            self._detonar_vizinhos(tijolo.rect.center)
        else:
            self.audio.tocar("tijolo")

        cfg = self.cfg_dificuldade
        if random.random() < cfg["chance_drop"]:
            eh_armadilha = random.random() < cfg["chance_armadilha"]
            if eh_armadilha:
                tipo_sorteado = random.choice(list(TIPOS_ARMADILHA.keys()))
            else:
                tipo_sorteado = random.choice(list(TIPOS_POWERUP.keys()))
            self.capsulas.append(
                Capsula(tijolo.rect.centerx, tijolo.rect.centery, tipo_sorteado, eh_armadilha)
            )

    def _detonar_vizinhos(self, centro):
        """Destrói tijolos destrutíveis adjacentes quando um bloco explosivo detona."""
        cx, cy = centro
        for outro in self.tijolos[:]:
            if not outro.destrutivel:
                continue
            dist = math.hypot(outro.rect.centerx - cx, outro.rect.centery - cy)
            if dist <= 115:
                self._atingir_tijolo(outro, dano=3)

    def _aplicar_capsula(self, cap):
        """Ativa o buff positivo ou a penalidade da armadilha coletada."""
        duracao = self.cfg_dificuldade["duracao_efeito"]

        if cap.eh_armadilha:
            self.audio.tocar("armadilha")
            self.combo = 0
            self.tremor_tela = 0.18
            self.textos_flutuantes.append(
                TextoFlutuante(cap.rect.centerx, cap.rect.centery, f"! {cap.tipo} !", cap.cor)
            )
            if cap.tipo == "ENCOLHER":
                self.raquete.ativar_encolhimento(duracao)
            elif cap.tipo == "TURBO":
                for bola in self.bolas:
                    bola.aplicar_turbo()
            elif cap.tipo == "INVERTER":
                self.raquete.ativar_inversao(duracao)
            return

        self.audio.tocar("powerup")
        self.pontuacao += 150
        self.textos_flutuantes.append(
            TextoFlutuante(cap.rect.centerx, cap.rect.centery, cap.tipo, cap.cor)
        )

        if cap.tipo == "EXPANDIR":
            self.raquete.ativar_expansao(duracao)
        elif cap.tipo == "LASER":
            self.raquete.ativar_laser(duracao)
        elif cap.tipo == "FOGO":
            for bola in self.bolas:
                bola.tempo_fogo = duracao
        elif cap.tipo == "VIDA":
            self.vidas = min(VIDAS_MAXIMAS, self.vidas + 1)
        elif cap.tipo == "MULTIBOLA" and self.bolas:
            base = self.bolas[0]
            for angulo in (-28, 28):
                nova = Bola(base.x, base.y, presa=False, velocidade=base.velocidade)
                nova.tempo_fogo = base.tempo_fogo
                nova.lancar(angulo)
                self.bolas.append(nova)
    def _desenhar_hud(self):
        """Renderiza a barra superior com nome do jogador, pontuação, fase e vidas."""
        pygame.draw.rect(self.tela, (16, 20, 42), (0, 0, LARGURA_TELA, 54))
        pygame.draw.line(self.tela, COR_DESTAQUE_CIANO, (0, 54), (LARGURA_TELA, 54), 2)

        nome_exibicao = self.nome_jogador[:13]
        txt_jogador = self.fonte_hud.render(f"JOGADOR: {nome_exibicao}", True, COR_DESTAQUE_AMARELO)
        txt_pontos = self.fonte_hud.render(f"PONTOS: {self.pontuacao:06d}", True, COR_TEXTO_PRINCIPAL)
        txt_fase = self.fonte_hud.render(
            f"FASE {self.fase_atual + 1}/{self.gerenciador_fases.total_fases}",
            True,
            COR_DESTAQUE_CIANO,
        )

        self.tela.blit(txt_jogador, (18, 17))
        self.tela.blit(txt_pontos, (305, 17))
        self.tela.blit(txt_fase, (515, 17))

        for i in range(self.vidas):
            cx = 650 + i * 22
            pygame.draw.circle(self.tela, COR_DESTAQUE_MAGENTA, (cx, 27), 7)
            pygame.draw.circle(self.tela, (255, 180, 215), (cx - 2, 25), 2)

        status_som = "SOM:ON[M]" if self.audio.ativo else "SOM:OFF[M]"
        cor_som = COR_DESTAQUE_VERDE if self.audio.ativo else COR_TEXTO_SECUNDARIO
        txt_som = self.fonte_pequena.render(status_som, True, cor_som)
        self.tela.blit(txt_som, (LARGURA_TELA - txt_som.get_width() - 16, 20))

        if self.chefao and self.chefao.vivo:
            largura_barra = 340
            x_barra = LARGURA_TELA // 2 - largura_barra // 2
            y_barra = 64
            proporcao = self.chefao.vida / self.chefao.vida_max
            pygame.draw.rect(self.tela, (30, 16, 44), (x_barra, y_barra, largura_barra, 12), border_radius=6)
            pygame.draw.rect(
                self.tela,
                COR_PERIGO_VERMELHO,
                (x_barra, y_barra, int(largura_barra * proporcao), 12),
                border_radius=6,
            )
            pygame.draw.rect(self.tela, COR_DESTAQUE_AMARELO, (x_barra, y_barra, largura_barra, 12), 1, border_radius=6)

        alertas = []
        if self.raquete.tempo_invertida > 0:
            alertas.append((f"CONTROLES INVERTIDOS ({self.raquete.tempo_invertida:.1f}s)", COR_PERIGO_ROXO))
        if self.raquete.tempo_encolhida > 0:
            alertas.append((f"RAQUETE ENCOLHIDA ({self.raquete.tempo_encolhida:.1f}s)", COR_PERIGO_VERMELHO))
        if self.raquete.tempo_laser > 0:
            alertas.append((f"LASER ATIVO ({self.raquete.tempo_laser:.1f}s)", COR_DESTAQUE_LARANJA))
        if any(b.tempo_fogo > 0 for b in self.bolas):
            alertas.append(("BOLA DE FOGO", COR_DESTAQUE_AMARELO))

        if alertas:
            texto_alerta, cor_alerta = alertas[0]
            self._desenhar_texto_centralizado(self.fonte_pequena, texto_alerta, cor_alerta, ALTURA_TELA - 18)

    def _desenhar_texto_centralizado(self, fonte, texto, cor, y):
        """Auxiliar para centralizar linhas de texto horizontalmente."""
        surf = fonte.render(texto, True, cor)
        self.tela.blit(surf, surf.get_rect(center=(LARGURA_TELA // 2, y)))

    def _desenhar_menu(self):
        """Renderiza a tela inicial com dificuldade, comandos e pontuações."""
        pulso = int(8 * math.sin(self.tempo_global * 4))
        self._desenhar_texto_centralizado(
            self.fonte_titulo, "NEON BREAKOUT", COR_DESTAQUE_CIANO, 105 + pulso // 2
        )
        self._desenhar_texto_centralizado(
            self.fonte_subtitulo, "EDICAO FEIRA DE JOGOS // ATARI REIMAGINED", COR_DESTAQUE_MAGENTA, 152
        )

        self._desenhar_texto_centralizado(
            self.fonte_texto, "SELECIONE A DIFICULDADE (SETAS < > ou 1 / 2 / 3):", COR_TEXTO_SECUNDARIO, 198
        )
        largura_btn = 160
        espaco_btn = 24
        total_w = 3 * largura_btn + 2 * espaco_btn
        inicio_x = (LARGURA_TELA - total_w) // 2

        for idx, chave in enumerate(ORDEM_DIFICULDADES):
            info = DIFICULDADES[chave]
            selecionado = idx == self.indice_dificuldade
            rect_btn = pygame.Rect(inicio_x + idx * (largura_btn + espaco_btn), 218, largura_btn, 40)
            cor_fundo_btn = (34, 42, 82) if selecionado else (16, 20, 42)
            cor_borda_btn = info["cor"] if selecionado else (70, 80, 120)

            pygame.draw.rect(self.tela, cor_fundo_btn, rect_btn, border_radius=10)
            pygame.draw.rect(self.tela, cor_borda_btn, rect_btn, 3 if selecionado else 1, border_radius=10)
            lbl = self.fonte_hud.render(info["rotulo"], True, info["cor"] if selecionado else COR_TEXTO_SECUNDARIO)
            self.tela.blit(lbl, lbl.get_rect(center=rect_btn.center))

        # Painel de comandos
        painel = pygame.Rect(LARGURA_TELA // 2 - 295, 276, 590, 152)
        pygame.draw.rect(self.tela, (18, 22, 48), painel, border_radius=12)
        pygame.draw.rect(self.tela, COR_DESTAQUE_CIANO, painel, 2, border_radius=12)

        self._desenhar_texto_centralizado(
            self.fonte_subtitulo, "[ ENTER ] ou [ ESPACO ]  -  INICIAR PARTIDA", COR_DESTAQUE_VERDE, 306
        )
        self._desenhar_texto_centralizado(
            self.fonte_subtitulo, "[ I ]  -  COMO JOGAR, ARMADILHAS E CHEFAO", COR_DESTAQUE_AMARELO, 348
        )
        self._desenhar_texto_centralizado(
            self.fonte_texto, "[ F11 ] Tela Cheia   |   [ M ] Audio   |   [ ESC ] Sair", COR_TEXTO_SECUNDARIO, 394
        )

        # Painel de pontuações dos jogadores da sessão
        painel_pontos = pygame.Rect(LARGURA_TELA // 2 - 295, 446, 590, 212)
        pygame.draw.rect(self.tela, (18, 22, 48), painel_pontos, border_radius=12)
        pygame.draw.rect(self.tela, COR_DESTAQUE_MAGENTA, painel_pontos, 2, border_radius=12)

        self._desenhar_texto_centralizado(
            self.fonte_hud, "PONTUACAO DOS JOGADORES", COR_DESTAQUE_AMARELO, 470
        )
        pygame.draw.line(
            self.tela,
            COR_DESTAQUE_MAGENTA,
            (painel_pontos.left + 24, 490),
            (painel_pontos.right - 24, 490),
            1,
        )

        if not self.historico_partidas:
            self._desenhar_texto_centralizado(
                self.fonte_texto,
                "Nenhuma partida registrada ainda — aperte ENTER para jogar!",
                COR_TEXTO_SECUNDARIO,
                565,
            )
        else:
            y_linha = 510
            for idx, item in enumerate(self.historico_partidas):
                cor_linha = COR_DESTAQUE_VERDE if idx == 0 else COR_TEXTO_PRINCIPAL
                texto_registro = (
                    f"{item['nome']:<16}   {item['dificuldade']:<8}   {item['pontos']:06d} PTS"
                )
                self._desenhar_texto_centralizado(self.fonte_hud, texto_registro, cor_linha, y_linha)
                y_linha += 34

    def _desenhar_tela_nome(self):
        """Renderiza a caixa de texto para o jogador digitar seu nome."""
        self._desenhar_texto_centralizado(
            self.fonte_titulo, "IDENTIFICACAO", COR_DESTAQUE_CIANO, 155
        )

        painel = pygame.Rect(LARGURA_TELA // 2 - 290, 225, 580, 270)
        pygame.draw.rect(self.tela, (18, 22, 48), painel, border_radius=14)
        pygame.draw.rect(self.tela, COR_DESTAQUE_MAGENTA, painel, 2, border_radius=14)

        self._desenhar_texto_centralizado(
            self.fonte_subtitulo, "DIGITE O NOME DO JOGADOR:", COR_TEXTO_PRINCIPAL, 272
        )

        caixa_texto = pygame.Rect(LARGURA_TELA // 2 - 210, 315, 420, 56)
        pygame.draw.rect(self.tela, (10, 14, 30), caixa_texto, border_radius=10)
        pygame.draw.rect(self.tela, COR_DESTAQUE_AMARELO, caixa_texto, 2, border_radius=10)

        cursor = "_" if int(self.tempo_global * 3) % 2 == 0 else " "
        texto_exibido = f"{self.nome_jogador}{cursor}"
        surf_nome = self.fonte_subtitulo.render(texto_exibido, True, COR_DESTAQUE_AMARELO)
        self.tela.blit(surf_nome, surf_nome.get_rect(center=caixa_texto.center))

        self._desenhar_texto_centralizado(
            self.fonte_subtitulo, "[ ENTER ] Confirmar e Jogar", COR_DESTAQUE_VERDE, 415
        )
        self._desenhar_texto_centralizado(
            self.fonte_texto, "[ ESC ] Voltar ao Menu", COR_TEXTO_SECUNDARIO, 458
        )
    def _desenhar_instrucoes(self):
        """Renderiza a tela informativa com controles, blocos, bônus e armadilhas."""
        self._desenhar_texto_centralizado(
            self.fonte_titulo, "GUIA DE SOBREVIVENCIA", COR_DESTAQUE_CIANO, 82
        )

        painel = pygame.Rect(75, 130, LARGURA_TELA - 150, 480)
        pygame.draw.rect(self.tela, (18, 22, 48), painel, border_radius=12)
        pygame.draw.rect(self.tela, COR_DESTAQUE_MAGENTA, painel, 2, border_radius=12)

        linhas = [
            ("CONTROLES:", COR_DESTAQUE_AMARELO),
            ("  Setas / A-D / Mouse: Move raquete  |  Espaco/Clique: Lanca e atira", COR_TEXTO_PRINCIPAL),
            ("  P / ESC: Pausar   |   F11: Tela Cheia/Janela   |   M: Mutar som", COR_TEXTO_PRINCIPAL),
            ("", COR_TEXTO_PRINCIPAL),
            ("OBSTACULOS E INIMIGOS:", COR_DESTAQUE_AMARELO),
            ("  Prismas Cinza (X): Indestrutiveis  |  Laranja: Explode vizinhos", COR_TEXTO_PRINCIPAL),
            ("  Drones Roxos: Desviam a bola (destrua com Laser ou Bola de Fogo)", COR_TEXTO_PRINCIPAL),
            ("  Fase 4 (Chefao Core): Atira plasma que encolhe e paralisa a raquete", COR_TEXTO_PRINCIPAL),
            ("", COR_TEXTO_PRINCIPAL),
            ("CAPSULAS POSITIVAS (BORDAS ARREDONDADAS):", COR_DESTAQUE_VERDE),
            ("  [EXP] Raquete maior   [3X] Multibola   [LSR] Lasers   [FGO] Fogo   [+1V] Vida", COR_DESTAQUE_CIANO),
            ("", COR_TEXTO_PRINCIPAL),
            ("ARMADILHAS PARA DESVIAR (CAPSULAS QUADRADAS):", COR_PERIGO_VERMELHO),
            ("  [-LARG] Encolhe raquete   [FAST] Acelera bola   [INV] Inverte controles", COR_PERIGO_ROXO),
        ]

        y = 152
        for texto, cor in linhas:
            surf = self.fonte_texto.render(texto, True, cor)
            self.tela.blit(surf, (105, y))
            y += 30

        self._desenhar_texto_centralizado(
            self.fonte_subtitulo, "Pressione [ ENTER ] ou [ ESC ] para voltar", COR_DESTAQUE_VERDE, 645
        )

    def _desenhar_partida(self):
        """Desenha todos os elementos ativos da arena durante o jogo."""
        self._desenhar_hud()

        for tijolo in self.tijolos:
            tijolo.desenhar(self.tela)

        if self.chefao and self.chefao.vivo:
            self.chefao.desenhar(self.tela)

        for drone in self.drones:
            drone.desenhar(self.tela)

        for cap in self.capsulas:
            cap.desenhar(self.tela, self.fonte_pequena)

        for laser in self.lasers:
            laser.desenhar(self.tela)

        for tiro in self.tiros_inimigos:
            tiro.desenhar(self.tela)

        self.raquete.desenhar(self.tela)

        for bola in self.bolas:
            bola.desenhar(self.tela)

        for onda in self.ondas_choque:
            onda.desenhar(self.tela)

        for p in self.particulas:
            p.desenhar(self.tela)

        for txt in self.textos_flutuantes:
            txt.desenhar(self.tela, self.fonte_pequena)

        if any(b.presa for b in self.bolas):
            info = self.gerenciador_fases.obter_info_fase(self.fase_atual)
            self._desenhar_texto_centralizado(
                self.fonte_subtitulo, info["nome"], COR_DESTAQUE_AMARELO, 455
            )
            self._desenhar_texto_centralizado(
                self.fonte_texto, info["subtitulo"], COR_TEXTO_SECUNDARIO, 488
            )
            self._desenhar_texto_centralizado(
                self.fonte_texto,
                "Pressione ESPACO ou CLIQUE para lancar a bola",
                COR_TEXTO_PRINCIPAL,
                525,
            )

    def _desenhar_overlay_central(self, titulo, subtitulo, instrucao, cor_titulo, subtitulo_extra=None):
        """Desenha um painel semitransparente para Pausa, Transição ou Fim."""
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((8, 10, 22, 185))
        self.tela.blit(overlay, (0, 0))

        altura_caixa = 305 if subtitulo_extra else 270
        caixa = pygame.Rect(
            LARGURA_TELA // 2 - 345,
            ALTURA_TELA // 2 - altura_caixa // 2,
            690,
            altura_caixa,
        )
        pygame.draw.rect(self.tela, (20, 24, 52), caixa, border_radius=14)
        pygame.draw.rect(self.tela, cor_titulo, caixa, 3, border_radius=14)

        if subtitulo_extra:
            self._desenhar_texto_centralizado(
                self.fonte_titulo, titulo, cor_titulo, ALTURA_TELA // 2 - 90
            )
            self._desenhar_texto_centralizado(
                self.fonte_subtitulo, subtitulo, COR_DESTAQUE_CIANO, ALTURA_TELA // 2 - 22
            )
            self._desenhar_texto_centralizado(
                self.fonte_subtitulo, subtitulo_extra, COR_DESTAQUE_AMARELO, ALTURA_TELA // 2 + 22
            )
            self._desenhar_texto_centralizado(
                self.fonte_texto, instrucao, COR_TEXTO_PRINCIPAL, ALTURA_TELA // 2 + 95
            )
        else:
            self._desenhar_texto_centralizado(
                self.fonte_titulo, titulo, cor_titulo, ALTURA_TELA // 2 - 70
            )
            self._desenhar_texto_centralizado(
                self.fonte_subtitulo, subtitulo, COR_TEXTO_PRINCIPAL, ALTURA_TELA // 2
            )
            self._desenhar_texto_centralizado(
                self.fonte_texto, instrucao, COR_DESTAQUE_AMARELO, ALTURA_TELA // 2 + 72
            )

    def executar(self):
        """Executa o loop principal da aplicação a 60 quadros por segundo."""
        rodando = True
        while rodando:
            dt = min(self.relogio.tick(FPS) / 1000.0, 0.05)
            self.tempo_global += dt
            if self.tremor_tela > 0:
                self.tremor_tela = max(0.0, self.tremor_tela - dt)

            rodando = self._processar_eventos()
            self.fundo.atualizar(dt)

            if self.estado == "JOGANDO":
                self._atualizar_jogando(dt)

            self.tela.fill(COR_FUNDO)
            self.fundo.desenhar(self.tela)

            if self.estado == "MENU":
                self._desenhar_menu()
            elif self.estado == "NOME_JOGADOR":
                self._desenhar_tela_nome()
            elif self.estado == "INSTRUCOES":
                self._desenhar_instrucoes()
            elif self.estado == "JOGANDO":
                self._desenhar_partida()
            elif self.estado == "PAUSADO":
                self._desenhar_partida()
                self._desenhar_overlay_central(
                    "JOGO PAUSADO",
                    f"{self.nome_jogador}  |  Pontuacao: {self.pontuacao:06d}",
                    "[ P / ENTER ] Continuar   |   [ Q ] Menu Inicial",
                    COR_DESTAQUE_CIANO,
                )
            elif self.estado == "TRANSICAO_FASE":
                self._desenhar_partida()
                self._desenhar_overlay_central(
                    "FASE CONCLUIDA!",
                    f"{self.nome_jogador}  |  Pontos: {self.pontuacao:06d}",
                    "Pressione [ ENTER ] ou [ ESPACO ] para a proxima fase",
                    COR_DESTAQUE_VERDE,
                )
            elif self.estado == "FIM_DE_JOGO":
                titulo = "VITORIA TOTAL!" if self.vitoria_final else "FIM DE JOGO"
                cor = COR_DESTAQUE_VERDE if self.vitoria_final else COR_DESTAQUE_MAGENTA
                self._desenhar_overlay_central(
                    titulo,
                    f"JOGADOR: {self.nome_jogador}",
                    "[ ENTER ] Jogar Novamente  |  [ N ] Novo Jogador  |  [ ESC ] Menu",
                    cor,
                    subtitulo_extra=f"PONTUACAO FINAL: {self.pontuacao:06d} PTS",
                )

            if self.tremor_tela > 0:
                desloc_x = random.randint(-5, 5)
                desloc_y = random.randint(-5, 5)
                copia = self.tela.copy()
                self.tela.fill(COR_FUNDO)
                self.tela.blit(copia, (desloc_x, desloc_y))

            pygame.display.flip()

        pygame.quit()