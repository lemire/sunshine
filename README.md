# Indexation de la base de données shunshine

La base de données Sunshine de l’Ontario, officiellement appelée Public Sector Salary Disclosure (divulgation des salaires du secteur public), est une liste annuelle publiée par le gouvernement de l’Ontario, conformément à la Public Sector Salary Disclosure Act de 1996. Elle recense les employés du secteur public et des organisations financées par la province qui gagnent un salaire de 100 000 $ ou plus par an. Cette initiative vise à promouvoir la transparence et la responsabilité dans l’utilisation des fonds publics.
Nous pouvons utiliser cette base de données pour tester les index dans les bases de données.


Nous utilisons SQLite comme moteur de base de données pour ce projet.
SQLite est une bibliothèque légère qui permet de créer une base complète sous la forme d’un seul fichier (ici database.bin). Aucun serveur n’est requis, l’installation est immédiate et la portabilité est excellente : le fichier peut être copié, envoyé ou archivé comme n’importe quel autre. Pour un ensemble de données de taille modeste comme la divulgation des salaires du secteur public de l’Ontario, SQLite offre des performances très satisfaisantes, une API simple et une excellente fiabilité transactionnelle. C’est donc un choix idéal pour illustrer concrètement l’impact des index sur les performances sans introduire la complexité d’un SGBD client-serveur.
Il est parfaitement possible de faire des analyses de données avec des bases de données légères comme SQLite et DuckDB. Le principle d'utilisation est le même qu'avec des bases de données comme SQL Server, Oracle, MySQL, etc. à la différence prêt que l'utilisation est plus simple.

## Prérequis

Avant de procéder, assurez-vous d'installer Python 3.7 ou une version ultérieure sur votre machine.

- **Pour Windows** :
  1. Téléchargez l'installateur depuis https://www.python.org/downloads/windows/
  2. Lancez l'installateur et cochez l'option "Add Python to PATH" avant de cliquer sur "Install Now".
  3. Ouvrez l'invite de commandes :
     - Cliquez sur le menu Démarrer (icône Windows en bas à gauche), tapez "Invite de commandes" ou "cmd", puis cliquez sur l'application correspondante.
  4. Vérifiez l'installation en tapant :
     ```
     python --version
     ```
     ou
     ```
     python3 --version
     ```

- **Pour macOS** :
  1. Ouvrez le Terminal.
  2. Installez Homebrew si ce n'est pas déjà fait :
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
  3. Installez Python 3 avec Homebrew :
     ```
     brew install python
     ```
  4. Vérifiez l'installation :
     ```
     python3 --version
     ```

Le nom de l'interpréteur Python sur votre système peut être `python` ou `python3` selon votre système. 


## Obtention des fichiers du projet

Pour obtenir les fichiers du projet, vous pouvez télécharger une archive ZIP depuis GitHub :

1. Rendez-vous sur la page du projet : https://github.com/lemire/sunshine
2. Cliquez sur le bouton vert « Code » puis sur « Download ZIP ».
3. Décompressez l’archive téléchargée sur votre ordinateur.
4. Ouvrez le dossier extrait dans votre terminal ou explorateur de fichiers pour suivre les instructions d’installation ci-dessus.

## Examen du code

Nous vous invitons à lire (au moins rapidement) le code Python des différents fichiers du projet. Portez attention au code SQL.


## Création de la base de données


Placez-vous dans le répertoire principal du projet. La commande

```bash
python3 python/create.py  data/tbs-pssd-compendium-salary-disclosed-2024-en-utf-8-2025-03-26.csv database.bin
```

ou 

```bash
python python/create.py  data/tbs-pssd-compendium-salary-disclosed-2024-en-utf-8-2025-03-26.csv database.bin
```

devrait créer une base de données "database.bin" normalisée.





## Description du schéma de la base de données

