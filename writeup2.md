Après avoir fait la configuration de la VM et monté correctement l'ISO, on peut effectuer l'étape suivante.

<h1> Syslinux Prompt</h1>

On maintient SHIFT lors du lancement de la VM, ce qui lance Lilo ("Linux Loader") et attends nos instructions.

> boot:_

On entre :

>live init=/bin/bash

Quand la VM se lance, un programme nommé "init" se lance, trouvé à  `/bin/init`  ou  `/sbin/init`. Ce programme est responsable du lancement du système et de la création d'un environnement utilisable.

Écrire  `init=/bin/bash`  indique au kernel de lancer  `/bin/bash`  à la place.

Et on est connecté en root dans un nouveau shell.