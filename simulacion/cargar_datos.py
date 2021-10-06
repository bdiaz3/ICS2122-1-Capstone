from parametros import BASES_UTLIMA_SOL, TODAS, BASES_MODELO_VIEJO, BASES_MODELO_UNIFORME, NUEVO

def cargar_bases():
    with open("Datos/bases.csv") as bases:
        lista_bases = []
        bases_utilizadas = NUEVO
        lineas = bases.readlines()
        for l in range(len(lineas)):
            if l != 0:
                if bases_utilizadas[l-1] == 1:
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