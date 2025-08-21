import pandas as pd
import numpy as np
import os
import time
from datetime import date
from google.colab import drive

drive.mount("/content/drive")
#Rutas del drive pa guardar el inventario...
Ruta_Inv_act =  "/content/drive/MyDrive/KIOSCO/Kiosco actual.csv"
Ruta_hist_dia = "/content/drive/MyDrive/KIOSCO/Historial_dia.csv"
Ruta_hist_total = "/content/drive/MyDrive/KIOSCO/Historial_mes.csv"
Ruta_inv_inicial = "/content/drive/MyDrive/KIOSCO/Kiosco inicial.csv"

#Fecha del dia.
Dia = date.today().strftime("%d-%m-%Y")

#Funcion  Reposicion, esto para saber cuando los productos estan por acabarse y hay que reponerlos
def actualizar_reposicion(df):
  Condiciones = [
    (df["Stock"] < 10),
    (df["Stock"] >= 10) & (df["Stock"] < 20),   #Las condiciones las puse al azar, despues analizo eso mjr.
    (df["Stock"] >= 20)
  ]
  Valores = ["Critico", "Medio", "Suficiente"]
  #me daba error sin el default, este sirve para si ninguna opcion cumple mis condiciones, su valor sera un texto vacio.
  df["Reposicion"] = np.select(Condiciones, Valores, default = "")
  return df


#Inventario cargar el dia anterior
if os.path.exists(Ruta_Inv_act): #Esto sirve si el inventario actual existe, usar este. s
  df = pd.read_csv(Ruta_Inv_act, encoding="latin-1") #Para que lea el excel de manera correcta
  #Reiniciar ventas y ingreos y el stock dejarlo en existencias inicales. para el inv del nuevo dia
  df["Existencias iniciales"] = df["Stock"]
  df["Ventas"] = 0
  df["Ingresos"] = 0
  df = actualizar_reposicion(df)
#En caso que no exista el arhcivo, significa que este es el 1ra dia usando el programa. lo que tiene que usar el excel inicial
else:
  df = pd.read_csv(Ruta_inv_inicial, encoding="latin-1")
  #Agregamos columans que no tiene el excel. para manejar mejor el inventario
  df["Ventas"] = 0

  #Esto es para calcular el stock
  df["Stock"] = df["Existencias iniciales"] - df["Ventas"]

  #Ingresos
  df["Ingresos"] = df["Ventas"] * df["Precio"]
  df = actualizar_reposicion(df)

def menu(df):
  while True: # bucle
    print("--------------------------------------------------------------------")
    print("Menu del inventario del Kiosco ")
    print("Opciones")
    print("1.- Ingresar ventas de productos")
    print("2.- Agregar stock de productos")
    print("3.- Mostrar inventario")
    print("4.- Cerrar caja")
    print("--------------------------------------------------------------------")
    opcion = input("Ingrese una opcion: ")
    if opcion == "1":
      producto = int(input("Ingrese el codigo del producto: "))
      if producto not in df["ID"].values:
        print("Producto no encontrado")
        continue
      cantidad = int(input("Ingrese la cantidad de productos: "))
      df.loc[df["ID"] == producto, "Ventas"] += cantidad
      df["Ingresos"] = df["Ventas"] * df["Precio"]
      df["Stock"] = df["Existencias iniciales"] - df["Ventas"]
      df = actualizar_reposicion(df)
      nombre = df.loc[df["ID"] == producto, "Nombre"].values[0]
      print(f"Se ha vendido {cantidad} productos de {nombre}.")
      #Falta agregar que si el numero de ventas es mayor al stock esta de un aviso.




    if opcion == "2":
      producto = int(input("Ingrese el codigo del producto: "))
      if producto not in df["ID"].values:
        print("Producto no encontrado")
        continue
      cantidad = int(input("Ingrese la cantidad a agregar al stock: "))
      df.loc[df["ID"] == producto, "Stock"] += cantidad
      df.loc[df["ID"] == producto, "Existencias iniciales"] += cantidad
      df = actualizar_reposicion(df)
      nombre = df.loc[df["ID"] == producto, "Nombre"].values[0]
      print(f"Se ha agregado {cantidad} productos de {nombre} al stock.")

    if opcion == "3":
      display(df.head(200))

    if opcion == "4":
      print("Cerrando caja...")
      for i in range(3):
        time.sleep(0.3)
        print("....")
      print(f"Resumen del dia {Dia}: ")
      ventas_totales = df["Ventas"].sum()
      ingresos_totales = df["Ingresos"].sum()
      Criticos = df[df["Reposicion"] == "Critico"] [["Nombre", "Stock", "Reposicion"]]
      print(f"Ventas totales del dia: {ventas_totales}")
      print(f"Ingresos totales del dia: {ingresos_totales}")
      print("Productos que necesitan reposicion para el proximo dia: ")
      print(Criticos)
      print("--------------------------------------------------------------------")
      break
      #poner un top de productos mas vendidos.
menu(df)


#Me falta agregar que cuando se cierre la caja, guarde todos los datos de ese dia en un excel a la mi capeta "KIOSCO" y que se cree uno nuevo para el siguiente dia.