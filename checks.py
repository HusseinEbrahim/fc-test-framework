import time


def attitude_spread(fc, samples=20, delay=0.05):
    """Read attitude repeatedly; return how much roll and pitch varied (max - min)."""
    rolls, pitches = [], []
    for _ in range(samples):
        reading = fc.attitude()
        rolls.append(reading["roll"])
        pitches.append(reading["pitch"])
        time.sleep(delay)
    return max(rolls) - min(rolls), max(pitches) - min(pitches)