import moduloBD as bd
from  itertools import combinations
import sqlite3 
from tkinter import ttk, messagebox

def posibles_tri(valor,palo,conn):
    cursor = conn.cursor() 
    sql = "SELECT count(*) from tricas where valor = '%s'" % (valor)
    cursor.execute(sql)
    cuantas = cursor.fetchone()[0]
    sql = "SELECT * from tricas_posibles_tricas where valor = '%s'" % (valor)
    cursor.execute(sql)
    for row in cursor:
        sql = "SELECT count(*) from escaleras where valor = '%s' and palo = '%s'" % (row[1],row[0])
        cursor.execute(sql)
        hay = cursor.fetchone()[0]
        if hay == 1:
            return False
    if cuantas == 0:
        cursor.execute("SELECT valor, palo from falta_trica")
        for row in cursor:
            if valor == row[0] and palo == row[1]:
                return True
        return False
    else:
        return False            

def eval_tres(palo, orden, conn):
    if bd.cantidad('Casa',conn)== 3:
        if bd.cantidad('Joker_Casa',conn):
            cursor = conn.cursor() 
            sql = "SELECT orden FROM cartas_casa where valor != 'Joker' and palo = '%s'" % (palo)
            cursor.execute(sql)    
            ordenes = cursor.fetchall()
            for ord in ordenes:
                if (orden == ord[0] - 1) or (orden == ord[0] + 1):
                    return True
            return False        
        else:
            return False    
    else:
        return False    

def sirve_esca(valor, palo, orden, conn):
    #print("En sirve esca " + valor + palo + str(orden))
    if eval_tres(palo,orden,conn):
        return True
    else:        
        cursor = conn.cursor() 
        cursor.execute("SELECT id FROM id_posibles")
        try:
            id_esca = cursor.fetchone()[0]
            sql = "SELECT * FROM faltantes_esca_palo where palo = '%s'" % (palo) 
            cursor.execute(sql)
            try:
                faltantes = cursor.fetchall()
                if faltantes == []:
                    return False
                else:    
                    for row in faltantes:
                        if row[3] == -1:  #orden_falta == -1
                            if orden == row[2]:
                                return True        
                    sql = "SELECT min, max FROM numeros_esca WHERE id = %s" % (id_esca)
                    cursor.execute(sql)
                    try:
                        ind = cursor.fetchone()                    
                        if orden == ind[0] - 1 or orden == ind[1] + 1:
                            return True
                        else:
                            return False
                    except TypeError:        
                        return False
            except TypeError:
                return False                    
        except TypeError:
            return False

def ya_existe(valor, palo,conn):
    cursor = conn.cursor() 
    sql = "SELECT count(*) FROM cartas_casa WHERE valor = '%s' and  palo = '%s' " % (valor, palo)
    cursor.execute(sql)
    hay = cursor.fetchone()[0]
    if hay == 1:
        return True
    else:
        return False    

def sirve_para_bajar(carta, conn):
#        print("En sirve carta es " + str(carta))
        valor = carta[0]
        palo = carta[1]
        orden = carta[5]
        id = carta[4]
        if ya_existe(valor, palo,conn):
            return(["nada",-1])
        else:    
            if posibles_tri(valor, palo, conn):
                return(["trica",id])
            elif sirve_esca(valor,palo,orden,conn):
#                print("devuelvo escalera")
                return(["escalera"])
            else:
                return(["nada",-1])
        
def leer_mesa(conn):
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM mesa WHERE ID = (SELECT MAX(ID)  FROM mesa)")
    carta = cursor.fetchone()
    return carta 

def obtener_tricas(conn):
    tricas = []
    cursor = conn.cursor() 
    cursor.execute("SELECT lugar FROM tricas")
    tri = cursor.fetchall()
    for row in tri:
        tricas.append(row[0])
    return tricas

def obtener_escaleras(conn):
    esca = []
    cursor = conn.cursor() 
    cursor.execute("SELECT DISTINCT ID from escaleras")
    ids = cursor.fetchall()
    es = []
    for i in ids:
        sql = "SELECT valor, palo, color, imagen ,orden,lugar FROM view_escaleras where id = %s" % (i)
        cursor.execute(sql)
        tri = cursor.fetchall()
        for row in tri:
            es.append(row)
        esca.append(es)  
    #print("escaleras en obtener escaleras es " + (str(esca)))      
    return esca

