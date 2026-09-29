import os
import tempfile
import matplotlib
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
from manimlib import *

os.makedirs("/tmp/mpl", exist_ok=True)
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"
matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["svg.fonttype"] = "path"

# -------------------------------------------------------------------------
# Typography & 3Blue1Brown Mathematical Styling (Computer Modern)
# -------------------------------------------------------------------------
FONT_SERIF = "cmr10"

def CMMath(tex_str, color=WHITE, height=1.0):
    """
    Renders an authentic Donald Knuth Computer Modern LaTeX math formula
    via Matplotlib mathtext SVG with zero system LaTeX installation requirements.
    """
    fig = plt.figure(figsize=(10, 2), dpi=300)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.patch.set_alpha(0)
    ax.text(0.5, 0.5, f"${tex_str}$", fontsize=36, color="white", ha="center", va="center")

    tmp_path = tempfile.mktemp(suffix=".svg")
    plt.savefig(tmp_path, format="svg", bbox_inches="tight", pad_inches=0.01, transparent=True)
    plt.close(fig)

    mob = SVGMobject(tmp_path)
    mob.set_color(color)
    if height is not None:
        mob.set_height(height)
    try:
        os.remove(tmp_path)
    except Exception:
        pass
    return mob

# 3Blue1Brown Signature Color Palette
BG_COLOR = "#000000"          # Pure mathematical blackboard black
PANEL_BG = "#0B0E14"          # Deep understated charcoal
PANEL_BORDER = "#2B313A"      # Thin subtle border

COLOR_EP = "#FFFF00"          # Potential Energy (3b1b Yellow)
COLOR_EK = "#58C4DD"          # Kinetic Energy (3b1b Cyan / Blue)
COLOR_ETOT = "#83C167"        # Total Energy (3b1b Green)
COLOR_FORCE = "#FC6255"       # External Force / Impulse (3b1b Coral Red)
COLOR_TEAL = "#5CD0B3"        # Electrostatic (3b1b Teal)
COLOR_CHASSIS = "#1C2128"     # Dark chassis body
COLOR_OUTLINE = "#D0D7DE"     # Crisp vector stroke
COLOR_GRID = "#1A1E24"        # Very subtle grid lines

CORNER_RAD = 0.04             # Crisp subtle 3b1b corner radius


# -------------------------------------------------------------------------
# Procedural Mechanical Mobjects
# -------------------------------------------------------------------------

def make_spring(start_pt, end_pt, num_coils=9, width=0.38):
    """Generates a clean, crisp 2D zigzag spring path between start_pt and end_pt."""
    start_pt = np.array(start_pt, dtype=float)
    end_pt = np.array(end_pt, dtype=float)
    diff = end_pt - start_pt
    length = np.linalg.norm(diff)
    if length < 0.1:
        line = VMobject()
        line.set_points_as_corners([start_pt, end_pt])
        return line

    u = diff / length
    v = np.array([-u[1], u[0], 0.0])

    lead = min(0.3, length * 0.15)
    body_len = max(0.01, length - 2 * lead)

    pts = [start_pt, start_pt + u * lead]
    num_peaks = 2 * num_coils
    for i in range(num_peaks):
        frac = (i + 0.5) / num_peaks
        side = 1.0 if (i % 2 == 0) else -1.0
        peak = start_pt + u * (lead + frac * body_len) + v * (side * width / 2.0)
        pts.append(peak)
    pts.append(end_pt - u * lead)
    pts.append(end_pt)

    spring = VMobject()
    spring.set_points_as_corners(pts)
    return spring


