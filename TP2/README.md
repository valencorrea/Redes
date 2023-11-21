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


