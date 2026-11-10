"""
2D INERTIAL PHYSICS & RAYCASTING ENGINE SANDBOX (Public Edition)
- Pure Python 2D kinematics with velocity, acceleration limits, and viscous damping.
- Analytical 4-axis cardinal raycasting (N, S, E, W) and Circle-AABB collision response.
- Hardware-independent math engine decoupled from the responsive Tkinter viewport.
- Built-in unit test suite (run with: python public_engine_sandbox.py --test).
"""

import math
import sys
import tkinter as tk
import unittest
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ObstacleBox:
    """Immutable Axis-Aligned Bounding Box (AABB) representing a static obstacle."""
    x: float
    y: float
    w: float
    h: float


@dataclass
class KinematicAgent:
    """Dynamic 2D entity with position, velocity, and physical radius."""
    agent_id: str
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 12.0


class WaypointPatrolController:
    """
    Default public navigation controller.
    Guides the agent sequentially through a list of 2D coordinates.
    Can be replaced at runtime with custom navigation policies.
    """

    def __init__(self, waypoints: List[Tuple[float, float]], arrival_threshold: float = 22.0):
        if not waypoints:
            raise ValueError("Waypoint list cannot be empty.")
        self.waypoints = waypoints
        self.arrival_threshold = arrival_threshold
        self.current_index = 0

    @property
    def current_target(self) -> Tuple[float, float]:
        return self.waypoints[self.current_index]

    def compute_target(self, agent: KinematicAgent) -> Tuple[float, float]:
        tx, ty = self.current_target
        if math.hypot(tx - agent.x, ty - agent.y) <= self.arrival_threshold:
            self.current_index = (self.current_index + 1) % len(self.waypoints)
            tx, ty = self.current_target
        return tx, ty


