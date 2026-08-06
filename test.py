import sqlite3

conexao = sqlite3.connect("gymtrack.db")

cursor = conexao.cursor()

registro = cursor.execute("SELECT * FROM treinos_dia WHERE velocidade = 6.5").fetchone()

conexao.close()

print(registro)