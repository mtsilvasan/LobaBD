from ast import Global
from pickle import FALSE
from sys import builtin_module_names
from PIL import Image, ImageTk
from  itertools import combinations
import random as rd
from tkinter import ttk, messagebox
from tkinter.messagebox import askyesno
import tkinter as tk
import logging
import os
import time
import moduloBD as bd
import casaBD as cbd
import mesaBD as mbd
import sqlite3 
import sys


class Baraja():

    def barajar(self,conn):
        mylist =[]
        for i in range (0,108):            
            mylist.append(i)
        rd.shuffle(mylist)

        bd.barajar(mylist, conn)

    def repartir(self,cp,conn):
        result = bd.repartir(cp,conn)
        #print(str(result))
        i=0
        for res in result['Casa']:
            bot_casa[i].change_image(res[2])
            i+=1
        i=0    
        for res in result['Jugador']:
            bot_jug[i].change_image(res[3])
            i+=1

        btnmesa.change_image(result['Mesa'][3])
        resto.change_image(result['Color'][3])

        if cp == 'jug':
            actualizar_mensaje("Es tu turno!\n Ordena tus cartas, haciendo click en una carta y moviendola con los botones \nAtras y Adelante y cuando estes listo toma una carta del mazo o de la mesa")
        else:
            actualizar_mensaje("Juega el bot")
            time.sleep(1)            
            objCartasCasa.jugar()
        
class Mesa:
    def __init__(self): 
        self.ultTrica = 0
        self.ultEsca = 1

    def reset(self):
        self.__init__()

    def puntaje(self, quien):
        if quien == 'BOT':
            actualizar_mensaje("El bot gano la partida. Para continuar jugando presiona el boton Reiniciar")
            valor = int(pts_bot.cget("text"))
            valor =+1 
            pts_bot.config(text=valor)        
        else:    
            actualizar_mensaje("Ganaste la partida. Para continuar jugando presiona el boton Reiniciar")
            valor = int(pts_jug.cget("text"))
            valor =+1 
            pts_jug.config(text=valor)
        time.sleep(1)  

    def pintar_trica(self,de_quien,lista,conn):
        i = objMesa.ultTrica
        cartas = mbd.agregar_trica(de_quien,lista,i,conn)
        for t in cartas:
            bot_trica[i].change_image(t[3])
            i+=1
        objMesa.ultTrica = i
            
    def pintar_esca(self,lista,cual):
        """Funcion que solo pinta la escalera dponde corresponde
        ordena la lista antes de pintar, inclusive la ordena si tiene joker"""
        #print("lista es " + str(lista))
        ordered = sorted(lista, key=lambda carta: carta[-2]) 
        #li = mbd.agregar_trica_escalera('escalera',de_quien,lugares,cual,conn)
        #objMesa.escaleras.append(ordered)
        i=0
        for esc in ordered:
            mbd.agregar_escalera(esc,cual,conn)
            if cual == 1:
                bot_esca1[i].change_image(esc[3])    
            elif cual == 2:            
                bot_esca2[i].change_image(esc[3])    
            elif cual == 3:
                bot_esca3[i].change_image(esc[3])    
            else:
                bot_esca4[i].change_image(esc[3])    
            i+=1
                

    def grisar_todo(self):
        btnmesa.change_image("img/gris.png")
        for i in range(10):
            bot_casa[i].change_image("img/gris.png")
            bot_jug[i].change_image("img/gris.png")
        for i in range(18):
            bot_trica[i].change_image("img/fondo.png")
        for i in range(5):
            bot_esca1[i].change_image("img/fondo.png")
            bot_esca2[i].change_image("img/fondo.png")
            bot_esca3[i].change_image("img/fondo.png")
            bot_esca4[i].change_image("img/fondo.png")
            
    def evaluar_sope(self,quien,carta):
        esta = mbd.en_trica(carta,quien,conn)
        if esta:
            return ['Tricas']
        falta_esca = mbd.en_esca(carta,quien,conn)    
        if falta_esca[0]:
            return ['Escaleras',falta_esca[1]]
        else:
            falta_esca = mbd.en_esca1(carta,quien,conn)    
            if falta_esca[0]:
                return ['Escaleras',falta_esca[1]]
            else:    
                return ['Nada']    

    def grisar_cartas(self,de_quien):
        global check
        if de_quien == 'Jug':
            for i in range(10):
                bot_jug[i].change_image("img/gris.png")
                #juegos.check[i].set(True)  
                check[i].set(False) 
            lista = bd.obtener_imagenes('Jug',conn)  
            i=0 
            for li in lista:
                bot_jug[i].change_image(li)
                i+=1
        else:#casa
            for i in range(10):
                bot_casa[i].change_image("img/gris.png")
            lista = bd.obtener_imagenes('Casa',conn)  
            i=0 
            for li in lista:
                bot_casa[i].change_image(li)
                i+=1
            

