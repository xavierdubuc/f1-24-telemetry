Status : not tested yet, didn't have the time to launch the game yet :)

This project is a fork of excellent project [f1-23-telemetry](https://github.com/chrishannam/f1-23-telemetry) of Chris Hannam. My only contribution here is to implement the f1 24 changes.

# F1 24 Telemetry Supporting v29x3
Currently supporting the `v3` from the F1 25 UDP specification which is available [here](https://forums.ea.com/blog/f1-games-game-info-hub-en/ea-sports%E2%84%A2-f1%C2%AE25-udp-specification/12187347)

# Installing

It's not working right now, I let the original author of this publish his own version (or take my small contribution
as part of the new version, I don't mind). If after "some time" he doesn't do it, then maybe it's a signal that he won't
and I may then consider the idea of publish it on PyPI.

```commandline
pip install f1-25-telemetry
```

# Running
```commandline
telemetry-f1-25-listener
```

# Usage

```python
from f1_25_telemetry.listener import TelemetryListener

listener = TelemetryListener(port=20777, host='localhost')
packet = listener.get()
```

# Releasing
```commandline
pip install --upgrade build twine
python -m build
python3 -m twine upload f1-25-telemetry dist/
```
