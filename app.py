import sqlite3
from typing import Optional
from flask import Flask, render_template, request, redirect, flash

DATABASE = 'stock.db'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'anything-hard-to-guess'
		
conn = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = conn.cursor()

@app.route('/', methods=['GET', 'POST'])
def inicioC():
	if (request.method == 'GET'):
		q1 = 'select * from clases'
		cursor.execute(q1)
		clases = cursor.fetchall()
		ctx = { 'clases':clases }
		return(render_template('login.html', **ctx))

@app.route('/<id_clase>', methods=['GET'])
def inicioCS(id_clase):
	if (request.method == 'GET'):
		q1 = 'select * from clases'
		cursor.execute(q1)
		clases = cursor.fetchall()
		
		q1 = 'select * from subclases where id_clase = ' + str(id_clase)
		cursor.execute(q1)
		subclases = cursor.fetchall()

		ctx = { 'clases':clases, 'id_clase':id_clase, 
		 		'subclases':subclases }
		return(render_template('login.html', **ctx))

@app.route('/<id_clase>/<id_subclase>', methods=['GET'])
def inicioCSP(id_clase, id_subclase):
	if (request.method == 'GET'):
		q1 = 'select * from clases'
		cursor.execute(q1)
		clases = cursor.fetchall()
		
		q1 = 'select * from subclases where id_clase = ' + str(id_clase)
		cursor.execute(q1)
		subclases = cursor.fetchall()

		q1 = 'select * from productos where id_clase = ' + str(id_clase) + ' and id_subclase = ' + str(id_subclase)
		cursor.execute(q1)
		productos = cursor.fetchall()

		ctx = { 'clases':clases, 'id_clase':id_clase, 
		 		'subclases':subclases, 'id_subclase':id_subclase, 
		 		'productos':productos }
		return(render_template('login.html', **ctx))

def chk_fecha(fecha):
	fecha = fecha.replace('/', '-')
	if (fecha.find('-') > 0):
		m, a = fecha.split('-')
		try:
			mes = int(m)
			if (1 <= mes <= 12):
				try:
					anio = int(a)
					if (anio < 100):
						anio += 2000
						fecha = '-'.join([str(mes), str(anio)]) 
						return(fecha)
				except:
					flash('Año fuera de rango')
					return(-1)	# anio esta fuera de rango
			else:
				flash('Mes debe estar entre 1 y 12')
				return(-2)	# mes esta fuera de rango
		except:
			flash('El mes debe ser numérico')
			return(-3)	# mes no es numerico
	else:
		flash('Debe ser algo de la forma mm/aaaa')
		return(-4)	# falta el separador


@app.route('/<id_clase>/<id_subclase>/<id_producto>', methods=['GET', 'POST'])
def inicioCSPS(id_clase, id_subclase, id_producto):
	q1 = 'select * from clases'
	cursor.execute(q1)
	clases = cursor.fetchall()
	
	q1 = 'select * from subclases where id_clase = ' + str(id_clase)
	cursor.execute(q1)
	subclases = cursor.fetchall()

	q1 = 'select * from productos where id_clase = ' + str(id_clase) + ' and id_subclase = ' + str(id_subclase)
	cursor.execute(q1)
	productos = cursor.fetchall()

	q1 = 'select * from productos where id = ' + str(id_producto)
	cursor.execute(q1)
	producto = cursor.fetchone()

	if (request.method == 'GET'):
		q1 = 'select *, ' + \
			' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
			' where id_producto = ' + str(id_producto)
		cursor.execute(q1)
		stocks = cursor.fetchall()
		ctx = { 'clases':clases, 'id_clase':id_clase, 'subclases':subclases, 
		 		'id_subclase':id_subclase, 'productos':productos, 'id_producto':id_producto, 
				'producto':producto, 'stocks':stocks }
		return(render_template('login.html', **ctx))

	elif (request.method == 'POST'):
		cantidad = request.form.get('cantidad')
		fecha = request.form.get('fecha')
		fecha = chk_fecha(fecha)
		if (type(fecha) == str):
			q1 = 'insert into stocks values (NULL, ' + \
				cantidad + ', "' + fecha + '", ' + str(id_producto) + ')'
			cursor.execute(q1)
			conn.commit()

		q1 = 'select *, ' + \
			' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
			' where id_producto = ' + str(id_producto)
		cursor.execute(q1)
		stocks = cursor.fetchall()
		ctx = { 'clases':clases, 'id_clase':id_clase, 
		 		'subclases':subclases, 'id_subclase':id_subclase, 
				'productos':productos, 'id_producto':id_producto, 
				'stocks':stocks }
		return(render_template('login.html', **ctx))


