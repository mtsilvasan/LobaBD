
def barajar(lista,conn):
    cursor = conn.cursor() 
    i=0 
    for l in lista:
        sql = "UPDATE mazo SET  barajado=%s " \
                      "WHERE id=%s" % (l,i)
    
        i+=1
        try:
        # Execute the SQL command
            cursor.execute(sql)
            conn.commit()
        except:
        # Rollback in case there is any error
            conn.rollback()

def repartir(cp,conn):
    casa = []
    jugador = []
    mesa = []
    color = []
    cursor = conn.cursor() 
    if cp == 'jug':
        j = 0
        k = 0
        for i in range(0,18):
            if i % 2 != 0:
                sql1 = "INSERT INTO cartas_jugador ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, %s " \
                    "FROM mazo WHERE  barajado  = %s" % (j,i)         
                cursor.execute(sql1)
                j+=1
            else:    
                sql2 = "INSERT INTO cartas_casa ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, %s " \
                    "FROM mazo WHERE  barajado  = %s " % (k,i)         
                cursor.execute(sql2)
                k=+1
            sql = "UPDATE mazo SET estado = 1 WHERE barajado  = %s " % (i)                                 
            cursor.execute(sql)             
    else:
        j=0
        k=0
        for i in range(0,18):
            if i % 2 != 0:
                sql1 = "INSERT INTO cartas_casa ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, %s " \
                    "FROM mazo WHERE  barajado  = %s " % (j,i)         
                cursor.execute(sql1)
                j+=1
            else:    
                sql2 = "INSERT INTO cartas_jugador ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, %s " \
                    "FROM mazo WHERE  barajado  = %s " % (k,i)         
                cursor.execute(sql2)
                k+=1
            sql = "UPDATE mazo SET estado = 1 WHERE barajado  = %s " % (i)                                 
            cursor.execute(sql)  
            j+=1          
    cursor.execute("INSERT INTO mesa ( valor, palo, color, imagen, orden)  SELECT valor, palo, color, imagen, orden FROM mazo WHERE  barajado  = 19 ")
    cursor.execute("UPDATE mazo SET estado = 1 WHERE barajado  = 19 ")
    conn.commit()   

    cursor.execute("SELECT * from cartas_casa")
    for row in cursor:
        casa.append(tuple(row))

    cursor.execute("SELECT * from cartas_jugador")
    for row in cursor:
        jugador.append(tuple(row))    

    cursor.execute("SELECT * from mesa")
    mesa = tuple(cursor.fetchone())

    cursor.execute("SELECT * from mazo WHERE barajado = 20")
    color = cursor.fetchone()           
    return {'Casa':casa, 'Jugador':jugador, 'Mesa': mesa, 'Color': color}   

def cantidad(donde, conn):
    cursor = conn.cursor() 
    if donde == 'Casa':
        cursor.execute("SELECT count(*) from cartas_casa")
        return cursor.fetchone()[0]
    elif donde == 'Jug':
        cursor.execute("SELECT count(*) from cartas_jugador")
        return cursor.fetchone()[0]    
    elif donde == 'Mesa':     
        cursor.execute("SELECT count(*) from mesa")
        return cursor.fetchone()[0]
    elif donde == 'Tricas':    
        cursor.execute("SELECT count(*) from tricas")
        return cursor.fetchone()[0]
    elif donde == 'Escaleras':
        cursor.execute("SELECT count(*) from escaleras")
        return cursor.fetchone()[0]
    elif donde == 'Joker':
        cursor.execute("SELECT count(*) from jokers")
        return cursor.fetchone()[0]    
    elif donde == 'cora':
        cursor.execute("SELECT count(*) from cora")
        return cursor.fetchone()[0]    
    elif donde == 'treb':
        cursor.execute("SELECT count(*) from treb")
        return cursor.fetchone()[0]    
    elif donde == 'bast':
        cursor.execute("SELECT count(*) from bast")
        return cursor.fetchone()[0]    
    elif donde == 'romb':
        cursor.execute("SELECT count(*) from romb")
        return cursor.fetchone()[0] 
    elif donde == 'Joker_Casa':
        cursor.execute("SELECT count(*) from cartas_casa where valor = 'Joker'")
        return cursor.fetchone()[0] 
    