class DamperGraphic(VGroup):
    """Mechanical dashpot with cylinder housing and sliding piston."""
    def __init__(self, start_pt, end_pt, height=0.3, **kwargs):
        super().__init__(**kwargs)
        start_pt = np.array(start_pt, dtype=float)
        end_pt = np.array(end_pt, dtype=float)

        diff = end_pt - start_pt
        length = np.linalg.norm(diff)
        u = diff / (length + 1e-6)
        v = np.array([-u[1], u[0], 0.0])

        cyl_len = 1.4
        cyl_start = start_pt
        cyl_end = start_pt + u * cyl_len

        # Cylinder housing
        top_wall = Line(cyl_start + v * (height / 2), cyl_end + v * (height / 2), stroke_width=1.8, color=GREY_B)
        bot_wall = Line(cyl_start - v * (height / 2), cyl_end - v * (height / 2), stroke_width=1.8, color=GREY_B)
        back_wall = Line(cyl_start - v * (height / 2), cyl_start + v * (height / 2), stroke_width=2.2, color=GREY_B)
        fluid = Polygon(
            cyl_start - v * (height / 2),
            cyl_end - v * (height / 2),
            cyl_end + v * (height / 2),
            cyl_start + v * (height / 2),
            stroke_width=0, fill_color="#102A38", fill_opacity=0.3
        )

        # Piston rod and head
        rod_head_pos = start_pt + u * min(cyl_len * 0.85, max(0.2, length * 0.5))
        rod = Line(rod_head_pos, end_pt, stroke_width=2.0, color=GREY_A)
        piston_head = Line(
            rod_head_pos - v * (height * 0.42),
            rod_head_pos + v * (height * 0.42),
            stroke_width=3.2, color=WHITE
        )

        self.add(fluid, top_wall, bot_wall, back_wall, rod, piston_head)


class ChassisGraphic(VGroup):
    """Sleek mechanical chassis with sharp/subtle corners and thin spoked wheels."""
    def __init__(self, width=2.4, height=1.25, **kwargs):
        super().__init__(**kwargs)
        self.chassis_width = width
        self.chassis_height = height
        self.wheel_radius = 0.24

        # Main body with subtle 3b1b corner radius
        self.body = RoundedRectangle(
            width=width, height=height,
            corner_radius=CORNER_RAD,
            stroke_width=1.8, stroke_color=COLOR_OUTLINE,
            fill_color=COLOR_CHASSIS, fill_opacity=0.95
        )

        # Wheels with rotating spokes
        self.wheel1 = Circle(radius=self.wheel_radius, stroke_color=GREY_A, stroke_width=1.8, fill_color="#0D1117", fill_opacity=1.0)
        self.spoke1_a = Line(UP * self.wheel_radius, DOWN * self.wheel_radius, stroke_width=1.4, color=GREY_B)
        self.spoke1_b = Line(LEFT * self.wheel_radius, RIGHT * self.wheel_radius, stroke_width=1.4, color=GREY_B)
        self.wheel1_group = VGroup(self.wheel1, self.spoke1_a, self.spoke1_b)
        self.wheel1_group.shift(DOWN * (height / 2 + self.wheel_radius) + LEFT * (width * 0.32))

        self.wheel2 = Circle(radius=self.wheel_radius, stroke_color=GREY_A, stroke_width=1.8, fill_color="#0D1117", fill_opacity=1.0)
        self.spoke2_a = Line(UP * self.wheel_radius, DOWN * self.wheel_radius, stroke_width=1.4, color=GREY_B)
        self.spoke2_b = Line(LEFT * self.wheel_radius, RIGHT * self.wheel_radius, stroke_width=1.4, color=GREY_B)
        self.wheel2_group = VGroup(self.wheel2, self.spoke2_a, self.spoke2_b)
        self.wheel2_group.shift(DOWN * (height / 2 + self.wheel_radius) + RIGHT * (width * 0.32))

        # Typography inside chassis
        self.title_label = Text("Chassis", font=FONT_SERIF, font_size=18, color=WHITE)
        self.title_label.shift(UP * 0.28)
        self.sub_label = CMMath(r"\mathrm{Mass}\ m", color=COLOR_EK, height=1.2)
        self.sub_label.shift(DOWN * 0.05)
        self.energy_label = Text("Stores Kinetic Energy", font=FONT_SERIF, font_size=12, color=GREY_B)
        self.energy_label.shift(DOWN * 0.34)

        self.add(self.body, self.wheel1_group, self.wheel2_group, self.title_label, self.sub_label, self.energy_label)

    def rotate_wheels(self, angle):
        self.spoke1_a.rotate(angle, about_point=self.wheel1.get_center())
        self.spoke1_b.rotate(angle, about_point=self.wheel1.get_center())
        self.spoke2_a.rotate(angle, about_point=self.wheel2.get_center())
        self.spoke2_b.rotate(angle, about_point=self.wheel2.get_center())


