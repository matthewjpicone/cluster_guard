# -*- coding: utf-8 -*-
"""
TODO: Add to Central Connect
Author : matthewpicone
Date   : 2/12/2023
"""


class credentials:
    MASTER_DB_CONFIG = {
        "host": "100.87.130.132",
        "dbname": "postgres",
        "user": "matthewpicone",
        "password": "point-temple-hammer-71102102-^*(^"
    }

    SLAVE_DB_CONFIG = MASTER_DB_CONFIG.copy()
    SLAVE_DB_CONFIG['host'] = "100.67.248.140"