def tomarCarta(quien,de_donde,conn):
    cursor = conn.cursor() 
    if quien == 'Jug':
        if de_donde == 'mazo':
            cursor.execute("INSERT INTO cartas_jugador ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, (select max(lugar) from cartas_jugador) + 1 FROM mazo WHERE  barajado = (select min(barajado) from mazo where estado = 0)") 
            cursor.execute("UPDATE mazo SET estado = 1 WHERE barajado  = (select min(barajado) from mazo where estado = 0) ")
            cursor.execute("SELECT * FROM cartas_jugador WHERE ID = (SELECT MAX(ID)  FROM cartas_jugador)")
            carta = cursor.fetchone()
        else:#mesa   
            cursor.execute("INSERT INTO cartas_jugador ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, (select max(lugar) from cartas_jugador) + 1 FROM mesa WHERE ID = (SELECT MAX(ID)  FROM mesa)")
            cursor.execute("DELETE FROM mesa WHERE ID = (SELECT MAX(ID)  FROM mesa) ") 
            #hay q borrar la ultima de la mesa
            cursor.execute("SELECT * FROM cartas_jugador WHERE ID = (SELECT MAX(ID)  FROM cartas_jugador)")
            carta = cursor.fetchone()
    else:#casa:            
        if de_donde == 'mazo':
            cursor.execute("INSERT INTO cartas_casa ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, (select max(lugar) from cartas_casa) + 1 FROM mazo WHERE  barajado = (select min(barajado) from mazo where estado = 0)") 
            cursor.execute("UPDATE mazo SET estado = 1 WHERE barajado  = (select min(barajado) from mazo where estado = 0) ")
            cursor.execute("SELECT * FROM cartas_casa WHERE ID = (SELECT MAX(ID)  FROM cartas_casa)")
            carta = cursor.fetchone()
        else:#mesa           
            cursor.execute("INSERT INTO cartas_casa ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, (select max(lugar) from cartas_casa) + 1 FROM mesa WHERE ID = (SELECT MAX(ID)  FROM mesa)")
            cursor.execute("DELETE FROM mesa WHERE ID = (SELECT MAX(ID)  FROM mesa) ") 
            #hay q borrar la ultima de la mesa        
            cursor.execute("SELECT * FROM cartas_casa WHERE ID = (SELECT MAX(ID)  FROM cartas_casa)")
            carta = cursor.fetchone()
    conn.commit()
    return carta

def pasar(de_donde,a_donde,que_carta,conn):
    cursor = conn.cursor() 
    if de_donde == 'Jug':
        if a_donde == 'mesa':
            sql2 = "INSERT INTO mesa ( valor, palo, color, imagen, orden)  SELECT valor, palo, color, imagen, orden FROM cartas_jugador WHERE ID= %s " % (que_carta)
            cursor.execute(sql2) 
            sql = "DELETE FROM cartas_jugador WHERE ID = %s " % (que_carta)
            cursor.execute(sql)
    elif de_donde == 'Mesa':
        if a_donde == 'Casa':
            lu = cantidad('Casa',conn) - 1
            sql2 = "INSERT INTO cartas_casa ( valor, palo, color, imagen, orden, lugar)  SELECT valor, palo, color, imagen, orden, %s FROM mesa WHERE ID= %s " % (lu,que_carta)
            cursor.execute(sql2) 
            sql = "DELETE FROM mesa WHERE ID = %s " % (que_carta)
            cursor.execute(sql)        
    conn.commit()

def traer_carta(de_donde,que_carta,conn):
    cursor = conn.cursor() 
    if que_carta == "ultima":
        if de_donde == 'Jug':
            cursor.execute("SELECT * FROM cartas_jugador WHERE ID = (SELECT MAX(ID)  FROM cartas_jugador)")
            carta = cursor.fetchone()
        elif de_donde == 'Casa':
            cursor.execute("SELECT * FROM cartas_casa WHERE ID = (SELECT MAX(ID)  FROM cartas_casa)")
            carta = cursor.fetchone()
    return carta        


