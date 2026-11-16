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

## Nowy rok (2027)

Robot sam próbuje wczytać harmonogram na następny rok (adres `.../boleslawiec-2027r-gmina/kruszyn`). Dopóki COM-D go nie opublikuje, aplikacja pokazuje stare terminy, a po 31 grudnia – informację o braku terminów. Gdy harmonogram się pojawi, ręcznie uruchom workflow (krok 7). Daty zbiórek odzieży i gabarytów na 2027 trzeba dopisać ręcznie.

## Ważne zastrzeżenia

- **Repozytorium jest publiczne** – nie wpisuj w nim żadnych prywatnych danych (numerów prywatnych, adresów mieszkańców).
- GitHub wyłącza harmonogramy w repozytoriach nieaktywnych przez 60 dni. Robot od prądu zapisuje plik co godzinę, więc to zwykle nie grozi, ale gdyby harmonogram stanął, wejdź w *Actions* i kliknij *Enable workflow* (albo po prostu zrób dowolną edycję `wies.json`).
- Pogoda i jakość powietrza pochodzą z Open-Meteo (bez klucza), a prąd i apteki mają linki do źródeł oficjalnych – dane „wiążące” zawsze sprawdzaj u źródła.
- W razie wątpliwości co do śmieci: COM-D, tel. 76 870 21 68.