def tomar_descarte(conn):
    cursor = conn.cursor() 
    cursor.execute("SELECT count(*) FROM cartas_casa where id in (select doble from dobles)")
    if cursor.fetchone()[0] == 0:#no hay cartas en dobles
        cursor.execute("SELECT count(*) FROM descarte")
        if cursor.fetchone()[0] == 0:#no hay cartas en descarte
            cursor.execute("SELECT lugar, imagen FROM cartas_casa where id = (select min(id) from cartas_casa where valor != 'Joker')")
            return cursor.fetchone()        
        else:    
            cursor.execute("SELECT lugar,imagen FROM descarte")
            return cursor.fetchone()        
    else:
        cursor.execute("SELECT lugar, imagen FROM cartas_casa where id in (select doble from dobles)")
        return cursor.fetchone()        
        
def valida(order_list):
    #print("order list es" + str(order_list))
    j = 0
    for i in range(len(order_list)-1) :
        #print("dif es " + str(((order_list[i+1][2]) - (order_list[i][2]+1))))
        if ((order_list[i+1][2]) - (order_list[i][2]+1)) > 1:
            #print("en if")
            return False
        elif ((order_list[i+1][2]) - (order_list[i][2]+1)) == 1:    
            #print("en eliif")
            j+=1
    if j > 1:
        #print("j es "+ str(j))
        return False
    else:
        return True
        
def combinatoria(lista):
    #print("lista en combinatoriaaaaaa " + str(lista))            
    tam = len(lista)
    result = []
    for i in range (2,tam+1):
        for c in combinations(lista,i):
            #print("antes " + str(c))
            if valida(sorted(c, key=lambda carta: carta[-3])):
                #print("despues " + str(c))
                result.append(c)
                #print("es valida " + str(c))
    #print("result en combinatoria " + str(result))            
    return result

def armar_lista(palo, conn):
    esca = []
    cursor = conn.cursor() 
    sql = "SELECT valor, palo, orden, lugar, id from cartas_casa_sin_dobles where palo = '%s' order by orden" % (palo)
    cursor.execute(sql)
    for row in cursor:
        esca.append(tuple(row))
    #print(" esca en armar lista es " + str(esca))    
    return esca

def faltan_esca(lista):
    min = lista[0][2]
    max = lista[-1][2]
    return (max - min + 1) - len(lista)

def armado(id_esca,max_esca,valor, palo, orden, lugar,id_carta,conn):
    cursor = conn.cursor() 
    sql = "INSERT INTO escaleras (id, valor, palo, orden, lugar, id_carta) SELECT %s, valor, palo, orden, lugar, id_carta from posibles_esca WHERE id = %s" % (max_esca,id_esca)
    cursor.execute(sql)
    sql = "INSERT INTO escaleras (id, valor, palo, orden, lugar, id_carta) VALUES (%s, '%s', '%s', %s, %s, %s)" % (max_esca, valor,palo,orden,lugar, id_carta)
    cursor.execute(sql)
    sql = "DELETE FROM posibles_esca WHERE id = %s " % (id_esca)
    cursor.execute(sql)

def armar_con_joker(max_posi,max_esca,conn):
    me = max_esca
    #si tengo joker, armo otra escalera
    cursor = conn.cursor() 
    cursor.execute("select valor, palo, orden, lugar, id from jokers where lugar not in (select lugar from escaleras where valor = 'Joker')")
    rows = cursor.fetchall()
    for r in rows:    
        if max_posi > 0:#agregue alguna posible
            cursor.execute("SELECT id FROM id_posibles")
            try:
                id_esca = cursor.fetchone()[0]
                sql = "SELECT orden FROM faltantes_esca WHERE orden_falta is NULL and id = %s" % (id_esca)
                cursor.execute(sql)
                try:
                    faltante = cursor.fetchone()[0]
                    #print("faltante es " + str(faltante))
                    armado(id_esca,max_esca,r[0],r[1],faltante,r[3],r[4],conn)
                    me+=1
                except TypeError:
                    sql = "SELECT min, max FROM numeros_esca WHERE id = %s" % (id_esca)
                    cursor.execute(sql)
                    ind = cursor.fetchone()                    
                    if ind[0] == 0:#la primera carta es A
                        ord = ind[1] + 1
                    else:
                        ord = ind[0] - 1
                    armado(id_esca,max_esca,r[0],r[1],ord,r[3],r[4],conn)
                    me+=1   
                conn.commit()
            except TypeError:
                exit