La base de données est conçue pour gérer les informations des employés du secteur public, en se concentrant sur leurs employeurs, leurs données personnelles et leurs rémunérations annuelles. Elle comprend quatre tables principales : `employers`, `individuals`, `salaries` et une table système `sqlite_sequence`. La table `employers` stocke les informations sur les employeurs, avec un identifiant unique (`employer_id`), le nom de l'employeur (`employer_name`) et son secteur d'activité (`sector`), garantissant l'unicité de la combinaison nom-secteur. La table `individuals` recense les employés avec un identifiant unique (`individual_id`), leur nom de famille (`last_name`), prénom (`first_name`) et titre de poste (`job_title`), avec une contrainte d'unicité sur ces trois champs pour éviter les doublons. Des index sont définis sur `individuals.last_name`, `salaries.employer_id` et `salaries.individual_id` pour optimiser les requêtes.

La table `salaries` est le cœur de la base, reliant les employeurs et les employés via leurs identifiants (`employer_id` et `individual_id`) pour enregistrer les salaires (`salary`), avantages (`benefits`) et l'année (`year`). Une clé primaire composite sur `employer_id`, `individual_id` et `year` assure l'unicité des enregistrements annuels. Les clés étrangères établissent des relations avec les tables `employers` et `individuals`, garantissant l'intégrité référentielle. La table `sqlite_sequence` est utilisée par SQLite pour gérer les séquences des clés primaires auto-incrémentées. Ce schéma normalisé permet des requêtes efficaces sur les données salariales tout en maintenant une structure claire et cohérente.




## Table employers
- **employer_id** : INTEGER, clé primaire, auto-incrémenté
- **employer_name** : TEXT, nom de l'employeur, non nul
- **sector** : TEXT, secteur d'activité, non nul
- **Contrainte** : UNIQUE(employer_name, sector)

## Table sqlite_sequence
- **name** : TEXT, nom de la table
- **seq** : INTEGER, valeur de la séquence
- **Description** : Gère les séquences pour les clés primaires auto-incrémentées

## Table individuals
- **individual_id** : INTEGER, clé primaire, auto-incrémenté
- **last_name** : TEXT, nom de famille, non nul
- **first_name** : TEXT, prénom, non nul
- **job_title** : TEXT, titre de poste, non nul
- **Contrainte** : UNIQUE(last_name, first_name, job_title)
- **Index** : idx_individuals_last_name ON last_name

## Table salaries
- **employer_id** : INTEGER, clé étrangère référençant employers(employer_id)
- **individual_id** : INTEGER, clé étrangère référençant individuals(individual_id)
- **year** : INTEGER, année, non nul
- **salary** : REAL, salaire, non nul
- **benefits** : REAL, avantages, non nul
- **Clé primaire** : (employer_id, individual_id, year)
- **Index** : idx_salaries_employer_id ON employer_id
- **Index** : idx_salaries_individual_id ON individual_id


## Index sur les clé primaires ou étrangères

Les requêtes sur les clés étrangères et les clé primaires sont souvent de facto indexées
et elles ne nécessitent pas davantage d'indexation.


Le script `benchmark.py` effecture la requête suivante...

```sql
SELECT i.last_name, i.first_name, e.employer_name, e.sector, s.salary, s.year
FROM salaries s
JOIN employers e ON s.employer_id = e.employer_id
JOIN individuals i ON s.individual_id = i.individual_id
```

avec ou sans les index suivants.

```sql
CREATE INDEX idx_salaries_employer_id ON salaries(employer_id)
CREATE INDEX idx_salaries_individual_id ON salaries(individual_id)
```

En exécutant le script avec

```bash
 python3 python/benchmark.py database.bin  
```

ou 

```bash
 python python/benchmark.py database.bin  
```

vous devriez constater que l'index n'est pas utile.

## Index utile

Il peut être plus utile de mettre des index sur d'autres valeurs.
Considérons cette requête qui calcule le salaire moyen des gens nommés 'Smith'.

```sql
SELECT AVG(s.salary)
FROM salaries s
JOIN individuals i ON s.individual_id = i.individual_id
WHERE i.last_name = 'Smith'
```

Il peut être utile d'avoir un index sur la colonne `last_name`.

```SQL
CREATE INDEX idx_individuals_last_name ON individuals(last_name)
```


