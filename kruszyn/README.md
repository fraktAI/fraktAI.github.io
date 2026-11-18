# Mój ♥ Kruszyn – aplikacja wsi

Strona-aplikacja dla mieszkańców: pogoda, wywóz śmieci (z przypomnieniami w kalendarzu telefonu), msze, prąd, apteki, ważne telefony.
Działa za darmo na GitHubie, bez własnego serwera. Terminy śmieci odświeżają się same 4 razy na dobę.

## Co jest w repozytorium

| Plik / folder | Do czego służy |
|---|---|
| `index.html` | cała aplikacja (wygląd + logika) |
| `wies.json` | **Twoje dane do ręcznej edycji**: ogłoszenia, telefony, apteki, wpisy o prądzie |
| `data/waste.json` | terminy wywozu (tworzy robot, nie edytuj ręcznie) |
| `data/kruszyn-smieci.ics` | kalendarz do telefonu (tworzy robot) |
| `scripts/` | roboty: śmieci (COM-D), kalendarz `.ics`, wyłączenia prądu (Tauron) |
| `wylaczenia.json` | wyłączenia prądu dla Kruszyna (tworzy robot co godzinę) |
| `ostrzezenia.json` | ostrzeżenia pogodowe IMGW dla powiatu (tworzy robot co godzinę) |
| `data/tauron_config.json` | zapamiętane numery Kruszyna w bazie Tauron (tworzy robot) |
| `.github/workflows/publish.yml` | harmonogram robota i publikacja strony |
| `favicon.svg`, `icon-192.png`, `icon-512.png`, `manifest.webmanifest` | ikona i „instalacja” na ekranie telefonu |

## Uruchomienie – krok po kroku (ok. 15 minut)

**1. Konto.** Wejdź na https://github.com → *Sign up*. Załóż darmowe konto (zapamiętaj login).

**2. Nowe repozytorium.** Kliknij **+** (prawy górny róg) → *New repository*.
- Repository name: `kruszyn` (od tego zależy adres strony)
- Ustaw **Public** (konieczne dla darmowej strony)
- Zaznacz *Add a README file*? **Nie** – zostaw puste. → *Create repository*.

**3. Wgranie plików.** Na stronie nowego repozytorium kliknij *uploading an existing file* i przeciągnij **wszystkie pliki i foldery** z tej paczki (`index.html`, `wies.json`, `favicon.svg`, `icon-*.png`, `manifest.webmanifest`, `README.md`, foldery `data` i `scripts`). Na dole *Commit changes*.

**4. Plik robota (ważny, bo przeglądarka często pomija foldery z kropką).**
Kliknij *Add file → Create new file*. W polu nazwy wpisz dokładnie:
`.github/workflows/publish.yml`
(po wpisaniu `/` GitHub sam tworzy foldery). Wklej całą zawartość pliku `workflow-do-wklejenia.txt` → *Commit changes*.
Jeśli `.github/workflows/publish.yml` już jest w repozytorium – pomiń ten krok.

**5. Uprawnienia robota.** *Settings → Actions → General* → na dole *Workflow permissions* → **Read and write permissions** → *Save*.

**6. Włączenie strony.** *Settings → Pages* → w *Source* wybierz **GitHub Actions**.

**7. Pierwsze uruchomienie.** Zakładka **Actions** → po lewej *Publikacja strony* → *Run workflow* → zielony przycisk. Poczekaj 1–2 minuty, aż pojawi się zielony ptaszek.

**8. Gotowe.** Adres aplikacji: `https://TWÓJ-LOGIN.github.io/kruszyn/`
Ten link wyślij sąsiadom (np. SMS, Facebook, plakat z kodem QR).

## Dodanie do telefonu