class Juego:
    def __init__(self):
        self.current_player = 'jug'
        self.ronda = 1

    def reset(self):
        self.__init__()

    def flip_player(self):
        if self.current_player == 'bot':
            self.current_player = 'jug'
        elif self.current_player == 'jug':
            self.current_player = 'bot'

    def sigue_juego(self):
        if bd.cantidad('Jug',conn) >0 and bd.cantidad('Casa',conn) >0:        
            return True
        else:
            return False    
        


class JuegoCasa():
    def __init__(self): 
        pass


    def jugar(self):
        # debe organizar sus cartas al inicio y luego de bajar un juego
        #self.armar_juego()
        #debe validar si toma la carta de la mesa o la carta del mazo segun su juego
        bd.reordenar('Casa',conn)
        cbd.posibles_esca(conn)                    
        self.tomar_carta()

    def bajar_trica(self):
        tricas = cbd.obtener_tricas(conn)
        objMesa.pintar_trica('Casa',tricas,conn)
        bd.eliminar_varias('Casa',tricas,conn)
        
        bd.reordenar('Casa',conn)
        objMesa.grisar_cartas('Casa')  

    def bajar_esca(self):
        escaleras = cbd.obtener_escaleras(conn)
        #print("escaleras es" + str(escaleras))
        for e in escaleras:
            objMesa.pintar_esca(e,objMesa.ultEsca)
            objMesa.ultEsca += 1
        lugares = []
        for li in escaleras[0]:
            lugares.append(li[5])  
        #print("lista de luagres es " + str(lugares))    
        bd.eliminar_varias('Casa',lugares,conn)
        bd.reordenar('Casa',conn)
        objMesa.grisar_cartas('Casa')  
        
    def bajar_armadas(self):
        baje = False
        #si hay tricas hechas las bajo
        if bd.cantidad('Tricas', conn) > 0:            
            self.bajar_trica()
            baje = True
        if bd.cantidad('Escaleras', conn) > 0:            
            self.bajar_esca()
            baje = True

    def tomar_mazo(self):
        print("en tomar mazo " + str(bd.cantidad('Casa',conn)) )
        carta = bd.tomarCarta('Casa','mazo',conn)
        if bd.cantidad('Casa',conn) <=2:   
            self.sopar()
            self.botar()
        else:                
            #print("carta es " + str(carta))
            cant_cartas = bd.cantidad('Casa',conn) - 1
            bot_casa[cant_cartas].change_image(carta[2])
            cbd.eliminar_esc(conn)      
            cbd.posibles_esca(conn)
            time.sleep(0.5)        
            self.bajar_armadas()
            self.botar() 

    def tomar_carta(self):   
        carta = cbd.leer_mesa(conn)    
        if bd.cantidad('Casa',conn) <=2:   
            self.tomar_mazo()
        else:    
            li = cbd.sirve_para_bajar(carta, conn)
            #print("li es " + str(li))
            juego = li[0]
            indice = carta[4]
            #print("indice es "+ str(indice))
            if juego == "nada":
                self.tomar_mazo()
            elif juego == "escalera":
                #bd.pasar('Mesa','Casa',indice,conn)
                bd.obtener_imagen_mesa(conn)
                btnmesa.change_image(bd.obtener_imagen_mesa(conn))                                                
                carta = bd.tomarCarta('Casa','mesa',conn)
                cbd.eliminar_esc(conn)      
                cbd.posibles_esca(conn)
                self.bajar_esca()              
                self.bajar_armadas()
                self.botar()
            else: #trica
                bd.obtener_imagen_mesa(conn)
                btnmesa.change_image(bd.obtener_imagen_mesa(conn))
                #bd.pasar('Mesa','Casa',indice,conn)
                carta = bd.tomarCarta('Casa','mesa',conn)
                self.bajar_trica()
                self.bajar_armadas()
                self.botar()
            
    #def botar(self, donde, carta):
    def botar(self):  
        lista = cbd.tomar_descarte(conn)
        bd.eliminar('Casa',lista[0],conn)
        btnmesa.change_image(lista[1])
        bd.reordenar('Casa',conn)
        #cant = bd.cantidad('Casa',conn)
        objMesa.grisar_cartas('Casa')                                  
        cbd.eliminar_esc(conn)      
        if objJuego.sigue_juego():
            carta_jug = -1
            robo = False
            bajo = False  
            self.boto = False  
            objJuego.current_player = 'jug'
            objCartasJug.cambiar_estado("active")
            #la siguiente ya no sera la primera jugada
            #self.jugada =1
            time.sleep(0.5)
            actualizar_mensaje("Es tu turno, toma una casa de la mesa o del mazo ")
            objJuego.ronda +=1
            
        else:
            objMesa.puntaje('BOT')
            

    def sopar(self):
        cant = bd.cantidad('Casa',conn)
        if cant > 3:
            print("en if")
            juego = ['Nada']   
        else:    
            for i in range(0,cant):   
                if juego == ['Nada']:         
                    juego = objMesa.evaluar_sope('Casa',i) 
                    if juego[0]=='Tricas':
                        bd.eliminar('Casa',carta_jug,conn)                    
                        objMesa.grisar_cartas('Casa')                                  
                    elif juego[0]=='Escaleras': #es escalera
                        #self.cantCescaleras += 1
                        bd.eliminar('Casa',i,conn)
                        esca = mbd.devolver_esca(juego[1],conn)
                        objMesa.pintar_esca(esca, juego[1])
                        objMesa.grisar_cartas('Casa')  
                else:
                    sys.exit()                 
     
