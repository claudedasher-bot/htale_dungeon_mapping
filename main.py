import pygetwindow as gw
import get_coordinates
import re
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
debug = False

x_history = []
z_history = []
latest_coords = None
lock = threading.Lock()
last_plotted = None


y_maps = {}
axis = {}
if debug:
    print(gw.getAllTitles())

game = next(
    (w for w in gw.getAllWindows() if w.title == "Hytale"),
    None
)

if game is None:
    print("Open Hytale first!")
    exit()
else:
    print("Hytale detected!")
    print("Title:", game.title)
    print("Handle:", game._hWnd)
    print("Position:", game.left, game.top)
    print("Size:", game.width, game.height)
    
def receive_coords(text):
    global latest_coords
    print("raw:", text)
    try:
        x = int(float(text[0].strip(",")))
        y = int(float(text[1].strip(",")))
        z = int(float(text[2].strip(",")))
    except (ValueError, IndexError, TypeError) as e:
        print("skipped:", e)
        return
    with lock:
        latest_coords = (x, y, z)
listener = threading.Thread(
    target=get_coordinates.start,
    args=(game._hWnd, receive_coords),
    daemon=True
)

listener.start()

def get_latest_coords():
    with lock:
        return latest_coords

def get_y_range(y):
    return (y//10) * 10

def add_y_subplot(y_range):
    fig, ax = plt.subplots()
    axis[y_range] = ax

    line, = ax.plot(
        [], [],
        marker="o",
        linestyle="-",
        color="dodgerblue",
        label="Path"
    )

    current_dot, = ax.plot(
        [], [],
        marker="o",
        markersize=8,
        color="red",
        label="Current Position"
    )

    ax.set_title(f"Y {y_range} to {y_range + 9}")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Z Coordinate")
    ax.grid(True)
    ax.legend()
    ax.set_aspect("equal", adjustable="datalim")

    y_maps[y_range] = {
        "x": [],
        "z": [],
        "line": line,
        "dot": current_dot,
        "fig": fig
    }

    fig.show()
def plot():
    coords = get_latest_coords()

    if coords is not None:
        x, y, z = coords

        def update_plot(frame):
            global last_plotted

            with lock:
                coords = latest_coords

            if coords is None:
                return []

            x, y, z = coords
            y_range = get_y_range(y)

            if y_range not in y_maps:
                add_y_subplot(y_range)

            # only record actual movement (or a change of y level)
            if (x, z, y_range) != last_plotted:
                y_maps[y_range]["x"].append(x)
                y_maps[y_range]["z"].append(z)
                last_plotted = (x, z, y_range)

            for key, data in y_maps.items():
                data["line"].set_data(data["x"], data["z"])

                if key == y_range:
                    data["dot"].set_data([x], [z])
                else:
                    data["dot"].set_data([], [])

                axis[key].relim()
                axis[key].autoscale_view()
                data["fig"].canvas.draw_idle()

            return []

        # FuncAnimation needs a figure, so give it the first one
        # (created here so the loop has something to attach to)
        first_range = get_y_range(y)
        if first_range not in y_maps:
            add_y_subplot(first_range)

        ani = FuncAnimation(
            y_maps[first_range]["fig"],
            update_plot,
            interval=1000,
            cache_frame_data=False
        )

        plt.show()

        print(f"X: {x}, Y: {y}, Z: {z}")

try:
    while True:
        plot()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopping coordinate tracking...")

