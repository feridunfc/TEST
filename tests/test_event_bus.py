
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from infra.event_bus import EventBus
from schemas.events import Event

def run():
    bus = EventBus()
    received = []

    def on_md(ev):
        received.append(ev)

    bus.subscribe("MARKET_DATA", on_md)

    ev = Event.create("MARKET_DATA", "binance:btcusdt", {"bar": {"o":1,"h":2,"l":0.5,"c":1.3,"v":100}})
    bus.publish("MARKET_DATA", ev.asdict())

    assert len(received) == 1
    assert received[0]["payload"]["bar"]["c"] == 1.3
    print("event_bus_ok")

if __name__ == "__main__":
    run()
