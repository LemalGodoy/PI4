"""
Adapter para integrar o Level 7 (script standalone) ao loop principal do jogo.
Executa level_7.py como subprocesso e retorna o resultado ao main.py.
"""
import subprocess
import sys
import os

import pygame
import settings


def run_level_7():
    """
    Executa o Level 7 como subprocesso separado.
    Retorna True se o processo terminou normalmente (assume vitória),
    False caso contrário.
    """
    # Caminho do level_7.py
    level_7_path = os.path.join(os.path.dirname(__file__), "level_7.py")

    # Fechar temporariamente o display do main.py
    pygame.display.quit()

    try:
        # Executar level_7.py como subprocesso
        result = subprocess.run(
            [sys.executable, level_7_path],
            cwd=os.path.dirname(level_7_path)
        )
        won = (result.returncode == 0)
    except Exception as e:
        print(f"Erro ao executar Level 7: {e}")
        won = False

    # Restaurar o display do main.py
    settings.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Bazar dos Objetivos Globais - Menu ODS")

    return won
