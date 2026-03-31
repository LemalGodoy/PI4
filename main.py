import pygame
import sys
import settings
from engine.player import Player
from levels.level_1 import Level1Troll
from levels.level_16 import Level16Boss
from levels.level_7_adapter import run_level_7
from scenes.lobby import Lobby
from engine.renderer import draw_transition_screen


def main():
    lobby = Lobby()
    player = Player(settings.WIDTH // 2 - 20, settings.HEIGHT // 2 - 30)

    level1 = Level1Troll()
    level16 = Level16Boss()

    current_state = "LOBBY"
    current_ods = None
    transition_timer = 0
    lobby_pos = (player.rect.x, player.rect.y)

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if current_state == "LOBBY":
                    if event.key == pygame.K_e or event.key == pygame.K_RETURN:
                        door = lobby.get_interacting_door(player)
                        if door:
                            current_ods = door
                            lobby_pos = (player.rect.x, player.rect.y)
                            if door.id == 1:
                                current_state = "TRANSITION_L1"
                                transition_timer = 180
                            elif door.id == 7:
                                # Level 7 roda como subprocesso
                                won = run_level_7()
                                if won:
                                    lobby.doors[6].color = (0, 255, 0)
                                player.rect.x, player.rect.y = lobby_pos
                                current_state = "LOBBY"
                                current_ods = None
                            elif door.id == 16:
                                current_state = "LEVEL_16"
                                level16.reset(settings.WIDTH, settings.HEIGHT)
                                player.rect.x, player.rect.y = level16.player_start
                            else:
                                current_state = f"LEVEL_{door.id}"

                elif current_state.startswith("LEVEL_") or current_state == "TRANSITION_L1":
                    if event.key == pygame.K_ESCAPE:
                        if current_state in ["LEVEL_1", "TRANSITION_L1", "LEVEL_16"]:
                            player.rect.x, player.rect.y = lobby_pos
                            player.inverted_controls = False
                        else:
                            player.rect.y += 30
                        current_state = "LOBBY"
                        current_ods = None

        # ========================================== #
        # UPDATE & DRAW POR ESTADO
        # ========================================== #

        if current_state == "LOBBY":
            lobby.update(player, keys)
            lobby.draw(settings.screen, player)

        elif current_state == "TRANSITION_L1":
            draw_transition_screen(settings.screen)
            transition_timer -= 1
            if transition_timer <= 0:
                current_state = "LEVEL_1"
                level1.reset(settings.screen.get_width(), settings.screen.get_height(), player)
                player.rect.x, player.rect.y = level1.player_start

        elif current_state == "LEVEL_1":
            if not level1.won:
                level1.handle_movement(player, keys)
            level1.update(player)
            level1.draw(settings.screen)

            if not level1.won:
                # Desenhar o jogador na posição de tela (com offset da câmera)
                if level1.camera:
                    screen_rect = level1.camera.apply(player.rect)
                    player.draw_at(settings.screen, screen_rect.x, screen_rect.y)
                else:
                    player.draw(settings.screen)
            else:
                pygame.display.flip()
                pygame.time.wait(2000)
                lobby.doors[0].color = (0, 255, 0)
                current_state = "LOBBY"
                current_ods = None
                player.rect.x, player.rect.y = lobby_pos

        elif current_state == "LEVEL_16":
            if not level16.won:
                level16.handle_movement(player, keys)
            level16.update(player)

            if level16.downgrade:
                temp_w, temp_h = settings.WIDTH // 4, settings.HEIGHT // 4
                temp_surf = pygame.Surface((temp_w, temp_h))

                saved_boss_x, saved_boss_y = level16.boss_rect.x, level16.boss_rect.y
                level16.boss_rect.x //= 4
                level16.boss_rect.y //= 4
                level16.boss_rect.width //= 4
                level16.boss_rect.height //= 4

                level16.draw(temp_surf)

                level16.boss_rect.x, level16.boss_rect.y = saved_boss_x, saved_boss_y
                level16.boss_rect.width, level16.boss_rect.height = 100, 100

                if not level16.won:
                    saved_px, saved_py = player.rect.x, player.rect.y
                    player.rect.x //= 4
                    player.rect.y //= 4
                    player.rect.width //= 4
                    player.rect.height //= 4
                    player.draw(temp_surf)
                    player.rect.x, player.rect.y = saved_px, saved_py
                    player.rect.width, player.rect.height = 40, 60

                scaled_up = pygame.transform.scale(temp_surf, (settings.WIDTH, settings.HEIGHT))
                settings.screen.blit(scaled_up, (0, 0))
            else:
                level16.draw(settings.screen)
                if not level16.won:
                    player.draw(settings.screen)

            if level16.inverted_colors and not level16.won:
                inv_surf = pygame.Surface((settings.WIDTH, settings.HEIGHT))
                inv_surf.fill((255, 255, 255))
                settings.screen.blit(inv_surf, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

            if level16.won:
                pygame.display.flip()
                pygame.time.wait(3000)
                lobby.doors[15].color = (0, 255, 0)
                current_state = "LOBBY"
                current_ods = None
                player.rect.x, player.rect.y = lobby_pos

        else:
            # Placeholder para as outras ODS (2-15, 17)
            if current_ods:
                settings.screen.fill(current_ods.color)

                level_title = settings.title_font.render(
                    f"Fase da ODS {current_ods.id}", True, (255, 255, 255))
                level_name = settings.title_font.render(
                    current_ods.name, True, (255, 255, 255))
                dev_msg = settings.font.render(
                    "O código e a dinâmica dessa fase específica entrarão aqui.",
                    True, (220, 220, 220))
                exit_text = settings.font.render(
                    ">>> Pressione ESC para voltar ao Bazar <<<",
                    True, (255, 255, 255))

                cx = settings.WIDTH // 2
                cy = settings.HEIGHT // 2
                settings.screen.blit(level_title, (cx - level_title.get_width() // 2, cy - 80))
                settings.screen.blit(level_name, (cx - level_name.get_width() // 2, cy - 30))
                settings.screen.blit(dev_msg, (cx - dev_msg.get_width() // 2, cy + 20))
                settings.screen.blit(exit_text, (cx - exit_text.get_width() // 2, cy + 100))

        pygame.display.flip()
        settings.clock.tick(60)

 
if __name__ == "__main__":
    main()
