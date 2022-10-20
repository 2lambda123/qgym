"""This module contains a class used for rendering the scheduling environment."""


from typing import Any, Mapping

import numpy as np
import pygame
from qgym.utils import GateEncoder

# Define some colors used during rendering
BACKGROUND_COLOR = (150, 150, 150)  # Gray
TEXT_COLOR = (225, 225, 225)  # White
GATE_COLOR = (0, 0, 0)  # Black


class SchedulingVisualiser:
    """
    Visualiser class for the scheduling environment
    """

    def __init__(
        self,
        *,
        gate_encoder: GateEncoder,
        gate_cycle_length: Mapping[int, int],
        n_qubits: int,
    ) -> None:
        """
        Initialize the visualiser.

        :param gate_encoder: GateEncoder object of the scheduling environment.
        :param gate_cycle_length: Mapping of cycle lengths for the gates of the
            scheduling environment.
        :param n_qubits: number of qubits of the scheduling environment.
        """

        # Rendering data
        self.screen = None
        self.is_open = False
        self.screen_width = 1500
        self.screen_height = 800

        self._gate_encoder = gate_encoder
        self._gate_cycle_length = gate_cycle_length
        self._n_qubits = n_qubits
        self._gate_height = self.screen_height / self._n_qubits

        # define attributes that are set later
        self.font = None
        self._cycle_width = None
        self._encoded_circuit = None

    def render(self, state: Mapping[str, Any], mode: str) -> Any:
        """
        Render the current state using pygame.

        :param state: Current state of the schedule.
        :param mode: Mode to start pygame for ("human" and "rgb_array" are supported).
        :raise ValueError: When an invalid mode is provided.
        :return: The rendered state.
        """

        if self.screen is None:
            self.start(mode)

        self._encoded_circuit = state["encoded_circuit"]

        self.screen.fill(BACKGROUND_COLOR)

        pygame.time.delay(10)

        self._cycle_width = self.screen_width / (state["cycle"] + 10)

        for gate_idx, scheduled_cycle in enumerate(state["schedule"]):
            if scheduled_cycle != -1:
                self._draw_scheduled_gate(gate_idx, scheduled_cycle)

        if mode == "human":
            pygame.event.pump()
            pygame.display.flip()
            return self.is_open
        elif mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
            )
        else:
            raise ValueError(
                f"You provided an invalid mode '{mode}',"
                f" the only supported modes are 'human' and 'rgb_array'."
            )

    def _draw_scheduled_gate(self, gate_idx: int, scheduled_cycle: int) -> None:
        """
        Draw a gate on the screen.

        :param gate_idx: index of the gate to draw.
        :param scheduled_cycle: cycle the gate is scheduled.
        """

        gate = self._encoded_circuit[gate_idx]

        self._draw_gate_block(gate.name, gate.q1, scheduled_cycle)
        if gate.q1 != gate.q2:
            self._draw_gate_block(gate.name, gate.q2, scheduled_cycle)

    def _draw_gate_block(
        self, gate_int_name: int, qubit: int, scheduled_cycle: int
    ) -> None:
        """
        Draw a single block of a gate (gates can consist of 1 or 2 blocks).

        :param gate_int_name: integer encoding of the gate name.
        :param qubit: qubit in which the gate acts.
        :param scheduled_cycle: cycle in which the gate is scheduled.
        """

        gate_width = self._cycle_width * self._gate_cycle_length[gate_int_name]

        gate_box = pygame.Rect(0, 0, gate_width, self._gate_height)
        box_x = self.screen_width - scheduled_cycle * self._cycle_width
        box_y = self.screen_height - qubit * self._gate_height
        gate_box.bottomright = (box_x, box_y)

        pygame.draw.rect(self.screen, GATE_COLOR, gate_box)

        gate_name = self._gate_encoder.decode_gates(gate_int_name)
        text = self.font.render(gate_name.upper(), True, TEXT_COLOR)
        text_position = text.get_rect(center=gate_box.center)
        self.screen.blit(text, text_position)

    def start(self, mode: str) -> None:
        """
        Start pygame in the given mode.

        :param mode: Mode to start pygame for ("human" and "rgb_array" are supported).
        :raise ValueError: When an invalid mode is provided.
        """

        pygame.display.init()
        if mode == "human":
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
        elif mode == "rgb_array":
            self.screen = pygame.Surface((self.screen_width, self.screen_height))
        else:
            raise ValueError(
                f"You provided an invalid mode '{mode}',"
                f" the only supported modes are 'human' and 'rgb_array'."
            )

        pygame.display.set_caption("Scheduling Environment")

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 12)

        self.is_open = True

    def close(self) -> None:
        """
        Close the screen used for rendering.
        """

        if self.screen is not None:
            pygame.display.quit()
            pygame.font.quit()
            self.is_open = False
            self.screen = None
