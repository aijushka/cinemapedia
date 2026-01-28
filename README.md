# cinemapedia

## toiminnot
Apurina silloin kun ei osaa valita, mitä leffaa haluaa katsoa.

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään sovellukseen elokuvien arvosteluja. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan kyseisiä arvosteluja.
* Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät arvostelut.
* Käyttäjä pystyy etsimään elokuvia eri hakusanoilla. Käyttäjä pystyy hakemaan sekä itse lisäämiään että muiden käyttäjien lisäämiä arvosteluja.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän lisäämät arvostelut.
* Käyttäjä pystyy valitsemaan arvostelulleen yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.
* Sovelluksessa on mahdollista kommentoida muiden käyttäjien, sekä omia arvosteluja.

## asennus ohjeet
Asenna `flask`-kirjasto:
```
$ pip install flask
```
Luo tietokannan taulut:
```
$ sqlite3 database.db < schema.sql
```
Voit käynnistää sovelluksen näin:
```
$ flask run
``` 
