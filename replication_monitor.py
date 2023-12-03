# -*- coding: utf-8 -*-
"""
PostgreSQL Replication Monitor

This module provides a graphical user interface for monitoring the replication status and delay between a PostgreSQL
master and slave server. It utilizes psycopg2 for database connections and tkinter for the graphical user interface.
The application continuously checks and displays the replication status and delay in real-time, offering insights into
the health and performance of PostgreSQL server replication.

Example
-------
To use this module, ensure that psycopg2, tkinter, and matplotlib are installed, then run:

    $ python postgresql_replication_monitor.py

The GUI will display the current replication status of the master and slave servers, along with a plot of replication
delay over time.

Notes
-----
This module requires a configuration file `credentials.py` containing `MASTER_DB_CONFIG` and `SLAVE_DB_CONFIG` for
database connections. The replication delay is graphed using matplotlib and updated in real-time using a tkinter
interface.

Attributes
----------
MASTER_DB_CONFIG : dict
    Configuration dictionary for the master PostgreSQL database connection.
SLAVE_DB_CONFIG : dict
    Configuration dictionary for the slave PostgreSQL database connection.
replication_delays : collections.deque
    A deque object used to store and update replication delay data.

Author : matthewpicone
Date   : 03/12/2023
"""
from collections import deque

import psycopg2
import tkinter as tk
from threading import Thread
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import credentials

# Configuration
MASTER_DB_CONFIG = credentials.credentials.MASTER_DB_CONFIG
SLAVE_DB_CONFIG = credentials.credentials.SLAVE_DB_CONFIG

# Data storage for replication delay
replication_delays = deque(maxlen=300)  # Set the maximum length to 300


def update_replication_data(is_in_recovery, replication_delay):
    """
    Update the replication delay data.

    Parameters
    ----------
    is_in_recovery : bool
        Indicates whether the slave database is in recovery mode.
    replication_delay : datetime.timedelta
        The time delay in replication from the master to the slave.

    Notes
    -----
    This function appends the current timestamp and replication delay to the global deque.
    It maintains a maximum length of 300 elements for the deque.
    """
    global replication_delays
    if replication_delay is not None and replication_delay != 0:
        replication_delays.append((datetime.datetime.now(), replication_delay))

        if len(replication_delays) > 300:
            replication_delays.popleft()
    else:
        replication_delays.append((datetime.datetime.now(), 0))