"""-------------------------------------hasta aca clase juego casa--------------------------------"""

class JuegoJug():
    def __init__(self):
        global cartasJug        
        self.cantCtricas = 0
        self.cantCescaleras = 0
        self.cantCsope = 0
        self.debe_bajar = False
        self.robo = False
        self.bajo = False
        self.ya_tomo = False
        self.tiro = True

    def reset(self):
        self.__init__()


    def robar(self):
        """
        esta permitido que el jugador tome la carta de la mesa si la va usar para bajar un juego
        """
        #global turnos, carta_jug, robo, bajo
        if objJuego.sigue_juego():
            if objJuego.current_player == 'jug':
                cant_cartas = bd.cantidad('Jug',conn)
                if cant_cartas ==10:
                    messagebox.showinfo(title="Loba 1.0", message="No puede tomar la carta de la mesa, ya tiene 10 cartas") 
                    actualizar_mensaje("No puede tomar la carta de la mesa, ya tiene 10 cartas") 
                else:
                    if (not self.ya_tomo or not self.robo):
                        self.robo = True
                        carta = bd.tomarCarta('Jug','mesa',conn)
                        bot_jug[cant_cartas].change_image(carta[3])
                        #si toma la carta el jugador debe bajar un juego
                        self.bajo = False
                        #inicializa la variable para senalar la carta marcada
                        carta_jug = -1
                        #habilito el check del jugador en su carta numero 10
                        juegos[9].config(state="normal") 
                        #habilito todos los checks
                        for i in range (10):
                            juegos[i].config(state="normal")

                        if bd.cantidad('Mesa',conn) == 0:
                            #tomo la unica carta de la mesa
                            btnmesa.change_image("img/gris.png")
                        else:
                            bd.obtener_imagen_mesa(conn)
                            btnmesa.change_image(bd.obtener_imagen_mesa(conn))                                                
                    self.debe_bajar = True
                    self.tiro = False
                    actualizar_mensaje("Debes bajar un juego y luego descartar una carta")       
        

    def tomar(self):
        global carta_jug
        #global turnos, carta_jug, ya_tomo
        if objJuego.sigue_juego():
            if objJuego.current_player == 'jug':
                if self.tiro:
                    if not self.ya_tomo and not self.robo:
                        #se setea la variable que ya tomo una carta en True
                        self.ya_tomo = True 
                        self.tiro = False
                        carta = bd.tomarCarta('Jug','mazo',conn)
                        cant_cartas = bd.cantidad('Jug',conn)
                        bot_jug[cant_cartas-1].change_image(carta[3])
                        #inicializa la variable para senalar la carta marcada
                        carta_jug = -1
                        if objJuego.ronda == 1:
                            #habilito el check del jugador en su carta numero 10
                            juegos[9].config(state="normal") 
                            #habilito todos los checks
                            for i in range (10):
                                #juegos[i].state(['!selected'])
                                juegos[i].config(state="normal")
                        actualizar_mensaje("Baja un juego si lo deseas o presiona el mouse sobre la carta que descartaras\n y presiona el boton Basura")
                else:
                    actualizar_mensaje("ya tomaste la carta que te corresponde en este turno, debes desechar una carta ")
        else:
            messagebox.showinfo(title="Loba 1.0", message="No puede tomar la carta, la partida ya finalizo") 

    def sopar(self):
        if objJuego.current_player == 'jug':
            if self.puedeBajar("sopar"):
                if carta_jug == -1:
                    messagebox.showinfo(title="Loba 1.0", message="Seleccione una carta para sopar")
                    actualizar_mensaje("Seleccione una carta para sopar")   
                else:
                    juego = objMesa.evaluar_sope('Jug',carta_jug)   
                    if juego[0]=='Tricas':
                        bd.eliminar('Jug',carta_jug,conn)
                        self.cantCsope +=1
                        self.bajo = True
                        objMesa.grisar_cartas('Jug')                                  
                    elif juego[0]=='Escaleras': #es escalera
                        self.cantCsope +=1
                        bd.eliminar('Jug',carta_jug,conn)
                        esca = mbd.devolver_esca(juego[1],conn)
                        objMesa.pintar_esca(esca, juego[1])
                        self.bajo = True
                        objMesa.grisar_cartas('Jug')                              
                    else:    
                        messagebox.showinfo(title="Loba 1.0", message="No puede sopar esa carta")
        

    def cambiar_estado(self,estado):
        for i in range (10):
            juegos[i].config(state=estado)
            bot_jug[i].config(state=estado)
        atras.config(state=estado)
        adel.config(state=estado)
        btnmesa.config(state=estado)
        resto.config(state=estado)
        descarte.config(state=estado)
        botar.config(state=estado)
        self.robo = False
        self.ya_tomo = False
        if estado == "disabled":
            actualizar_mensaje("Es el turno del bot")
        else:
            actualizar_mensaje("Es tu turno")    

    def devolver(self):
        global carta_jug,check
        """ Si el jugador tomo una carta de la mesa y no pudo bajar un juego,
        la carta debe ser devuelta a la mesa"""
        carta_mesa = bd.traer_carta('Jug','ultima',conn)
        bd.pasar('Jug','mesa',carta_mesa[5],conn)
        #se muestra el anverso de la carta para la carta de la mesa
        btnmesa.change_image(carta_mesa[3])            
        bot_jug[bd.cantidad('Jug',conn)].change_image("img/gris.png")
        carta_jug = -1
        self.robo = False
        for i in range(10):
            check[i].set(False)

    def puedeBajar(self, mensaje):
        """Funcion que devuelve true si la suma de cartas del jugador 
        entre las que tiene en mesa y las que bajo son 10
        """
        cant = bd.cantidad('Jug',conn)
        if cant + self.cantCtricas + self.cantCescaleras +self.cantCsope == 10:    
            return True
        else:
            print("cant ctricas es " + str(self.cantCtricas))
            print("cant esca" + str(self.cantCescaleras))
            print("cant sope" + str(self.cantCsope))
            print("cant jug en puede bajar es" + str(cant))
            messagebox.showinfo(title="Loba 1.0", message="Para " + mensaje + " debes tomar una carta antes")

    def marcadas(self):
        #global selected
        selected = []
        for c in check:
            selected.append(c.get())
        ind = [indice for indice, dato in enumerate(selected) if dato == 1]
        #for x, n in enumerate( check ):
            #selected.append( n.get() )
        #if selected.count(1)>= 3:
        if len(ind) >= 3:
            return True
        else:
            messagebox.showinfo(title="Loba 1.0", message="Deben haber al menos tres cartas para bajar")
        return False    

    def juegoValido(self):
        """
        Funcion que determina si con las cartas marcadas se puede hacer una trica o una escalera"""
        selected = []
        for c in check:
            selected.append(c.get())
        ind = [indice for indice, dato in enumerate(selected) if dato == 1]
        #posible_juego =[]
        cant = 0
        for i in ind:
            #en posible juego quedan las cartas marcadas por el jugador
            bd.agregar_posible_juego(i,conn)
            cant+=1
        if cant >= 3:
            #puede ser trica o escalera
            res = bd.esEscalera(conn)
            if res[0]:
                return("escalera",res[1])
            else:    
                res = bd.esTrica(conn)
                if res[0]:
                    return("trica",ind)
                else:
                    return([],"nada",[]) 
        else:               
            return([],"nada",[])         

    def bajar(self):
        global check
        """Funcion que es llamada desde el boton bajar presionado por el jugador"""
        if objJuego.current_player == 'jug':
            if self.puedeBajar("bajar"):
                if self.marcadas():
                    juego = self.juegoValido()
                    if self.debe_bajar and juego[0]==[]:
                            messagebox.showinfo(title="Loba 1.0", message="No es un juego valido, la carta tomada de la mesa sera devuelta")
                            self.devolver()
                            self.debe_bajar = False
                    else:
                        if juego[0]=="trica":
                            objMesa.pintar_trica('Jug',juego[1],conn)
                            #elimino las cartas del juego del 
                            bd.eliminar_varias('Jug',juego[1],conn)
                            #las cartas q componen la trica debeb quedar en gris
                            self.cantCtricas +=3  
                            self.bajo = True
                            bd.reordenar('Jug',conn)
                            objMesa.grisar_cartas('Jug')  
                        elif juego[0]=="escalera": #es escalera
                            lista = juego[1]                            
                            self.cantCescaleras += len(lista)
                            lugares = []
                            for li in lista:
                                lugares.append(li[5])                            
                            objMesa.pintar_esca(lista, objMesa.ultEsca)#, lugares) 
                            objMesa.ultEsca += 1
                            bd.eliminar_varias('Jug',lugares,conn)
                            #las cartas q componen la trica debeb quedar en gris                            
                            self.bajo = True
                            bd.reordenar('Jug',conn)
                            objMesa.grisar_cartas('Jug') 
                            #falta agregar ca cantidad de cartas q componen la escalera a self.escaleras
                        #falta eliminar las cartas de las cartas del jugador
                        #falta desmarcar o deshabilitar los check del jugador
                        
                        else:    
                            for i in range(10):
                                #desmarco los check
                                check[i].set(False)
                            bd.borrar_posibles(conn)    
                            messagebox.showinfo(title="Loba 1.0", message="No es un juego valido")
                        if self.debe_bajar:
                            self.debe_bajar = False    

    def botar(self):
        global carta_jug
        if "img/gris.png" in bot_jug[0].image_path:
            messagebox.showinfo(title="Loba 1.0", message="Aun no puede desechar, no ha iniciado el juego")
            actualizar_mensaje("Aun no puede desechar, no ha iniciado el juego")
        else:
            if not self.ya_tomo and not self.robo:
                messagebox.showinfo(title="Loba 1.0", message="No puede desechar una carta sin tomar una previamente")
                actualizar_mensaje("No puede desechar una carta sin tomar una previamente")   
            elif self.tiro:
                messagebox.showinfo(title="Loba 1.0", message="Ya tiro una carta en esta ronda")                                
            else:
                if carta_jug == -1:
                    messagebox.showinfo(title="Loba 1.0", message="Seleccione una carta para desecharla")
                    actualizar_mensaje("Seleccione una carta para desecharla")   
                else:
                    if (self.robo == False and self.ya_tomo == True) or (self.robo and self.bajo):
                        btnmesa.change_image(bot_jug[carta_jug].image_path)
                        bd.eliminar('Jug',carta_jug,conn)
                        bd.reordenar('Jug',conn)
                        cant = bd.cantidad('Jug',conn)
                        for i in range (carta_jug,cant):    
                            bot_jug[i].change_image(bot_jug[i+1].image_path) 
                        bot_jug[cant].change_image("img/gris.png")
                        if objJuego.sigue_juego():
                            carta_jug = -1  
                            objJuego.current_player = 'bot'  
                            #deshabilito lo correspondiente al jugador
                            self.cambiar_estado("disabled")
                            self.ya_tomo = False
                            self.robo=False
                            objCartasCasa.jugar()
                            self.tiro = True
                        else:
                            messagebox.showinfo(title="Loba 1.0", message="Ganaste la partida!")
                            objMesa.puntaje('jug')
                            #aumentar el puntaje del jugador
                    else: #robo y no bajo
                        #debe devolver    
                        messagebox.showinfo(title="Loba 1.0", message="Toma una carta de la mesa y no bajo un juego, la carta tomada de la mesa sera devuelta")
                        self.devolver()

    
