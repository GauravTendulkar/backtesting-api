import duckdb

# duckdb_conn = []
# for i in range(5):
#     duckdb_conn = duckdb.connect(database=f"database_duckdb/stocks_{i}.duckdb")

# duckdb_conn = duckdb.connect(database="database_duckdb/stocks.duckdb", config={"threads": 4
#                                                                             #    , "memory_limit": "4GB"
#                                                                                })

duckdb_conn = duckdb.connect()