This project is a fork of excellent project [f1-23-telemetry](https://github.com/chrishannam/f1-23-telemetry) of Chris Hannam. My only contribution here is to implement the f1 24 changes.

# F1 24 Telemetry Supporting v29x3
Currently supporting the `v27.2` from the F1 24 UDP specification which is available [here](https://answers.ea.com/t5/General-Discussion/F1-24-UDP-Specification/td-p/13745220)

# Installing

```commandline
pip install f1-24-telemetry
```

# Running
```commandline
telemetry-f1-24-listener
```

# Usage

```python
from f1_24_telemetry.listener import TelemetryListener

listener = TelemetryListener(port=20777, host='localhost')
packet = listener.get()
```

# Releasing
```commandline
pip install --upgrade build twine
python -m build
python3 -m twine upload f1-24-telemetry dist/
```