def check_master_status():
    """
    Continuously check the replication status of the master database.

    This function establishes a connection to the master database, queries the
    replication status, and updates the master status in the GUI.
    In case of an error, it updates the GUI with the error information.
    """
    while True:
        try:
            with psycopg2.connect(**MASTER_DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM pg_stat_replication;")
                    replication_status = cur.fetchall()
                    master_status.set(f"Master Replication Status:\n{replication_status}")
                    master_status_color.set("green")
                    master_status_indicator.itemconfig(master_status_rectangle, fill="green")
        except Exception as e:
            master_status.set(f"Error: {e}")
            master_status_color.set("red")
            master_status_indicator.itemconfig(master_status_rectangle, fill="red")
        time.sleep(1)


def check_slave_status():
    """
    Continuously check the status and replication delay of the slave database.

    This function establishes a connection to the slave database, queries its
    recovery status and replication delay, and updates the slave status in the GUI.
    In case of an error, it updates the GUI with the error information.
    """
    while True:
        try:
            with psycopg2.connect(**SLAVE_DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_is_in_recovery();")
                    is_in_recovery = cur.fetchone()[0]
                    cur.execute("SELECT now() - pg_last_xact_replay_timestamp() AS replication_delay;")
                    replication_delay = cur.fetchone()[0]
                    slave_status.set(f"Slave Recovery Mode: {is_in_recovery}\nReplication Delay: {replication_delay}")
                    update_replication_data(is_in_recovery, replication_delay)
                    slave_status_color.set("green")
                    slave_status_indicator.itemconfig(slave_status_rectangle, fill="green")
        except Exception as e:
            slave_status.set(f"Error: {e}")
            slave_status_color.set("red")
            slave_status_indicator.itemconfig(slave_status_rectangle, fill="red")
        time.sleep(1)


def plot_replication_delay(fig, ax):
    """
    Plot the replication delay on a given matplotlib figure and axis.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The matplotlib figure object.
    ax : matplotlib.axes.Axes
        The matplotlib axis object on which to plot the data.

    Notes
    -----
    This function plots the replication delays stored in the global deque, displaying
    the time in seconds against the replication delay.
    """
    ax.clear()
    x_vals, y_vals = zip(*replication_delays) if replication_delays else ([], [])
    x_vals = [(x_vals[-1] - x).total_seconds() for x in x_vals]
    x_vals = [x_vals[-1] - x for x in x_vals]

    ax.plot(x_vals, y_vals, '-', color='blue')
    ax.set_title("Replication Delay Over Last 30 Minutes")
    ax.set_xlabel("Time (seconds past)")
    ax.set_ylabel("Replication Delay (seconds)")


def refresh_plot():
    """
    Refresh the replication delay plot.

    This function updates the plot with the latest replication delay data.
    """
    plot_replication_delay(fig, ax)
    canvas.draw()


# Set up the Tkinter window
root = tk.Tk()
root.title("PostgreSQL Replication Monitor")

# Reactively stretch when the window is resized
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# Status variables
master_status = tk.StringVar(root, value="Checking Master Status...")
slave_status = tk.StringVar(root, value="Checking Slave Status...")

# Indicator colors
master_status_color = tk.StringVar(root, value="gray")  # Default color is gray
slave_status_color = tk.StringVar(root, value="gray")  # Default color is gray

# Create frames for better layout
master_frame = tk.Frame(root, padx=10, pady=10)
master_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")

slave_frame = tk.Frame(root, padx=10, pady=10)
slave_frame.grid(row=0, column=2, rowspan=2, columnspan=2, sticky="nsew")

plot_frame = tk.Frame(root)
plot_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")

# Create and pack widgets with padding
master_label_title = tk.Label(master_frame, text=f"Master {MASTER_DB_CONFIG['host']}", font=("Helvetica", 14))
master_label_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

# Create a small canvas for the indicator square
master_status_indicator = tk.Canvas(master_frame, width=15, height=15)
master_status_indicator.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="e")

# Create a rectangle on the canvas for the indicator
master_status_rectangle = master_status_indicator.create_rectangle(0, 0, 15, 15, fill=master_status_color.get())
master_status_indicator.itemconfig(master_status_rectangle, fill=master_status_color.get())  # Set initial color

master_label = tk.Label(master_frame, textvariable=master_status, justify=tk.LEFT, wraplength=480, relief=tk.SUNKEN,
                        bg="white", anchor='w')
master_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

slave_label_title = tk.Label(slave_frame, text=f"Slave {SLAVE_DB_CONFIG['host']}", font=("Helvetica", 14))
slave_label_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

# Create a small canvas for the indicator square
slave_status_indicator = tk.Canvas(slave_frame, width=15, height=15)
slave_status_indicator.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="e")

# Create a rectangle on the canvas for the indicator
slave_status_rectangle = slave_status_indicator.create_rectangle(0, 0, 15, 15, fill=slave_status_color.get())
slave_status_indicator.itemconfig(slave_status_rectangle, fill=slave_status_color.get())  # Set initial color

slave_label = tk.Label(slave_frame, textvariable=slave_status, justify=tk.LEFT, wraplength=480, relief=tk.SUNKEN,
                       bg="white", anchor='w')
slave_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Matplotlib plot setup with padding
fig, ax = plt.subplots()

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, sticky="nsew")


def update_plot():
    refresh_plot()
    root.after(1000, update_plot)  # Refresh every 60 seconds


update_plot()

# Start threads for monitoring
Thread(target=check_master_status, daemon=True).start()
Thread(target=check_slave_status, daemon=True).start()

# Start the Tkinter event loop
root.mainloop()