# -------------------------------------------------------------------------
# Dynamic Energy HUD
# -------------------------------------------------------------------------

class EnergyHUD(VGroup):
    """Dynamic HUD displaying real-time potential, kinetic, and total stored energy."""
    def __init__(self, width=4.6, height=2.2, **kwargs):
        super().__init__(**kwargs)
        self.hud_width = width
        self.hud_height = height
        self.max_bar_w = 2.2

        # Panel frame with crisp subtle corner
        self.bg = RoundedRectangle(
            width=width, height=height, corner_radius=CORNER_RAD,
            fill_color=PANEL_BG, fill_opacity=0.85,
            stroke_color=PANEL_BORDER, stroke_width=1.2
        )

        title = Text("Stored Energy & Dynamic Memory", font=FONT_SERIF, font_size=13, color=WHITE)
        title.shift(UP * 0.8)

        # Potential Energy Row
        lbl_ep = Text("Potential (Spring):", font=FONT_SERIF, font_size=13, color=COLOR_EP)
        lbl_ep.shift(UP * 0.38 + LEFT * 1.1)
        self.bg_bar_ep = Rectangle(width=self.max_bar_w, height=0.16, fill_color="#181C24", fill_opacity=1.0, stroke_width=0)
        self.bg_bar_ep.shift(UP * 0.38 + RIGHT * 0.9)
        self.bar_ep = Rectangle(width=0.01, height=0.16, fill_color=COLOR_EP, fill_opacity=1.0, stroke_width=0)
        self.bar_ep.align_to(self.bg_bar_ep, LEFT)

        # Kinetic Energy Row
        lbl_ek = Text("Kinetic (Chassis):", font=FONT_SERIF, font_size=13, color=COLOR_EK)
        lbl_ek.shift(UP * 0.04 + LEFT * 1.1)
        self.bg_bar_ek = Rectangle(width=self.max_bar_w, height=0.16, fill_color="#181C24", fill_opacity=1.0, stroke_width=0)
        self.bg_bar_ek.shift(UP * 0.04 + RIGHT * 0.9)
        self.bar_ek = Rectangle(width=0.01, height=0.16, fill_color=COLOR_EK, fill_opacity=1.0, stroke_width=0)
        self.bar_ek.align_to(self.bg_bar_ek, LEFT)

        # Total Stored Energy Row
        lbl_etot = Text("Total Energy:", font=FONT_SERIF, font_size=13, color=COLOR_ETOT)
        lbl_etot.shift(DOWN * 0.3 + LEFT * 1.1)
        self.bg_bar_etot = Rectangle(width=self.max_bar_w, height=0.16, fill_color="#181C24", fill_opacity=1.0, stroke_width=0)
        self.bg_bar_etot.shift(DOWN * 0.3 + RIGHT * 0.9)
        self.bar_etot = Rectangle(width=0.01, height=0.16, fill_color=COLOR_ETOT, fill_opacity=1.0, stroke_width=0)
        self.bar_etot.align_to(self.bg_bar_etot, LEFT)

        # Readout labels
        self.num_ep = DecimalNumber(0.0, num_decimal_places=1, font_size=12, color=GREY_B)
        ep_group = VGroup(
            Text("Ep: ", font=FONT_SERIF, font_size=12, color=GREY_B),
            self.num_ep,
            Text(" J", font=FONT_SERIF, font_size=12, color=GREY_B)
        ).arrange(RIGHT, buff=0.2)

        self.num_ek = DecimalNumber(0.0, num_decimal_places=1, font_size=12, color=GREY_B)
        ek_group = VGroup(
            Text("Ek: ", font=FONT_SERIF, font_size=12, color=GREY_B),
            self.num_ek,
            Text(" J", font=FONT_SERIF, font_size=12, color=GREY_B)
        ).arrange(RIGHT, buff=0.2)

        self.num_etot = DecimalNumber(0.0, num_decimal_places=1, font_size=12, color=GREY_B)
        etot_group = VGroup(
            Text("Total: ", font=FONT_SERIF, font_size=12, color=GREY_B),
            self.num_etot,
            Text(" J", font=FONT_SERIF, font_size=12, color=GREY_B)
        ).arrange(RIGHT, buff=0.2)

        bottom_row = VGroup(ep_group, ek_group, etot_group).arrange(RIGHT, buff=0.4)
        bottom_row.move_to(self.bg.get_center() + DOWN * 0.72)

        self.add(
            self.bg, title,
            lbl_ep, self.bg_bar_ep, self.bar_ep,
            lbl_ek, self.bg_bar_ek, self.bar_ek,
            lbl_etot, self.bg_bar_etot, self.bar_etot,
            bottom_row
        )

    def update_values(self, ep, ek, etot, max_scale=12.0):
        w_ep = max(0.01, min(self.max_bar_w, (ep / max_scale) * self.max_bar_w))
        w_ek = max(0.01, min(self.max_bar_w, (ek / max_scale) * self.max_bar_w))
        w_etot = max(0.01, min(self.max_bar_w, (etot / max_scale) * self.max_bar_w))

        left_x = self.bg_bar_ep.get_left()[0]

        self.bar_ep.set_width(w_ep, stretch=True)
        self.bar_ep.move_to([left_x + w_ep / 2, self.bg_bar_ep.get_center()[1], 0])

        self.bar_ek.set_width(w_ek, stretch=True)
        self.bar_ek.move_to([left_x + w_ek / 2, self.bg_bar_ek.get_center()[1], 0])

        self.bar_etot.set_width(w_etot, stretch=True)
        self.bar_etot.move_to([left_x + w_etot / 2, self.bg_bar_etot.get_center()[1], 0])

        self.num_ep.set_value(ep)
        self.num_ek.set_value(ek)
        self.num_etot.set_value(etot)