- **Ikona na ekranie głównym.** iPhone (Safari): przycisk *Udostępnij → Do ekranu początkowego*. Android (Chrome): menu ⋮ → *Zainstaluj aplikację* / *Dodaj do ekranu głównego*.
- **Przypomnienia o śmieciach.** Na stronie wejdź w *Wywóz śmieci* → *Przypomnienia w telefonie* → *Dodaj do kalendarza*. Kalendarz sam się aktualizuje, a przypomnienie przychodzi o 18:00 dzień przed wywozem. Jeśli przycisk nie działa, pobierz plik `.ics` i otwórz go w telefonie.

Aplikacja nie wysyła powiadomień push (wymagałoby to serwera) – tę rolę pełni kalendarz.

## Jak coś zmienić

**Ogłoszenia, telefony, apteki, prąd** → edytuj `wies.json`: klik w plik → ikona ołówka → zmień → *Commit changes*. Strona odświeży się sama w ok. minutę. Uważaj na przecinki i cudzysłowy, bo błąd w pliku sprawi, że aplikacja użyje danych wbudowanych. Przykład ogłoszenia:
```json
"ogloszenia": [
  {"tytul": "Zebranie wiejskie", "tresc": "Sobota 18:00, świetlica", "od": "2026-11-20", "do": "2026-11-28", "pilne": false}
]
```
Przykład wpisu o prądzie: `"prad": [{"typ": "planowane", "dzien": "2026-12-03", "godz": "8:00 – 14:00", "gdzie": "Kruszyn, ul. ..."}]`

**Msze** – godziny są wpisane w `index.html` (sekcja `MSZE ŚWIĘTE`) jako reguły; źródło: kruszyn.com. Gdy parafia zmieni porządek, trzeba poprawić te reguły – napisz do mnie, zrobię to.

**Śmieci – dzień zbiórek dodatkowych.** Daty odzieży i gabarytów (2 razy w roku) wpisane są w `scripts/kruszyn_scraper.py` w słowniku `PDF_2026`. Podział „odzież 02.03 i 16.11 / gabaryty 07.03 i 01.08” to moje założenie z PDF-a – **sprawdź z harmonogramem**.

## Co dzieje się automatycznie

Robot 4 razy na dobę (ok. 4:17, 10:17, 16:17, 22:17) pobiera terminy ze strony COM-D, odbudowuje cały rok, zapisuje `data/waste.json` i kalendarz `.ics`, po czym publikuje stronę. Jeśli strona COM-D się zmieni lub nie odpowie, robot **niczego nie nadpisuje** – aplikacja pokazuje ostatnie dobre dane, a w zakładce Actions pojawi się czerwony krzyżyk z komunikatem. Wtedy napisz do mnie.

## Prąd – jak to działa i co sprawdzić po pierwszym uruchomieniu

Co godzinę robot pyta publiczne API Tauron Dystrybucja o wyłączenia (planowane i awarie) na 30 dni do przodu i zostawia te, w których tekście jest „Kruszyn”. Wynik trafia do `wylaczenia.json` i na kafel **Prąd**. Gdy jest awaria lub wyłączenie dziś/jutro, kafel robi się czerwony.

Tauron nie daje oficjalnego, gwarantowanego API, więc po pierwszym uruchomieniu **sprawdź**:
1. *Actions → Publikacja strony →* otwórz przebieg → krok *Pobierz wyłączenia prądu z Tauron*. Ma być zielony ptaszek i napis „Zapisano wylaczenia.json”.
2. W repozytorium pojawił się plik `data/tauron_config.json` z nazwą „Kruszyn” (to wieś w gminie Bolesławiec, a nie inny Kruszyn).
3. Jeśli krok jest czerwony: skopiuj jego komunikat do mnie. Najpewniej Tauron zablokował serwery GitHuba albo zmienił format – to da się poprawić.

Pamiętaj: dla wsi Tauron zwraca wyłączenia z całej okolicy, a robot wybiera te z nazwą „Kruszyn”. Gdy komunikat wymienia tylko sąsiednią wieś lub ulicę, na liście go nie będzie. Dlatego wiążące informacje zawsze sprawdzaj na tauron-dystrybucja.pl.

