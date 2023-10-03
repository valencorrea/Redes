# Introducción a Sistemas Distribuidos


| Nombre alumno                     | Padron | Mail                 | Github                                     |              
|-----------------------------------|--------|----------------------|--------------------------------------------|
| Pablo Salvador Dimartino          | 101231 | pdimartino@fi.uba.ar | [GitHub](https://github.com/psdimartino) |
| Valentina Laura Correa            | 104415 | vcorrea@fi.uba.ar    | [GitHub](https://github.com/valencorrea)   |
| Agustin Ariel Andrade             | XXXXXX | aandrade@fi.uba.ar   | [GitHub](https://github.com/AgussAndrade) | 
| Stephanie Ingrid Izquierdo Osorio | 104196 | sizquierdo@fi.uba.ar | [GitHub](https://github.com/stephanieizquierdo) | 
| Juan Sebastian Burgos             | XXXXXX | jsburgos@fi.uba.ar   | [GitHub](https://github.com/juansburgos) | 

## Introducción
La presente entrega contiene los requerimientos pedidos para el trabajo practico
grupal N°1 de la materia Introducción a los sistemas distribuidos - CURSO: 01-Alvarez Hamelin

## Objetivo

En este trabajo práctico buscamos comprender y poner en práctica los conceptos y
herramientas necesarias para la organización de un protocolo RDT.
Para esto desarrollamos una aplicación de arquitectura cliente-servidor 
que implemente las siguientes funcionalidades de transferencia de archivos:

UPLOAD: Transferencia de un archivo del cliente hacia el servidor

DOWNLOAD: Transferencia de un archivo del servidor hacia el cliente

Dicho servidor debe procesar de forma concurrente la transferencia
de archivos de carga y descargas con múltiples clientes.

Para tal finalidad, será necesario comprender cómo se comunican los procesos a 
través de la red, y cuál es el modelo de servicio que la capa de transporte 
le ofrece a la capa de aplicación. Como protocolo de capa de transporte, 
se implementa UDP. El protocolo UDP es un servicio 
sin conexión, no ofrece fiabilidad, ni control de flujos, ni control de conge
stión, es por eso que se implementa una versión utilizando 
el protocolo Stop & Wait y otra versión utilizando el protocolo Selective repeat,
con el objetivo de lograr una transferencia confiable al utilizar el protocolo.

## Hipótesis y supuestos

 - Existe un tamaño máximo contemplado en el protocolo por el tamaño de los paquetes 
 - No hay restricciones en el tamaño de los archivos que se le pueden mandar al servidor 
 - En caso de que el cliente intente descargar un archivo que no existe en el servidor el cliente time out [TO DO]
 - El time out es de 5 segundos (o milisegundos?)
 - 
## Implementación

Procederemos a explicar nuestra estructura

### Cliente

El cliente puede tener dos funcionalidades que se divide en dos aplicaciones de línea de comandos: upload y download.

El comando upload envía un archivo al servidor para ser guardado con el nombre asignado.

`python3 file-upload [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME] [-saw STOPANDWAIT] [-sr SELECTIVE REPEAT]`

Donde cada flag indica:

- -h/--help: Imprime el mensaje de "help"
- -v/--verbose: Incrementa en uno la verbosidad en cuanto al sistema de logueo del servidor
- -q/--quiet: Decrementa en uno la verbosidad en cuanto al sistema de logueo. 
- -H/--host: Indica la dirección IP del servicio 
- p/--port: Indica el puerto 
- -s/--src: Indica el path del archivo a subir. 
- -n/--name: Nombre del archivo a subir. 
- -saw/--stopAndWait: Para indicar el protocolo a utilizar sea Stop and Wait.
- -sr/--selectiveRepeat: Para indicar que el protocolo a utilizar sea Selective repeat

En nuestra implementación esta operación sigue los siguientes pasos:

Crea un Socket con el protocolo correspondiente según el parámetro ingresado 
en protocol en el host "localhost" y el puerto pasado por parámetro.

Envía una estructura Metadata (el tipo de comando, el nombre del archivo, y 
el tamaño de este), descripta en la sección de protocolo.
Comienza el envío del archivo en sí, para ello, se dividen los mensajes 
largos en segmentos más cortos de tamaño CHUNCK_SIZE(256).
Es decir que se envían mensajes de este tamaño hasta completar el archivo 
o hasta que quede un segmento menor al tamaño del archivo, de ser así se 
manda un último mensaje con este tamaño inferior.
Por último, se espera una respuesta del servidor para corroborar si la transferencia de archivos se resolvió de forma correcta.


### Ejecución


### Otros links
- [Enunciado](https://drive.google.com/file/d/1c0npGce0MuamsgeVyxAR7qn6hFDeaE0t/view?usp=sharing)
