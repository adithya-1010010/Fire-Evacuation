"""Pygame view. It only DRAWS the simulation and passes key presses to it.

The core (environment, agent, astar, simulation, generator, scenarios) knows nothing about
this file. Run it with:  python run_gui.py
"""

import copy

import pygame

from .environment import WALL, EXIT
from .generator import random_environment, generate_environment, DIFFICULTIES, MIN_SIZE, MAX_SIZE
from .scenarios import SCENARIOS
from .simulation import (Simulation, ESCAPED, FAILED, cell_text, moves_text,
                         K_MOVE, K_FIRE, K_PLAN, K_REPLAN, K_GOOD, K_BAD)

# ---------------------------------------------------------------- layout
WIDTH, HEIGHT = 1240, 700
MENU_W = 680                                     # width of the button column in the menus
GRID_X, GRID_Y, GRID_SIZE = 16, 16, 600          # the map is drawn inside this square
PANEL_X, PANEL_W = 660, 564                      # information panel on the right

# ---------------------------------------------------------------- colours
BACKGROUND = (22, 24, 32)
CARD = (34, 38, 50)
CARD_LIGHT = (46, 51, 66)
TEXT = (236, 238, 245)
MUTED = (150, 156, 175)
ACCENT = (255, 170, 60)

WALL_COLOR = (60, 64, 84)
FLOOR_COLOR = (232, 234, 241)
EXIT_COLOR = (46, 180, 96)
FIRE_COLOR = (226, 62, 34)
FLAME_COLOR = (255, 205, 70)
KNOWN_RING = (255, 255, 255)
AGENT_COLOR = (36, 112, 235)
START_COLOR = (50, 200, 190)
ROUTE_COLOR = (250, 196, 24)
WALKED_COLOR = (50, 200, 190)
SENSE_COLOR = (70, 140, 255, 80)                 # translucent: the area the agent can see

STAGE_COLORS = {"PERCEIVE": (70, 140, 230), "REASON": (150, 110, 230),
                "DECIDE": (240, 150, 50), "ACT": (60, 190, 120), "WORLD": (226, 70, 50)}
KIND_COLORS = {K_MOVE: (170, 176, 195), K_FIRE: (255, 200, 90), K_PLAN: (110, 170, 255),
               K_REPLAN: (255, 150, 70), K_GOOD: (100, 225, 130), K_BAD: (255, 105, 95)}
STATUS_COLORS = {"EVACUATING": (60, 120, 220), ESCAPED: (46, 180, 96), FAILED: (220, 70, 60)}

USE_SYSTEM_FONT = False       # False = pygame's own font (original look). True = Helvetica/Arial if installed
FONT_NAMES = "helveticaneue,arial,segoeui,dejavusans,liberationsans,freesans"   # used when True
SCALE = 2                     # system font only: text is drawn 2x bigger and shrunk
REPORT_SIZE = 23                                 # text size inside the route report
DELAYS = [900, 500, 250, 120, 60]                # milliseconds between steps, slow -> fast

PRESETS = [("Fire Blocks Route", "Fire blocks the short route once. The agent replans and finds another way."),
           ("Multiple Replanning", "Fire blocks the route twice. The agent has to replan two times."),
           ("No Safe Route", "Fire blocks every route. The agent discovers there is no way out.")]