@app.route('/abm/<oper>/<id_clase>/<id_subclase>/<id_producto>/<id_stock>', methods=['GET', 'POST'])
def abm(oper, id_clase, id_subclase, id_producto, id_stock):
	q1 = 'select * from stocks where id = ' + str(id_stock)
	cursor.execute(q1)
	stock = cursor.fetchone()

	if (request.method == 'GET'):

		if (oper == 'B'):		# borrar registro
			q1 = 'delete from stocks where id = ' + str(id_stock)
			cursor.execute(q1)
			conn.commit()

		elif (oper == 'D'):		# decrementar 1
			q1 = 'update stocks set cantidad = cantidad - 1 where id = ' + str(id_stock)
			cursor.execute(q1)
			conn.commit()

		elif (oper == 'I'):		# incrementar 1
			q1 = 'update stocks set cantidad = cantidad + 1 where id = ' + str(id_stock)
			cursor.execute(q1)
			conn.commit()

	elif (request.method == 'POST'):
		cantidad = request.form.get('cantidad')
		fecha = request.form.get('fecha')
		fecha = chk_fecha(fecha)
		if (type(fecha) == int):
			flash('Valor invalido en fecha')

		else:
			q1 = 'insert into stocks values (NULL, ' + \
				cantidad + ', "' + fecha + '", ' + str(id_producto) + ')'
			cursor.execute(q1)
			conn.commit()

		q1 = 'select *, ' + \
			' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
			' where id_producto = ' + str(id_producto)
		cursor.execute(q1)
		stocks = cursor.fetchall()
	
	q1 = 'select * from clases'
	cursor.execute(q1)
	clases = cursor.fetchall()
	
	q1 = 'select * from subclases where id_clase = ' + str(id_clase)
	cursor.execute(q1)
	subclases = cursor.fetchall()

	q1 = 'select * from productos where id_clase = ' + str(id_clase) + ' and id_subclase = ' + str(id_subclase)
	cursor.execute(q1)
	productos = cursor.fetchall()

	q1 = 'select *, ' + \
		' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
		' where id_producto = ' + str(id_producto)
	cursor.execute(q1)
	stocks = cursor.fetchall()

	ctx = { 'clases':clases, 'id_clase':id_clase, 
			'subclases':subclases, 'id_subclase':id_subclase, 
			'productos':productos, 'id_producto':id_producto, 
			'stocks':stocks }
	return(render_template('login.html', **ctx))


@app.route('/letras')
def letras():
	q1 = 'SELECT DISTINCT(SUBSTR(producto, 1, 1)) FROM productos ORDER BY producto'
	cursor.execute(q1)
	letras = cursor.fetchall()
	ctx = { 'letras':letras }
	return(render_template('letras.html', **ctx))

@app.route('/prods/<letra>')
def prods(letra):
	q1 = 'SELECT DISTINCT(SUBSTR(producto, 1, 1)) FROM productos ORDER BY producto'
	cursor.execute(q1)
	letras = cursor.fetchall()

	q1 = 'select * from productos where SUBSTR(producto, 1, 1) = "' + str(letra) + '" order by producto'
	cursor.execute(q1)
	productos = cursor.fetchall()

	ctx = { 'letras':letras, 'productos':productos }
	return(render_template('letras.html', **ctx))

