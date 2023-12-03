#Nota: esta es la version mejorada a fecha 12/05/2022
#Donde aplico el Metodo de la Brujula (o de Bowditch) para corregir la poligonal.
#mejoro el aspecto de la interfaz grafica y la presentacion del resultado.

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from io import open
from math import sin, cos, pi, hypot#No es una buena practica importar todo un modulo
from pyautocad import APoint, Autocad, aDouble
from tkinter.font import Font

raiz = Tk()
raiz.title("Recomputar Parcelas")
raiz.geometry("480x390")
raiz.resizable(False, False)
#----------------------------------------------------------------------Clase-----------------------------------------------------------------

class Linea:

	def __init__(self, cuadrante, angulo, distancia):

		self.cuadrante = cuadrante# debe ser 1, 2, 3 o 4
		self.angulo = angulo# debe estar escrito en grados con decimales, no en grados, minutos y segundos.
		self.distancia = distancia
		self.azimut = 0
		self.x_final = 0
		self.y_final = 0

	def definir_azimut(self):
		
		if self.cuadrante == 1:
			self.azimut = self.angulo

		elif self.cuadrante == 2:
			self.azimut = 180 - self.angulo

		elif self.cuadrante == 3:
			self.azimut = 180 + self.angulo

		elif self.cuadrante == 4:
			self.azimut = 360 - self.angulo

	def calcular_coord_punto_final(self, x_inicial, y_inicial):

		self.definir_azimut()#se debe ejecutar este metodo antes de hacer los calculos.
		self.x_final = x_inicial + self.distancia * sin(self.azimut*(pi/180))
		self.y_final = y_inicial + self.distancia * cos(self.azimut*(pi/180))
		return self.x_final, self.y_final


#--------------------------------------------------------------------Variables----------------------------------------------

texto_data_introducida = []
este = StringVar()
norte = StringVar()
coordenadas = list()
coord_corregidas = list()
azimuts_distancias = []#Azimuts y distancias usados para calcular las proyecciones que sirven para corregir la posicional.
se_puede_calcular = True
error_lineal_de_cierre = None

#--------------------------------------------------------------------Funciones--------------------------------------------------

def borrar():
	global cuandro_respuesta
	valor = messagebox.askokcancel("Aviso", "Desea borrar el contenido de la pantalla ?")

	if valor:
		#para un Entry se puede usar 0 como primer indice, pero para el Text se debe usar "1.0" como indice.		
		cuandro_respuesta.delete("1.0", END)

def probar_formato(linea, numero_linea):
	#Esta funcion sirve para probar que la informacion que se resive cumple con el formato	
	
	cumple_1 = False
	cumple_2 = False
	cumple_3 = False
	texto_aviso = "Errores: \n"
	
	try:
		cuadrante = int(linea[0])
		if cuadrante >= 1 and cuadrante <= 4: 
			cumple_1 = True

		else:
			texto_aviso += "-El cuadrante debe ser un numero entre 1 y 4 \n"	

	except ValueError:
		texto_aviso += "-El cuadrante no puede ser una letra, ni una combinación entre letras y números \n"

	try:
		rumbo = float(linea[1])
		minutos_rumbo = int(linea[1].split(".")[1])#aqui estoy extrayendo la parte decimal del rumo:

		if rumbo >= 0 and rumbo <= 90 and minutos_rumbo < 60:
			cumple_2 = True
		
		else:
			texto_aviso += "-Los rumbos son mayores de 0° y menores que 90° (0° <= R <= 90°), ademas la parte decimal de este no puede superar los 60''(Minutos) \n"

	except ValueError:
		texto_aviso += "-No es necesario poner letras en el rumbo \n"

	except IndexError:
		texto_aviso += "-Para rumbos sin minutos agregue el punto y dos ceros Ejemplo: 30 = 30.00\n"

	try:
		distancia = float(linea[2])
		if distancia < 0:
			texto_aviso += "-Las distancias no pueden ser negativas \n"

		else:
			cumple_3 = True

	except ValueError:
		texto_aviso += "-Las distancias no pueden contener letras \n"

	if cumple_1 and cumple_2 and cumple_3:
		return True

	else:
		messagebox.showwarning("La liena No.{} no cumple con el formato".format(numero_linea), texto_aviso)
		return False					