class Gui:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Intelligent Fire Evacuation Agent")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.text_cache = {}
        self.scale = SCALE if USE_SYSTEM_FONT else 1

        self.screen_name = "main"          # main, new, custom, presets, help, sim
        self.running = True

        # custom environment settings
        self.rows = 20
        self.cols = 20
        self.difficulty = 1                # index into DIFFICULTIES
        self.field = 0                     # 0 rows, 1 cols, 2 difficulty

        # simulation state
        self.pristine = None               # untouched copy, so R can replay the same environment
        self.env = None
        self.sim = None
        self.paused = False
        self.speed = 2
        self.last_step_time = 0
        self.show_report = False           # at the end the panel shows the route report
        self.report_seen = False
        self.report_scroll = 0

    # ================================================================ main loop
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_report(-event.y * 2)
            if self.screen_name == "sim":
                self.update_simulation()
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

    # ================================================================ input
    def handle_key(self, key):
        if self.screen_name == "main":
            if key == pygame.K_1:
                self.screen_name = "new"
            elif key == pygame.K_2:
                self.screen_name = "presets"
            elif key == pygame.K_3:
                self.screen_name = "help"
            elif key in (pygame.K_4, pygame.K_ESCAPE):
                self.running = False
        elif self.screen_name == "new":
            if key == pygame.K_1:
                self.start(random_environment())
            elif key == pygame.K_2:
                self.screen_name = "custom"
            elif key in (pygame.K_3, pygame.K_ESCAPE):
                self.screen_name = "main"
        elif self.screen_name == "custom":
            self.handle_custom_key(key)
        elif self.screen_name == "presets":
            numbers = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}
            if key in numbers:
                self.start(SCENARIOS[numbers[key]]())
            elif key in (pygame.K_4, pygame.K_ESCAPE):
                self.screen_name = "main"
        elif self.screen_name == "help":
            self.screen_name = "main"
        elif self.screen_name == "sim":
            self.handle_sim_key(key)

    def handle_custom_key(self, key):
        if key == pygame.K_ESCAPE:
            self.screen_name = "new"
        elif key == pygame.K_UP:
            self.field = (self.field - 1) % 3
        elif key == pygame.K_DOWN:
            self.field = (self.field + 1) % 3
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            change = 1 if key == pygame.K_RIGHT else -1
            if self.field == 0:
                self.rows = min(MAX_SIZE, max(MIN_SIZE, self.rows + change))
            elif self.field == 1:
                self.cols = min(MAX_SIZE, max(MIN_SIZE, self.cols + change))
            else:
                self.difficulty = (self.difficulty + change) % len(DIFFICULTIES)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            name = list(DIFFICULTIES)[self.difficulty]
            self.start(generate_environment(self.rows, self.cols, name))

    def handle_sim_key(self, key):
        finished = not self.sim.is_running()
        if key == pygame.K_ESCAPE:
            self.screen_name = "main"
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_n:
            self.paused = True
            self.take_step()
        elif key == pygame.K_r:
            self.start(self.pristine, keep_pristine=True)
        elif key == pygame.K_TAB and finished:
            self.show_report = not self.show_report
            self.report_scroll = 0
        elif key == pygame.K_UP:
            if finished and self.show_report:
                self.scroll_report(-3)
            else:
                self.speed = min(len(DELAYS) - 1, self.speed + 1)
        elif key == pygame.K_DOWN:
            if finished and self.show_report:
                self.scroll_report(3)
            else:
                self.speed = max(0, self.speed - 1)
        elif key == pygame.K_PAGEUP:
            self.scroll_report(-12)
        elif key == pygame.K_PAGEDOWN:
            self.scroll_report(12)

    def scroll_report(self, lines):
        """Scroll the end-of-run report (draw_report keeps the value in range)."""
        if self.sim is not None and self.screen_name == "sim" and not self.sim.is_running() and self.show_report:
            self.report_scroll = max(0, self.report_scroll + lines)

    # ================================================================ simulation
    def start(self, env, keep_pristine=False):
        """Begin a run. We keep an untouched copy so R can replay the same environment."""
        if not keep_pristine:
            self.pristine = copy.deepcopy(env)
        self.env = copy.deepcopy(self.pristine)
        self.sim = Simulation(self.env)
        self.paused = False
        self.show_report = False
        self.report_seen = False
        self.report_scroll = 0
        self.last_step_time = pygame.time.get_ticks()
        self.screen_name = "sim"

    def update_simulation(self):
        if self.paused or not self.sim.is_running():
            return
        now = pygame.time.get_ticks()
        if now - self.last_step_time >= DELAYS[self.speed]:
            self.last_step_time = now
            self.take_step()

    def take_step(self):
        if not self.sim.is_running():
            return
        self.sim.step()
        if not self.sim.is_running() and not self.report_seen:
            self.report_seen = True              # the run just ended: show the route report
            self.show_report = True
            self.report_scroll = 0

    # ================================================================ small drawing helpers
    def font(self, size, bold):
        key = (size, bold)
        if key not in self.fonts:
            if USE_SYSTEM_FONT:
                pixels = max(8, int(size * 0.74)) * self.scale
                self.fonts[key] = pygame.font.SysFont(FONT_NAMES, pixels, bold=bold)
            else:
                self.fonts[key] = pygame.font.Font(None, max(8, int(size * 0.92)))
        return self.fonts[key]

    def render(self, message, size, color, bold=None):
        """Turn text into a picture. Cached, so drawing it again is fast."""
        if bold is None:
            bold = size >= 26                       # only used by the system font
        key = (message, size, color, bold)
        picture = self.text_cache.get(key)
        if picture is None:
            picture = self.font(size, bold).render(message, True, color)
            if self.scale > 1:                      # system font: shrink the double-size text
                width = max(1, picture.get_width() // self.scale)
                height = max(1, picture.get_height() // self.scale)
                picture = pygame.transform.smoothscale(picture, (width, height))
            if len(self.text_cache) > 3000:
                self.text_cache.clear()
            self.text_cache[key] = picture
        return picture

    def text(self, message, x, y, size=22, color=TEXT, bold=None):
        picture = self.render(message, size, color, bold)
        self.screen.blit(picture, (x, y))
        return picture.get_width()

    def text_center(self, message, cx, cy, size=22, color=TEXT, bold=None):
        picture = self.render(message, size, color, bold)
        self.screen.blit(picture, (cx - picture.get_width() // 2, cy - picture.get_height() // 2))

    def text_right(self, message, right, y, size=22, color=TEXT, bold=None):
        picture = self.render(message, size, color, bold)
        self.screen.blit(picture, (right - picture.get_width(), y))

    def line_height(self, size):
        return self.font(size, False).get_linesize() // self.scale + 2

    def box(self, x, y, w, h, color, radius=10):
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=radius)

    def outline(self, x, y, w, h, color, radius=10, width=2):
        pygame.draw.rect(self.screen, color, (x, y, w, h), width, border_radius=radius)

    def wrap(self, message, size, width, bold=None):
        """Split a message into lines that fit inside `width` pixels."""
        if bold is None:
            bold = size >= 26
        font = self.font(size, bold)
        lines, line = [], ""
        for word in message.split(" "):
            attempt = word if not line else line + " " + word
            if font.size(attempt)[0] // self.scale <= width:
                line = attempt
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    # ================================================================ screens
    def draw(self):
        self.screen.fill(BACKGROUND)
        if self.screen_name == "main":
            self.draw_main()
        elif self.screen_name == "new":
            self.draw_buttons("New Simulation", "Choose how the building is made.",
                              [("Random Environment", "The program chooses the size, walls, exit and fire."),
                               ("Custom Environment", "You choose rows, columns and difficulty."),
                               ("Back", "")], "Press 1, 2 or 3.")
        elif self.screen_name == "custom":
            self.draw_custom()
        elif self.screen_name == "presets":
            self.draw_buttons("Preset Scenarios", "Fixed demonstrations of the agent's behaviour.",
                              PRESETS + [("Back", "")], "Press 1, 2, 3 or 4.")
        elif self.screen_name == "help":
            self.draw_help()
        else:
            self.draw_simulation()

    def draw_title(self, title, subtitle):
        self.text_center(title, WIDTH // 2, 92, 60)
        self.text_center(subtitle, WIDTH // 2, 144, 26, MUTED)
        self.box(WIDTH // 2 - 40, 172, 80, 5, ACCENT, 3)

    def draw_buttons(self, title, subtitle, items, footer):
        self.draw_title(title, subtitle)
        x, w, h, gap = (WIDTH - MENU_W) // 2, MENU_W, 78, 16
        top = 210
        for i, (label, description) in enumerate(items):
            y = top + i * (h + gap)
            self.box(x, y, w, h, CARD, 14)
            self.outline(x, y, w, h, CARD_LIGHT, 14)
            self.box(x + 16, y + 15, 48, 48, ACCENT, 10)
            self.text_center(str(i + 1), x + 40, y + 39, 38, BACKGROUND)
            if description:
                self.text(label, x + 86, y + 13, 34)
                self.text(description, x + 86, y + 47, 22, MUTED)
            else:
                self.text(label, x + 86, y + 22, 34)
        self.text_center(footer, WIDTH // 2, HEIGHT - 44, 24, MUTED)

    def draw_main(self):
        self.draw_buttons("INTELLIGENT FIRE EVACUATION AGENT",
                          "A classical-AI agent: rules + A* search + replanning",
                          [("New Simulation", "Random or custom building"),
                           ("Preset Scenarios", "Replanning, multiple replanning, no safe route"),
                           ("Help", "How to read the screen"),
                           ("Exit", "")], "Press 1, 2, 3 or 4")

    def draw_custom(self):
        self.draw_title("Custom Environment", "You choose the size and difficulty. The program builds the rest.")
        names = list(DIFFICULTIES)
        settings = DIFFICULTIES[names[self.difficulty]]
        rows = [("Rows", str(self.rows), f"{MIN_SIZE} to {MAX_SIZE}"),
                ("Columns", str(self.cols), f"{MIN_SIZE} to {MAX_SIZE}"),
                ("Difficulty", names[self.difficulty],
                 f"{int(settings['wall_density'] * 100)}% walls, {settings['fire_count']} fire events, "
                 f"first fire at tick {settings['first_tick']}")]
        x, w, h = (WIDTH - MENU_W) // 2, MENU_W, 88
        for i, (label, value, note) in enumerate(rows):
            y = 210 + i * (h + 16)
            selected = i == self.field
            self.box(x, y, w, h, CARD_LIGHT if selected else CARD, 14)
            self.outline(x, y, w, h, ACCENT if selected else CARD_LIGHT, 14)
            self.text(label, x + 24, y + 14, 34, ACCENT if selected else TEXT)
            self.text(note, x + 24, y + 54, 22, MUTED)
            self.text_right(("<   " + value + "   >") if selected else value, x + w - 24, y + 22, 38)
        self.text_center("UP / DOWN choose a field        LEFT / RIGHT change it", WIDTH // 2, 520 + 74, 24, MUTED)
        self.text_center("ENTER start        ESC back", WIDTH // 2, HEIGHT - 44, 24, MUTED)

    def draw_help(self):
        self.draw_title("Help", "How to read the simulation screen")
        x, w = (WIDTH - 900) // 2, 900
        self.box(x, 200, w, 430, CARD, 14)
        self.outline(x, 200, w, 430, CARD_LIGHT, 14)
        lines = [
            ("The agent (blue circle) must reach the exit (green) while fire (red) appears.", TEXT),
            ("It only knows about fire inside its sensing area (light blue). Known fire has a white ring.", TEXT),
            ("Yellow line: the route A* found.  When fire appears on it, the agent replans.", TEXT),
            ("Teal line: the cells the agent has really walked, from the start (S).", TEXT),
            ("", TEXT),
            ("Each step the agent does:", ACCENT),
            ("PERCEIVE   look for fire within 4 cells and remember it", TEXT),
            ("REASON     is my route still safe?", TEXT),
            ("DECIDE     keep going, or run A* again (replan)", TEXT),
            ("ACT        move one cell", TEXT),
            ("", TEXT),
            ("When the run ends, the panel shows the full route the agent took.", MUTED),
            ("SPACE pause    N one step    UP/DOWN speed    R restart    TAB steps/report    ESC menu", MUTED),
        ]
        for i, (line, color) in enumerate(lines):
            self.text(line, x + 28, 218 + i * 30, 24, color)
        self.text_center("Press any key to go back", WIDTH // 2, HEIGHT - 44, 24, MUTED)

    # ================================================================ simulation screen
    def draw_simulation(self):
        self.draw_grid()
        self.draw_legend()
        self.draw_panel()

    def center(self, cell, size, left, top):
        return (left + cell[1] * size + size // 2, top + cell[0] * size + size // 2)

    def draw_grid(self):
        env, sim = self.env, self.sim
        agent = sim.agent
        finished = not sim.is_running()
        size = max(4, min(GRID_SIZE // env.cols, GRID_SIZE // env.rows))
        width, height = size * env.cols, size * env.rows
        left = GRID_X + (GRID_SIZE - width) // 2
        top = GRID_Y + (GRID_SIZE - height) // 2
        self.box(left - 8, top - 8, width + 16, height + 16, CARD, 14)

        # the cells
        for r in range(env.rows):
            for c in range(env.cols):
                rect = (left + c * size, top + r * size, size - 1, size - 1)
                if env.grid[r][c] == WALL:
                    color = WALL_COLOR
                elif (r, c) in env.fire:
                    color = FIRE_COLOR
                elif (r, c) == env.exit_pos:
                    color = EXIT_COLOR
                else:
                    color = FLOOR_COLOR
                pygame.draw.rect(self.screen, color, rect)

        # the area the agent can see (Manhattan sensing radius)
        if not finished:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            radius = agent.sensing_radius
            pr, pc = agent.pos
            for r in range(max(0, pr - radius), min(env.rows, pr + radius + 1)):
                span = radius - abs(r - pr)
                for c in range(max(0, pc - span), min(env.cols, pc + span + 1)):
                    if env.grid[r][c] != WALL:
                        pygame.draw.rect(overlay, SENSE_COLOR, (c * size, r * size, size - 1, size - 1))
            self.screen.blit(overlay, (left, top))

        # exit label and flames
        label_size = max(12, int(size * 0.8))
        if size >= 16:
            self.text_center("E", *self.center(env.exit_pos, size, left, top), label_size, TEXT)
        for cell in env.fire:
            pygame.draw.circle(self.screen, FLAME_COLOR, self.center(cell, size, left, top), max(2, size // 4))
        for cell in agent.known_fire:
            pygame.draw.circle(self.screen, KNOWN_RING, self.center(cell, size, left, top),
                               max(3, size // 2 - 1), 2)

        # the route the agent has really walked (teal)
        walked = [self.center(cell, size, left, top) for cell in agent.walked]
        line_width = max(3, size // 3) if finished else max(2, size // 5)
        if len(walked) >= 2:
            pygame.draw.lines(self.screen, WALKED_COLOR, False, walked, line_width)
        for point in walked:
            pygame.draw.circle(self.screen, WALKED_COLOR, point, max(1, line_width // 2))

        # the route A* wants to follow next (yellow)
        if agent.path:
            points = [self.center(agent.pos, size, left, top)]
            points += [self.center(cell, size, left, top) for cell in agent.path]
            pygame.draw.lines(self.screen, ROUTE_COLOR, False, points, max(2, size // 5))

        # start marker and the agent
        start = self.center(agent.walked[0], size, left, top)
        pygame.draw.circle(self.screen, START_COLOR, start, max(4, size // 3))
        if size >= 16:
            self.text_center("S", start[0], start[1], label_size, BACKGROUND)
        here = self.center(agent.pos, size, left, top)
        pygame.draw.circle(self.screen, AGENT_COLOR, here, max(3, size // 2 - 2))
        pygame.draw.circle(self.screen, TEXT, here, max(3, size // 2 - 2), 2)

    def draw_legend(self):
        items = [("rect", WALL_COLOR, "Wall"), ("rect", FLOOR_COLOR, "Floor"), ("rect", EXIT_COLOR, "Exit"),
                 ("rect", FIRE_COLOR, "Fire"), ("ring", KNOWN_RING, "Fire it knows"),
                 ("dot", AGENT_COLOR, "Agent"), ("dot", START_COLOR, "Start"),
                 ("line", ROUTE_COLOR, "Planned route"), ("line", WALKED_COLOR, "Walked route"),
                 ("rect", (150, 190, 250), "What it sees")]
        for i, (shape, color, label) in enumerate(items):
            x = GRID_X + (i % 5) * 126
            y = GRID_Y + GRID_SIZE + 26 + (i // 5) * 26
            if shape == "rect":
                pygame.draw.rect(self.screen, color, (x, y, 16, 16))
            elif shape == "ring":
                pygame.draw.rect(self.screen, FIRE_COLOR, (x, y, 16, 16))
                pygame.draw.circle(self.screen, color, (x + 8, y + 8), 7, 2)
            elif shape == "dot":
                pygame.draw.circle(self.screen, color, (x + 8, y + 8), 8)
            else:
                pygame.draw.line(self.screen, color, (x, y + 8), (x + 16, y + 8), 4)
            self.text(label, x + 22, y + 1, 20, MUTED)

    # ================================================================ right-hand panel
    def draw_panel(self):
        sim, agent = self.sim, self.sim.agent
        finished = not sim.is_running()

        # header: environment name and status badge
        self.text(self.env.name, PANEL_X, 22, 34)
        badge = STATUS_COLORS[sim.status]
        self.box(PANEL_X + PANEL_W - 150, 16, 150, 36, badge, 18)
        self.text_center(sim.status, PANEL_X + PANEL_W - 75, 34, 26)

        # numbers
        tiles = [("Steps", sim.steps), ("Replans", agent.replans), ("Fire known", len(agent.known_fire)),
                 ("Route left", len(agent.path)), ("Clock", self.env.tick)]
        tile_w = (PANEL_W - 4 * 8) // 5
        for i, (label, value) in enumerate(tiles):
            x = PANEL_X + i * (tile_w + 8)
            self.box(x, 62, tile_w, 54, CARD)
            self.text_center(label, x + tile_w // 2, 74, 20, MUTED)
            self.text_center(str(value), x + tile_w // 2, 98, 38)

        if finished and self.show_report:
            self.draw_report()
        else:
            self.draw_step_card()
            self.draw_history_card()

        # key hints
        if finished:
            hints = ["TAB  report / steps     UP, DOWN, PAGE UP/DOWN or mouse wheel  scroll",
                     "R  run again     ESC  menu"]
        else:
            state = "PAUSED" if self.paused else "RUNNING"
            hints = [f"{state}   speed {self.speed + 1}/{len(DELAYS)}      SPACE pause   N one step   UP/DOWN speed",
                     "R restart     ESC menu"]
        self.text(hints[0], PANEL_X, 652, 20, MUTED)
        self.text(hints[1], PANEL_X, 674, 20, MUTED)

    def draw_step_card(self):
        """What the agent did in the latest step, one row per stage, in plain words."""
        y, h = 126, 244
        self.box(PANEL_X, y, PANEL_W, h, CARD)
        last = self.sim.last_step
        if last is None:
            self.text("Starting...", PANEL_X + 14, y + 12, 28)
            return
        self.text(f"Step {last['number']}  -  what the agent just did", PANEL_X + 14, y + 10, 28)
        rows = [("PERCEIVE", last["perceive"]), ("REASON", last["reason"]), ("DECIDE", last["decide"]),
                ("ACT", last["act"] or "No move this step."),
                ("WORLD", last["environment"] or "No new fire started.")]
        for i, (stage, message) in enumerate(rows):
            ry = y + 44 + i * 39
            self.box(PANEL_X + 12, ry, 96, 26, STAGE_COLORS[stage], 6)
            self.text_center(stage, PANEL_X + 60, ry + 13, 20, bold=True)
            for j, line in enumerate(self.wrap(message, 23, PANEL_W - 140)[:2]):
                self.text(line, PANEL_X + 120, ry + 1 + j * 19, 23)

    def draw_history_card(self):
        """The last few steps, newest at the bottom, coloured by what happened."""
        y, h = 378, 264
        self.box(PANEL_X, y, PANEL_W, h, CARD)
        self.text("Step history", PANEL_X + 14, y + 10, 28)
        history = self.sim.history
        if not history:
            return
        size = 22
        line_height = self.line_height(size)
        capacity = (h - 48) // line_height
        shown = []                                    # newest first, until the card is full
        used = 0
        for kind, message in reversed(history):
            lines = self.wrap(message, size, PANEL_W - 52)
            if used + len(lines) > capacity:
                break
            shown.append((kind, lines))
            used += len(lines)
        shown.reverse()
        ly = y + 42
        for index, (kind, lines) in enumerate(shown):
            color = KIND_COLORS[kind]
            if kind == K_MOVE and index == len(shown) - 1:
                color = TEXT
            pygame.draw.circle(self.screen, color, (PANEL_X + 20, ly + 7), 4)
            for line in lines:
                self.text(line, PANEL_X + 34, ly, size, color)
                ly += line_height

    # ================================================================ end of run: route report
    def report_lines(self):
        """Lines of the report as (style, text). The panel scrolls through them."""
        sim, agent = self.sim, self.sim.agent
        width = PANEL_W - 30
        lines = [("head", f"Route the agent took ({moves_text(sim.steps)})")]
        cells = " > ".join(cell_text(cell) for cell in agent.walked)
        for part in self.wrap(cells, REPORT_SIZE, width):
            lines.append(("cells", part))
        metrics = sim.get_metrics()
        lines += [("gap", ""), ("head", "Numbers"),
                  ("text", f"First route found by A*: {moves_text(metrics['initial_path_length'] or 0)}"),
                  ("text", f"Replans: {metrics['replans']}     Fire the agent saw: {len(agent.known_fire)}"),
                  ("text", f"A* cells explored: {metrics['nodes_explored_total']}"),
                  ("text", f"A* time: {metrics['astar_time_ms']} ms"),
                  ("gap", ""), ("head", f"Every step ({len(sim.history)})")]
        for kind, message in sim.history:           # all steps, not only the important ones
            for k, part in enumerate(self.wrap(message, REPORT_SIZE, width)):
                lines.append((kind, part if k == 0 else "     " + part))
        return lines

    def draw_report(self):
        sim, agent = self.sim, self.sim.agent
        escaped = sim.status == ESCAPED
        y, h = 126, 516
        self.box(PANEL_X, y, PANEL_W, h, CARD)
        self.text("AGENT ESCAPED" if escaped else "AGENT FAILED", PANEL_X + 14, y + 10, 50,
                  STATUS_COLORS[sim.status])
        if escaped:
            summary = (f"The agent walked from {cell_text(agent.walked[0])} to the exit {cell_text(agent.pos)} "
                       f"in {sim.steps} steps with {agent.replans} replan(s). The route it took is the teal line.")
        else:
            summary = (f"The agent started at {cell_text(agent.walked[0])} and stopped at {cell_text(agent.pos)} "
                       f"after {sim.steps} steps. Reason: {sim.failure_reason}. "
                       f"The route it took is the teal line.")
        ty = y + 64
        for line in self.wrap(summary, 22, PANEL_W - 28)[:3]:
            self.text(line, PANEL_X + 14, ty, 22)
            ty += 19

        # scrolling part
        top = y + 120
        line_height = self.line_height(REPORT_SIZE) + 3
        visible = (y + h - 10 - top) // line_height
        lines = self.report_lines()
        self.report_scroll = max(0, min(self.report_scroll, max(0, len(lines) - visible)))
        for i, (style, message) in enumerate(lines[self.report_scroll:self.report_scroll + visible]):
            ly = top + i * line_height
            if style == "head":
                self.text(message, PANEL_X + 14, ly, 26, ACCENT)
            elif style == "cells":
                self.text(message, PANEL_X + 14, ly, REPORT_SIZE, WALKED_COLOR)
            elif style == "text":
                self.text(message, PANEL_X + 14, ly, REPORT_SIZE, TEXT)
            elif style != "gap":
                self.text(message, PANEL_X + 14, ly, REPORT_SIZE, KIND_COLORS[style])
        if len(lines) > visible:
            self.text("more below (DOWN)" if self.report_scroll + visible < len(lines) else "end of report",
                      PANEL_X + PANEL_W - 170, y + 14, 18, MUTED)


def main():
    Gui().run()


if __name__ == "__main__":
    main()
