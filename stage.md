This document describes a project the Épicerie Le Détour submits for a winter 2026 internship. 

# Proposition de stage

## Titre du projet

Conception, intégration et mise à jour d'un système d'infrastructure-as-code pour une Épicerie communautaire à Pointe-Saint-Charles.

## Description

L'Épicerie le Détour est une épicerie autogérée sous forme d'OBNL, abordable et ouverte à tous et toutes, vectrice de transformation sociale. Ses missions sont d’offrir un service alimentaire abordable ouvert à tous et toutes, de créer du lien social en travailler activement en faveur d’une mixité sociale, d'être un espace d’expérimentation de l’autogestion ainsi qu'un espace de transformation social.

Pour son fonctionnement, des membres volontaires du Détour maintiennent des services informatiques (VPS ou auto‑hébergés) et services (logiciels personnalisés, configurations de sauvegarde ou logiciels libres tiers) nécessaires à la mission de l’épicerie, par exemple :
- sauvegardes borg multi‑store
- proxys Google Drive afin que leur contenu puissent être sauvegardés directement par les systèmes de l'Épicerie
- instances de Wordpress, Grafana et Mattermost
- applications développées en interne pour vérifier le statut des membres ou pour scanner les bons alimentaires du programme Nourrir la Pointe

Ces services sont deployées sous forme d'infrastructure-as-code avec Ansilble. Une configuration Vagrant permet le développement, l’expérimentation, les tests et le déploiement en préproduction sur des machines virtuelles locales sécurisées. Le déploiement et les mises à jour des serveurs réels ne sont effectués que lorsqu’ils fonctionnent correctement en local sur un réseau virtuel.

Ce projet de stage vise à corriger et améliorer la configuration Ansible de l’Épicerie le Détour. À la fin du projet, toutes les automatisations de configuration pourront à nouveau être exécutées, les systèmes seront surveillés afin d’anticiper les problèmes et planifier les investissements, et l'équipe d'IT de l'Épicerie recevra des notifications en cas de problème.

La configuration Ansible de l’Épicerie le Détour présente trois problèmes à résoudre.

Premièrement, la configuration Ansible n’est plus exécutable :
- les serveurs utilisent un système d’exploitation (Debian Buster) trop ancien et non‑migrable, ce qui empêche l’exécution d’Ansible
- l’environnement de développement Vagrant n’est plus facilement exécutable sur les machines Debian, car Vagrant, VirtualBox et les images cloud ne sont plus aussi bien pris en charge en raison de problèmes de licence

Ensuite, le système a toujours été très déficient en matière de surveillance et d’alerte. Les bénévoles du Détour gèrent également certains services du Bâtiment 7 (l'OBNL propriétaire des locaux physique de l'Épicerie) dans un playbook Ansible séparé : cet effort dupliqué devrait être fusionné en un seul projet. Enfin, certains serveurs doivent être migrés vers de nouvelles machines physiques auto‑hébergées dans les locaux de l’Épicerie le Détour.

Ce projet vise à résoudre tous ces problèmes. Par ordre de priorité:
- Remettre à jour l'environnement de développement et migrer l'ancien VPS afin de garantir un environnement minimalement fonctionnel
- Consolidation des VPS du B7, migration les Raspberry Pi et remettre en route le kiosk web pour rationaliser l’utilisation matérielle des systèmes
- Configurer un tableau de bord de statut pour permettre de surveiller efficacement nos ressources les plus importantes
- Configurer un système d’alerte pour prévenir les bénévoles IT des problèmes les plus fréquents avant qu’ils n’atteignent la production et n’affectent les autres membres
- Améliorer la documentation et formaliser les concepts et bonnes pratiques qui ne peuvent pas être exprimés directement dans la configuration Ansible

Ce stage sera suivi par des professionels de l'informatique (développeurs web senior, tech leads en 3D / jeux vidéos, C++ / Python ou ingénieurs de recherche) membres et bénévoles de l'Épicerie Le Détour. L'équipe de stagiaires sera pleinement intégrée aux membres actuels du Détour et partageront nos outils de communications, Slack et GitHub notamment. Les mentors de stage seront disponibles de façon limitées et probablement en dehors des heures de bureaux classiques: tôt le matin, en soirées et en fin de semaines. Nous établirons donc en tout debut de stage une façon de travailler commune afin de garantir le meilleur suivi possible des stagiaires.

La majorité du stage s'effectuera à distance: aucun local ou bureau n'est prévu pour acceuillir les stagiaires, et aucun équiment ne leur sera fourni. Cependant, n'importe quel ordinateur personnel pouvant faire tourner Debian linux nativement ou sous forme de machine virtuelle sera suffisant pour les besoins de ce stage.

Le stage aura 4 phases:
- une première phase courte où l'équipe de stagiaire réalisera un prototype simple d'un setup Ansible avec trois machines virtuelles liées par une connexion wireguard. Le but de ce prototype sera de familiariser les stagiaires avec les outils utilisés pour la gestion de notre infrastructure.
- la seconde partie consiste en l'objectif principal du projet: réparer le setup Ansible actuel et effectuer les migrations et mise à jours demandées
- la troisième partie sera considérée comme un objectif optionnel: configurer le système de monitoring et développer les scripts d'alerting
- la dernière partie sera d'effectuer une présentation vidéo du système du Détour à fin de documentation. Nous chercherons également, en accord avec les stagiaires, à laisser les stagiaires présenter notre setup et leur travail dans le cadre d'une ou deux des manifestations régulières de Montréal autour des logiciels libres.

Le plan de travail est détaillé sur le GitHub du projet :  https://github.com/orgs/epicerieledetour/projects/2/views/2?pane=info et sera mis à jour de façon continuelle pendant le stage.

## Expertise requise

L'équipe de stagiaire idéale sait installer Debian Linux sur des machines physiques ou virtuelle et est à l'aise avec sa manipulation en ligne de commande. Elle a une compréhension basique des protocoles, outils et termes utilisés: HTTP/S, SSH, chiffrement avec clés asymétriques, virtualisation, VPN et wireguard.

Les stagiaires travailleront depuis une distribution Linux Debian Trixie installée sur leur machines personnelles, soit physique, soit sous forme de machine virtuelle. Le travail sera effectué sous forme de Pull Request GitHub.  

Une grosse partie du stage sera consacrée à de l'automatisation du travail d'administrateur système, mais la partie alerting nécessitera certainement de programmer des outils simples en Python et du SQL au dessus de bases de données comme Prometheus. 