def cargar_archivo():
	#Esta función se en carga de cargar el archivo y mostrar la informción en la pantalla.
	#Ademas de avisar si hay errores. 
	global cuandro_respuesta
	global texto_data_introducida
	global se_puede_calcular
	global azimuts_distancias
	global coordenadas

	if texto_data_introducida != []:#Para que se trabaje con la nueva información en caso de que el usuario cambie de archivo.
		texto_data_introducida = []
		azimuts_distancias = []
		coordenadas = []
		cuandro_respuesta.delete("1.0", END)
		se_puede_calcular = True

	archivo = filedialog.askopenfilename(title="Seleccione txt", initialdir = "desktop", filetypes = (("Ficheros de Texto", "*.txt"), ("Todos los Ficheros", "*.*")))
	
	try:
		archivo = open(archivo, "r")
	
	except FileNotFoundError:
		archivo = False
		pass#Con un 'return' aqui las cosas se simplifican.

	archivo = archivo.readlines() if archivo else [] 
	
	for i in range(len(archivo)):
		linea = archivo[i]
		#print(linea)
		if linea.count(",") != 2:
			messagebox.showwarning("Formato Erroneo", "La linea No.{} no cumple con el formato csv, debe tener al menos dos comas.".format(i + 1))
			se_puede_calcular = False
			break
		
		else:
			linea = linea.split(",")
			if probar_formato(linea, i + 1):
				texto_data_introducida.append(linea)

			else:
				se_puede_calcular = False
				texto_data_introducida.append(linea)
				break	

	if not (len(texto_data_introducida) == 0):

		para_mostrar = "Se han introducido los siguientes datos: \n \n"

		for n, l in list(enumerate(texto_data_introducida, start = 1)):
			para_mostrar += "{}- {},{},{}".format(n, l[0], l[1], l[2])

		if se_puede_calcular == False:
			para_mostrar += " \n Por favor corrige el error, para poder realizar los calculos"

		cuandro_respuesta.insert(INSERT, para_mostrar)
		#print(texto_data_introducida)


def aviso_Instrucciones():
	#Muestra una ventana emergente con las intrucciones de uso del programa.
	#y deja un ejemplo de input en la pantalla. 
	global cuandro_respuesta
	texto = "Para usar este programa primero debe espesificar las coordenadas del Puto Base, use el comando 'ID' de AutoCAD y haga clic donde sea que desee que empieze a dibujarce la poligonal." 
	texto += "\n\nDespues use las coordenadas que aparezcan en la consola para llenar las casillas Este(x) y Norte(Y)."
	texto += "\n\nLuego, seleccione un archivo de texto (ejemplo.txt) con el siguiente fromato: cuadrante,rumbo,distancia."
	texto += "\n\nEjemplo: 1,35.20,50.42"
	texto += "\n\nEs un rumbo  N 35°20' E con una distancia de 50.42 metros."
	texto += "\n\nRecuerde que los cuadrantes son: 1 = NE, 2 = SE, 3 = SW\ny 4 = NW."
	texto += "\n\nObserve el ejemplo que hay en la pantalla."
	texto += "\n\nLuego de haberlo hecho pulse el botón que dice 'Calcular Coordenadas' e inmediatamete prodrá exportarlas en formato cvs dentro de un txt e impotarlas a AutoCAD."
	messagebox.showinfo("Instrucciones", texto)
	cuandro_respuesta.insert(INSERT, "\nEjemplo: \n\n2,85.20,100.15 \n4,52.45,40.84 \n3,65.42,150.82 \n1,83.32,100.45 \n\n")


