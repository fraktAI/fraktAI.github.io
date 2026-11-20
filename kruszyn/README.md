# Mój ♥ Kruszyn

Aplikacja dla mieszkańców Kruszyna (gmina Bolesławiec, woj. dolnośląskie): pogoda, wywóz śmieci, msze, prąd, autobusy, wydarzenia i drużyna Znicz Kruszyn. Wszystko w jednym miejscu, na telefonie i komputerze.

Działa za darmo na GitHub Pages, bez własnego serwera i bez bazy danych. Dane odświeżają się same dzięki robotom w GitHub Actions.

**Adres aplikacji:** https://fraktai.github.io/kruszyn/

---

## Co potrafi

| Kafelek / widok | Co pokazuje |
|---|---|
| **Pogoda** | bieżąca pogoda i prognoza na 5 dni (Open-Meteo), jakość powietrza, ostrzeżenia IMGW dla powiatu bolesławieckiego |
| **Wydarzenia** | nadchodzące i ostatnie 5 minionych wydarzeń we wsi; każdy może dodać swoje przez formularz Google; kalendarz do subskrypcji w telefonie |
| **Wywóz śmieci** | najbliższe odbiory, pełny harmonogram, kalendarz `.ics` z przypomnieniami |
| **Znicz Kruszyn** | najbliższe mecze, ostatnie wyniki i tabela (klasa B, grupa Jelenia Góra) |
| **Prąd** | planowane wyłączenia i awarie dla Kruszyna (Tauron Dystrybucja) |
| **Msze święte** | stały porządek nabożeństw w Kruszynie i Łazisku oraz bieżące intencje mszalne |
| **Autobusy** | rozkład PKS Bolesławiec z trzech przystanków, najbliższe odjazdy z odliczaniem |
| **Apteka całodobowa** | dyżurna apteka (dane z `wies.json`) |
| **PSZOK** | godziny otwarcia, zasady, co przyjmuje punkt |
| **Ważne telefony** | numery alarmowe, awarie, urząd (dane z `wies.json`) |
| **Napisz do twórcy** | link do formularza kontaktowego; przycisk „Postaw kawę" (do wyłączenia) |

Dodatkowo:

- **Instalacja jak zwykła aplikacja** (PWA): na Androidzie „Zainstaluj", na iPhonie „Do ekranu początkowego".
- **Działa bez internetu**: pokazuje ostatnio pobrane dane (service worker).
- **Ustawienia wyglądu:** jasny / ciemny motyw, trzy zestawy kolorów (zielony, niebieski, czerwony), powiększenie tekstu.
- **Odświeżanie po powrocie:** jeśli aplikacja była w tle ponad 5 minut, sama pobiera dane od nowa (ważne na iPhonie, który wznawia aplikacje z pamięci).
- Układ dopasowany do telefonu i komputera.

---

## Jak to działa

```
 Źródła danych                 GitHub Actions (roboty)              GitHub Pages
 ─────────────                 ───────────────────────              ────────────
 com-d.pl (śmieci)      ─┐
 Tauron (prąd)           │
 IMGW (ostrzeżenia)      ├──►  skrypty Pythona w scripts/  ──►  pliki JSON w repo  ──►  strona
 kruszyn.com (intencje)  │      (czas: ok. 1–2 minuty)            + commit przez bota     (index.html
 regiowyniki.pl (Znicz)  │                                                                  czyta JSON)
 Arkusz Google (wydarz.) ─┘
```

1. **Roboty** (`scripts/*.py`) pobierają dane ze stron źródłowych i zapisują je jako pliki JSON.
2. **Workflow** (`.github/workflows/publish.yml`) uruchamia roboty według harmonogramu, zapisuje zmiany w repozytorium i publikuje stronę.
3. **Aplikacja** (`index.html`) przy otwarciu pobiera te pliki JSON i pokazuje je. Pogoda i jakość powietrza idą prosto z Open-Meteo, bez robota.

### Zasady bezpieczeństwa danych

- Robot **nigdy nie nadpisuje** dobrych danych złymi: gdy źródło odpowie czymś nieoczekiwanym, plik zostaje taki, jaki był.
- Każdy krok robota ma `continue-on-error`, więc awaria jednego źródła nie wstrzymuje publikacji reszty.
- Gdy krok się nie uda, w podsumowaniu uruchomienia pojawia się żółte ostrzeżenie (`::warning::`).
- Aplikacja ma wbudowane dane awaryjne dla śmieci i telefonów, więc pokazuje coś nawet bez internetu i bez plików z robotów.