def eliminar(de_donde,que_carta,conn):
    cursor = conn.cursor() 
    if de_donde == 'Jug':
        #elimino de las cartas del jugador 
        #agrego a las cartas de la mesa
        sql = "INSERT INTO mesa (valor, palo, color, imagen, orden) SELECT valor, palo, color, imagen, orden FROM cartas_jugador WHERE lugar = %s " % (que_carta)   
        cursor.execute(sql)
        sql = "DELETE FROM cartas_jugador WHERE lugar = %s " % (que_carta)                                 
        cursor.execute(sql)
        sql = "UPDATE cartas_jugador SET lugar = lugar -1 WHERE lugar > %s " % (que_carta)                                 
        cursor.execute(sql)
    else:
        sql = "INSERT INTO mesa (valor, palo, color, imagen, orden) SELECT valor, palo, color, imagen, orden FROM cartas_casa WHERE lugar = %s " % (que_carta)   
        cursor.execute(sql)
        sql = "DELETE FROM cartas_casa WHERE lugar = %s " % (que_carta)                                 
        cursor.execute(sql)
        sql = "UPDATE cartas_casa SET lugar = lugar -1 WHERE lugar > %s " % (que_carta)                                 
        cursor.execute(sql)
    conn.commit()

def agregar_posible_juego(que_carta,conn):
    cursor = conn.cursor() 
    sql = "INSERT INTO posible_jugador (valor, palo, color, imagen, orden, lugar) SELECT valor, palo, color, imagen, orden, lugar FROM cartas_jugador WHERE lugar = %s " % (que_carta)   
    cursor.execute(sql)
    conn.commit()

def armar_escalera(conn, estado):
    cursor = conn.cursor() 
    if estado == 'medio':
        cursor.execute("SELECT orden FROM faltantes_jugador")
        orden = cursor.fetchone()[0]        
        sql = "UPDATE posible_jugador SET  orden=%s " \
                      "WHERE valor='Joker'" % (orden)
        cursor.execute(sql)
        conn.commit()
    else:
        cursor.execute("SELECT minimo FROM min_jugador")
        min = cursor.fetchone()[0]    
        if min > 0:
            sql = "UPDATE posible_jugador SET  orden=%s " \
                      "WHERE valor='Joker'" % (min-1)
            cursor.execute(sql)
            conn.commit()
        else:
            cursor.execute("SELECT minimo FROM min_jugador")
            max = cursor.fetchone()[0]    
            sql = "UPDATE posible_jugador SET  orden=%s " \
                      "WHERE valor='Joker'" % (max+1)
            cursor.execute(sql)
            conn.commit()
    esca = []        
    cursor.execute("SELECT valor, palo, color, imagen, orden, lugar from posible_jugador order by orden")
    for row in cursor:
        esca.append(tuple(row))
    return esca

def esEscalera(conn):
    cursor = conn.cursor() 
    cursor.execute("SELECT * from cuantos_palos")
    cuantos = cursor.fetchone()[0]    
    if cuantos > 1:
        return [False]
    else:    
        cursor.execute("SELECT count(*) from hay_joker_jug")
        cuantos = cursor.fetchone()[0]        
        if cuantos > 1:
            return [False]
        elif cuantos == 1:
            #hay un joker
            cursor.execute("SELECT * from min_max")
            cua = cursor.fetchone()  
            if cua[0]== 0 and cua[1] in (11,12): 
                #tengo que cambiar el valor 
                cursor.execute("UPDATE posible_jugador set orden = 13 where orden = 0")
                conn.commit()
            cursor.execute("SELECT count(*) from cuenta_posible_esc")
            c = cursor.fetchone()[0]            
            if c == 1:
                #hay un faltante al medio
                return [True,armar_escalera(conn,'medio')]
            elif c == 0 or c == 2:
                #hay un faltante al extremo
                return [True,armar_escalera(conn,'extremo')]
        else:
            cursor.execute("SELECT * from min_max")
            cua = cursor.fetchone()  
            if cua[0]== 0 and cua[1] in (11,12):                         
                #tengo que cambiar el valor 
                cursor.execute("UPDATE posible_jugador set orden = 13 where orden = 0")
                conn.commit()
            cursor.execute("SELECT * from faltantes_jugador")
            try:
                cuantos = cursor.fetchone()[0]        
            except TypeError:
                return [True,armar_escalera(conn,'lista')]          
            if cuantos == 0:
                return [True,armar_escalera(conn,'lista')]      

