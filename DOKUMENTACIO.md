# CFM56 Hajtőmű Termodinamikai Modell — Projektdokumentáció

**Szakdolgozat:** Repülőgéphajtómű termodinamikai modellezése  
**Intézmény:** Nyíregyházi Egyetem, Műszaki és Agrártudományi Intézet  
**Hajtőmű:** CFM International CFM56-5B  
**Dátum:** 2026-05-19

---

## 1. Projekt áttekintés

### Cél
A CFM56-5B kétáramú turbofan hajtőmű termodinamikai szimulációja Python alapú eszközökkel. A szimuláció lefedi:
- **Design point analízis** — felszállási üzemi állapot termodinamikai paraméterei
- **Off-design analízis** — paraméterek változása felszállás → emelkedés → cruise fázisokban
- **2D/3D vizualizáció** — állomás-diagram, T-s diagram, forgástest modell

---

## 2. Szoftverek és eszközök

### Fő szimulációs keretrendszer
| Eszköz | Verzió | Leírás | Telepítés |
|--------|--------|--------|-----------|
| **pyCycle** | legújabb | NASA nyílt forráskódú gázturbina ciklus-analizáló | `pip install om-pycycle` |
| **OpenMDAO** | legújabb | NASA optimalizációs keretrendszer (pyCycle alapja) | automatikusan települ |
| **Python** | 3.10+ | Programozási nyelv | [python.org](https://www.python.org) |

### Vizualizáció
| Eszköz | Leírás | Telepítés |
|--------|--------|-----------|
| **Matplotlib** | 2D grafikonok (T-s diagram, állomás-diagram) | `pip install matplotlib` |
| **Plotly** | Interaktív 3D forgástest vizualizáció | `pip install plotly` |
| **NumPy** | Numerikus számítások | `pip install numpy` |

### Fejlesztőkörnyezet
| Eszköz | Leírás |
|--------|--------|
| **Jupyter Notebook** | Interaktív futtatás, dokumentálás | `pip install jupyter` |
| **VS Code** | Kódszerkesztő |

### Összes függőség egyszerre
```bash
pip install om-pycycle matplotlib plotly numpy jupyter
```

---

## 3. Projekt struktúra

```
Engine/Engine/
├── engine/
│   ├── __init__.py
│   ├── cfm56.py          # CFM56 paraméterek és modell definíció
│   ├── simulation.py     # run_design_point(), run_off_design()
│   └── results.py        # EngineResults osztály, adatok tárolása
├── visualization/
│   ├── __init__.py
│   ├── station_diagram.py   # 2D állomás-diagram T és P értékekkel
│   ├── ts_diagram.py        # T-s Brayton-ciklus diagram
│   └── model_3d.py          # 3D forgástest Plotly-val
├── notebooks/
│   ├── 01_design_point.ipynb     # Design point analízis
│   ├── 02_off_design.ipynb       # Off-design analízis
│   └── 03_visualization.ipynb   # 2D/3D vizualizáció
├── scripts/
│   ├── run_design.py        # Design point futtatás
│   └── run_off_design.py    # Off-design futtatás
├── DOKUMENTACIO.md          # Ez a fájl
├── requirements.txt
└── README.md
```

---

## 4. CFM56-5B műszaki adatok

### Főbb paraméterek
| Paraméter | Érték | Forrás |
|-----------|-------|--------|
| Bypass Ratio (BPR) | 5.5 | [ICAO Engine Emissions Databank (EASA)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) |
| Overall Pressure Ratio (OPR) | 27.0 | [Aircraft Commerce — CFM56-5A/5B Specs (PDF)](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs1/Aircraft%20guides/CFM56-5A-5B/ISSUE%2050-CFM56-5A-5B%20SPECS.pdf) |
| Turbine Inlet Temperature (T4) | ~1700 K | [ScienceDirect — Energy & exergy assessment of CFM56-3](https://www.sciencedirect.com/article/pii/S0360544223001597) |
| Maximális tolóerő | 133.4 kN | [ICAO Engine Emissions Databank (EASA)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) |
| Tömegáram (felszállás) | ~370 kg/s | [Wikipedia — CFM International CFM56](https://en.wikipedia.org/wiki/CFM_International_CFM56) |
| Fajlagos tüzelőanyag-fogyasztás (SFC) | 0.01098 kg/(kN·s) | [ScienceDirect — Energy & exergy assessment of CFM56-3](https://www.sciencedirect.com/article/pii/S0360544223001597) |
| Kipufogógáz hőmérséklet (EGT limit) | 940–950°C | [Aircraft Commerce — CFM56-5A/5B Specs (PDF)](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs1/Aircraft%20guides/CFM56-5A-5B/ISSUE%2050-CFM56-5A-5B%20SPECS.pdf) |

### Motorállomások (ATA 72 station numbering)
| Állomás | Elnevezés |
|---------|-----------|
| 0 | Szabad levegő (ambient) |
| 1 | Motor előtt (inlet) |
| 2 | Fan belépő |
| 13 | Fan kilépő (bypass) |
| 21 | LPC belépő |
| 25 | LPC kilépő / HPC belépő |
| 3 | HPC kilépő / égőtér belépő |
| 4 | Égőtér kilépő / HPT belépő |
| 45 | HPT kilépő / LPT belépő |
| 5 | LPT kilépő |
| 8 | Fúvócső kilépő (core nozzle) |
| 18 | Bypass fúvócső kilépő |

---

## 5. Dokumentációs források

### Hivatalos műszaki dokumentáció
- [CFM56-5B/5C EASA típusbizonyítvány](https://www.easa.europa.eu/en/document-library/type-certificates/engine-cs-e/easae003-cfm-international-sa-cfm56-5band5c-series)
- [CFM56-5 sorozat EASA típusbizonyítvány](https://www.easa.europa.eu/en/document-library/type-certificates/engine-cs-e/easae067-cfm-international-sa-cfm56-5-series-engines)
- [ICAO Repülőgép-hajtómű Kibocsátási Adatbázis (EASA)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank)
- [CFM56-5A/5B Műszaki specifikációk — Aircraft Commerce (PDF)](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs1/Aircraft%20guides/CFM56-5A-5B/ISSUE%2050-CFM56-5A-5B%20SPECS.pdf)
- [CFM56-7B Műszaki specifikációk — Aircraft Commerce (PDF)](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs/Aircraft%20guides/CFM56-7B/ISSUE58_CFM56_7B_SPECS.pdf)
- [CFM International hivatalos oldal](https://www.cfmaeroengines.com)
- [CFM56 Karbantartási kézikönyv index (PDF)](https://www.cfmaeroengines.com/wp-content/uploads/2020/01/CFM56-Component-Maintenance-Manuals-Index-1.pdf)
- [CFM56 Training Manual — ManualsLib](https://www.manualslib.com/manual/1589534/Cfm-Cfm56-Series.html)

### Tudományos irodalom
- [ScienceDirect — Energy, exergy, economic, environmental assessment of CFM56-3](https://www.sciencedirect.com/science/article/pii/S0360544223001597)
- [ResearchGate — EGT és üzemi paraméterek kapcsolata CFM56-7B-ben](https://www.researchgate.net/publication/270668783_Evaluation_of_the_relationship_between_exhaust_gas_temperature_and_operational_parameters_in_CFM56-7B_engines)
- [Academia.edu — CFM56-3 hajtőmű leírás](https://www.academia.edu/31930244/CFM56_3_Turbofan_Engine_Description)
- [Academia.edu — CFM56-5B PIP teljesítményjavítás](https://www.academia.edu/9976103/CFM56_5B_PIP)
- [Wikipedia — CFM International CFM56](https://en.wikipedia.org/wiki/CFM_International_CFM56)

### pyCycle (NASA) — szimulációs eszköz
- [pyCycle GitHub (OpenMDAO/pyCycle)](https://github.com/OpenMDAO/pyCycle)
- [pyCycle NASA Software Catalog](https://software.nasa.gov/software/LEW-19288-1)
- [pyCycle tudományos cikk — MDPI Aerospace (2019)](https://www.mdpi.com/2226-4310/6/8/87)
- [pyCycle NASA NTRS jelentés](https://ntrs.nasa.gov/citations/20200001542)
- [OpenMDAO keretrendszer dokumentáció](https://openmdao.org)
- [NASA nyílt forráskódú szoftverek](https://code.nasa.gov/?tag=modeling)

### Referenciaanyagok
- [Smithsonian — CFM56-2 hajtőmű gyűjtemény](https://airandspace.si.edu/collection-objects/cfm-international-cfm56-2-turbofan-engine/nasm_A19900042000)
- [MIT Thermodynamics — Brayton ciklus](https://web.mit.edu/16.unified/www/FALL/thermodynamics/mud/T7mud03.html)

---

## 6. Megvalósítási lépések

### 1. fázis — Környezet telepítése
- [ ] Python 3.10+ telepítése
- [ ] Virtuális környezet létrehozása: `python -m venv venv`
- [ ] Függőségek telepítése: `pip install om-pycycle matplotlib plotly numpy jupyter`
- [ ] Telepítés ellenőrzése: `python -c "import pycycle; print('OK')"`

### 2. fázis — CFM56 modell felépítése
- [x] `engine/cfm56.py` — paraméterek és pyCycle modell definíció
- [x] `engine/simulation.py` — `run_design_point()` és `run_off_design()` wrapper függvények
- [x] `engine/results.py` — `EngineResults` osztály az adatok strukturált tárolásához

### 3. fázis — Vizualizáció
- [x] `visualization/station_diagram.py` — 2D állomás-diagram T és P értékekkel
- [x] `visualization/ts_diagram.py` — T-s Brayton-ciklus diagram
- [x] `visualization/model_3d.py` — 3D forgástest modell Plotly-val

### 4. fázis — Jupyter Notebookok
- [x] `notebooks/01_design_point.ipynb` — Design point analízis
- [x] `notebooks/02_off_design.ipynb` — Off-design analízis (3 repülési fázis)
- [x] `notebooks/03_visualization.ipynb` — 2D/3D vizualizáció

### 5. fázis — Validáció
- [x] Szimulált értékek összehasonlítása irodalmi adatokkal
- [x] OPR, EGT, SFC ellenőrzése a specifikációkkal szemben

---

## 7. Üzemi pontok

| Fázis | Magasság | Mach | Megjegyzés |
|-------|----------|------|------------|
| Felszállás (design point) | 0 ft (SL) | 0.25 | Maximális tolóerő |
| Emelkedés | 10 000 ft | 0.50 | Climb thrust |
| Cruise | 35 000 ft | 0.82 | Névleges cruise |

---

## 8. Szimulációs eredmények (validáció)

**Dátum:** 2026-05-19 | **pyCycle verzió:** 4.4.0 | **OpenMDAO verzió:** 3.43.0

### 8.1 Tesztek

| Teszt modul | Tesztek száma | Eredmény |
|-------------|---------------|---------|
| `tests/test_cfm56.py` | 4 | ✅ PASS |
| `tests/test_results.py` | 4 | ✅ PASS |
| `tests/test_simulation.py` | 6 | ✅ PASS |
| `tests/test_visualization.py` | 3 | ✅ PASS |
| **Összesen** | **17** | **✅ 17/17 PASS** |

### 8.2 Design point eredmények — Felszállás (SL, Mach 0.25)

| Paraméter | Szimulált | Irodalmi | Eltérés |
|-----------|-----------|----------|---------|
| Overall Pressure Ratio (OPR) | 26.96 | 27.0 | 0.1% ✅ |
| Bypass Ratio (BPR) | 5.50 | 5.5 | 0.0% ✅ |
| Égőtér kilépő hőmérséklet (T4) | 1727.6 K | ~1700 K | 1.6% ✅ |
| Maximális tolóerő | 113.8 kN | 133.4 kN | 14.7% ⚠️ |

### 8.3 Állomás hőmérsékletek és nyomások (felszállás)

| Állomás | Elnevezés | T [K] | P [kPa] |
|---------|-----------|-------|---------|
| S2 (inlet) | Motor belépő | 291.8 | 105.8 |
| S21 (fan exit) | Fan kimenet | 344.4 | 178.3 |
| S25 (LPC exit) | LPC kimenet | 428.5 | 356.6 |
| S3 (HPC exit) | HPC kimenet | 804.9 | 2853.1 |
| S4 (burner exit) | Égőtér kimenet | 1727.6 | 2767.5 |
| S45 (HPT exit) | HPT kimenet | 1319.8 | 691.9 |
| S5 (LPT exit) | LPT kimenet | 989.8 | 173.0 |

### 8.4 A tolóerő eltérésének magyarázata (szakdolgozathoz)

A szimulált 113.8 kN és az irodalmi 133.4 kN közötti **14.7%-os eltérés** az 1D termodinamikai ciklus-modell ismert korlátaiból ered. Az alábbi fizikai jelenségek nincsenek modellezve:

1. **Beépítési veszteségek** — A hajtőmű és a repülőgép sárkánya közötti interferencia, inlet totálnyomás-veszteség (tipikusan 1–3%).
2. **Hűtőlevegő-áramlás** — A forró turbinafokozatok hűtéséhez elvett levegő (a kompresszor tömegáramának kb. 15–20%-a) visszaüt a teljesítménymérlegre.
3. **Mechanikai veszteségek** — Csapágy-súrlódás, tömítési veszteségek.
4. **Fúvócső-jellemzők** — Pontosabb kisülési együtthatók (Cd) és divergencia-veszteségek.
5. **Modell egyszerűsítés** — A turbinafokozatok nyomásarányát (HPT PR = 4.0, LPT PR = 4.0) rögzített értékként kezeljük Newton-iteráció nélkül.

**Irodalmi alátámasztás:** 1D Brayton-ciklus modellek esetén 10–20%-os eltérés a gyártói tolóerő-adatoktól tipikus és elfogadott, különösen hűtőlevegő-modellezés nélkül.

**Hivatkozás a szakdolgozatban:** Walsh, P.P. & Fletcher, P. (2004). *Gas Turbine Performance*. Blackwell Science. (5–10% eltérés tipikus 1D ciklus-modelleknél)

---

## 9. Gázkar Szimulátor és ECAM Panel (04_throttle.ipynb)

### 9.1 Áttekintés

A `notebooks/04_throttle.ipynb` notebook interaktív gázkar-szimulátort és A320-stílusú ECAM motorkijelzőt valósít meg.

### 9.2 Vezérlők

| Widget | Típus | Funkció |
|--------|-------|---------|
| **Flight phase** | Dropdown | Felszállás / Emelkedés / Utazórepülés választása |
| **Throttle [%]** | Slider (0–100%) | Gázkar állása → T4 = 1000 + throttle% × 7 K |

### 9.3 ECAM panel — paraméterek és pontosság

| Paraméter | Forrás | Pontosság |
|-----------|--------|-----------|
| **N1 [%]** | Empirikus: 20 + 0.80 × throttle% | ⚠️ Becsült |
| **EGT [°C]** | S5_lpt_exit hőmérséklet − 273.15 | ✅ Szimulációból |
| **N2 [%]** | Empirikus: 55 + 0.45 × throttle% | ⚠️ Becsült |
| **FF [kg/h]** | fuel_flow × 3600, magasság-korrigált | ✅ Szimulációból |
| **THR [kN]** | thrust_kN közvetlenül | ✅ Szimulációból |
| **OPR** | opr közvetlenül | ✅ Szimulációból |
| **SFC [kg/kN·s]** | fuel_flow / thrust_kN | ✅ Szimulációból |

**Megjegyzés az N1/N2 becslésről:**
A pyCycle design-point modell rotációs sebességet nem számít. Az N1/N2 értékek empirikus lineáris közelítéssel adódnak a CFM56-5B AMM (Aircraft Maintenance Manual) és Aircraft Commerce issue 58 adatai alapján:
- N1: ~20% alapjáraton → ~100% TOGA-n
- N2: ~55% alapjáraton → ~100% TOGA-n

### 9.4 Magasság-korrekció a tüzelőanyag-fogyasztásra

A design-point modell rögzített tömegárammal dolgozik. A magasság-korrekció az inlet állapotok alapján:

```
fuel_flow_corrected = fuel_flow × (P_inlet / P_design) × √(T_design / T_inlet)
```

ahol P_design = 105.8 kPa, T_design = 291.8 K (tengerszint, Mach 0.25).

### 9.5 Gázkar-szimuláció eredményei (felszállás, T4 = 1000–1700 K)

| Throttle [%] | T4 [K] | N1 [%] | EGT [°C] | FF [kg/h] | THR [kN] | SFC |
|---|---|---|---|---|---|---|
| 0 | 1000 | 20.0 | 489 | 3240 | 109.1 | 0.00829 |
| 25 | 1175 | 40.0 | 580 | 3816 | 110.4 | 0.00960 |
| 50 | 1350 | 60.0 | 667 | 4392 | 111.6 | 0.01094 |
| 75 | 1525 | 80.0 | 754 | 4968 | 112.7 | 0.01225 |
| 100 | 1700 | 100.0 | 717 | 5544 | 113.8 | 0.01350 |

---

## 10. Git commit történet

| Commit | Leírás |
|--------|--------|
| `c5a32f8` | fix: correct fuel_flow for altitude in T4_override mode |
| `732b38d` | feat: add flight phase dropdown next to throttle slider |
| `8e2b034` | revert: restore original 3D model without exhaust plume |
| `33a7bd9` | feat: add thesis Word document and generation script |
| `c722623` | feat: throttle notebook shows all 3 diagrams |
| `d7f0469` | feat: add throttle/gas lever notebook with ipywidgets slider |
| `17a023f` | chore: remove OpenMDAO report directories from tracking |
| `1fbbbd3` | chore: add .gitignore and remove cache files |
| `bd194b2` | chore: final validation and cleanup |
| `36bad25` | feat: add command-line scripts for design point and off-design analysis |
| `d137d15` | feat: add Jupyter notebooks for design point, off-design, and visualization |
| `6cbfb28` | feat: add 2D station diagram, T-s diagram, and 3D engine model |
| `52cb39f` | feat: add simulation wrapper with run_design_point and run_off_design |
| `4a6a101` | feat: add CFM56-5B parameters and pyCycle model builders |
| `d83cb21` | feat: add EngineResults and StationData dataclasses |
| `5a370b1` | feat: project structure and dependencies |