### Harmonogram

| Kiedy (czas UTC) | Co robi |
|---|---|
| `17 3,9,15,21 * * *` (4 razy na dobę) | pełny przebieg: śmieci, prąd, IMGW, intencje, Znicz, wydarzenia |
| `7 * * * *` (co godzinę) | lekki przebieg: prąd, IMGW, wydarzenia (bez śmieci, intencji i Znicza) |
| ręcznie (Actions → Run workflow) | pełny przebieg w dowolnej chwili |

---

## Struktura repozytorium

Aplikacja leży w podfolderze `kruszyn/`, bo w tym samym repozytorium (`fraktAI.github.io`) może działać inna strona. Dzięki temu adres to `…github.io/kruszyn/`.

```
fraktAI.github.io/
├── .github/workflows/publish.yml     ← workflow (musi być w głównym folderze repo)
└── kruszyn/
    ├── index.html                    ← cała aplikacja (wygląd + logika)
    ├── wies.json                     ← dane edytowane ręcznie (telefony, apteki, PSZOK, ogłoszenia)
    ├── manifest.webmanifest          ← ustawienia instalacji (PWA)
    ├── sw.js                         ← działanie offline
    ├── favicon.svg, icon-*.png       ← ikony aplikacji
    ├── wydarzenia_url.txt            ← adres CSV z arkusza Google z wydarzeniami
    ├── scripts/                      ← roboty (Python, bez dodatkowych bibliotek)
    │   ├── kruszyn_scraper.py        ← śmieci z com-d.pl
    │   ├── make_ics.py               ← kalendarz śmieci .ics
    │   ├── tauron_outages.py         ← wyłączenia prądu
    │   ├── imgw_warnings.py          ← ostrzeżenia pogodowe
    │   ├── kruszyn_intencje.py       ← intencje mszalne
    │   ├── znicz_mecze.py            ← mecze i tabela Znicza
    │   └── wydarzenia.py             ← wydarzenia z arkusza Google
    ├── data/                         ← dane tworzone przez roboty i edytowane ręcznie
    │   ├── waste.json                ← terminy śmieci (robot)
    │   ├── kruszyn-smieci.ics        ← kalendarz śmieci (robot)
    │   ├── wydarzenia.json           ← wydarzenia (robot)
    │   ├── kruszyn-wydarzenia.ics    ← kalendarz wydarzeń (robot)
    │   ├── tauron_config.json        ← zapamiętane identyfikatory Kruszyna w Tauron (robot)
    │   └── autobusy.json             ← rozkład PKS (RĘCZNIE, patrz niżej)
    ├── wylaczenia.json               ← prąd (robot)
    ├── ostrzezenia.json              ← IMGW (robot)
    ├── intencje.json                 ← intencje mszalne (robot)
    └── znicz.json                    ← Znicz (robot)
```

> Pliki `*.json` w głównym folderze aplikacji tworzone przez roboty (`wylaczenia`, `ostrzezenia`, `intencje`, `znicz`) są **generowane automatycznie**: nie edytuj ich ręcznie, bo robot je nadpisze.
>
> Pliki w stylu `index-1.html`, `index-2.html`, `workflow-do-wklejenia.txt` to kopie robocze. Aplikacji nie są potrzebne i można je usunąć.

---

## Skąd pochodzą dane

