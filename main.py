import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.animation import FuncAnimation

DEPTH_DATA_FILE = "depth_data.csv" # file name of depth data
ANOMALY_WINDOW = 5 # window used to calculate local median to identify anomalies
ANOMALY_THRESHOLD = 30 # threshold to classify a point as an anomaly
SMOOTHING_WINDOW = 8 # level of smoothing of the curve to reduce noise

depths = []

######################################
### extract the data from the file ###
######################################

with open(DEPTH_DATA_FILE, 'r') as file:
    reader = csv.reader(file) # read file with csv library for easy decoding

    next(reader) # skip the first line since it contains column names

    for row in reader:
        try:
            depths.append(float(row[1])) # add data to global depths array
        except (ValueError, IndexError):
            continue # corrupted data not in a floating point format will be skipped over

#######################################
### find anomalies and smooth curve ###
#######################################

# this method calculates a local median calculated from a given window around the current value
# if the current value is greater than the threshold, it is classifies as an anomaly

anomalies = [] # indices of the anomalies

for i in range(len(depths)):
    start = max(0, i - ANOMALY_WINDOW // 2) # start of the window
    end = min(len(depths), i + ANOMALY_WINDOW // 2 + 1) # end of the window

    local_values = depths[start:end]
    median = np.median(local_values) # median of the local values

    # if difference is greater than threshold, it is an anomaly
    if abs(depths[i] - median) > ANOMALY_THRESHOLD: 
        anomalies.append(i)

# remove all the anomalous values in the array
depths_clean = [
    value for i, value in enumerate(depths)
    if i not in anomalies
]

# smooth the curve to reduce noise
smoothed = np.convolve(
    depths_clean,
    np.ones(SMOOTHING_WINDOW) / SMOOTHING_WINDOW,
    mode="valid"
)

depths = smoothed

########################################
### display depth/time graph of data ###
########################################

plt.rcParams["toolbar"] = "None" # hide toolbar for a clean window

fig, ax = plt.subplots(figsize=(10, 6))

# set the colors of the graph

# background
fig.patch.set_facecolor("#111111")
ax.set_facecolor("#111111")

# line
line, = ax.plot(
    [],
    [],
    color="#00ff9d",
    linewidth=2
)

# text
ax.set_xlabel("Time (s)", color="white")
ax.set_ylabel("Depth", color="white")
ax.set_title("Depth Sensor", color="white")

# tick colors
ax.tick_params(axis="both", colors="white")

# grid
ax.grid(
    True,
    color="#444444",
    linestyle="--",
    alpha=0.5
)

# spine
for spine in ax.spines.values():
    spine.set_color("#666666")

line, = ax.plot([], [], linewidth=1)

# axis labels
ax.set_xlabel("Time")
ax.set_ylabel("Depth")
ax.set_title("Depth Sensor Readings")

# make sure y-axis intervals are appropriate and neat
ax.yaxis.set_major_locator(
    MaxNLocator(integer=True, nbins=8)
)

# move x axis to the top since all the y-values are negative
ax.xaxis.tick_top()
ax.xaxis.set_label_position("top")

def update(frame):
    # display values as they are detected by the sensor
    # add one more value each second
    x = list(range(frame + 1))
    y = depths[:frame + 1]

    line.set_data(x, y)

    # expand the current line to fill the graph
    ax.set_xlim(0, max(5, frame))

    # Dynamically adjust the y-axis
    ymin = min(y)
    ymax = max(y)

    # force y-axis to have height even if all depths have same value
    if ymin == ymax:
        ymin -= 1
        ymax += 1

    # add padding between data and axes
    padding = (ymax - ymin) * 0.1

    ax.set_ylim(
        ymin - padding,
        ymax + padding
    )

    return line,

# animate the graph to update it every second and add a new data point
animation = FuncAnimation(
    fig,
    update,
    frames=len(depths),
    interval=1000, # set interval to 1 second to simulate sensor readings every second
    repeat=False
)

plt.show()