@app.route('/prodstock/<letra>/<id_producto>', methods=['GET', 'POST'])
def prodstock(letra, id_producto):
	q1 = 'SELECT DISTINCT(SUBSTR(producto, 1, 1)) FROM productos ORDER BY producto'
	cursor.execute(q1)
	letras = cursor.fetchall()

	q1 = 'select * from productos where SUBSTR(producto, 1, 1) = "' + str(letra) + '" order by producto'
	cursor.execute(q1)
	productos = cursor.fetchall()

	if (request.method == 'POST'):
		cantidad = request.form.get('cantidad')
		fecha = request.form.get('fecha')
		fecha = chk_fecha(fecha)
		if (type(fecha) == int):
			flash('Valor invalido en fecha')

		else:
			q1 = 'insert into stocks values (NULL, ' + \
				cantidad + ', "' + fecha + '", ' + str(id_producto) + ')'
			cursor.execute(q1)
			conn.commit()

	q1 = 'select *, ' + \
		' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
		' where id_producto = ' + str(id_producto)
	cursor.execute(q1)
	stocks = cursor.fetchall()

	ctx = { 'letras':letras, 'letra':letra, 'productos':productos, 'id_producto':id_producto, 'stocks':stocks }
	return(render_template('letras.html', **ctx))

@app.route('/abmlet/<oper>/<letra>/<id_producto>/<id_stock>', methods=['GET', 'POST'])
def abmlet(oper, letra, id_producto, id_stock):
	q1 = 'select * from stocks where id = ' + str(id_stock)
	cursor.execute(q1)
	stock = cursor.fetchone()

	if (request.method == 'GET'):

		if (oper == 'B'):		# borrar registro
			q1 = 'delete from stocks where id = ' + str(id_stock)
			cursor.execute(q1)
			conn.commit()

		elif (oper == 'D'):		# decrementar 1
			q1 = 'update stocks set cantidad = cantidad - 1 where id = ' + str(id_stock)
			cursor.execute(q1)
			conn.commit()

		elif (oper == 'I'):		# incrementar 1
			q1 = 'update stocks set cantidad = cantidad + 1 where id = ' + str(id_stock)
			cursor.execute(q1)
			conn.commit()

	elif (request.method == 'POST'):
		cantidad = request.form.get('cantidad')
		fecha = request.form.get('fecha')
		fecha = chk_fecha(fecha)
		if (type(fecha) == int):
			flash('Valor invalido en fecha')

		else:
			q1 = 'insert into stocks values (NULL, ' + \
				cantidad + ', "' + fecha + '", ' + str(id_producto) + ')'
			cursor.execute(q1)
			conn.commit()

	q1 = 'SELECT DISTINCT(SUBSTR(producto, 1, 1)) FROM productos ORDER BY producto'
	cursor.execute(q1)
	letras = cursor.fetchall()

	q1 = 'select * from productos where SUBSTR(producto, 1, 1) = "' + str(letra) + '" order by producto'
	cursor.execute(q1)
	productos = cursor.fetchall()

	q1 = 'select *, ' + \
		' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
		' where id_producto = ' + str(id_producto)
	cursor.execute(q1)
	stocks = cursor.fetchall()

	ctx = { 'letras':letras, 'letra':letra,  'productos':productos, 'id_producto':id_producto, 'stocks':stocks }
	return(render_template('letras.html', **ctx))


@app.route('/k')
def inicio_k():
	datos = []
	k1 = []
	q1 = 'select * from clases'
	cursor.execute(q1)
	clases = cursor.fetchall()
	for clase in clases:
		k2 = []
		q2 = 'select * from subclases where id_clase = ' + str(clase[0])
		cursor.execute(q2)
		subclases = cursor.fetchall()
		for subclase in subclases:
			k3 = []
			q3 = 'select * from productos where id_clase = ' + str(clase[0]) + ' and id_subclase = ' + str(subclase[0])
			cursor.execute(q3)
			productos = cursor.fetchall()
			for producto in productos:
				k4 = []
				q4 = 'select * from stocks where id_producto = ' + str(producto[0])
				cursor.execute(q4)
				stocks = cursor.fetchall()
				for stock in stocks:
					k4.append([stock[1], stock[2]])
				k3.append([producto[1], k4])
			k2.append([subclase[1], k3])
		k1.append([clase[1], k2])
	datos.append(k1)
	return(render_template('productos_k.html', datos = datos))

@app.route('/vw')
def inicio_vw():
	q1 = 'select * from vw_productos'
	cursor.execute(q1)
	productos = cursor.fetchall()
	return(render_template('productos_vw.html', productos = productos))



if (__name__ == '__main__'):
	app.run(debug=False)