def calcular_coordenadas():
	#Se encarga de calcular las coordenadas en base a los rumbos y distancias introducidos,
	#tomando como punto de partida el Punto Base.	
	global cuandro_respuesta
	global texto_data_introducida
	global coordenadas
	global se_puede_calcular
	global error_lineal_de_cierre
	global azimuts_distancias

	coordenadas = []# si las borro aqui no se acumulan al realizar varios calculos (que es lo que me parece mas logico).
	texto_mostrar = "\n \n Resultados: \n \n"

	if texto_data_introducida == []:
		messagebox.showwarning("No Hay Datos", "No se han cargado datos para realizar calculos.")

	elif se_puede_calcular == False:
		messagebox.showwarning("Hay Errores", "No se pueden hacer los calculos debido los errores que se informaron, por favor corrijalos y vuelva a intentar.")

	else:

		x = este.get()
		y = norte.get()
		#print(x, y)
		try:
			x = float(x)
			y = float(y)

		except ValueError:
			messagebox.showwarning('Error en las Coordenadas', "Procure que las coordenadas del Puto Base esten bien escritas.")
			return None#Esto es para terminar la ejecuion de la funcion y que no se lean las lineas siguientes.

		if abs(x) >= 10_000_000 or abs(y) >= 10_000_000:
			messagebox.showwarning('Coordenadas muy Altas', 'El uso de valores absolutos muy altos en las coordenadas puede causar errores en la ejcución del programa, por favor use valores menores de 10,000,000.')
			return None#esto es lo mismo que poner solo return.

		coordenadas.append((x, y))

		for i in range(len(texto_data_introducida) - 1):
			#Extraer la informacion:
			cuadrante = int(texto_data_introducida[i][0])
			grados = int(texto_data_introducida[i][1].split(".")[0])
			minutos = int(texto_data_introducida[i][1].split(".")[1])
			rumbo_en_decimales = grados + minutos/60
			distancia = float(texto_data_introducida[i][2])

			#Crear la linea y calcular las coordenadas:
			line = Linea(cuadrante, rumbo_en_decimales, distancia)
			coordenadas.append(line.calcular_coord_punto_final(x, y))
			azimuts_distancias.append((line.azimut, line.distancia))
			x = line.x_final
			y = line.y_final

		#Calcular el Error Lineal de Cierre:

		cuadrante_f = int(texto_data_introducida[len(texto_data_introducida) - 1][0])
		grados_f = int(texto_data_introducida[len(texto_data_introducida) - 1][1].split(".")[0])
		minutos_f = int(texto_data_introducida[len(texto_data_introducida) - 1][1].split(".")[1])
		rumbo_en_decimales_f = grados_f + minutos_f/60
		distancia_f = float(texto_data_introducida[len(texto_data_introducida) - 1][2])
			
		ultima_linea = Linea(cuadrante_f, rumbo_en_decimales_f, distancia_f)
		coordenadas.append(ultima_linea.calcular_coord_punto_final(coordenadas[len(coordenadas) - 1][0], coordenadas[len(coordenadas) - 1][1]))
		error_lineal_de_cierre = round(hypot(coordenadas[0][0] - coordenadas[len(coordenadas) - 1][0], coordenadas[0][1] - coordenadas[len(coordenadas) - 1][1]), 3)
		azimuts_distancias.append((ultima_linea.azimut, ultima_linea.distancia))

		#Mostrar resultados y avisar al usuario:
		for i in range(len(coordenadas)):
			texto_mostrar += "{}- E = {}, N = {} \n".format(i + 1, round(coordenadas[i][0], 3), round(coordenadas[i][1], 3))

		messagebox.showinfo("Calculos Completados", "Desliza hacia abajo para ver el resultado en la pantalla, ahora puedes exportar las coordenadas e impotar la poligonal a AutoCAD.")
			
		cuandro_respuesta.insert(INSERT, texto_mostrar)


def exportar_archivo():
	#Guarda las coordenadas no corregidas en un archivo txt.
	global coordenadas

	if len(coordenadas) == 0:
		messagebox.showwarning("No Hay Datos", "No hay datos que guardar.")
	else:	
		direccion_archivo = filedialog.asksaveasfilename(defaultextension = ".txt", filetypes = (("Ficheros de Texto", "*.txt"), ("Todos los Ficheros", "*.*")))
		archivo = open(direccion_archivo, "w")
		texto = ""

		for x, y in coordenadas:#Solo para recordar que se puede hacer esto con los for.
			texto += "{},{}\n".format(round(x, 3), round(y, 3))
			
		messagebox.showinfo("Coordenadas Exportadas", "La informacion ha sido guardada existosamente en: \n {} ".format(direccion_archivo))	
		archivo.write(texto)
		archivo.close()


