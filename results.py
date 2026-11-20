import sqlite3

# Show how many KV is in each databases
for db in [
    "./data/store1/database1.db",
    "./data/store2/database2.db",
    "./data/store3/database3.db"
]:
    with sqlite3.connect(db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM kv_store"
        ).fetchone()[0]

    print("%s: %d keys" % (db, count))