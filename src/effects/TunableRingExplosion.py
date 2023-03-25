from math import pi, sin, cos
from random import uniform

from asciimatics.particles import ParticleEmitter, Particle
from asciimatics.screen import Screen


class TunableRingExplosion(ParticleEmitter):
    def __init__(
        self, screen, x, y, life_time, width=8, color=1, particles_set="***:. "
    ):
        super(TunableRingExplosion, self).__init__(
            screen, x, y, 30, self._next_particle, 1, life_time
        )
        self.particles_set = particles_set
        self.width = width
        self._colour = color
        self._acceleration = 1.0 - (1.0 / life_time)

    def _next_particle(self):
        direction = uniform(0, 2 * pi)
        return Particle(
            self.particles_set,
            self._x,
            self._y,
            sin(direction) * 3 * self.width / self._life_time,
            cos(direction) * 1.5 * self.width / self._life_time,
            [(self._colour, Screen.A_BOLD, 0), (self._colour, 0, 0), (0, 0, 0)],
            self._life_time,
            self._explode,
        )

    def _explode(self, particle):
        particle.dy *= self._acceleration
        particle.dx *= self._acceleration
        particle.x += particle.dx
        particle.y += particle.dy

        return int(particle.x), int(particle.y)