| Dane | Źródło | Plik | Aktualizacja |
|---|---|---|---|
| Pogoda, jakość powietrza | [Open-Meteo](https://open-meteo.com/) (bezpośrednio z aplikacji) | – | przy każdym otwarciu |
| Terminy śmieci | [com-d.pl](http://www.com-d.pl/) (harmonogram gminy) | `data/waste.json` | 4× na dobę |
| Ostrzeżenia pogodowe | [IMGW](https://danepubliczne.imgw.pl/) (powiat bolesławiecki, TERYT `0201`) | `ostrzezenia.json` | co godzinę |
| Wyłączenia prądu | Tauron Dystrybucja (publiczne API formularza „wyłączenia") | `wylaczenia.json` | co godzinę |
| Intencje mszalne | [kruszyn.com](https://kruszyn.com/ogloszenia-parafialne/) | `intencje.json` | 4× na dobę |
| Mecze Znicza | [regiowyniki.pl](https://regiowyniki.pl/) | `znicz.json` | 4× na dobę |
| Wydarzenia | formularz Google → arkusz → zakładka „Publiczne" | `data/wydarzenia.json` | co godzinę |
| Autobusy | rozkłady przystankowe [PKS Bolesławiec](https://www.pks-boleslawiec.pl/) | `data/autobusy.json` | **ręcznie** |
| Telefony, apteki, PSZOK | wpisane ręcznie | `wies.json` | ręcznie |
| Msze (stały porządek) | [kruszyn.com](https://kruszyn.com/porzadek-nabozenstw/) | w `index.html` | ręcznie |

Dane z Tauron, com-d.pl, regiowyniki.pl i kruszyn.com nie pochodzą z oficjalnych, gwarantowanych API. Gdy zmieni się wygląd lub format tych stron, odpowiedni robot przestanie działać (nie zepsuje przy tym starych danych) i trzeba go poprawić.

---

## Co edytujesz ręcznie

### `wies.json` – telefony, apteki, PSZOK

Zwykły plik tekstowy z danymi. Edytujesz go bezpośrednio na GitHubie (ikona ołówka), a po zapisaniu zmiany pojawiają się w aplikacji. Przykładowe wpisy:

```json
{ "grupa": "Alarmowe", "nazwa": "Numer alarmowy", "opis": "każda służba", "tel": "112", "sos": true }
{ "nazwa": "Apteka „U Nelli”", "adres": "ul. Dolne Młyny 21c, Bolesławiec", "tel": "75 640 92 13", "cala_doba": true }
```

Sekcje: `ogloszenia`, `telefony`, `apteki`, `prad` (wpisy ręczne dodatkowe do danych z Tauron) i `pszok`. Uważaj na przecinki i cudzysłowy: pomyłka w JSON powoduje, że aplikacja użyje wbudowanych danych awaryjnych. Po edycji warto sprawdzić plik w [jsonlint.com](https://jsonlint.com/).

### `data/autobusy.json` – rozkład jazdy

Autobusów nie da się pobierać automatycznie, bo PKS udostępnia tylko pliki PDF. Rozkład jest więc przepisany ręcznie z rozkładów przystankowych (Kruszyn Orzechowa, Kruszyn 1, Kruszyn 2).

Gdy PKS wyda nowy rozkład:

1. Pobierz aktualne PDF-y (linki są w stopce widoku „Autobusy").
2. Popraw godziny w `data/autobusy.json` (format wpisu: `"05:23 End"` – godzina i litery kursu).
3. Zmień pola `wazny_od` i `zaktualizowano`. Są one pokazywane w aplikacji jako „Rozkład ważny od…" i „ostatnia aktualizacja".

Litery przy godzinach aplikacja rozumie sama: wielkie litery to dni kursowania (`D` pon–pt, `E` pon–sob, `C` weekendy i święta, `T` codziennie, `S` dni nauki szkolnej), małe litery to wyjątki (`d`, `m`, `n` – wybrane święta i 24/31 grudnia). Pełna legenda jest w pliku w polu `legenda`. Rozkład obejmuje tylko dni robocze, bo w PDF-ach nie ma osobnych tabel na weekend.

### Stałe w `index.html`

Kilka ustawień jest w kodzie, w sekcjach opatrzonych komentarzem:

| Stała | Co robi |
|---|---|
| `SHOW_COFFEE` (`true` / `false`) | pokazuje lub ukrywa przycisk „Postaw kawę" |
| `COFFEE_URL` | adres strony buycoffee.to |
| `FORM` (w sekcji wydarzeń) | adres formularza Google do dodawania wydarzeń |
| `AWAY_MS` | po ilu milisekundach w tle aplikacja się odświeża (domyślnie 5 minut) |
| link w stopce „Napisz do twórcy" | adres formularza kontaktowego Google |

> **Nie edytuj ani nie usuwaj** komentarzy `/*WASTE_DATA_START*/` i `/*WASTE_DATA_END*/` w `index.html`. Robot od śmieci wstawia między nimi świeże dane awaryjne.

---

## Wydarzenia: formularz Google → arkusz → aplikacja

1. Mieszkaniec klika w aplikacji „Dodaj wydarzenie" i wypełnia formularz Google.
2. Odpowiedzi trafiają do arkusza Google (zakładka „Odpowiedzi z formularza 1").
3. **Moderacja:** wydarzenie pojawi się w aplikacji dopiero po wpisaniu `TAK` w kolumnie **Zatwierdzone** (N). Wpisanie `TAK` w kolumnie **Anulowane** (O) ukrywa wydarzenie.
4. Zakładka **Publiczne** (formuła `QUERY`) wybiera tylko zatwierdzone wiersze i jest opublikowana jako CSV.
5. Adres tego CSV jest w pliku `wydarzenia_url.txt`. Robot `wydarzenia.py` czyta go co godzinę i zapisuje `data/wydarzenia.json` oraz kalendarz `data/kruszyn-wydarzenia.ics`.

Kolumny arkusza: A Sygnatura czasowa · B Nazwa wydarzenia · C Data · D Kategoria · E Godzina · F Data zakończenia · G Miejsce · H Opis · I Organizator · J Telefon · K Link · L Kto dodaje · M Zgoda na publikację · N Zatwierdzone · O Anulowane.

Formuła w komórce A1 zakładki „Publiczne":

```
=IFERROR(QUERY('Odpowiedzi z formularza 1'!A:O; "select B, C, D, E, F, G, H, I, J, K where N = 'TAK' and (O is null or O <> 'TAK') and M is not null"; 1); "")
```

Publikacja CSV: Plik → Udostępnij → Opublikuj w internecie → wybierz zakładkę „Publiczne" i format CSV → skopiuj link do `wydarzenia_url.txt`.

Robot rozumie zarówno daty zapisane jako tekst (`2026-11-26`, `26.11.2026`), jak i liczby seryjne z arkusza (`46352`), oraz godziny w postaci ułamka doby (`0,7083` = 17:00). Wiersze bez nazwy lub daty są pomijane, a jeśli arkusz nagle będzie pusty, robot nie kasuje zapisanych wydarzeń.

---

## Uruchomienie od zera

1. Utwórz repozytorium `<twój-login>.github.io` (albo użyj istniejącego) i wgraj pliki aplikacji do folderu `kruszyn/`. Workflow wgraj do `.github/workflows/publish.yml` w głównym folderze.
2. **Settings → Pages → Source: GitHub Actions.**
3. **Settings → Actions → General → Workflow permissions → Read and write permissions** (bot musi móc zapisywać dane w repozytorium).
4. **Actions → „Publikacja strony" → Run workflow.** Pierwsze uruchomienie tworzy pliki z danymi i publikuje stronę.
5. Gdy zmieniasz nazwę repozytorium lub folderu, popraw adresy w `manifest.webmanifest` oraz `kruszyn/` w workflow.

Workflow nie używa żadnych sekretów ani kluczy: wszystkie źródła są publiczne.

### Zapisywanie zmian przez bota

Bot (`kruszyn-bot`) zapisuje wygenerowane pliki do gałęzi `main`. Gdy w tym samym czasie ktoś edytuje repozytorium, push może zostać odrzucony. Workflow robi wtedy `git pull --rebase` i ponawia próbę do trzech razy.

---

## Uruchamianie i testowanie lokalnie

Roboty używają tylko biblioteki standardowej Pythona (3.10+), więc nic nie trzeba instalować. Z folderu `kruszyn/`:

```bash
python3 scripts/imgw_warnings.py --selftest     # test samego parsera, bez internetu
python3 scripts/wydarzenia.py --selftest
python3 scripts/tauron_outages.py --discover    # pokaż surową odpowiedź Tauron (diagnostyka)
python3 scripts/kruszyn_intencje.py --discover  # pokaż, co robot widzi na stronie parafii
python3 scripts/znicz_mecze.py --discover       # pokaż, co robot widzi na regiowyniki.pl
```

Podgląd strony (wymagany serwer, bo `file://` blokuje pobieranie plików JSON):

```bash
python3 -m http.server 8000
# otwórz http://localhost:8000/
```

---

## Gdy coś nie działa

Pierwsze miejsce: **Actions → ostatnie uruchomienie → krok, który się nie udał**. Przy błędach źródeł w podsumowaniu jest żółte ostrzeżenie.

| Objaw | Zwykła przyczyna |
|---|---|
| Brak ostrzeżeń IMGW w aplikacji | normalne, gdy nie ma ostrzeżeń: IMGW odpowiada „Brak ostrzeżeń meteorologicznych" i robot zapisuje pustą listę |
| Brak kafelka Znicza | robot nie rozpoznał strony regiowyniki.pl lub nie ma meczów; uruchom `--discover` |
| Brak prądu mimo awarii | Tauron zwraca dane dla całej okolicy; robot zostawia tylko wpisy z nazwą „Kruszyn". 0 wpisów oznacza zwykle brak wyłączeń |
| Wydarzenia nie pokazują się | brak `TAK` w kolumnie Zatwierdzone, pusty `wydarzenia_url.txt` albo zakładka „Publiczne" nie jest opublikowana jako CSV |
| Aplikacja pokazuje starą wersję po aktualizacji | service worker trzyma kopię; zamknij aplikację całkowicie i otwórz ponownie, na telefonie ewentualnie wyczyść dane strony |
| `python: can't open file 'scripts/…'` | workflow szuka skryptów w złym folderze; sprawdź `working-directory: kruszyn` |
| `fatal: pathspec '…json' did not match any files` | stara wersja kroku zapisu; użyj aktualnego workflow, który dodaje tylko istniejące pliki |
| `UnicodeEncodeError` w User-Agent | w nagłówkach HTTP nie wolno używać polskich liter; User-Agent robotów jest ASCII |
| Push odrzucony („fetch first") | ktoś zapisał zmiany w trakcie pracy bota; workflow sam ponawia próbę |
| 404 przy śmieciach na rok 2027 | COM-D nie opublikował jeszcze harmonogramu na nowy rok; normalne, dane z 2026 zostają |

---

## Dla rozwijającego aplikację

Struktura `index.html`:

- **Widoki** to elementy `<section class="view" id="v-…">`. Ich lista jest w tablicy `VIEWS` w skrypcie; nawigacja po adresie `#/nazwa`.
- **Kafelki** strony głównej są w `<div class="tiles">`. Kolejność w kodzie to kolejność na ekranie. Ostrzeżenia (`t-warn`, `t-imgw`) są zawsze na górze.
- **Dane** każdej funkcji pobiera osobny blok (`(async function () { … })()`), który robi `fetch` swojego pliku JSON i w razie błędu po prostu nic nie pokazuje.
- **Stopka** (kontakt, kawa, źródła) jest pokazywana tylko na stronie głównej.
- Preferencje użytkownika (motyw, kolory, powiększenie, wybrany przystanek) są w `localStorage` pod kluczami `kr-theme`, `kr-pal`, `kr-zoom`, `busStop`. Zapis jest opakowany w `try/catch`, bo przeglądarki w trybie prywatnym go blokują.

**Dodanie nowej funkcji** to zwykle cztery kroki:

1. Robot w `scripts/` zapisujący plik JSON (zasada: przy nietypowej odpowiedzi nie nadpisuj starego pliku, w User-Agent tylko znaki ASCII).
2. Krok w `publish.yml` z `continue-on-error: true` oraz dopisanie pliku do kroku „Przygotuj pliki strony".
3. Kafelek i widok w `index.html`, nazwa widoku w tablicy `VIEWS`.
4. Wpis w tym README.

---

## Plany

- Powiadomienia (ostrzeżenia IMGW, wydarzenia, mecze Znicza): propozycja kanałów to Telegram lub push w aplikacji.
- Wiadomości z Kruszyna z bolec.info.
- Kod QR do aplikacji na plakaty.
- Zgłaszanie problemów (drogi, oświetlenie).
- Intencje mszalne z Łazisk.

---

## Uwagi

- Aplikacja jest nieoficjalna i tworzona społecznie. Dane pochodzą ze stron zewnętrznych i mogą być nieaktualne. W sprawach ważnych (autobus, prąd, godziny mszy) sprawdź źródło lub zadzwoń.
- Pokazywane są tylko krótkie dane i linki do źródeł, bez kopiowania treści cudzych serwisów.
- Pomysły, uwagi i zgłoszenia błędów: formularz „Napisz do twórcy" na dole strony głównej.
