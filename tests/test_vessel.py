"""Tests for fleet-homunculus."""

import time
import pytest
from fleet_homunculus import Vessel, PainSignal, ReflexArc, FleetBody, PainLevel


def test_vessel_creation():
    """Test creating a vessel."""
    vessel = Vessel(vessel_id="v1", name="Test Vessel")
    assert vessel.vessel_id == "v1"
    assert vessel.name == "Test Vessel"
    assert vessel.current_health == 100.0
    assert vessel.max_health == 100.0
    assert vessel.status == "active"


def test_vessel_damage():
    """Test vessel damage."""
    vessel = Vessel(vessel_id="v1", name="Test Vessel")

    # Minor damage - no pain signal
    signal = vessel.take_damage(5)
    assert signal is None
    assert vessel.current_health == 95.0

    # Moderate damage - generates signal
    signal = vessel.take_damage(25)  # 70 health left
    assert signal is not None
    assert signal.level == PainLevel.MILD  # Changed: 25 damage gives MILD
    assert vessel.current_health == 70.0


def test_vessel_critical_damage():
    """Test critical damage."""
    vessel = Vessel(vessel_id="v1", name="Test Vessel")
    signal = vessel.take_damage(100)

    assert signal is not None
    assert signal.level == PainLevel.CRITICAL
    assert vessel.status == "destroyed"
    assert vessel.current_health == 0
    assert not vessel.is_alive()


def test_vessel_heal():
    """Test vessel healing."""
    vessel = Vessel(vessel_id="v1", name="Test Vessel")
    vessel.take_damage(50)

    vessel.heal(20)
    assert vessel.current_health == 70.0

    vessel.heal(100)  # Overheal
    assert vessel.current_health == 100.0


def test_pain_signal():
    """Test pain signal."""
    signal = PainSignal(
        vessel_id="v1",
        message="Test pain",
        level=PainLevel.SEVERE
    )
    assert signal.vessel_id == "v1"
    assert signal.is_severe_or_worse()
    assert not signal.is_critical()


def test_reflex_arc():
    """Test reflex arc."""
    triggered = []

    def action(signal):
        triggered.append(signal)

    reflex = ReflexArc(
        name="test_reflex",
        trigger_level=PainLevel.SEVERE,
        action=action,
        cooldown=1.0
    )

    # Mild signal shouldn't trigger
    mild_signal = PainSignal("v1", "mild", PainLevel.MILD)
    assert reflex.trigger(mild_signal) is False
    assert len(triggered) == 0

    # Severe signal should trigger
    severe_signal = PainSignal("v1", "severe", PainLevel.SEVERE)
    assert reflex.trigger(severe_signal) is True
    assert len(triggered) == 1

    # Cooldown prevents immediate re-trigger
    assert reflex.trigger(severe_signal) is False
    assert len(triggered) == 1


def test_fleet_body():
    """Test fleet body management."""
    fleet = FleetBody(fleet_id="fleet1")
    vessel1 = Vessel(vessel_id="v1", name="Vessel 1")
    vessel2 = Vessel(vessel_id="v2", name="Vessel 2")

    fleet.add_vessel(vessel1)
    fleet.add_vessel(vessel2)

    assert len(fleet.get_all_vessels()) == 2
    assert fleet.get_vessel("v1") is vessel1
    assert fleet.get_vessel("unknown") is None


def test_fleet_damage_and_pain():
    """Test fleet damage processing."""
    fleet = FleetBody(fleet_id="fleet1")
    vessel = Vessel(vessel_id="v1", name="Vessel 1")
    fleet.add_vessel(vessel)

    signal = fleet.damage_vessel("v1", 30)
    assert signal is not None
    assert signal.vessel_id == "v1"

    history = fleet.get_pain_history()
    assert len(history) == 1
    assert history[0] == signal


def test_fleet_reflex():
    """Test fleet reflexes."""
    triggered = []

    def action(signal):
        triggered.append(signal)

    reflex = ReflexArc(
        name="heal_reflex",
        trigger_level=PainLevel.SEVERE,
        action=action
    )

    fleet = FleetBody(fleet_id="fleet1")
    fleet.add_reflex(reflex)

    vessel = Vessel(vessel_id="v1", name="Vessel 1")
    fleet.add_vessel(vessel)

    # Damage to severe level should trigger reflex
    fleet.damage_vessel("v1", 80)
    assert len(triggered) == 1


def test_fleet_health():
    """Test fleet health calculation."""
    fleet = FleetBody(fleet_id="fleet1")
    fleet.add_vessel(Vessel(vessel_id="v1", name="V1"))
    fleet.add_vessel(Vessel(vessel_id="v2", name="V2"))

    assert fleet.get_fleet_health() == 1.0

    fleet.damage_vessel("v1", 50)
    # 50% + 100% / 2 = 75%
    assert fleet.get_fleet_health() == 0.75


def test_critical_vessels():
    """Test getting critical vessels."""
    fleet = FleetBody(fleet_id="fleet1")
    fleet.add_vessel(Vessel(vessel_id="v1", name="V1"))
    fleet.add_vessel(Vessel(vessel_id="v2", name="V2"))

    fleet.damage_vessel("v1", 80)  # 20% health
    critical = fleet.get_critical_vessels()
    assert len(critical) == 1
    assert critical[0].vessel_id == "v1"


def test_count_by_status():
    """Test counting vessels by status."""
    fleet = FleetBody(fleet_id="fleet1")
    fleet.add_vessel(Vessel(vessel_id="v1", name="V1"))
    fleet.add_vessel(Vessel(vessel_id="v2", name="V2"))
    fleet.add_vessel(Vessel(vessel_id="v3", name="V3"))

    fleet.damage_vessel("v1", 40)  # damaged (60 health)
    fleet.damage_vessel("v2", 100)  # destroyed

    counts = fleet.count_by_status()
    assert counts.get("active", 0) == 1  # v3
    assert counts.get("damaged", 0) == 1  # v1
    assert counts.get("destroyed", 0) == 1  # v2


def test_reflex_cooldown():
    """Test reflex cooldown behavior."""
    count = [0]

    def action(signal):
        count[0] += 1

    reflex = ReflexArc(
        name="rapid_reflex",
        trigger_level=PainLevel.MILD,
        action=action,
        cooldown=0.1  # 100ms cooldown
    )

    signal = PainSignal("v1", "test", PainLevel.SEVERE)

    # First trigger
    assert reflex.trigger(signal) is True
    assert count[0] == 1

    # Immediate re-trigger blocked by cooldown
    assert reflex.trigger(signal) is False
    assert count[0] == 1

    # Wait for cooldown
    time.sleep(0.15)
    assert reflex.trigger(signal) is True
    assert count[0] == 2


def test_pain_history_filter():
    """Test pain history filtering."""
    fleet = FleetBody(fleet_id="fleet1")
    fleet.add_vessel(Vessel(vessel_id="v1", name="V1"))
    fleet.add_vessel(Vessel(vessel_id="v2", name="V2"))

    fleet.damage_vessel("v1", 30)
    fleet.damage_vessel("v2", 40)
    fleet.damage_vessel("v1", 20)

    v1_history = fleet.get_pain_history(vessel_id="v1")
    assert len(v1_history) == 2
    assert all(s.vessel_id == "v1" for s in v1_history)
