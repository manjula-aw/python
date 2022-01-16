import sqlite3

sqlitedbfile = 'vtap';

conn = sqlite3.connect(sqlitedbfile)
c = conn.cursor()
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
data = c.fetchall()

f = open(sqlitedbfile + "-out.txt", "w")

tables = [];
for row in data:
    f.write(str(row))
    f.write("\n")
    tables.append(row[0])

def read_from_db(tablename, c):
    c.execute('SELECT * FROM ' + tablename)
    data = c.fetchall()
    for row in data:
        f.write(str(row))
        f.write("\n")


for tablename in tables:
    read_from_db(tablename, c);


f.close()
