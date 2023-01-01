import sqlite3 

def agregar_escalera(row,i,conn):
    cursor = conn.cursor() 
    cursor.execute("INSERT INTO escaleras_mesa (valor, palo, color, imagen, orden, id) VALUES (?,?,?,?,?,?)",(row[0],row[1],row[2],row[3],row[4],i))
    conn.commit()        

def agregar_trica(de_quien,args,i,conn):
    #print("donde es " + str(donde) + " i es " + str(i) + " args es" + str(args))
    cartas = []
    cursor = conn.cursor() 
    if de_quien == 'Jug':
        query = f"SELECT valor, palo, color, imagen, orden FROM cartas_jugador WHERE lugar in ({','.join(['?']*len(args))})"
        cursor.execute(query, args)
    else:
        #print("args en casa es " + str(args))
        query = f"SELECT valor, palo, color, imagen, orden FROM cartas_casa WHERE lugar in ({','.join(['?']*len(args))})"
        cursor.execute(query, args)
    obj = cursor.fetchall()    
    for row in obj:
        cartas.append(tuple(row))        
        sql = "INSERT INTO tricas_mesa (valor, palo, color, imagen, id) VALUES ('%s','%s','%s','%s',%s)" % (row[0],row[1],row[2],row[3],i)
        cursor.execute(sql)
        conn.commit()                          
    return cartas

def esca_mesa(conn):
    esca = []
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM escaleras_mesa")
    obj = cursor.fetchall()    
    for row in obj:
        esca.append(tuple(row))    
    return esca

def en_trica(i,quien,conn):
    cursor = conn.cursor() 
    if quien == 'Jug':
        sql = "SELECT valor, palo, color, imagen, orden FROM cartas_jugador WHERE lugar = %s " % (i)   
    else:    
        sql = "SELECT valor, palo, color, imagen, orden FROM cartas_casa WHERE lugar = %s " % (i)   
    cursor.execute(sql)
    carta = cursor.fetchone()
    query = "SELECT count(*) FROM tricas_mesa where valor = '%s' and palo = '%s' "%  (carta[0],carta[1])
    cursor.execute(query)
    hay = cursor.fetchone()
    if hay[0] == 1: 
        return True
    else:
        return False   
 
def insertar_en_esca(carta,i,conn):
    cursor = conn.cursor() 
    query = "INSERT INTO escaleras_mesa VALUES ('%s','%s','%s','%s',%s,%s) " % (carta[0],carta[1],carta[2],carta[3],carta[4], i) 
    cursor.execute(query)
    conn.commit()  

def sin_joker(carta,i,conn):
    palo = carta[1]
    orden = carta[4]
    cursor = conn.cursor() 
    query = "SELECT DISTINCT ID from escaleras_mesa WHERE palo = '%s' " % (palo)
    cursor.execute(query)
    esca = cursor.fetchall()
    for row in esca:
        iden = row[0]
        query = "SELECT id, minimo, maximo from min_max_mesa WHERE id = %s " % (iden)
        cursor.execute(query)
        esca_hay = cursor.fetchone()  
        if esca_hay[1] - 1 == orden:
            insertar_en_esca(carta,i,conn)
        elif esca_hay[2] + 1 == orden:
            insertar_en_esca(carta,i,conn)
    return [True,i]            

def agregar_joker(carta,i,conn):
    nueva = list(carta)
    cursor = conn.cursor() 
    query = "SELECT id, minimo, maximo from min_max_mesa WHERE id = %s " % (i)
    cursor.execute(query)
    esca_hay = cursor.fetchone()
    if  esca_hay[1] == 0: #la primera carta es un joker
        #agrego el joker al final
        nueva[4] = esca_hay[2] +1
        insertar_en_esca(nueva,i,conn) 
    else:
        nueva[4] = esca_hay[1] - 1
    return [True,i]    

def reordenar_esca(i,donde, conn):
    cursor = conn.cursor() 
    sql = "SELECT max(orden) max,min(orden) min from escaleras_mesa where valor != 'Joker' and id = %s" % (i) 
    cursor.execute(sql)
    max_min = cursor.fetchone()
    if donde == 'inicio':
        sql= "UPDATE escaleras_mesa SET orden = %s WHERE id = %s and valor = 'Joker'" % (max_min[1]+1,i)
        cursor.execute(sql)
    else:    
        print("max min es " + str(max_min[0]-1))
        sql = "UPDATE escaleras_mesa SET orden = %s WHERE id = %s and valor = 'Joker'" % (max_min[0]-1,i)
        cursor.execute(sql)
    conn.commit() 
    