def esTrica(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * from cuantos_palos")
    palos = cursor.fetchone()[0]     
    cursor.execute("SELECT * from valores_trica")
    cuantos = cursor.fetchone()[0]        
    if palos == 3 and cuantos == 3:#es una trica
        cursor.execute("SELECT valor, palo, color, imagen, orden, lugar from posible_jugador")
        trica = []
        for row in cursor:
            trica.append(tuple(row))
        return [True,trica]
    else:
        return [False]    
    
def eliminar_varias(de_donde,args,conn):
    cursor = conn.cursor() 
    if de_donde == 'Jug':
        query = f"DELETE FROM cartas_jugador WHERE lugar in ({','.join(['?']*len(args))})"
        cursor.execute(query, args)
        #elimino las cartas de posble_juego
        cursor.execute("DELETE FROM posible_jugador")
    else:
        query = f"DELETE FROM cartas_casa WHERE lugar in ({','.join(['?']*len(args))})"
        cursor.execute(query, args)
    conn.commit()    

def trueque(carta_jug,donde, conn):
    #print("donde es " + donde)
    #print("carta_jug es " + str(carta_jug))
    cursor = conn.cursor()
    if donde == 'atras':
        sql = "SELECT id from cartas_jugador where lugar = %s" % (carta_jug -1)
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        sql = "UPDATE cartas_jugador set lugar = %s WHERE lugar = %s" % (carta_jug -1, carta_jug)
        cursor.execute(sql)
        sql = "UPDATE cartas_jugador set lugar = %s WHERE id = %s" % (carta_jug, id)
        cursor.execute(sql)
    else:
        sql = "SELECT id from cartas_jugador where lugar = %s" % (carta_jug +1)
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        sql = "UPDATE cartas_jugador set lugar = %s WHERE lugar = %s" % (carta_jug +1, carta_jug)
        cursor.execute(sql)
        sql = "UPDATE cartas_jugador set lugar = %s WHERE id = %s" % (carta_jug, id)
        cursor.execute(sql)
    conn.commit()

def reordenar(donde,conn):
    cursor = conn.cursor()
    if donde == 'Jug':
        cursor.execute("SELECT id from cartas_jugador order by id")
        cur = cursor.fetchall()
        i=0
        for row in cur:
            cursor.execute("UPDATE cartas_jugador SET lugar = %s WHERE id = %s" % (i,row[0]))
            i+=1         
        conn.commit() 
    else: #casa           
        cursor.execute("SELECT id from cartas_casa order by id")
        cur = cursor.fetchall()
        i=0
        for row in cur:
            sql = "UPDATE cartas_casa SET lugar = %s WHERE id = %s" % (i,row[0])
            cursor.execute(sql)
            i+=1         
        conn.commit() 

def obtener_imagenes(donde,conn):
    cursor = conn.cursor()
    if donde == 'Jug':
        cursor.execute("SELECT imagen from cartas_jugador order by lugar")
    else:
        cursor.execute("SELECT color from cartas_casa order by lugar")
    lis = cursor.fetchall()
    result = []
    for l in lis:
        result.append(l[0])
    return(result)    

def obtener_imagen_mesa(conn):    
    cursor = conn.cursor()
    cursor.execute("SELECT imagen from mesa where id in (select max(id) from mesa)")
    img = cursor.fetchone()[0]
    return img

def borrar_posbles(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posible_jugador ") 
    conn.commit()

def borrar(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mesa ")   
    cursor.execute("DELETE FROM cartas_casa ")   
    cursor.execute("DELETE FROM cartas_casa_bis ")  
    cursor.execute("DELETE FROM cartas_jugador ") 
    cursor.execute("DELETE FROM tricas_mesa ") 
    cursor.execute("DELETE FROM escaleras_mesa ") 
    cursor.execute("DELETE FROM posible_jugador ") 
    cursor.execute("UPDATE mazo set estado = 0")   
    cursor.execute("DELETE FROM escaleras")
    cursor.execute("DELETE FROM posibles_esca")

    conn.commit()

        







        





        



    


