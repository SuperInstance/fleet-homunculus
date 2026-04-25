# fleet-homunculus

Fleet body image — vessel health monitoring and reflex arcs.

Every fleet agent needs a body image — a model of its own capabilities, health, and status. Fleet Homunculus provides that model.

## What It Does

- **Vessel Health** — CPU, memory, disk, network status monitoring
- **Reflex Arcs** — Automatic responses to health events (restart, scale, alert)
- **Body Schema** — Self-model of agent capabilities and limitations
- **Proprioception** — Awareness of position in the fleet topology

## Installation

```bash
pip install fleet-homunculus
```

## Part of the Cocapn Fleet

Used by all fleet agents for self-monitoring and health reporting to the Keeper.

## License

MIT
