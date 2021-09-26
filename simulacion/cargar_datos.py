def cargar_bases():
    with open("Datos/bases.csv") as bases:
        lista_bases = []
        bases_utilizadas = [1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1,1,1,1,1,0,0]
        lineas = bases.readlines()
        for l in range(len(lineas)-1):
            if l != 0:
                if bases_utilizadas[l] == 1:
                    linea = lineas[l].strip().split(";")
                    lista_bases.append((float(linea[0]),float(linea[1])))
    return lista_bases

def cargar_centros():
    with open("Datos/centros.csv") as centros:
        next(centros)
        disponibles = []
        lineas = centros.readlines()
        for linea in lineas:
            linea = linea.strip().split(";")
            disponibles.append((float(linea[0]),float(linea[1])))
    return disponibles