def en_esca(i,quien,conn):
    cursor = conn.cursor() 
    if quien == 'Jug':
        sql = "SELECT valor, palo, color, imagen, orden FROM cartas_jugador WHERE lugar = %s " % (i)   
    else:
        sql = "SELECT valor, palo, color, imagen, orden FROM cartas_casa WHERE lugar = %s " % (i)       
    cursor.execute(sql)
    carta = cursor.fetchone()
    #print("carta es " + str(carta))
    if carta[0] == 'Joker':
        #busco una escalera sin joker        
        cursor.execute("SELECT id FROM mesa_sin_joker")
        try:
            hay = cursor.fetchone()[0]  
            return agregar_joker(carta,hay,conn)                  
        except TypeError:
            return [False]  
    else:          
        palo = carta[1]
        orden = carta[4]
        cursor = conn.cursor() 
        query = "SELECT DISTINCT ID from escaleras_mesa WHERE palo = '%s' " % (palo)
        cursor.execute(query)
        esca = cursor.fetchall()
        for row in esca:
            iden = row[0]
            query = "SELECT id, minimo, maximo from min_max_mesa WHERE id = %s " % (iden)
            cursor.execute(query)
            esca_hay = cursor.fetchone()
            #print("orden es " + str(orden))
            #print("esca hay es " + str(esca_hay))
            if orden == esca_hay[1] - 1:#comparo con el minimo
                #reviso si esa escalera tiene joker y si esta en ese lugar
                query = "SELECT orden from mesa_con_joker WHERE id = %s " % (iden)
                cursor.execute(query)
                try:
                    ord_jok = cursor.fetchone()[0]
                except:
                    return sin_joker(carta,esca_hay[0],conn)                              
                if int(ord_jok) == int(orden):
                    #debo recorrer el numero al joker
                    if ord_jok == 0: #el joker juega el papel de la A
                        #actualizar el orden del joker a la ultima 
                        ultima = esca_hay[2] + 1
                        que_esca = esca_hay[0]
                        query = "UPDATE escaleras_mesa SET orden = %s WHERE valor = 'Joker' and id = %s " % (ultima, que_esca)
                        cursor.execute(query)
                    else:
                        ante = esca_hay[1] -2
                        que_esca = esca_hay[0]
                        query = "UPDATE escaleras_mesa SET orden = %s WHERE valor = 'Joker' and id = %s " % (ante, que_esca)
                        cursor.execute(query)                    
                    insertar_en_esca(carta,que_esca,conn)                    
                else:
                    insertar_en_esca(carta,iden,conn)
                return [True,esca_hay[0]]    
            elif orden == esca_hay[2] + 1:#comparo con el maximo
                insertar_en_esca(carta,iden,conn)
                return [True,esca_hay[0]]    
        return [False]    

def en_esca1(i,quien,conn):
    cursor = conn.cursor() 
    if quien == 'Jug':
        sql = "SELECT valor, palo, color, imagen, orden FROM cartas_jugador WHERE lugar = %s " % (i)   
    else:
        sql = "SELECT valor, palo, color, imagen, orden FROM cartas_casa WHERE lugar = %s " % (i)       
    cursor.execute(sql)
    carta = cursor.fetchone()
    palo = carta[1]
    orden = carta[4]
    cursor = conn.cursor() 
    query = "SELECT DISTINCT ID from escaleras_mesa WHERE palo = '%s' " % (palo)
    cursor.execute(query)
    esca = cursor.fetchall()
    for row in esca:
        iden = row[0]
        query = "SELECT id, minimo, maximo from min_max_mesa_joker WHERE id = %s " % (iden)
        cursor.execute(query)
        esca_hay = cursor.fetchone()
        if orden == esca_hay[1] - 1 :#comparo con el minimo o uno menor
            #reviso si esa escalera tiene joker y si esta en ese lugar
            query = "SELECT orden from mesa_con_joker WHERE id = %s " % (iden)
            cursor.execute(query)
            try:
                ord_jok = cursor.fetchone()[0]
                print("ord jok es "+ str(ord_jok))
            except:
                return sin_joker(carta,esca_hay[0],conn)   
            
            if int(ord_jok) == int(orden):
                print("en if")
                #debo recorrer el numero al joker
                if ord_jok == 0: #el joker juega el papel de la A
                    #actualizar el orden del joker a la ultima 
                    ultima = esca_hay[2] + 1
                    que_esca = esca_hay[0]
                    query = "UPDATE escaleras_mesa SET orden = %s WHERE valor = 'Joker' and id = %s " % (ultima, que_esca)
                    cursor.execute(query)
                else:
                    ante = esca_hay[1] -2
                    que_esca = esca_hay[0]
                    query = "UPDATE escaleras_mesa SET orden = %s WHERE valor = 'Joker' and id = %s " % (ante, que_esca)
                    cursor.execute(query)                    
                insertar_en_esca(carta,que_esca,conn)                    
            else:
                insertar_en_esca(carta,iden,conn)
            return [True,esca_hay[0]]  
        elif orden == esca_hay[1] - 2:    
            print("1") 
            insertar_en_esca(carta,iden,conn)
            reordenar_esca(i,'inicio',conn)
            return [True,esca_hay[0]]   
        elif orden == esca_hay[2] + 1:
            insertar_en_esca(carta,iden,conn)
            return [True,esca_hay[0]]   
        elif (orden == esca_hay[2] + 2):#comparo con el maximo     
            print("2") 
            insertar_en_esca(carta,iden,conn)
            reordenar_esca(i,'fin',conn)
            return [True,esca_hay[0]]   
        else:
            return [False]    
    return [False]    

def devolver_esca(cual,conn):
    lista = []
    cursor = conn.cursor() 
    query = "SELECT * from escaleras_mesa WHERE id = %s " % (cual)
    cursor.execute(query)
    esca = cursor.fetchall()
    for row in esca:
        lista.append(row)
    #print("en devolver esca " + str(lista))    
    return lista

conn = sqlite3.connect("loba.db")
print(en_esca1(3, 'Jug', conn))
#reordenar_esca(1,'fin',conn)