class InertialPhysicsEngine:
    """
    Pure mathematical 2D physics and raycasting engine.
    Completely decoupled from GUI frameworks.
    """

    def __init__(
        self,
        obstacles: Optional[List[ObstacleBox]] = None,
        max_speed: float = 8.0,
        max_accel: float = 3.0,
        damping: float = 0.96,
        restitution: float = 0.4,
    ):
        self.obstacles: List[ObstacleBox] = obstacles if obstacles is not None else self._default_arena()
        self.max_speed = max_speed
        self.max_accel = max_accel
        self.damping = damping
        self.restitution = restitution

    @staticmethod
    def _default_arena() -> List[ObstacleBox]:
        return [
            # Outer perimeter walls
            ObstacleBox(50.0, 40.0, 820.0, 15.0),
            ObstacleBox(50.0, 40.0, 15.0, 840.0),
            ObstacleBox(855.0, 40.0, 15.0, 840.0),
            ObstacleBox(50.0, 880.0, 820.0, 15.0),
            # Internal structural pillars
            ObstacleBox(220.0, 190.0, 120.0, 90.0),
            ObstacleBox(560.0, 180.0, 110.0, 130.0),
            ObstacleBox(410.0, 420.0, 100.0, 100.0),
            ObstacleBox(200.0, 650.0, 130.0, 90.0),
            ObstacleBox(580.0, 640.0, 120.0, 110.0),
        ]

    def check_collision(self, x: float, y: float, radius: float = 12.0) -> bool:
        """Checks Circle-AABB intersection using expanded bounding bounds."""
        for box in self.obstacles:
            if (box.x - radius < x < box.x + box.w + radius) and (
                box.y - radius < y < box.y + box.h + radius
            ):
                return True
        return False

    def cast_cardinal_rays(
        self, x: float, y: float, max_range: float = 160.0, beam_margin: float = 1.5
    ) -> Dict[str, float]:
        """
        Analytical O(N) raycasting along the 4 cardinal axes (N, S, E, W).
        Computes exact distance to the closest obstacle boundary within max_range.
        """
        readings = {"N": max_range, "S": max_range, "E": max_range, "W": max_range}

        for box in self.obstacles:
            # Check horizontal overlap for North/South vertical rays
            if (box.x - beam_margin) <= x <= (box.x + box.w + beam_margin):
                # North ray (dy = -1)
                bottom_edge = box.y + box.h + beam_margin
                if bottom_edge <= y:
                    dist_n = y - bottom_edge
                    if dist_n < readings["N"]:
                        readings["N"] = max(0.0, dist_n)
                # South ray (dy = +1)
                top_edge = box.y - beam_margin
                if top_edge >= y:
                    dist_s = top_edge - y
                    if dist_s < readings["S"]:
                        readings["S"] = max(0.0, dist_s)

            # Check vertical overlap for East/West horizontal rays
            if (box.y - beam_margin) <= y <= (box.y + box.h + beam_margin):
                # West ray (dx = -1)
                right_edge = box.x + box.w + beam_margin
                if right_edge <= x:
                    dist_w = x - right_edge
                    if dist_w < readings["W"]:
                        readings["W"] = max(0.0, dist_w)
                # East ray (dx = +1)
                left_edge = box.x - beam_margin
                if left_edge >= x:
                    dist_e = left_edge - x
                    if dist_e < readings["E"]:
                        readings["E"] = max(0.0, dist_e)

        return readings

    def step_kinematics(
        self,
        agent: KinematicAgent,
        target_x: float,
        target_y: float,
        ray_data: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        Advances the kinematic state by one discrete step.
        Returns True if a boundary collision occurred during the step.
        """
        dx = target_x - agent.x
        dy = target_y - agent.y
        dist = math.hypot(dx, dy)

        # Basic proximity speed modulation if ray sensor data is provided
        throttle = 1.0
        if ray_data:
            if (ray_data.get("N", 160.0) < 40.0 and dy < 0) or (
                ray_data.get("S", 160.0) < 40.0 and dy > 0
            ):
                throttle = 0.45
            if (ray_data.get("W", 160.0) < 40.0 and dx < 0) or (
                ray_data.get("E", 160.0) < 40.0 and dx > 0
            ):
                throttle = 0.45

        effective_speed = self.max_speed * throttle

        if dist > 1e-4:
            desired_vx = (dx / dist) * effective_speed
            desired_vy = (dy / dist) * effective_speed
        else:
            desired_vx, desired_vy = 0.0, 0.0

        steer_x = desired_vx - agent.vx
        steer_y = desired_vy - agent.vy
        steer_mag = math.hypot(steer_x, steer_y)

        if steer_mag > self.max_accel and steer_mag > 0.0:
            steer_x = (steer_x / steer_mag) * self.max_accel
            steer_y = (steer_y / steer_mag) * self.max_accel

        agent.vx = (agent.vx + steer_x) * self.damping
        agent.vy = (agent.vy + steer_y) * self.damping

        speed_mag = math.hypot(agent.vx, agent.vy)
        if speed_mag > self.max_speed:
            agent.vx = (agent.vx / speed_mag) * self.max_speed
            agent.vy = (agent.vy / speed_mag) * self.max_speed

        next_x = agent.x + agent.vx
        next_y = agent.y + agent.vy
        collided = False

        if not self.check_collision(next_x, agent.y, agent.radius):
            agent.x = next_x
        else:
            agent.vx = -agent.vx * self.restitution
            collided = True

        if not self.check_collision(agent.x, next_y, agent.radius):
            agent.y = next_y
        else:
            agent.vy = -agent.vy * self.restitution
            collided = True

        return collided


class SandboxViewportGUI:
    """Responsive Tkinter visualization layer for the 2D Physics Sandbox."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("2D Inertial Physics & Raycasting Sandbox")
        self.root.configure(bg="#060814")

        self.engine = InertialPhysicsEngine()
        self.agent = KinematicAgent("AGENT_01", x=130.0, y=120.0, radius=12.0)

        default_waypoints = [
            (760.0, 120.0),
            (760.0, 480.0),
            (460.0, 320.0),
            (140.0, 520.0),
            (460.0, 800.0),
            (760.0, 800.0),
            (130.0, 120.0),
        ]
        self.controller = WaypointPatrolController(default_waypoints)
        self.latest_rays: Dict[str, float] = {"N": 160.0, "S": 160.0, "E": 160.0, "W": 160.0}
        self.collision_counter = 0

        # Responsive Viewport Scaling
        self.logical_w, self.logical_h = 920.0, 940.0
        self.root.update_idletasks()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()

        scale_w = (scr_w * 0.94) / self.logical_w
        scale_h = (scr_h * 0.82) / self.logical_h
        self.scale = min(scale_w, scale_h, 1.0)

        self.width = int(scr_w * 0.96) if scr_w < 1000 else int(self.logical_w * self.scale)
        self.height = int(self.logical_h * self.scale)

        map_w = self.logical_w * self.scale
        self.offset_x = max(10.0, (self.width - map_w) / 2.0)
        self.offset_y = 8.0

        self.lbl_hud = tk.Label(
            root,
            text="",
            bg="#0b132b",
            fg="#00f5d4",
            font=("Courier", 8, "bold"),
            pady=6,
            padx=6,
            justify=tk.CENTER,
        )
        self.lbl_hud.pack(fill=tk.X, side=tk.TOP)

        self.canvas = tk.Canvas(
            root, width=self.width, height=self.height, bg="#070b19", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._init_static_scene()
        self.root.after(30, self._loop)

    def _sx(self, val: float) -> float:
        return self.offset_x + (val * self.scale)

    def _sy(self, val: float) -> float:
        return self.offset_y + (val * self.scale)

    def _sr(self, val: float) -> float:
        return max(1.0, val * self.scale)

    def _init_static_scene(self):
        """Renders static geometry once at startup to minimize frame overhead."""
        self.canvas.delete("static_layer")
        for box in self.engine.obstacles:
            self.canvas.create_rectangle(
                self._sx(box.x),
                self._sy(box.y),
                self._sx(box.x + box.w),
                self._sy(box.y + box.h),
                fill="#1b263b",
                outline="#415a77",
                width=2,
                tags="static_layer",
            )

        self.gfx_agent = self.canvas.create_oval(0, 0, 0, 0, fill="#ffd166", outline="#00f5d4", width=3)
        self.gfx_label = self.canvas.create_text(
            0, 0, text=self.agent.agent_id, fill="#ffd166", font=("Courier", 7, "bold")
        )

    def _update(self):
        try:
            self.latest_rays = self.engine.cast_cardinal_rays(
                self.agent.x, self.agent.y, max_range=160.0
            )
            tx, ty = self.controller.compute_target(self.agent)
            hit = self.engine.step_kinematics(self.agent, tx, ty, ray_data=self.latest_rays)
            if hit:
                self.collision_counter += 1
        except Exception as exc:
            print(f"[ENGINE UPDATE ERROR]: {exc}", file=sys.stderr)

    def _render(self):
        try:
            self.canvas.delete("dynamic_layer")

            # Draw active target beacon
            tx, ty = self.controller.current_target
            bx, by, br = self._sx(tx), self._sy(ty), self._sr(8.0)
            self.canvas.create_oval(
                bx - br, by - br, bx + br, by + br, outline="#ff4d6d", width=2, dash=(3, 2), tags="dynamic_layer"
            )
            self.canvas.create_text(
                bx, by - self._sr(14.0), text="BEACON", fill="#ff4d6d", font=("Courier", 6, "bold"), tags="dynamic_layer"
            )

            # Draw 4 cardinal laser beams
            ax, ay = self._sx(self.agent.x), self._sy(self.agent.y)
            r_data = self.latest_rays
            self.canvas.create_line(
                ax, ay, ax, self._sy(self.agent.y - r_data["N"]), fill="#00ffcc", width=1, dash=(2, 2), tags="dynamic_layer"
            )
            self.canvas.create_line(
                ax, ay, ax, self._sy(self.agent.y + r_data["S"]), fill="#00ffcc", width=1, dash=(2, 2), tags="dynamic_layer"
            )
            self.canvas.create_line(
                ax, ay, self._sx(self.agent.x - r_data["W"]), ay, fill="#00ffcc", width=1, dash=(2, 2), tags="dynamic_layer"
            )
            self.canvas.create_line(
                ax, ay, self._sx(self.agent.x + r_data["E"]), ay, fill="#00ffcc", width=1, dash=(2, 2), tags="dynamic_layer"
            )

            # Update agent transform
            rad = self._sr(self.agent.radius)
            self.canvas.coords(self.gfx_agent, ax - rad, ay - rad, ax + rad, ay + rad)
            self.canvas.coords(self.gfx_label, ax, ay - self._sr(18.0))
            self.canvas.tag_raise(self.gfx_agent)
            self.canvas.tag_raise(self.gfx_label)

            speed = math.hypot(self.agent.vx, self.agent.vy)
            hud = (
                f"[PUBLIC ENGINE SANDBOX] POS: ({int(self.agent.x)}, {int(self.agent.y)}) | "
                f"SPEED: {speed:.1f} px/f | BEACON: #{self.controller.current_index + 1} | BOUNCES: {self.collision_counter}\n"
                f"4-AXIS RAYCAST -> N:{int(r_data['N'])}  E:{int(r_data['E'])}  S:{int(r_data['S'])}  W:{int(r_data['W'])}"
            )
            self.lbl_hud.config(text=hud)
        except Exception as exc:
            print(f"[RENDER ERROR]: {exc}", file=sys.stderr)

    def _loop(self):
        try:
            if not self.root.winfo_exists():
                return
            self._update()
            self._render()
            self.root.after(28, self._loop)
        except tk.TclError:
            pass


# =====================================================================
# UNIT TEST SUITE (Run with: python public_engine_sandbox.py --test)
# =====================================================================
class TestPublicEngineSandbox(unittest.TestCase):
    def setUp(self):
        self.custom_boxes = [
            ObstacleBox(0.0, 0.0, 200.0, 10.0),    # North wall (y: 0..10)
            ObstacleBox(0.0, 190.0, 200.0, 10.0),  # South wall (y: 190..200)
            ObstacleBox(0.0, 0.0, 10.0, 200.0),    # West wall  (x: 0..10)
            ObstacleBox(190.0, 0.0, 10.0, 200.0),  # East wall  (x: 190..200)
        ]
        self.engine = InertialPhysicsEngine(obstacles=self.custom_boxes)

    def test_analytical_raycasting_accuracy(self):
        # Agent placed at center (100, 100); walls are at 10 and 190 with 1.5 beam margin
        rays = self.engine.cast_cardinal_rays(100.0, 100.0, max_range=150.0, beam_margin=1.5)
        self.assertAlmostEqual(rays["N"], 88.5, places=2)
        self.assertAlmostEqual(rays["S"], 88.5, places=2)
        self.assertAlmostEqual(rays["E"], 88.5, places=2)
        self.assertAlmostEqual(rays["W"], 88.5, places=2)

    def test_collision_detection_and_bounce(self):
        # Place agent right next to the West wall moving left
        agent = KinematicAgent("TEST", x=23.0, y=100.0, vx=-5.0, vy=0.0, radius=12.0)
        collided = self.engine.step_kinematics(agent, target_x=0.0, target_y=100.0)
        self.assertTrue(collided)
        # Velocity X must invert due to elastic restitution
        self.assertGreater(agent.vx, 0.0)

    def test_waypoint_controller_cycling(self):
        wps = [(100.0, 100.0), (150.0, 150.0)]
        ctrl = WaypointPatrolController(wps, arrival_threshold=15.0)
        agent = KinematicAgent("TEST", x=95.0, y=95.0)
        target = ctrl.compute_target(agent)
        # Since agent is within 15px of (100, 100), controller should advance to index 1
        self.assertEqual(target, (150.0, 150.0))


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        unittest.main()
    else:
        root = tk.Tk()
        app = SandboxViewportGUI(root)
        root.mainloop()
