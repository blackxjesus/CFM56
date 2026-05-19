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
- [ ] `engine/cfm56.py` — paraméterek és pyCycle modell definíció
- [ ] `engine/simulation.py` — `run_design_point()` és `run_off_design()` wrapper függvények
- [ ] `engine/results.py` — `EngineResults` osztály az adatok strukturált tárolásához

### 3. fázis — Vizualizáció
- [ ] `visualization/station_diagram.py` — 2D állomás-diagram T és P értékekkel
- [ ] `visualization/ts_diagram.py` — T-s Brayton-ciklus diagram
- [ ] `visualization/model_3d.py` — 3D forgástest modell Plotly-val

### 4. fázis — Jupyter Notebookok
- [ ] `notebooks/01_design_point.ipynb` — Design point analízis
- [ ] `notebooks/02_off_design.ipynb` — Off-design analízis (3 repülési fázis)
- [ ] `notebooks/03_visualization.ipynb` — 2D/3D vizualizáció

### 5. fázis — Validáció
- [ ] Szimulált értékek összehasonlítása irodalmi adatokkal
- [ ] OPR, EGT, SFC ellenőrzése a specifikációkkal szemben

---

## 7. Üzemi pontok

| Fázis | Magasság | Mach | Megjegyzés |
|-------|----------|------|------------|
| Felszállás (design point) | 0 ft (SL) | 0.25 | Maximális tolóerő |
| Emelkedés | 10 000 ft | 0.50 | Climb thrust |
| Cruise | 35 000 ft | 0.82 | Névleges cruise |
