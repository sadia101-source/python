import pygame
import random
import math
import sys

pygame.init()

WIDTH = 1000
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ghost Rider")

clock = pygame.time.Clock()

BLACK = (10, 10, 15)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
GREEN = (40, 220, 80)
BLUE = (50, 150, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 220, 50)

font = pygame.font.SysFont("arial", 25, bold=True)
big_font = pygame.font.SysFont("arial", 70, bold=True)
medium_font = pygame.font.SysFont("arial", 40, bold=True)

try:
    player_image = pygame.image.load("a.jpg").convert()
    ghost_image = pygame.image.load("c.jpg").convert()
except pygame.error as e:
    print("Could not load a.jpg or c.jpg")
    print("Make sure both files are in the same folder as this Python file.")
    pygame.quit()
    sys.exit()

PLAYER_SIZE = 55
GHOST_SIZE = 55

player_image = pygame.transform.scale(
    player_image, (PLAYER_SIZE, PLAYER_SIZE)
)

ghost_image = pygame.transform.scale(
    ghost_image, (GHOST_SIZE, GHOST_SIZE)
)

player = pygame.Rect(
    WIDTH // 2 - PLAYER_SIZE // 2,
    HEIGHT // 2 - PLAYER_SIZE // 2,
    PLAYER_SIZE,
    PLAYER_SIZE
)

PLAYER_SPEED = 5

last_direction = pygame.Vector2(0, -1)

bullets = []

BULLET_SPEED = 12
BULLET_RADIUS = 5

SHOOT_COOLDOWN = 180  # milliseconds
last_shot_time = 0

ghosts = []

GHOST_SPEED = 1.7
GHOST_HIT_DISTANCE = 40

# Each ghost will contain:
# {
#   "rect": pygame.Rect,
#   "hits": number of hits received
# }

kills = 0
game_over = False
game_won = False

# Spawn a ghost every 7 seconds
SPAWN_INTERVAL = 7000
last_spawn_time = pygame.time.get_ticks()


def create_ghost():
    """Create a ghost somewhere around the edge of the screen."""

    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x = random.randint(0, WIDTH - GHOST_SIZE)
        y = -GHOST_SIZE

    elif side == "bottom":
        x = random.randint(0, WIDTH - GHOST_SIZE)
        y = HEIGHT

    elif side == "left":
        x = -GHOST_SIZE
        y = random.randint(0, HEIGHT - GHOST_SIZE)

    else:
        x = WIDTH
        y = random.randint(0, HEIGHT - GHOST_SIZE)

    ghost = {
        "rect": pygame.Rect(x, y, GHOST_SIZE, GHOST_SIZE),
        "hits": 0
    }

    ghosts.append(ghost)


for _ in range(3):
    create_ghost()


