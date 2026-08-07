import sqlite3

conexao = sqlite3.connect("gymtrack.db")

cursor = conexao.cursor()

registro = cursor.execute("SELECT * FROM treinos_dia WHERE velocidade = 6.5").fetchone()
cursor.execute("UPDATE cadastros SET admin=1 WHERE email = 'ivvansanper@gmail.com'")

resultado = cursor.execute("SELECT * FROM cadastros").fetchall()
conexao.commit()
conexao.close()

print(registro)
print(resultado)