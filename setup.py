from setuptools import setup

setup(
    name='cluster_guard',
    version='1.0.0',
    packages=[''],
    url='matthewpicone.com',
    license='MIT',
    author='Matthew Picone',
    author_email='mail@matthewpicone.com',
    description='This module provides a graphical user interface for monitoring the replication status and delay between a PostgreSQL master and slave server. It utilizes psycopg2 for database connections and tkinter for the graphical user interface. The application continuously checks and displays the replication status and delay in real-time, offering insights into the health and performance of PostgreSQL server replication. '
)
