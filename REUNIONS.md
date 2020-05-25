# Meetings minutes

## 2020-05-19

- Introduction au projet
  - Découpage en [Milestones](https://github.com/epicerieledetour/ansible-automation/milestones?direction=asc&sort=due_date&state=open)
  - Première priorité: [installation initiale du serveur](https://github.com/epicerieledetour/ansible-automation/milestone/1)
- Méthodes de travail:
  - Tous les changements au code / documentation passe par des PRs
  - Pour la première semaine, point tous les jours à 9H par vidéoconférence
  - Une courte PR par jour sur le fichier [SCRUMS.md](SCRUMS.md) pour répondre aux questions classiques de la [méthodologie Scrum](https%3A%2F%2Ffr.wikipedia.org%2Fwiki%2FScrum_%28d%25C3%25A9veloppement%29):
    - Sur quoi j'ai travaillé aujourd'hui ?
    - Qu'est-ce que je compte faire demain ?
    - Sur quoi suis-je bloqué ?
    - Qu'ai-je appris aujourd'hui ? (question supplémentaire ajoutée pour le stage)
  - Surtout ne pas rester bloqué: poser ses questions sur le [canal Slack](https://epicerieledetour.slack.com/archives/CAFUP51N3) si quelque chose coince, les membres du Comité Informatique essayerons de répondre dès que possible
  
## 2020-05-20

- Point sur la première PR
  - Charles n'avait pas vu qu'Hugo avait déjà apporté des changements valides la veille au soir
  - Faire des PR indépendantes pour les Scrums
- Plan pour la suite: Ansible authorized_key et configurer le firewall

## 2020-05-21

- Rappel de faire les PR de scrums tous les soirs
- Présentation du système de RFC du Détour
- Prochain point quand on a un Grafana installé avec des métriques serveur basiques (CPU, MEM, etc), sans auth ni chiffrement pour le moment

## 2020-05-22

- Point rapide, continuation du travail de setup de Grafana

## 2020-05-25

- Code Review des deux PRs de cette fin de semaine #55 #56
- Discussion sur l'importance des Firewall avec test sur un NGinx non configuré
- Présentation de `netstat -plntu` pour afficher les ports ouverts
- Suite du projet: fail2ban et affichage des alertes fw / fail2ban #18 #19 #20

