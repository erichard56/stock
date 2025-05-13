import sqlite3
from typing import Optional
from flask import Flask, render_template, request, redirect, flash

DATABASE = 'stock.db'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'anything-hard-to-guess'
		
conn = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = conn.cursor()

###########################

def chk_fecha(fecha):
	fecha = fecha.replace('/', '-')
	if (fecha.find('-') > 0 or fecha.find('-')):
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


##############

@app.route('/', methods=['GET', 'POST'])
@app.route('/stock', methods=['GET', 'POST'])
@app.route('/stock/<oper>/<letra>', methods=['GET', 'POST'])
@app.route('/stock/<oper>/<letra>/<id_producto>', methods=['GET', 'POST'])
@app.route('/stock/<oper>/<letra>/<id_producto>/<id_stock>', methods=['GET', 'POST'])
def stock(oper = None, letra = None, id_producto = None, id_stock = None):

	# obtengo todas las primeras letras de todos los producto	q1 = 'SELECT DISTINCT(SUBSTR(producto, 1, 1)) FROM productos ORDER BY producto'
	q1 = 'SELECT DISTINCT(SUBSTR(producto, 1, 1)) FROM productos ORDER BY producto'
	cursor.execute(q1)
	letras = cursor.fetchall()

	productos = None
	if (oper == "@"):	#indica que debo buscar ltodos los productos que comiencen por esa letra
		q1 = 'select * from productos where SUBSTR(producto, 1, 1) = "' + str(letra) + \
				'" order by producto'
		cursor.execute(q1)
		productos = cursor.fetchall()
		if (len(productos) == 1):
			id_producto = productos[0][0]
	
	elif (oper == "@@"):
		q1 = 'select * from productos where SUBSTR(producto, 1, 1) = "' + str(letra) + \
				'" order by producto'
		cursor.execute(q1)
		productos = cursor.fetchall()
		if (len(productos) == 1):
			id_producto = productos[0][0]

		q1 = 'select *, ' + \
			' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
			' where id_producto = ' + str(id_producto)
		cursor.execute(q1)
		stocks = cursor.fetchall()

	elif (oper == 'B'):		# borrar registro
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

	if (oper is not None and oper in "BDI"):
		q1 = 'select * from productos where SUBSTR(producto, 1, 1) = "' + str(letra) + \
				'" order by producto'
		cursor.execute(q1)
		productos = cursor.fetchall()
		if (len(productos) == 1):
			id_producto = productos[0][0]


	if (id_producto is not None):
		q1 = 'select *, ' + \
			' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
			' where id_producto = ' + str(id_producto)
		cursor.execute(q1)
		stocks = cursor.fetchall()
	else:
		stocks = None		

	if (request.method == 'POST'):
		busq = request.form.get("busq")
		if (len(busq) > 0):
			q1 = 'select * from productos where producto like "%' + str(busq).strip() + \
					'%" order by producto'
			cursor.execute(q1)
			productos = cursor.fetchall()
			if (len(productos) == 0):
				flash('No hay productos con esa descripcion')

			else:
				if (len(productos) == 1):
					id_producto = productos[0][0]
					# obtengo todos los registros de stock
					q1 = 'select *, ' + \
						' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
						' where id_producto = ' + str(id_producto)
					cursor.execute(q1)
					stocks = cursor.fetchall()
				else:
					id_producto = None
		
		else:
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

			# obtengo todos los registros de stock
			q1 = 'select *, ' + \
				' (substr(fecha, instr(fecha, "-") + 1, 4) * 12 + substr(fecha, 1, instr(fecha, "-") - 1))  - (strftime("%Y", datetime()) * 12 + strftime("%m", datetime()))from stocks ' + \
				' where id_producto = ' + str(id_producto)
			cursor.execute(q1)
			stocks = cursor.fetchall()



	ctx = { 'letras':letras, 'letra':letra, 'productos':productos, 'id_producto':id_producto, 'stocks':stocks }
	return(render_template('stock.html', **ctx))

#############

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