#inicio del juego
def resetear_objetos():
    global  objMesa,  objCartasJug, objJuego
    objMesa.reset()
    objJuego.reset()
    objCartasJug.reset()

def ini():
    global  objBaraja, objMesa, objCartasCasa, objCartasJug, objJuego
    objCartasCasa = JuegoCasa()
    objCartasJug = JuegoJug()    
    objBaraja = Baraja() 
    objMesa = Mesa()
    objJuego = Juego()

def iniciar():  

    objBaraja.barajar(conn)
    
    bd.borrar(conn)
    objMesa.grisar_todo()
    #inicializo el juegop de la casa, el juego del jugador y la mesa
    #las 9 cartas quedan en las listas de cartas de la casa y del jugador
    objJuego.current_player = 'jug'
    objBaraja.repartir(objJuego.current_player,conn)
    
def rein():
    global  objCartasCasa, objCartasJug
    resetear_objetos()
    iniciar()        

def reiniciar():  

    global  objBaraja, objMesa, objCartas,objBasicos, objCartasCasa, objCartasJug, objJuego

    print("en reiniciar")
    if bd.cantidad('Casa',conn) >0 and bd.cantidad('Jug',conn) > 0:
        answer = askyesno(title='Confirmación',message='Hay un juego en curso, deseas empezar de nuevo?')
        if answer:
            rein()            
    else:            
        rein()
        
    
