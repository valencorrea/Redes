# TP2 SDN
### Ejecución
Para poder ejecutar el programa es necesario situarse dentro de \textbf{\textbackslash{TP2}} y correr el comando:
```python3 pox/pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning misc.controller```

El cual no solo levanta la herramienta POX sino que además se le indica el nivel de log del programa y también se lo configura para que aprenda automaticamente
la topología seteada por properties.

A su vez, en una nueva terminal y tambien desde la ruta \TP2, deberemos correr:

```sudo mn --custom ./topology.py --topo customTopo,switches=2  --mac --arp -x --switch ovsk --controller remote```

En donde utilizando mininet (mn) podremos setear para nuestra topologia (customTopo) la cantidad de switches deseada (switches=n).

Se podrá visualizar que se abre una terminal xterm para cada host virtual y los switches, permitiendonos así realizar pruebas

### Pruebas

### Bloqueo a cualquier host con puerto destino 80

Comenzamos levantando una conexion en el host 1 en el puerto 80 y a traves del protocolo udp. Una vez levantada esta, procedemos a probar su conexion con un cliente establecido desde el host 3

En la terminal del host 1: `iperf -s -p 80`

En la terminal del host 3: `  iperf -c 10.0.0.1 -p 80 `
Veremos que la regla se aplicaya que no se logra establecer la comunicación. Podemos probar además con UDP agregando el flag `-u` para demostrar que la regla aplica para ambos protocolos de transporte.


### Bloqueo de paquetes UDP provenientes del host1 con puerto destino 5001

Para la tercera prueba creamos server en el host 1 que responda los mensajes udp al puerto 5001. 
En la terminal del host 1: `iperf -s -p 5001 -u`
Y luego nos intentamos conectar desde el host 3:  iperf -u -c 10.0.0.1 -p 5001

Se podra ver que ocurrió un timeou debido a que al intentar enviar paquetes que cumplen con los clientes filtros de la regla, estos nunca llegan a destino.

### Bloqueo de paquetes entre dos hosts elegidos arbitrariamente

En este trabajo practico decidimos bloquear la conexion entre el host 1 y el host 4, aunque al haber hecho esta configuracion a traves de un archivo de properties, el cambio de los mismos se puede realizar facilmente.

Al ejecutar `pingall` en la terminal de mininet, notamos como desde host_1 no se puede acceder a host_4  y viceversa.