def trazar_poligono(coords, elc, color, acad):
	#Traza el poligono en AutoCAD con puntos en cada uno de sus vertices y señala el Error Lineal de Cierra.

	para_pl = []

	for x, y in coords:
		acad.model.AddPoint(APoint(x, y)).Color = 7
		para_pl.append(x)
		para_pl.append(y)

	para_pl = aDouble(para_pl)
	nueva_polilinea = acad.model.AddLightWeightPolyline(para_pl)
	nueva_polilinea.Color = color
		
	try:
	#Puede que el programa se rompa al intentar asignar un tipo de linea que no este en las configuraciones.
		nueva_polilinea.LineType = "ACAD_ISO02W100"
	except:
		pass
	

	punto_inicial = APoint(coords[0][0], coords[0][1])
	punto_final = APoint(coords[len(coords) - 1][0], coords[len(coords) - 1][1])
	posicion_texto = APoint((punto_inicial.x + punto_final.x)//2 + 0.5, (punto_inicial.y + punto_final.y)//2 - 0.5) 

	if elc != None:
		text_E1 = acad.model.AddText("Error Lineal de Cierre = {} m".format(elc), posicion_texto, 0.5)
		text_E1.Color = 2
	else:
		text = acad.model.AddText('Poligonal Ajustada, Error Lineal de Cierre = 0.00 m', posicion_texto, 0.5)
		text.Color = 2


def bowditch_method(coordenadas, azimuts_distancias):
	#Esta función aplica el metod de correccion de la brujula o de bowditch a una poligonal descrita por sus rumbos y distancias.
	#Ir a la pagina 248 de la 11a. Edición del libro de Topografia de Paul R. Wolf y Charles D.Ghiliani para ver la explicación del metodo que se aplica aqui. 

	punto_base = [coordenadas[0][0], coordenadas[0][1]]
	coordenadas_corregidas = list()
	perimetro = sum([d for a, d in azimuts_distancias])
	proyecciones = list()

	#Desplazar el punto base en direccion este para evitar que las poligonales se corten:

	max_x = float('-inf')
	min_x = float('inf')

	for i in range(len(coordenadas)):
		
		if coordenadas[i][0] > max_x:
			max_x = coordenadas[i][0]

		if coordenadas[i][0] < min_x:
			min_x = coordenadas[i][0]

	
	#Sumar la diferencia de estas dos a la coordenada x del punto_base:

	punto_base[0] += (max_x - min_x)*1.05#Con un aumento del 5% para asegurar que esten separadas por mas del minimo.		

	#Ahora empieza el proceso de correccion:

	#1-Agregar el punto base a la lista de coordenadas corregidas:
	coordenadas_corregidas.append(tuple(punto_base))


	#2-Calcular las proyeciones:
	for i in range(len(azimuts_distancias)):
		proyec_x = azimuts_distancias[i][1] * sin(azimuts_distancias[i][0] * pi/180)
		proyec_y = azimuts_distancias[i][1] * cos(azimuts_distancias[i][0] * pi/180)
		proyecciones.append([proyec_x, proyec_y])

	#3-Cacular los errores en la proyeciones:
	error_x = sum([px for px, py in proyecciones])
	error_y = sum([py for px, py in proyecciones])

	#4-Usar estos errores para corregir las proyecciones y calcular las coordenadas corregidas en base a estas,
	#el Punto Base ira cambiando de valor conforma se vayan sumadno proyecciones para generar las coordenadas de la
	#poligonal corregida:

	for i in range(len(proyecciones)):
		punto_base[0] += proyecciones[i][0] + (error_x/perimetro)*azimuts_distancias[i][1]*(-1)
		punto_base[1] += proyecciones[i][1] + (error_y/perimetro)*azimuts_distancias[i][1]*(-1)
		coordenadas_corregidas.append(tuple(punto_base))
	
	return coordenadas_corregidas


def dibujar_resultados():
	#Ejecuta las funciones que dibujan los resultados en AutoCAD. 
	global coordenadas
	global error_lineal_de_cierre
	global azimuts_distancias
	
	if len(coordenadas) == 0:
		messagebox.showwarning("Sin Puntos", "No hay puntos que importar, por favor pulse el botón 'Calcular Coordenadas'.")
		return#Esto marca el fin de la ejecucion de la función

	else:
		acad = Autocad()

	#Comprobar que AutoCAD este abierto y con al menos una pestaña activa:
	try:
		acad.model.AddPoint(APoint(coordenadas[0][0], coordenadas[0][1], 0))

	except:
		messagebox.showwarning("Error de Conexión", "Ha Ocurrido un error al conectarce con AutoCAD, verifique que el programa este activo y que almenos una pestaña este abierta.")
		return#Esto causa que las demas lineas de codigo de esta función no se ejecuten.

	#llegados a este punto todo esta en orden para poder trazar las polilineas:

	trazar_poligono(coordenadas, error_lineal_de_cierre, 6, acad)

	coordenadas_corregidas = bowditch_method(coordenadas, azimuts_distancias)

	trazar_poligono(coordenadas_corregidas, None, 3, acad)

	messagebox.showinfo("Trazado Exitoso", "Las poligonales ha sido trazadas existosamente!")
	acad.prompt('Las parcelas recomputadas han sido trazadas con exito!')#Esto aparecera en la consola del AutoCAD.


#------------------------------------------------------Interfaces graficas-------------------------------------------------------------

#ver FONT OPTIONS en https://tcl.tk/man/tcl8.6/TkCmd/font.htm
fuente_titulo = Font(family = 'Helvetica', size = 11, weight = 'bold', slant = 'roman')
fuente_general = Font(family = 'Helvetica', size = 10)

label1 = Label(raiz, text = " Introduzca las Coordenadas del Punto Base: ")
label1.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
label1.config(font = fuente_titulo),

label2 = Label(raiz, text = "Este (X) = ", font = fuente_general)
label2.grid(row = 1, column = 0, padx = 3, pady = 5)

label3 = Label(raiz, text="Norte (Y) = ", padx = 3, pady = 5, font = fuente_general)
label3.grid(row = 2, column = 0)

entry1 = Entry(raiz, textvariable = este, font = fuente_general, borderwidth = 4)
entry1.grid(row = 1, column = 1)

entry2 = Entry(raiz, textvariable = norte, font = fuente_general, borderwidth = 4)
entry2.grid(row = 2, column = 1)

label4 = Label(raiz, text = "Pantalla:", font = Font(family = 'Helvetica', size = 10, weight = 'bold', underline = 1))
label4.grid(row = 3, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = "w")

cuandro_respuesta = Text(raiz, width = 60, height = 10, font = fuente_general, borderwidth = 4)#, size = 10))
cuandro_respuesta.grid(row = 4, column = 0, columnspan = 3, rowspan = 2)

scroll_vert = Scrollbar(raiz, command = cuandro_respuesta.yview)
scroll_vert.grid(row = 4, column = 3, sticky="nsew", rowspan = 2)
scroll_vert.config(cursor = 'double_arrow')
cuandro_respuesta.config(yscrollcommand = scroll_vert.set)

#----------------------------------------------------------------------Botones-----------------------------------------------------------------------------------

#Frame que contiene los botones del fondo.
frame_fondo = Frame(raiz)
#frame_fondo.config(bg = 'black')#Asignar un color al background es buena para visualizar el frame.
frame_fondo.grid(row = 6, column = 0, columnspan = 3, pady = 10, padx = 2)

#Padings y ancho comun para todos los botones"
padx = 3
pady = 3
ancho = 17

#Las ubicaciones de estos botones son respectivas al frame_fondo, no a la raiz.

boton_instrucciones = Button(frame_fondo, text = "Instrucciones", command = aviso_Instrucciones, font = fuente_general, width = ancho)
boton_instrucciones.grid(row = 0, column = 0, padx = padx, pady = pady)
boton_instrucciones.config(cursor = "question_arrow")

boton_cargar = Button(frame_fondo, text = "Cargar Archivo", command = cargar_archivo, font = fuente_general, width = ancho)
boton_cargar.grid(row = 0, column = 1, padx = padx, pady = pady)
boton_cargar.config(cursor = "hand2")

boton_exportar = Button(frame_fondo, text = "Exportar Coordenadas", command = exportar_archivo, font = fuente_general, width = ancho)
boton_exportar.grid(row = 0, column = 2, padx = padx, pady = pady)
boton_exportar.config(cursor = "hand2")

boton_calcular = Button(frame_fondo, text = "Calcular Coordenadas", command = calcular_coordenadas, font = fuente_general, width = ancho)
boton_calcular.grid(row = 1, column = 0, padx = padx, pady = pady)
boton_calcular.config(cursor = "hand2")

boton_borrar = Button(frame_fondo, text = "Limpiar Pantalla", command = borrar, font = fuente_general, width = ancho)
boton_borrar.grid(row = 1, column = 1, padx = padx, pady = pady)
boton_borrar.config(cursor = "hand2")

boton_dibujar = Button(frame_fondo, text = "Importar a AutoCAD", command = dibujar_resultados, font = fuente_general, width = ancho)
boton_dibujar.grid(row = 1, column = 2, padx = padx, pady = pady)
boton_dibujar.config(cursor = "hand2")

raiz.mainloop()	