def mover_atras():
    global carta_jug
    if carta_jug == -1:
        messagebox.showerror(title="Error", message="Debe seleccionar la carta que desa mover y luego presionar el boton para mover hacia la izquierda")
    else:
        if carta_jug-1 == -1:
            messagebox.showerror(title="Error", message="La carta no se puede mover a la izquierda ")
        else:
            imagen = bot_jug[carta_jug-1].image_path
            bot_jug[carta_jug-1].change_image(bot_jug[carta_jug].image_path)    
            bot_jug[carta_jug].change_image(imagen)  
            #juegos[carta_jug].toggle()  
            bd.trueque(carta_jug,'atras',conn)
            carta_jug = carta_jug-1
            #juegos[carta_jug].toggle()  
            

def mover_adelante():
    global carta_jug
    if carta_jug == -1:
        messagebox.showerror(title="Error", message="Debe seleccionar la carta que desa mover y luego presionar el boton para mover hacia la derecha")
    else:
        if carta_jug+1 == 9:
            messagebox.showerror(title="Error", message="La carta no se puede mover a la derecha")
        else:
            imagen = bot_jug[carta_jug+1].image_path
            bot_jug[carta_jug+1].change_image(bot_jug[carta_jug].image_path)    
            bot_jug[carta_jug].change_image(imagen)
            #juegos[carta_jug].toggle()  
            bd.trueque(carta_jug,'adelante',conn)
            carta_jug = carta_jug+1
            #juegos[carta_jug].toggle()  
            