En exécutant le script avec

```bash
 python3 python/query.py database.bin  
```

ou 

```bash
 python python/query.py database.bin  
```

vous devriez constater que l'index est utile.



## Démonstration vidéo

L'activité ne nécessite que la saisie de trois commandes. Vous pouvez consulter la vidéo suivante pour voir un résultat possible. (La vidéo ne sert pas à expliquer l'activité, elle n'est qu'une illustration.)

[![Démonstration vidéo](https://img.youtube.com/vi/D3G_7uV1YKA/maxresdefault.jpg)](https://www.youtube.com/watch?v=D3G_7uV1YKA)


## Examen du plan d'exécution (optionnel)

Comme la plupart des moteurs de base de données, sqlite vous permet d'obtenir un plan d'exécution. Avec
sqlite, il suffit de précéder votre requête de l'expression `"EXPLAIN QUERY PLAN:"`.



Vous pouvez obtenir les plans d'exécution en exécutant le script avec

```bash
 python3 python/explain_plan.py database.bin  
```

ou 

```bash
 python python/explain_plan.py database.bin  
```

Le résultat devrait ressembler à ceci: 

```
Query 1: Join query for salaries with employer and individual details
Query:
SELECT i.last_name, i.first_name, e.employer_name, e.sector, s.salary, s.year
            FROM salaries s
            JOIN employers e ON s.employer_id = e.employer_id
            JOIN individuals i ON s.individual_id = i.individual_id

EXPLAIN QUERY PLAN:
  5 | 0 | 216 | SCAN s
  7 | 0 | 45 | SEARCH e USING INTEGER PRIMARY KEY (rowid=?)
  10 | 0 | 45 | SEARCH i USING INTEGER PRIMARY KEY (rowid=?)

Query 2: Average salary for individuals with last name 'Smith'
Query:
SELECT AVG(s.salary)
            FROM salaries s
            JOIN individuals i ON s.individual_id = i.individual_id
            WHERE i.last_name = 'Smith'

EXPLAIN QUERY PLAN:
  5 | 0 | 54 | SEARCH i USING COVERING INDEX idx_individuals_last_name (last_name=?)
  9 | 0 | 61 | SEARCH s USING INDEX idx_salaries_individual_id (individual_id=?)
```

### Interprétation des plans d'exécution

Le plan d'exécution révèle comment SQLite optimise les requêtes en utilisant les index disponibles. Voici ce que suggère chaque plan concernant les index :

- **Requête 1** : Cette requête est une jointure complète sans condition WHERE, récupérant toutes les lignes. Le plan montre :
  - Un balayage complet (SCAN) de la table `salaries`, car aucune condition ne permet de filtrer les données.
  - Des recherches par clé primaire sur `employers` et `individuals` pour récupérer les détails joints.
  - **Suggestion** : Les index sur `salaries.employer_id` et `salaries.individual_id` ne sont pas utilisés ici, car un scan complet est nécessaire. Cela explique pourquoi, dans `benchmark.py`, ajouter ces index n'améliore pas les performances pour cette requête spécifique. Les index sont utiles pour les requêtes avec filtres ou jointures sélectives, mais pas pour les scans complets.

- **Requête 2** : Cette requête filtre sur `i.last_name = 'Smith'` et joint les tables. Le plan montre :
  - Une recherche (SEARCH) sur la table `individuals` en utilisant l'index couvrant `idx_individuals_last_name`. Cela signifie que l'index sur `last_name` est efficace pour filtrer rapidement les individus sans accéder à la table elle-même (couvrant, car il contient toutes les colonnes nécessaires).
  - Une recherche sur la table `salaries` en utilisant l'index `idx_salaries_individual_id` pour récupérer les salaires correspondants.
  - **Suggestion** : L'index sur `individuals.last_name` est très utile ici, car il évite un balayage complet de la table `individuals`. L'index sur `salaries.individual_id` aide également à accélérer la jointure. Sans ces index, la requête serait beaucoup plus lente, comme démontré dans `query.py`.
