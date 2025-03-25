# Witam
Witam w moim projekcie zaliczeniowym z pierwszego
bloku WWW 2024/2025. Jako temat wybrałem otwarcia
szachowe.  
Główna strona internetowa: https://www.thechesswebsite.com/chess-openings/

## Struktura projektu

### Katalog `ip-chess-openings`
Katalog zawiera projekt Jekylla tworzący
stronę internetową o otwarciach szachowych.

### `main.py`
Plik main.py służy do zescrape'owania danych ze stron
internetowych i zapisania ich w katalogu Jekylla.

## Pliki markdown w głównym katalogu

### `basic_markdown.md`
Plik zawiera tytuł, opis (zawierający podstawowe
informacje na temat otwarć szachowych) oraz podstawowe
informacje na temat otwarć szachowych wraz z obrazkami.  
Wszystkie dane zostały zescrape'owane z głównej strony
przy pomocy `BeautifulSoup`.

### `enhanced_markdown.md`
Plik zawiera wszystkie informacje zawarte w pliku
`basic_markdown.md` oraz dodatkowe informacje
i materiał wideo do każdego otwarcia wyszukane przy
użyciu biblioteki `duckduckgo_search`. 

___
#### Brzydki wygląd strony internetowej
Starałem się upięknić stronę poprzez użycie różnych
theme-ów (chociażby minima, jak widać w pliku
`_config.yml`), ale żadne podejście się nie udało.
Byłbym wdzięczny za wskazówkę, jak to naprawić.

_Ignacy Pernach_