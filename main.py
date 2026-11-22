"""
Ponto de entrada principal da aplicação Neon Breakout.

Instancia e inicia o controlador do jogo em tela cheia.
"""

from jogo import JogoBreakout


def main():
    """Inicializa e executa o jogo Breakout."""
    jogo = JogoBreakout()
    jogo.executar()


if __name__ == "__main__":
    main()