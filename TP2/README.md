# TP2 SDN
### Ejecución
Para poder ejecutar el programa es necesario situarse dentro de \textbf{\textbackslash{TP2}} y correr el comando:
```python3 pox/pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning misc.controller```

El cual no solo levanta la herramienta POX sino que además se le indica el nivel de log del programa y también se lo configura para que aprenda automaticamente
la topología seteada por properties.

A su vez, en una nueva terminal y tambien desde la ruta \TP2, deberemos correr:

```sudo mn --custom ./topology.py --topo customTopo,switches=2  --mac --arp -x --switch ovsk --controller remote```

En donde utilizando mininet (mn) podremos setear para nuestra topologia (customTopo) la cantidad de switches deseada (switches=n).