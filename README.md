# Cinemapedia™
Sovellus elokuvien ja sarjojen arvosteluille.

## toiminnot
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään sovellukseen elokuvien ja sarjojen arvosteluja. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan omia arvostelujaan.
* Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät arvostelut.
* Käyttäjä pystyy etsimään arvosteluja/elokuvia/sarjoja eri hakusanoilla. Hakiessa käyttäjä näkee sekä itse lisätyt että muiden käyttäjien arvostelut.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät käyttäjien arvostelujen lukumäärän ja niiden lisäämät arvostelut.
* Käyttäjä pystyy valitsemaan arvostelulleen genre- ja kieli-luokittelun. Mahdolliset luokat löytyy tietokannasta.
* Sovelluksessa on mahdollista kommentoida muiden käyttäjien, sekä omiin arvosteluihin.

## asennus-ohjeet
Asenna `flask`-kirjasto
```
$ pip install flask
```
Lisää alkutiedot (init.sql) ja tietokannan taulut (schema.sql)
```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```
Käynnistä sovellus!
```
$ flask run
``` 