## Ostrzeżenia pogodowe IMGW

Co godzinę robot pobiera z IMGW ostrzeżenia meteorologiczne (wiatr, burze, mróz, gołoledź, upał, opady) dla **powiatu bolesławieckiego** (kod TERYT 0201) i zapisuje je w `ostrzezenia.json`. Gdy jakieś obowiązuje, na ekranie głównym pojawia się czerwony kafel z najgroźniejszym zjawiskiem i stopniem (1–3), a szczegóły są w *Pogoda*. Gdy nic nie obowiązuje, kafla nie ma.

Po pierwszym uruchomieniu sprawdź w *Actions* krok *Pobierz ostrzeżenia IMGW* (ma być zielony). Pusty plik (`"items": []`) jest normalny, gdy nie ma ostrzeżeń. Nie obejmuje to ostrzeżeń hydrologicznych (stan rzek, np. Bóbr).

## PSZOK

Kafel **PSZOK** na ekranie głównym pokazuje, czy punkt jest teraz otwarty (wt, czw, sob 10:00–18:00), a w środku są adres, telefony, mapa, lista co przyjmuje i czego nie przyjmuje oraz zasady. Dane pochodzą ze strony gminy i są w `wies.json` w sekcji `"pszok"` – gdy zmienią się godziny, popraw tylko tam (numery dni: 0 = niedziela, 1 = poniedziałek … 6 = sobota). Strona gminy nie podaje godzin w święta ani limitów ilości, więc aplikacja zaleca telefon.

## Intencje mszalne

Robot (4 razy na dobę) czyta stronę kruszyn.com/ogloszenia-parafialne/ i zapisuje intencje w `intencje.json`. W sekcji *Msze święte* pojawia się lista najbliższych intencji, a kafel na ekranie głównym pokazuje intencję najbliższej mszy. Robot pomija wpisy, w których dzień tygodnia nie zgadza się z datą. Gdy parafia zmieni układ strony, robot nie nadpisze starych danych, a w *Actions* pojawi się ostrzeżenie.

## Znicz Kruszyn

Robot (4 razy na dobę) czyta ze strony regiowyniki.pl terminarz i tabelę drużyny (klasa B, Jelenia Góra IV) i zapisuje je w `znicz.json`. Kafel na ekranie głównym pokazuje najbliższy mecz (gdy jest w ciągu tygodnia) albo ostatni wynik i miejsce w tabeli. W środku są najbliższe i ostatnie mecze (z oznaczeniem W/R/P) oraz pełna tabela. Mecze bez ustalonego terminu (np. runda wiosenna przed publikacją terminarza) są liczone, ale nie pokazywane z datą.
Robot opiera się na tekście strony, nie na jej wyglądzie, ale gdy regiowyniki.pl zmieni układ, w *Actions* pojawi się ostrzeżenie, a aplikacja zostanie przy ostatnich danych. Diagnostyka: `python3 scripts/znicz_mecze.py --discover`.

## Instalacja jako aplikacja (PWA) i praca bez internetu

Strona jest instalowalna. Na Androidzie (Chrome) i na komputerze (Chrome/Edge) na dole ekranu głównego pojawia się karta „Aplikacja w telefonie” z przyciskiem **Zainstaluj aplikację**. Na iPhonie karta pokazuje, jak dodać stronę przez Safari (*Udostępnij → Do ekranu początkowego*); instalacja przez inną przeglądarkę na iPhonie nie działa. Zainstalowana aplikacja otwiera się bez paska przeglądarki, ma własną ikonę, a przytrzymanie ikony na Androidzie daje skróty do Śmieci, Pogody i Mszy. Bez internetu pokazuje ostatnio pobrane dane (plik `sw.js`). Karta znika po instalacji lub po kliknięciu „Nie teraz”.
Instalacja działa tylko pod adresem `https://…github.io/kruszyn/` (nie z pliku otwartego z dysku).

