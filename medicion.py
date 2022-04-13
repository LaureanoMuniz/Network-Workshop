from ast import In
from scapy.all import *
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import numpy as np 

S1 = {}
listaDeFrames = []
columnas = ['Símbolo', 'Dirección', 'Protocolo', 'Tipo de difusión',
            'Nombre de la red', 'Hora de la medición', 'Fecha']
'''Columnas para guarda la info del paquete en el DataFrame'''
fecha = str(date.fromtimestamp(time.time()))
horario = str(datetime.now().time())
horarioSinMilisegundos = horario[:-7]


def mostrar_fuente(S): 
    ''' Función para mostrar los diferentes símbolos de la fuente con su probabilidad. '''
    N = sum(S.values())
    simbolos = sorted(S.items(), key=lambda x: -x[1])
    print("\n Valores de la fuente: \n")
    print(simbolos)
    #print("\n".join([" %s : %.5f" % (d, k/N) for d, k in simbolos]))
    print()


def callback(pkt):
    '''Función que guarda la info de un paquete en un DataFrame '''
    if pkt.haslayer(Ether):
        dire = "BROADCAST" if pkt[Ether].dst == "ff:ff:ff:ff:ff:ff" else "UNICAST" # Se define si es tipo BROADCAST o UNICAST.
        proto = pkt[Ether].type  # El campo type del frame tiene el protocolo
        s_i = (dire, proto)  # Aca se define el simbolo de la fuente
        values = {columnas[0]: [s_i], columnas[1]: [pkt[Ether].dst], columnas[2]: [proto], columnas[3]: [
            dire], columnas[4]: [nombre], columnas[5]: [horarioSinMilisegundos],  columnas[6]: [fecha]}

        df = pd.DataFrame(data=values, columns=columnas)
        listaDeFrames.append(df)
        if s_i not in S1:
            S1[s_i] = 0.0
        S1[s_i] += 1.0
    #mostrar_fuente(S1) #Si se descomenta muestra la fuente en todo momento.



print(horarioSinMilisegundos, fecha)


nombre = str(input("\n Ingrese su nombre en MAYUSCULAS \n"))
(sniff(prn=callback, count=10000))

mostrar_fuente(S1)
fd = pd.concat([listaDeFrames[i] for i in range(len(listaDeFrames))], ignore_index=True) # Concateno los frames para crear un solo frame.
# print(fd.to_markdown())

# Manipulo el DataFrame para
fd = fd.set_index('Símbolo')
porcentaje = fd.index.value_counts(normalize=True)
print("El porcentaje de cada simbolo es: \n")
print(porcentaje)
fd["Porcentaje"] = porcentaje
print("\n La información de cada simbolo es: \n")
informacion =  -np.log2(porcentaje)
fd["Información del símbolo"] = informacion
print(informacion)
grouped = fd.groupby(['Símbolo'], as_index=False).value_counts(normalize=True)
del grouped["proportion"]
print()
print(grouped.to_markdown())
# print(fd.to_markdown())

# print(porcentaje)


med = str(input("Queres guardar la medición?"))
if str(med.capitalize())[0] == "Y" or str(med.capitalize())[0] == "S":
    file_name = nombre + "0" + ".csv"
    if not Path(file_name).exists():
        grouped.to_csv(file_name, encoding='utf-8', ignore=False)
    else:
        while(Path(file_name).exists()):
            file_name = file_name[:-5] + \
                str(int(file_name[-5]) + 1) + file_name[-4:]
        grouped.to_csv(file_name, encoding='utf-8', index=False)