def revisar_duplicadas(conn):
    #funcion que revisara si hay una escalera dentro de otra
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM maxima_escalera")
    max_esca = cursor.fetchone()
    esca = max_esca[0]
    cant = max_esca[1]
    for i in range(3,cant):
        cant -=1
        sql = "SELECT * FROM maxima_escalera where id not in (%s)" % esca
        cursor.execute(sql)
        rows = cursor.fetchall()
        for r in rows:
            sql = "SELECT count(*) from  escaleras e1, escaleras e2 where e1.valor = e2.valor and e1.palo = e2.palo and e1.orden = e2.orden and e1.id = %s and e2.id =%s" % (r[0] ,esca)
            cursor.execute(sql)
            if cant == cursor.fetchone()[0]:#la escalera esta dentro de la escalera grande
                sql = "DELETE from escaleras where id = %s" % (r[0])
                cursor.execute(sql)
    conn.commit()        
        

def armar(lista,conn):
    if lista !=[]:
        print("lista en armar " + str(lista))
        cursor = conn.cursor() 
        cursor.execute("select COALESCE(max(id),0)  max from escaleras")
        max_esca = cursor.fetchone()[0] + 1
        cursor.execute("select COALESCE(max(id),0)  max from posibles_esca")
        max_posi = cursor.fetchone()[0] + 1
        cuantas = 0
        for lis in lista:
            if faltan_esca(lis) ==0 and len(lis) >=3:
                for l in lis:
                    sql = "INSERT INTO escaleras (id, valor, palo, orden, lugar, id_carta) VALUES (%s,'%s','%s',%s,%s,%s)" % (max_esca,l[0],l[1],l[2],l[3],l[4])
                    cursor.execute(sql)
                max_esca+=1
                cuantas +=1
            else:
                for l in lis:
                    #print("en for l es "+ str(l))
                    sql = "INSERT INTO posibles_esca (id, valor, palo, orden, lugar, id_carta) VALUES (%s,'%s','%s',%s,%s,%s)" % (max_posi,l[0],l[1],l[2],l[3],l[4])
                    cursor.execute(sql)
                max_posi+=1
        conn.commit()   
        armar_con_joker(max_posi,max_esca,conn)
        if cuantas > 1:
            revisar_duplicadas(conn)

def posibles_esca(conn):
    if bd.cantidad('cora', conn)>1:        
        armar(combinatoria(armar_lista('cor',conn)),conn)
    if bd.cantidad('bast', conn)>1:
        armar(combinatoria(armar_lista('bas',conn)),conn)
    if bd.cantidad('treb', conn)> 1:
        armar(combinatoria(armar_lista('tre',conn)),conn)
    if bd.cantidad('romb', conn)> 1:
        armar(combinatoria(armar_lista('rom',conn)),conn)
    esca = []    
    cursor = conn.cursor() 
    cursor.execute("SELECT * from escaleras")    
    lista = cursor.fetchall()
    for row in lista:
        esca.append(row)
    #print("escaleras en psoibles_esca es " + str(esca))    

def eliminar_esc(conn):
    cursor = conn.cursor() 
    cursor.execute("DELETE from escaleras")
    cursor.execute("DELETE from posibles_esca")
    conn.commit()         

"""def prueba(conn):
    cursor = conn.cursor() 
    sql = "select valor, palo, orden, lugar, id from jokers where lugar not in (select lugar from escaleras where valor = 'Joker')"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for r in rows:
        print(r)"""


conn = sqlite3.connect("loba.db")
#armar([(('7', 'cor', 6, 5), ('9', 'cor', 8, 4)), (('9', 'cor', 8, 4), ('10', 'cor', 9, 2)), (('7', 'cor', 6, 5), ('9', 'cor', 8, 4), ('10', 'cor', 9, 2))],conn)    
#print(faltan_esca((('7', 'cor', 6, 5), ('9', 'cor', 8, 4), ('10', 'cor', 9, 2))))
#posibles_esca(conn)
#prueba(conn)
#print(eval_tres('bas', 4, conn))
#print(combinatoria((('4', 'cor', 3, 10, 1995), ('7', 'cor', 6, 1, 1986))))
print(sirve_esca('6', 'rom',  5, conn))
#print(sirve_esca('2','rom',conn))
#revisar_duplicadas(conn)
#print(posibles_tri('8','tre',conn))
#print(obtener_escaleras(conn))