## Wydarzenia (formularz Google → arkusz → aplikacja)

Mieszkańcy dodają wydarzenia formularzem Google (przycisk w aplikacji). Odpowiedzi trafiają do Twojego arkusza, Ty zatwierdzasz wpis wpisując `TAK` w kolumnie „Zatwierdzone”, a robot co godzinę pobiera zatwierdzone wpisy i pokazuje je w aplikacji (nadchodzące + 5 ostatnich minionych, przycisk „Dodaj do kalendarza” i kalendarz do zasubskrybowania).

Jednorazowa konfiguracja arkusza:
1. W arkuszu: *Plik → Ustawienia* → Ustawienia regionalne: **Polska**, strefa czasowa: Warszawa.
2. Kolumna „Zatwierdzone” (N): zaznacz N2:N1000 → *Dane → Weryfikacja danych* → lista: `TAK`. Wpisuj zawsze wielkimi literami.
3. Dodaj nową zakładkę o nazwie **Publiczne**. W komórce A1 wklej (jedna linia, nazwę zakładki z odpowiedziami sprawdź na dole arkusza):
```
=IFERROR(QUERY('Odpowiedzi z formularza 1'!A:O; "select B, C, D, E, F, G, H, I, J, K where N = 'TAK' and (O is null or O <> 'TAK') and M is not null"; 1); "")
```
   Jeśli arkusz zgłosi błąd formuły, zamień średniki `;` na przecinki `,`.
4. *Plik → Udostępnij → Opublikuj w internecie*: w pierwszym polu wybierz **zakładkę Publiczne** (NIE „Cały dokument”, bo ujawniłbyś dane osób dodających), w drugim **Wartości rozdzielane przecinkami (.csv)** → *Opublikuj* → skopiuj link.
5. W repozytorium otwórz `kruszyn/wydarzenia_url.txt`, zastąp całą zawartość skopiowanym linkiem (jedna linia) i zapisz.
6. Uruchom *Run workflow*. W kroku *Pobierz wydarzenia z arkusza Google* ma być „Zapisano data/wydarzenia.json: nadchodzące N …”.

Codziennie: gdy dojdzie wpis (e-mail z formularza), sprawdź go i wpisz `TAK`; w ciągu godziny pojawi się w aplikacji. Wycofanie: `TAK` w kolumnie „Anulowane”. Nie usuwaj wierszy (minione wydarzenia są brane z tej samej tabeli) i nie zmieniaj ani nie dodawaj pytań w formularzu bez zmiany robota. Adres formularza w aplikacji jest w `index.html` (stała `FORM`).

## Nowy rok (2027)

Robot sam próbuje wczytać harmonogram na następny rok (adres `.../boleslawiec-2027r-gmina/kruszyn`). Dopóki COM-D go nie opublikuje, aplikacja pokazuje stare terminy, a po 31 grudnia – informację o braku terminów. Gdy harmonogram się pojawi, ręcznie uruchom workflow (krok 7). Daty zbiórek odzieży i gabarytów na 2027 trzeba dopisać ręcznie.

## Ważne zastrzeżenia

- **Repozytorium jest publiczne** – nie wpisuj w nim żadnych prywatnych danych (numerów prywatnych, adresów mieszkańców).
- GitHub wyłącza harmonogramy w repozytoriach nieaktywnych przez 60 dni. Robot od prądu zapisuje plik co godzinę, więc to zwykle nie grozi, ale gdyby harmonogram stanął, wejdź w *Actions* i kliknij *Enable workflow* (albo po prostu zrób dowolną edycję `wies.json`).
- Pogoda i jakość powietrza pochodzą z Open-Meteo (bez klucza), a prąd i apteki mają linki do źródeł oficjalnych – dane „wiążące” zawsze sprawdzaj u źródła.
- W razie wątpliwości co do śmieci: COM-D, tel. 76 870 21 68.
