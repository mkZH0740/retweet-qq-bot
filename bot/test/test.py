import sqlite3, time

st = time.time()
db = sqlite3.connect(r"C:\Users\mike\Desktop\workspace\proj4\src\bot\bin\logs.db")
res = db.execute("SELECT * FROM \"1012429452\" WHERE tw_type = 9").fetchall()
print(res)
print(time.time() - st)