def guardar_ultima(num):
        global bot_jug
        """Guarda el indice de la carta del jugador en la cual hace click"""
        global carta_jug
        carta_jug = num
        
def terminar():
    messagebox.showerror(title="Error", message="Se cerrara la ventana de juego")
    bd.borrar(conn)
    
    ventana.destroy() 
    conn.close()     

def ayuda():
    mensaje = """1- Se reparten 9 cartas a cada jugador dejando una dada vuelta al final.
    2- Se pueder realizar tricas y escaleras 
    3- Para iniciar un turno se levanta una carta del mazo.
    4- Si el jugador tiene un juego puede dejarlo sobre la mesa a la vista de todos (si el jugador lo desea).
    5- Si hay otros juegos sobre la mesa se puede "sopar" o sea agregar más cartas a un juego.
    6- Se cierra el turno tirando una carta.
    7- Para poder levantar una carta de las cartas desechadas se debe bajar el juego en la mesa.
    8- Gana la partida el jugador que se quede sin cartas en la mano."""
    messagebox.showinfo(title="Loba 1.0", message=mensaje)

def actualizar_mensaje(mnsj):
   mensaje["text"] = mnsj    
   
class ImageButton(tk.Button):
    def __init__(self, parent, image_path=None, *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)
        self.logger = logging.getLogger('main.ImageButton')
        ch = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] <%(name)s>: %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self._image_path = None
        self._image = None
        self.image_path = image_path

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, path):
        path = os.path.abspath(path)
        try:
            self._image = tk.PhotoImage(file=path)
            self.config(image=self._image)
            self._image_path = path
        except tk.TclError:
            self.logger.warn("No se pudo cargar la imagen desde '{}'".format(path))
    
    def change_image(self,imagen):    
        self.image_path = imagen

    

