import os
from typing import Literal

from pydantic import BaseModel, Field

from cascade.data import (
    Assessor,
    DataCard,
    Dataset,
    LabelingInfo,
    SchemaModifier,
)

HERE = os.path.dirname(os.path.abspath(__file__))


# Here we establish data contract
class SensorReading(BaseModel):
    device_id: str = Field(min_length=3)
    temperature_c: float = Field(ge=-90, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    status: Literal["ok", "degraded", "fault"]


GOOD = {"temperature_c": 21.5, "humidity_pct": 44.0, "status": "ok"}


class VendorFeed(Dataset):
    """
    Simulates the nightly data drop. Here vendor gets a single row wrong
    """

    def __init__(self, corrupt: bool = True, **kwargs):
        self._rows = [dict(GOOD, device_id=f"dev-{i:03d}") for i in range(6)]
        if corrupt:
            # humidity as a percentage *of a percentage* - unit bug
            self._rows[3]["humidity_pct"] = 4400.0
        super().__init__(**kwargs)

    def get(self, index):
        return self._rows[index]

    def __len__(self):
        return len(self._rows)


class ToCelsiusDelta(SchemaModifier):
    """
    A downstream stage that will automatically perform schema check
    """

    in_schema = SensorReading

    def get(self, index):
        reading = self._dataset[index]
        return {**reading, "temp_delta": reading["temperature_c"] - 20.0}


def data_card():
    return DataCard(
        name="vendor-sensor-feed",
        desc="Nightly CSV drop from the sensor vendor, one row per device per hour",
        source="s3://vendor-drop/sensors/",
        goal="Predict device fault 24h ahead",
        labeling_info=LabelingInfo(
            who=[Assessor(id="vendor-qa", position="external contractor")],
            process_desc="Status is set by the vendor's rule engine, not by us",
            docs="https://internal.example/wiki/sensor-feed",
        ),
        size=6,
        metrics={"expected_fault_rate": 0.02},
        schema=SensorReading.model_json_schema(),
    )


def build(corrupt: bool):
    ds = VendorFeed(corrupt=corrupt, data_card=data_card())
    ds = ToCelsiusDelta(ds)
    return ds


def root_cause(exc):
    while exc.__cause__ is not None:
        exc = exc.__cause__
    return exc


def main():
    print("CLEAN FEED")
    ds = build(corrupt=False)

    for i in range(len(ds)):
        try:
            ds[i]
        except Exception as e:
            print(f"got {e.__class__.__name__} on item {i}, (unexpected!)")

    print(f"{len(ds)} rows ok, row 3 -> {ds[3]}")

    print("\nCORRUPTED FEED: the contract should trip on row 3 ")
    ds = build(corrupt=True)
    for i in range(len(ds)):
        try:
            ds[i]
        except Exception as e:
            print(f"row {i}: raised {type(e).__name__} -> {e}")
            print(f"  root cause: {type(root_cause(e)).__name__}")
            print("  " + str(root_cause(e)).replace("\n", "\n  "))
            break
    else:
        print("no erros detected (unexpected!)")

    print("\nDATA CARD")
    meta = build(corrupt=False).get_meta()
    print(
        f"pipeline has {len(meta)} stages: {[b['name'].split('.')[-1] for b in meta]}"
    )
    card = meta[-1].get("data_card")
    for k, v in card.items():
        print(f"  {k}: {str(v)[:70]}")


if __name__ == "__main__":
    main()
