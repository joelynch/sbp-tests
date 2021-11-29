import os
import sys
import webbrowser
from typing import Iterator

import folium
import pandas as pd
from sbp.client import Framer, Handler
from sbp.client.drivers.file_driver import FileDriver
from sbp.navigation import SBP_MSG_POS_LLH
from tqdm import tqdm


def messages(path: str) -> Iterator[tuple]:
    with open(path, "rb") as s:
        with FileDriver(s) as driver:
            with Handler(
                Framer(driver.read, None, verbose=True),
                autostart=True,
            ) as handler:
                for msg, metadata in tqdm(handler.filter(SBP_MSG_POS_LLH), total=13678):
                    yield (
                        msg.lat,
                        msg.lon,
                        metadata["time"],
                    )


def main():
    msgs = messages(sys.argv[1])
    df = pd.DataFrame(msgs, columns=("lat", "lon", "time"))
    filtered = df[df["lat"] != 0]
    av_lat = filtered["lat"].mean()
    av_lon = filtered["lon"].mean()
    m = folium.Map(location=[av_lat, av_lon], tiles="cartodbpositron", zoom_start=14)
    folium.vector_layers.PolyLine(
        filtered[["lat", "lon"]],
        popup="<b>Path</b>",
        color="blue",
        weight=10,
    ).add_to(m)
    m.save("map.html")
    webbrowser.open("file://" + os.path.realpath("map.html"))


main()
