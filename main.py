import asyncio
import pygame
import random

pygame.init()

pygame.mixer.init()


screen = pygame.display.set_mode((800, 600))
running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 20, 1)

# load images and sprites
background = []
rain = []
tree = []
droplets = []
darker = []


def pg_load_png(fn: str, cvt_alpha=True):
    if cvt_alpha:
        return pygame.image.load(f"img/{fn}.png")
    return pygame.image.load(f"img/{fn}.png").convert()


for i in range(4):
    background.append(pg_load_png(f"bg{i}", cvt_alpha=False))

    rain.append(pg_load_png(f"rain{i}"))
    tree.append(pg_load_png(f"tree{i}"))
    droplets.append(pg_load_png(f"droplets{i}"))
    darker.append(pg_load_png("darker"))


window = pg_load_png("window")
slider_bg = pg_load_png("slider_bg")
slider_handle = pg_load_png("slider_handle")
options_img = [pg_load_png("options"), pg_load_png("close")]


for i in range(3):
    darker[i + 1].blit(darker[i], (0, 0))

# load sounds
sounds = {}

keys = ["brown", "pink", "flow", "wind", "drops"]
for key in keys:
    sounds[key] = [pygame.mixer.Sound(f"sfx/{key}.ogg")]
    sounds[key][0].set_volume(0)
    sounds[key][0].play(-1)


sounds["thunder"] = [[], [0], [50], 0]  # samples, frequency, volume, sprite
for i in range(3):
    sounds["thunder"][0].append(pygame.mixer.Sound(f"sfx/thunder{i}.ogg"))
    sounds["thunder"][0][i].set_volume(0.5)


async def main():
    running = 1
    timer = delay = 0
    mouse_pos = [0, 0]
    clicked = 0
    options = 0
    options_rect = pygame.Rect(760, 0, 40, 40)

    tree_sprite = 0
    frame = window.copy()
    bg_sprite = 0
    rain_sprite = 0
    droplets_sprite = 0
    thunder_sprite = 4

    while True:
        if timer % 3 == 1:
            frame.blit(background[bg_sprite], (151, 46))
            frame.blit(rain[rain_sprite], (151, 46))

        elif timer % 3 == 2:
            frame.blit(tree[tree_sprite], (151, 46))
            frame.blit(droplets[droplets_sprite], (151, 46))

            if thunder_sprite > 0:
                frame.blit(darker[thunder_sprite - 1], (151, 46))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = 0

        # clock.tick(60) # only for testing with regular pygame
        timer += 1
        if timer < 100:
            for key in keys:
                sounds[key][0].set_volume(timer * 0.005)
        if timer == 150:
            thunder_sprite = 0
            sounds["thunder"][0][1].play()
            sounds["thunder"][1][0] = 20

        if timer % 59 == 0:
            bg_sprite = (bg_sprite + 1) % 4
        if timer % 27 == 0:
            rain_sprite = (rain_sprite + 1) % 4
        if timer % 43 == 0:
            droplets_sprite = (droplets_sprite + 1) % 4
        if timer % 77 == 0:
            tree_sprite = (tree_sprite + 1) % 3
        if thunder_sprite < 4 and timer % 11 == 0:
            thunder_sprite += 1
        if timer % 83 == 0 and thunder_sprite == 4:
            if random.randint(0, 100) < sounds["thunder"][1][0]:
                thunder_sprite = 0
                sample = random.randint(0, len(sounds["thunder"][0]) - 1)
                sounds["thunder"][0][sample].set_volume(sounds["thunder"][2][0] * 0.01)
                sounds["thunder"][0][sample].play()

        if pygame.mouse.get_pressed()[0]:
            if not clicked:
                mouse_pos = list(pygame.mouse.get_pos())
                clicked = 1
            else:
                mouse_pos[1] = pygame.mouse.get_pos()[1]

        else:
            clicked = 0

        if clicked and options_rect.collidepoint(mouse_pos) and timer > delay:
            options = not (options)
            frame.blit(window, (0, 0))
            delay = timer + 30

        if options:
            if timer % 3 == 2:
                frame.blit(window, (0, 0))
                frame.blit(
                    font.render(
                        "Adjust sound volumes and thunder strike frequency.",
                        1,
                        (255, 255, 255),
                    ),
                    ((150, 575)),
                )
                frame.blit(font.render("thunder", 1, (255, 255, 255)), ((570, 25)))
                frame.blit(font.render("strikes", 1, (255, 255, 255)), ((670, 25)))

            if timer % 3 == 0:
                for i in range(len(sounds) - 1):
                    frame.blit(
                        font.render(keys[i], 1, (255, 255, 255)), ((75 + i * 100, 25))
                    )
                    slider(
                        (75 + i * 100, 50),
                        slider_bg,
                        slider_handle,
                        frame,
                        mouse_pos,
                        clicked,
                        sounds[keys[i]][0],
                    )

                slider(
                    (575, 50),
                    slider_bg,
                    slider_handle,
                    frame,
                    mouse_pos,
                    clicked,
                    sounds["thunder"][2],
                )
                slider(
                    (675, 50),
                    slider_bg,
                    slider_handle,
                    frame,
                    mouse_pos,
                    clicked,
                    sounds["thunder"][1],
                )

        if timer % 3 == 0:
            frame.blit(options_img[options], (765, 10))

            screen.blit(frame, (0, 0))

        pygame.display.flip()
        await asyncio.sleep(0)  # very important, and keep it 0

        if not running:
            pygame.quit()
            return


def slider(coords, background, handle, frame, mouse_pos, clicked, sound):

    frame.blit(background, coords)
    size = list(background.get_size())
    size[1] = size[1] - handle.get_size()[1]

    rect = pygame.Rect(coords[0], coords[1], size[0], size[1])

    if type(sound) == list:
        position = sound[0] * 0.01
    else:
        try:
            position = sound.get_volume()
        except:
            position = 0
            sound.set_volume(0)

    if clicked and rect.collidepoint(
        mouse_pos[0], mouse_pos[1] - handle.get_size()[1] / 2
    ):
        position = 1 - (mouse_pos[1] - coords[1] - handle.get_size()[1] / 2) / size[1]
        if type(sound) == list:
            sound[0] = int(position * 100)
        else:
            sound.set_volume(position)

    frame.blit(handle, (coords[0], coords[1] + size[1] * (1 - position)))


asyncio.run(main())

# do not add anything from here
# asyncio.run is non block on pg-wasm