ventana = tk.Tk()

ventana.title('Loba 1.0')
ventana.geometry('1425x900')
ventana['bg'] = '#eaeded'

ini()


conn = sqlite3.connect("loba.db")

tk.Frame(ventana)

#scrollbar = tk.Scrollbar(ventana)
#scrollbar.grid(row=0,column=1,sticky="nwes")

#checks para los juegos
juegos = [None] * 10
check = [] 
for k in range(10):
    check.append( tk.IntVar(ventana, value = 0) )
    juegos[k] = tk.Checkbutton(ventana, text="",state="disabled", variable=check[k], onvalue=1, offvalue=0)
    juegos[k].grid(padx=0, pady=0, row=0, column=k) 

#botones para las cartas del jugador
bot_jug = [None] * 10 
for j in range(10):
    bot_jug[j] = ImageButton(ventana,image_path="img/gris.png",text=j,state="active")#lambda e, n=i: self.button_click(n))
    bot_jug[j].grid(padx=0.1, pady=0.1, row=1, column=j) 
    bot_jug[j].bind('<Button-1>', lambda e: guardar_ultima(e.widget.cget('text')))
    #bot_jug[j] = tk.Frame(ventana, highlightbackground = "red", highlightthickness = 5, bd=0)

#botones para la mesa y el resto de la baraja
btnmesa = ImageButton(ventana,image_path="img/gris.png",text="",command=objCartasJug.robar) 
btnmesa.grid(row=2, column=2, columnspan = 3) 
resto = ImageButton(ventana,image_path="img/gris.png",text="",command=objCartasJug.tomar) 
resto.grid(row=2, column=6)    

#botones para las cartas de la casa
bot_casa = [None] * 10 
for i in range(10):
    bot_casa[i] = ImageButton(ventana,image_path="img/gris.png",text="",state="disabled")#lambda e, n=i: self.button_click(n))
    bot_casa[i].grid(padx=0.1, pady=0.1, row=3, column=i)  

#botones para las tricas
bot_trica = [None] * 18 

for i in range(9):
    bot_trica[i] = ImageButton(ventana,image_path="img/fondo.png",text="",state="disabled",borderwidth=0)#lambda e, n=i: self.button_click(n))
    #bot_trica[i] = tk.Frame(ventana, highlightbackground = "#eaeded", highlightthickness = 2, bd=0)
    bot_trica[i].grid(padx=0.1, pady=0.1, row=4, column=i)  
for i in range(9):
    bot_trica[i+9] = ImageButton(ventana,image_path="img/fondo.png",text="",state="disabled",borderwidth=0)#lambda e, n=i: self.button_click(n))
    #bot_trica[i+9] = tk.Frame(ventana, highlightbackground = "#eaeded", highlightthickness = 2, bd=0)
    bot_trica[i+9].grid(padx=0.1, pady=0.1, row=5, column=i)      

#botones para las escaleras

bot_esca1 = [None] * 5
for i in range (5):
    bot_esca1[i] = ImageButton(ventana,image_path="img/fondo.png",text="",state="disabled",borderwidth=0)#lambda e, n=i: self.button_click(n))
    #bot_esca1[i] = tk.Frame(ventana, highlightbackground = "#eaeded", highlightthickness = 2, bd=0)
    bot_esca1[i].grid(padx=0.1, pady=0.1, row=i+1, column=10)  