# -------------------------------------------------------------------------
# Oscilloscope / State Memory History Waveform
# -------------------------------------------------------------------------

class OscilloscopeGraphic(VGroup):
    """Displays a rolling history trace showing how memory persists through time."""
    def __init__(self, width=7.8, height=1.65, **kwargs):
        super().__init__(**kwargs)
        self.chart_w = width
        self.chart_h = height

        # Screen frame with crisp corner radius
        self.frame = RoundedRectangle(
            width=width, height=height, corner_radius=CORNER_RAD,
            fill_color="#06080C", fill_opacity=0.95,
            stroke_color=PANEL_BORDER, stroke_width=1.2
        )

        # Subtle grid lines
        grid = VGroup()
        for x in np.linspace(-width / 2 + 0.4, width / 2 - 0.4, 7):
            grid.add(Line([x, -height / 2 + 0.15, 0], [x, height / 2 - 0.15, 0], stroke_width=0.7, color=COLOR_GRID))
        for y in np.linspace(-height / 2 + 0.2, height / 2 - 0.2, 5):
            grid.add(Line([-width / 2 + 0.2, y, 0], [width / 2 - 0.2, y, 0], stroke_width=0.7, color=COLOR_GRID))

        # Center zero axis line
        center_line = Line([-width / 2 + 0.1, 0, 0], [width / 2 - 0.1, 0, 0], stroke_width=1.0, color="#1D3B53")

        # Label placed cleanly above frame
        self.label = Text("System Memory Trace: State x(t)", font=FONT_SERIF, font_size=13, color=COLOR_TEAL)
        self.label.next_to(self.frame, UP, buff=0.12).align_to(self.frame, LEFT).shift(RIGHT * 0.15)

        # Dynamic trace line
        self.wave_path = VMobject(stroke_color=COLOR_EP, stroke_width=2.0)

        self.add(self.frame, grid, center_line, self.wave_path, self.label)

    def update_trace(self, history_deque, time_window=4.0, max_amplitude=2.5):
        if len(history_deque) < 2:
            return

        t_now = history_deque[-1][0]
        center = self.frame.get_center()
        w = self.chart_w - 0.4
        h = self.chart_h - 0.4

        pts = []
        for t, x in history_deque:
            age = t_now - t
            if age > time_window:
                continue
            x_screen = center[0] + (w / 2) - (age / time_window) * w
            y_screen = center[1] + (x / max_amplitude) * (h / 2)
            y_screen = max(center[1] - h / 2, min(center[1] + h / 2, y_screen))
            pts.append([x_screen, y_screen, 0])

        if len(pts) >= 2:
            self.wave_path.set_points_as_corners(pts)
        else:
            self.wave_path.set_points_as_corners([[center[0] - w / 2, center[1], 0], [center[0] + w / 2, center[1], 0]])