# reset game
def reset_game():
    global kills
    global game_over
    global game_won
    global last_spawn_time
    global last_shot_time
    global last_direction

    player.center = (WIDTH // 2, HEIGHT // 2)

    bullets.clear()
    ghosts.clear()

    for _ in range(3):
        create_ghost()

    kills = 0
    game_over = False
    game_won = False

    last_spawn_time = pygame.time.get_ticks()
    last_shot_time = 0

    last_direction = pygame.Vector2(0, -1)


def shoot():
    global last_shot_time

    current_time = pygame.time.get_ticks()

    if current_time - last_shot_time < SHOOT_COOLDOWN:
        return

    last_shot_time = current_time

    bullet_position = pygame.Vector2(player.center)

    direction = last_direction.normalize()

    bullets.append({
        "pos": bullet_position,
        "direction": direction
    })


def draw_text(text, font_obj, color, x, y, center=True):
    surface = font_obj.render(text, True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)

running = True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Shoot on Space
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                if not game_over and not game_won:
                    shoot()

            if event.key == pygame.K_r:

                if game_over or game_won:
                    reset_game()


    if not game_over and not game_won:

        keys = pygame.key.get_pressed()

        movement = pygame.Vector2(0, 0)

        # Movements
        if keys[pygame.K_UP]:
            movement.y -= 1

        if keys[pygame.K_DOWN]:
            movement.y += 1

        if keys[pygame.K_LEFT]:
            movement.x -= 1

        if keys[pygame.K_KP_0]:
            movement.x += 1

        if movement.length() > 0:

            movement = movement.normalize()

            last_direction = movement

            player.x += int(movement.x * PLAYER_SPEED)
            player.y += int(movement.y * PLAYER_SPEED)

        # Keep player inside screen
        player.left = max(player.left, 0)
        player.right = min(player.right, WIDTH)

        player.top = max(player.top, 0)
        player.bottom = min(player.bottom, HEIGHT)

        current_time = pygame.time.get_ticks()

        if current_time - last_spawn_time >= SPAWN_INTERVAL:

            create_ghost()
            last_spawn_time = current_time

        
        player_center = pygame.Vector2(player.center)

        for ghost in ghosts:

            ghost_center = pygame.Vector2(ghost["rect"].center)

            direction = player_center - ghost_center

            if direction.length() > 0:
                direction = direction.normalize()

                ghost["rect"].x += int(direction.x * GHOST_SPEED)
                ghost["rect"].y += int(direction.y * GHOST_SPEED)

        
        for bullet in bullets[:]:

            bullet["pos"] += bullet["direction"] * BULLET_SPEED

            # Remove bullets outside screen
            if (
                bullet["pos"].x < 0
                or bullet["pos"].x > WIDTH
                or bullet["pos"].y < 0
                or bullet["pos"].y > HEIGHT
            ):
                bullets.remove(bullet)

        
        for bullet in bullets[:]:

            bullet_rect = pygame.Rect(
                int(bullet["pos"].x - BULLET_RADIUS),
                int(bullet["pos"].y - BULLET_RADIUS),
                BULLET_RADIUS * 2,
                BULLET_RADIUS * 2
            )

            bullet_hit = False

            for ghost in ghosts[:]:

                if bullet_rect.colliderect(ghost["rect"]):

                    # Bullet hit ghost
                    ghost["hits"] += 1
                    bullet_hit = True

                    # Remove bullet after one hit
                    if bullet in bullets:
                        bullets.remove(bullet)

                    # Ghost dies after 3 hits
                    if ghost["hits"] >= 3:

                        if ghost in ghosts:
                            ghosts.remove(ghost)

                        kills += 1

                        # 100 kills = win
                        if kills >= 100:
                            game_won = True

                    break

            if bullet_hit:
                continue

        for ghost in ghosts:

            distance = math.dist(
                player.center,
                ghost["rect"].center
            )

            if distance <= GHOST_HIT_DISTANCE:
                game_over = True
                break

        # ghost limit check
        if len(ghosts) > 6:
            game_over = True

    
    screen.fill(BLACK)

    for x in range(0, WIDTH, 50):
        pygame.draw.line(
            screen,
            (20, 20, 28),
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(
            screen,
            (20, 20, 28),
            (0, y),
            (WIDTH, y)
        )

    for bullet in bullets:

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                int(bullet["pos"].x),
                int(bullet["pos"].y)
            ),
            BULLET_RADIUS
        )

    for ghost in ghosts:

        rect = ghost["rect"]

        screen.blit(
            ghost_image,
            rect
        )

        hit_text = font.render(
            f"{ghost['hits']}/3",
            True,
            RED
        )

        hit_rect = hit_text.get_rect(
            center=(rect.centerx, rect.top - 10)
        )

        screen.blit(hit_text, hit_rect)

    screen.blit(
        player_image,
        player
    )

    draw_text(
        f"Ghosts: {len(ghosts)}/6",
        font,
        WHITE,
        20,
        20,
        center=False
    )

    draw_text(
        f"Ghosts Killed: {kills}/100",
        font,
        GREEN,
        20,
        55,
        center=False
    )

    draw_text(
        "SPACE = Shoot",
        font,
        YELLOW,
        WIDTH - 220,
        20,
        center=False
    )

    draw_text(
        "ARROW KEYS = Move",
        font,
        WHITE,
        WIDTH - 260,
        55,
        center=False
    )

    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        draw_text(
            "YOU DIED",
            big_font,
            RED,
            WIDTH // 2,
            HEIGHT // 2 - 80
        )

        if len(ghosts) > 6:
            reason = "Too many ghosts!"

        else:
            reason = "A ghost caught you!"

        draw_text(
            reason,
            medium_font,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2
        )

        draw_text(
            f"Ghosts killed: {kills}",
            font,
            GREEN,
            WIDTH // 2,
            HEIGHT // 2 + 60
        )

        draw_text(
            "Press R to restart",
            font,
            YELLOW,
            WIDTH // 2,
            HEIGHT // 2 + 110
        )

    if game_won:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((5, 5, 20))
        screen.blit(overlay, (0, 0))

        draw_text(
            "YOU WIN!",
            big_font,
            GREEN,
            WIDTH // 2,
            HEIGHT // 2 - 100
        )

        draw_text(
            "GHOST RIDER",
            big_font,
            YELLOW,
            WIDTH // 2,
            HEIGHT // 2
        )

        draw_text(
            "You killed 100 ghosts!",
            medium_font,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 + 80
        )

        draw_text(
            "Press R to play again",
            font,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 + 140
        )

    pygame.display.flip()

pygame.quit()
sys.exit()