bot_esca2 = [None] * 5
for i in range (5):
    bot_esca2[i] = ImageButton(ventana,image_path="img/fondo.png",text="",state="disabled",borderwidth=0)#lambda e, n=i: self.button_click(n))
    #bot_esca2[i] = tk.Frame(ventana, highlightbackground = "#eaeded", highlightthickness = 2, bd=0)
    bot_esca2[i].grid(padx=0.1, pady=0.1, row=i+1, column=11)  
bot_esca3 = [None] * 5
for i in range (5):
    bot_esca3[i] = ImageButton(ventana,image_path="img/fondo.png",text="",state="disabled",borderwidth=0)#lambda e, n=i: self.button_click(n))
    #bot_esca3[i] = tk.Frame(ventana, highlightbackground = "#eaeded", highlightthickness = 2, bd=0)
    bot_esca3[i].grid(padx=0.1, pady=0.1, row=i+1, column=12)
bot_esca4 = [None] * 5
for i in range (5):
    bot_esca4[i] = ImageButton(ventana,image_path="img/fondo.png",text="",state="disabled",borderwidth=0)#lambda e, n=i: self.button_click(n))
    #bot_esca4[i] = tk.Frame(ventana, highlightbackground = "#eaeded", highlightthickness = 2, bd=0)
    bot_esca4[i].grid(padx=0.1, pady=0.1, row=i+1, column=13)  

#boton para descartar
img0 = ImageTk.PhotoImage(Image.open('img/basura.png'))
descarte = tk.Button(ventana,image=img0, command=objCartasJug.botar) 
descarte.grid(row=2, column=7) 
#boton para sopar
imgSo = ImageTk.PhotoImage(Image.open('img/sopar.png'))
sopar = tk.Button(ventana,image=imgSo, command=objCartasJug.sopar) 
sopar.grid(row=2, column=8)
#boton para bajar jugadas
img1 = ImageTk.PhotoImage(Image.open('img/bajar.png'))
botar = tk.Button(ventana,image=img1, command=objCartasJug.bajar) 
botar.grid(row=2, column=9) 

#boton para mover hacia atras
img4 = ImageTk.PhotoImage(Image.open('img/atras.png'))
atras = tk.Button(ventana,image=img4, command=mover_atras) 
atras.grid(row=2, column=1)
#boton para mover hacia adelante
img5 = ImageTk.PhotoImage(Image.open('img/adelante.png'))
adel = tk.Button(ventana,image=img5, command=mover_adelante) 
adel.grid(row=2, column=2)

img = ImageTk.PhotoImage(Image.open('img/play.png'))
jugar = tk.Button(ventana,image=img, command=iniciar) 
jugar.grid(row=6, column=0) 
img2 = ImageTk.PhotoImage(Image.open('img/replay.png'))
repetir = tk.Button(ventana,image=img2, command=reiniciar) 

repetir.grid(row=6, column=1) 
img3 = ImageTk.PhotoImage(Image.open('img/exit.png'))
salir = tk.Button(ventana,image=img3, command=terminar) 
salir.grid(row=6, column=2) 

img6 = ImageTk.PhotoImage(Image.open('img/ayuda.png'))
ayuda = tk.Button(ventana,image=img6, command=ayuda) 
ayuda.grid(row=6, column=3)

mensaje = tk.Label(ventana,text="Presiona Play para iniciar el juego")
mensaje.grid(row=6,column=4, columnspan = 7, sticky="w")
mensaje.config(font=('Arial', 14),fg="red")

bot = tk.Label(ventana,text="BOT:")
bot.grid(row=6,column=10)
bot.config(font=('Arial', 24),fg="red") #Cambiar tipo y tamaño de fuente
jug = tk.Label(ventana,text="Jugador:")
jug.grid(row=6,column=12)
jug.config(font=('Arial', 24),fg="red") #Cambiar tipo y tamaño de fuente

pts_bot = tk.Label(ventana,text="0")
pts_bot.grid(row=6,column=11)
pts_bot.config(font=('Arial', 24),fg="red")
pts_jug = tk.Label(ventana,text="0")
pts_jug.grid(row=6,column=13)
pts_jug.config(font=('Arial', 24),fg="red")

ventana.mainloop()   