# -------------------------------------------------------------------------
# Live Interactive Scene: Physics Sandbox
# -------------------------------------------------------------------------

class InteractiveDynamicMemory(Scene):
    """
    Live interactive physics simulation demonstrating memory in dynamic systems:
    - Mass-spring-damper mechanical system
    - Real-time Energy HUD (Ep, Ek, Total)
    - Scrolling Oscilloscope memory waveform trace
    - Mouse drag & keyboard impulse / mode toggling
    """
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BG_COLOR, 1.0))

        # Simulation parameters
        self.mass = 1.0
        self.k = 18.0
        self.c = 0.9
        self.x = 0.0
        self.v = 0.0
        self.f_ext = 0.0
        self.sim_time = 0.0
        self.is_dragging = False
        self.drag_mouse_x = 0.0
        self.last_mouse_x = 0.0
        self.mode = "dynamic"  # "dynamic" or "memoryless"
        self.history = deque(maxlen=260)
        self.history.append((0.0, 0.0))

        # Scene layout coordinates
        self.wall_x = -5.8
        self.eq_x = -1.0
        self.mech_y = 0.5
        self.ground_y = self.mech_y - 0.95

        # Wall & Ground with thin, delicate 3b1b strokes
        wall_line = Line([self.wall_x, self.mech_y - 1.2, 0], [self.wall_x, self.mech_y + 1.2, 0], stroke_width=2.5, color=GREY_B)
        wall_hatch = VGroup(*[
            Line([self.wall_x, y, 0], [self.wall_x - 0.3, y - 0.3, 0], stroke_width=1.4, color=GREY_C)
            for y in np.linspace(self.mech_y - 1.2, self.mech_y + 1.2, 10)
        ])
        self.wall = VGroup(wall_line, wall_hatch)

        ground_line = Line([self.wall_x, self.ground_y, 0], [5.5, self.ground_y, 0], stroke_width=2.2, color=GREY_B)
        ground_hatch = VGroup(*[
            Line([x, self.ground_y, 0], [x - 0.25, self.ground_y - 0.25, 0], stroke_width=1.2, color=GREY_C)
            for x in np.linspace(self.wall_x, 5.5, 28)
        ])
        self.ground = VGroup(ground_line, ground_hatch)

        # Chassis
        self.chassis = ChassisGraphic(width=2.5, height=1.2)
        self.chassis.move_to([self.eq_x, self.mech_y, 0])

        # Equilibrium marker positioned neatly below track
        eq_marker = DashedLine([self.eq_x, self.ground_y - 0.45, 0], [self.eq_x, self.mech_y + 0.6, 0], stroke_width=1.2, color=GREY_C)
        eq_label = Text("x = 0  (Equilibrium)", font=FONT_SERIF, font_size=14, color=GREY_C).next_to(eq_marker, DOWN, buff=0.1)
        self.eq_group = VGroup(eq_marker, eq_label)

        # Dynamic Spring Mobject
        self.spring = VMobject(stroke_width=2.4, color=COLOR_EP)
        self.update_spring()

        # Dynamic Damper Mobject
        self.damper_group = VGroup()
        self.update_damper()

        # External Force Arrow
        self.force_arrow = Arrow(
            [self.eq_x + 1.5, self.mech_y, 0],
            [self.eq_x + 2.25, self.mech_y, 0],
            color=COLOR_FORCE, stroke_width=3.5, buff=0.0
        )
        self.force_arrow.set_opacity(0.0)

        # HUD (Top-Right)
        self.hud = EnergyHUD().to_corner(UR, buff=0.35)

        # Oscilloscope (Bottom-Left)
        self.oscilloscope = OscilloscopeGraphic(width=7.8, height=1.65).shift(LEFT * 2.6 + DOWN * 2.85)

        # Controls Banner (Bottom-Right)
        self.controls_banner = RoundedRectangle(
            width=4.8, height=1.65, corner_radius=CORNER_RAD,
            fill_color=PANEL_BG, fill_opacity=0.85,
            stroke_color=PANEL_BORDER, stroke_width=1.2
        ).shift(RIGHT * 4.3 + DOWN * 2.85)

        c_title = Text("Live Interaction Controls", font=FONT_SERIF, font_size=12, color=COLOR_TEAL).shift(UP * 0.52)
        c_m1 = Text("• Mouse: Drag mass to store Ep, then release", font=FONT_SERIF, font_size=11, color=WHITE).shift(UP * 0.23)
        c_m2 = Text("• [SPACE]: Strike chassis with Impulse F(t)", font=FONT_SERIF, font_size=11, color=COLOR_FORCE).shift(DOWN * 0.03)
        c_m3 = Text("• [M]: Toggle Memoryless vs Dynamic system", font=FONT_SERIF, font_size=11, color=COLOR_EP).shift(DOWN * 0.28)
        c_m4 = Text("• [R]: Reset system state to rest", font=FONT_SERIF, font_size=11, color=GREY_B).shift(DOWN * 0.53)

        c_text_group = VGroup(c_title, c_m1, c_m2, c_m3, c_m4).move_to(self.controls_banner.get_center())
        self.hud_controls = VGroup(self.controls_banner, c_text_group)

        # Mode Indicator (Top-Center)
        self.mode_label = Text("Mode: Dynamic System with Memory (Stores Energy)", font=FONT_SERIF, font_size=15, color=COLOR_ETOT)
        self.mode_label.to_edge(UP, buff=0.35)

        # Add everything to scene
        self.play(
            FadeIn(self.wall),
            FadeIn(self.ground),
            FadeIn(self.eq_group),
            FadeIn(self.chassis),
            FadeIn(self.spring),
            FadeIn(self.damper_group),
            FadeIn(self.hud),
            FadeIn(self.oscilloscope),
            FadeIn(self.hud_controls),
            FadeIn(self.mode_label),
            run_time=1.0
        )

        # Attach real-time simulation updater
        self.sim_mobject = Mobject()
        self.sim_mobject.add_updater(self.step_simulation_updater)
        self.add(self.sim_mobject)

        if self.window is not None:
            self.interact()
        else:
            self.wait(10.0)

    # ---------------------------------------------------------------------
    # Physics Engine & Updaters
    # ---------------------------------------------------------------------

    def step_simulation_updater(self, mob, dt):
        """Called every frame by ManimGL to advance physics."""
        sub_steps = 4
        sub_dt = dt / sub_steps

        for _ in range(sub_steps):
            if self.mode == "memoryless":
                if self.is_dragging:
                    self.x = self.drag_mouse_x
                    self.v = 0.0
                else:
                    self.v = self.f_ext / max(self.c, 0.2)
                    self.x += self.v * sub_dt
            else:
                if self.is_dragging:
                    target_x = self.drag_mouse_x
                    new_v = (target_x - self.x) / max(sub_dt, 1e-4)
                    self.v = 0.6 * self.v + 0.4 * new_v
                    self.x = target_x
                else:
                    a = (self.f_ext - self.c * self.v - self.k * self.x) / self.mass
                    self.v += a * sub_dt
                    self.x += self.v * sub_dt

        self.x = max(-3.2, min(3.8, self.x))
        self.sim_time += dt
        self.history.append((self.sim_time, self.x))

        curr_chassis_x = self.eq_x + self.x
        prev_center_x = self.chassis.body.get_center()[0]
        dx = curr_chassis_x - prev_center_x

        self.chassis.shift(RIGHT * dx)
        d_angle = -dx / self.chassis.wheel_radius
        self.chassis.rotate_wheels(d_angle)

        self.update_spring()
        self.update_damper()

        if self.mode == "dynamic":
            ep = 0.5 * self.k * (self.x ** 2)
            ek = 0.5 * self.mass * (self.v ** 2)
        else:
            ep = 0.0
            ek = 0.0
        etot = ep + ek

        self.hud.update_values(ep, ek, etot)
        self.oscilloscope.update_trace(self.history)

    def update_spring(self):
        """Redraws the spring between wall and chassis."""
        wall_anchor = [self.wall_x, self.mech_y + 0.35, 0]
        chassis_anchor = [self.chassis.body.get_left()[0], self.mech_y + 0.35, 0]
        new_spring = make_spring(wall_anchor, chassis_anchor, num_coils=9, width=0.38)

        if self.mode == "memoryless":
            new_spring.set_color(GREY_D)
        else:
            stretch = abs(self.x)
            color_factor = min(1.0, stretch / 2.0)
            glow_color = interpolate_color(COLOR_EP, "#FFA000", color_factor)
            new_spring.set_color(glow_color)

        self.spring.become(new_spring)

    def update_damper(self):
        """Redraws the damper between wall and chassis."""
        self.damper_group.submobjects.clear()
        wall_anchor = [self.wall_x, self.mech_y - 0.35, 0]
        chassis_anchor = [self.chassis.body.get_left()[0], self.mech_y - 0.35, 0]
        damper = DamperGraphic(wall_anchor, chassis_anchor, height=0.3)
        self.damper_group.add(*damper.submobjects)

    # ---------------------------------------------------------------------
    # Interactive Actions & Hotkeys
    # ---------------------------------------------------------------------

    def apply_impulse(self, velocity_kick=3.0):
        """Applies an instantaneous force impulse delta(t) kicking the chassis."""
        if self.mode == "dynamic":
            self.v += velocity_kick
        else:
            self.x += velocity_kick * 0.08
            self.v = 0.0

        self.force_arrow.set_opacity(1.0)
        self.add(self.force_arrow)
        self.force_arrow.next_to(self.chassis.body, RIGHT, buff=0.1)
        self.force_arrow.life = 0.35

        def fade_arrow(mob, dt):
            mob.life -= dt
            if mob.life <= 0:
                mob.remove_updater(fade_arrow)
                self.remove(mob)
            else:
                mob.set_opacity(float(max(0.0, min(1.0, mob.life / 0.35))))

        self.force_arrow.add_updater(fade_arrow)

    def toggle_mode(self, target_mode=None):
        """Switches between Dynamic System (with memory) and Memoryless System."""
        if target_mode is None:
            self.mode = "memoryless" if self.mode == "dynamic" else "dynamic"
        else:
            self.mode = target_mode

        if self.mode == "dynamic":
            new_label = Text("Mode: Dynamic System with Memory (Stores Energy)", font=FONT_SERIF, font_size=15, color=COLOR_ETOT)
        else:
            new_label = Text("Mode: Memoryless System (Zero Stored Energy)", font=FONT_SERIF, font_size=15, color=COLOR_FORCE)
            self.v = 0.0

        new_label.to_edge(UP, buff=0.35)
        self.mode_label.become(new_label)

    def reset_state(self):
        """Resets the system to equilibrium state."""
        self.x = 0.0
        self.v = 0.0
        self.f_ext = 0.0
        self.is_dragging = False

    # ---------------------------------------------------------------------
    # Window Event Handlers (Mouse & Keyboard Interaction)
    # ---------------------------------------------------------------------

    def on_mouse_press(self, point, button, mods):
        chassis_pt = self.chassis.body.get_center()
        dist = np.linalg.norm(point[:2] - chassis_pt[:2])
        if dist < 1.6:
            self.is_dragging = True
            self.drag_mouse_x = point[0] - self.eq_x
        super().on_mouse_press(point, button, mods)

    def on_mouse_drag(self, point, d_point, buttons, modifiers):
        if self.is_dragging:
            self.drag_mouse_x = point[0] - self.eq_x
        else:
            super().on_mouse_drag(point, d_point, buttons, modifiers)

    def on_mouse_release(self, point, button, mods):
        if self.is_dragging:
            self.is_dragging = False
        super().on_mouse_release(point, button, mods)

    def on_key_press(self, symbol, modifiers):
        try:
            char = chr(symbol).lower()
        except (OverflowError, ValueError):
            char = None

        if char == " ":
            self.apply_impulse(velocity_kick=3.0)
        elif char == "s":
            self.f_ext = 3.5 if self.f_ext == 0.0 else 0.0
        elif char == "m":
            self.toggle_mode()
        elif char == "r":
            self.reset_state()
        else:
            super().on_key_press(symbol, modifiers)


# -------------------------------------------------------------------------
# Backwards Compatibility Alias
# -------------------------------------------------------------------------

class MemoryInDynamicSystems(InteractiveDynamicMemory):
    """Alias ensuring both scene names boot directly into the interactive sandbox."""
    pass
