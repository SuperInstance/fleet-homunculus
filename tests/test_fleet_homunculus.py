"""Tests for fleet-homunculus — body image + reflex arcs."""
from fleet_homunculus import Vessel, FleetBody, PainSignal, ReflexArc, PainLevel

def test_vessel_health():
    v = Vessel(vessel_id="oracle1", name="Oracle1", max_health=100, current_health=85)
    assert v.status == "active"
    print("PASS: vessel health")

def test_fleet_body():
    fb = FleetBody(fleet_id="cocapn")
    fb.add_vessel(Vessel(vessel_id="oracle1", name="Oracle1"))
    fb.add_vessel(Vessel(vessel_id="fm", name="Forgemaster", current_health=60))
    vessels = fb.get_all_vessels()
    assert len(vessels) == 2
    print(f"PASS: fleet body → {len(vessels)} vessels")

def test_pain_signal():
    p = PainSignal(vessel_id="fm", message="disk at 95%", level=PainLevel.SEVERE)
    assert p.level == PainLevel.SEVERE
    print("PASS: pain signal")

def test_reflex_arc():
    fired = []
    arc = ReflexArc(
        name="disk_cleaner",
        trigger_level=PainLevel.SEVERE,
        action=lambda p: fired.append(p.message),
        cooldown=5.0
    )
    signal = PainSignal(vessel_id="fm", message="disk full", level=PainLevel.SEVERE)
    assert arc.should_trigger(signal)
    arc.trigger(signal)
    assert len(fired) == 1
    print("PASS: reflex arc fires")

def test_fleet_health():
    fb = FleetBody(fleet_id="cocapn")
    fb.add_vessel(Vessel(vessel_id="oracle1", name="Oracle1", current_health=100))
    fb.add_vessel(Vessel(vessel_id="fm", name="FM", current_health=50))
    health = fb.get_fleet_health()
    assert 0 <= health <= 100
    print(f"PASS: fleet health = {health:.0f}%")

if __name__ == "__main__":
    test_vessel_health()
    test_fleet_body()
    test_pain_signal()
    test_reflex_arc()
    test_fleet_health()
    print("\nAll 5 pass. The fleet feels its own body.")
