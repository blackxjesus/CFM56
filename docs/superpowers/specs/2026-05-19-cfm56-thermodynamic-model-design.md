# CFM56 Hajtőmű Termodinamikai Modell — Design Specifikáció

**Dátum:** 2026-05-19  
**Projekt:** Repülőgéphajtómű termodinamikai modellezése (BSc szakdolgozat)  
**Intézmény:** Nyíregyházi Egyetem, Műszaki és Agrártudományi Intézet  
**Hajtőmű:** CFM International CFM56-5B

---

## 1. Áttekintés

A projekt célja a CFM56-5B kétáramú turbofan hajtőmű termodinamikai szimulációjának elkészítése Python alapon, a NASA pyCycle könyvtárra építve. A szimuláció design point és off-design analízist végez három repülési fázisra, az eredményeket 2D és 3D vizualizációval szemlélteti, és Jupyter Notebookokon keresztül futtatható.

---

## 2. Hajtőmű — CFM56-5B

| Paraméter | Érték | Forrás |
|-----------|-------|--------|
| Bypass Ratio (BPR) | 5.5 | [ICAO Engine Emissions Databank (EASA)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) |
| Overall Pressure Ratio (OPR) | 27.0 | [Aircraft Commerce — CFM56-5A/5B Specs (PDF)](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs1/Aircraft%20guides/CFM56-5A-5B/ISSUE%2050-CFM56-5A-5B%20SPECS.pdf) |
| Turbine Inlet Temperature (T4) | ~1700 K | [ScienceDirect — Energy & exergy assessment of CFM56-3](https://www.sciencedirect.com/article/pii/S0360544223001597) |
| Maximális tolóerő | 133.4 kN | [ICAO Engine Emissions Databank (EASA)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) |
| Tömegáram (felszállás) | ~370 kg/s | [Wikipedia — CFM International CFM56](https://en.wikipedia.org/wiki/CFM_International_CFM56) |
| EGT limit | 940–950°C | [Aircraft Commerce — CFM56-5A/5B Specs (PDF)](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs1/Aircraft%20guides/CFM56-5A-5B/ISSUE%2050-CFM56-5A-5B%20SPECS.pdf) |

### Üzemi pontok

| Fázis | Magasság | Mach |
|-------|----------|------|
| Felszállás (design point) | 0 ft | 0.25 |
| Emelkedés | 10 000 ft | 0.50 |
| Cruise | 35 000 ft | 0.82 |

---

## 3. Megközelítés

**pyCycle + egyedi wrapper réteg.** A NASA pyCycle könyvtár végzi a termodinamikai számításokat (CEA-alapú anyagadatok, OpenMDAO solver). Fölé egy tiszta Python csomag (`engine/`) kerül, amely elrejti az OpenMDAO komplexitást és egyszerű függvényhívásokat (`run_design_point()`, `run_off_design()`) biztosít a Notebookoknak.

---

## 4. Architektúra

```
Engine/Engine/
├── engine/
│   ├── __init__.py
│   ├── cfm56.py          # CFM56-5B paraméterek és pyCycle modell definíció
│   ├── simulation.py     # run_design_point(), run_off_design() wrapper
│   └── results.py        # EngineResults adatosztály
├── visualization/
│   ├── __init__.py
│   ├── station_diagram.py   # 2D állomás-diagram Matplotlib-tel
│   ├── ts_diagram.py        # T-s Brayton-ciklus diagram
│   └── model_3d.py          # 3D forgástest Plotly-val
├── notebooks/
│   ├── 01_design_point.ipynb
│   ├── 02_off_design.ipynb
│   └── 03_visualization.ipynb
├── scripts/
│   ├── run_design.py
│   └── run_off_design.py
├── docs/
│   └── superpowers/specs/   # Ez a fájl
├── DOKUMENTACIO.md
└── requirements.txt
```

---

## 5. Komponensek részletezése

### 5.1 `engine/cfm56.py`
- CFM56-5B nyilvános paramétereit definiálja konstansként
- Felépíti a pyCycle kétáramú turbofan modellt (inlet → fan → splitter → LPC → HPC → combustor → HPT → LPT → nozzle + bypass nozzle)
- Visszaadja a konfigurált OpenMDAO `Problem` objektumot

### 5.2 `engine/simulation.py`
- `run_design_point(altitude, mach, throttle)` → `EngineResults`
- `run_off_design(flight_phases: list)` → `list[EngineResults]`
- Beállítja az OpenMDAO solver-t, futtatja a szimulációt, becsomagolja az eredményeket

### 5.3 `engine/results.py`
- `EngineResults` dataclass: minden állomás T (K), P (kPa), h (kJ/kg) értékei; tolóerő, SFC, hatásfok értékek
- `to_dataframe()` metódus pandas DataFrame exporthoz
- `summary()` metódus konzol-kimenetre

### 5.4 `visualization/station_diagram.py`
- Matplotlib alapú sematikus motordiagram
- Minden állomáson T és P értékek feliratozva
- Hőmérséklet-alapú színskála (kék→piros)
- PNG exportálható (szakdolgozatba illeszthető)

### 5.5 `visualization/ts_diagram.py`
- T-s diagram az összes üzemi pontra (felszállás / emelkedés / cruise)
- Izentrópikus és izobar folyamatok jelölve
- Minden fázis külön színnel

### 5.6 `visualization/model_3d.py`
- CFM56 keresztmetszeti profil pontjai alapján forgástest generálás
- Plotly `Surface` trace tengelykörüli forgatással
- Hőmérséklet-eloszlás megjelenítése színskálaként
- Interaktív HTML export (böngészőben forgatható)

### 5.7 Jupyter Notebookok
- `01_design_point.ipynb`: felszállási állapot részletes analízise, táblázatok, diagramok
- `02_off_design.ipynb`: három fázis összehasonlítása, paraméterváltozások
- `03_visualization.ipynb`: 2D/3D vizualizáció összefoglaló

---

## 6. Függőségek

```
om-pycycle
openmdao
numpy
matplotlib
plotly
jupyter
pandas
```

---

## 7. Validáció

A szimulált értékek ellenőrzése az alábbi nyilvános adatokkal:
- ICAO kibocsátási adatbázis (tolóerő, SFC)
- Aircraft Commerce CFM56-5A/5B specifikációs dokumentum (OPR, EGT)
- ScienceDirect CFM56-3 exergia analízis (hatásfok értékek)

Elfogadott eltérés: ±5% a tervezési paraméterektől.

---

## 8. Korlátok

- A szimuláció termodinamikai ciklus-szintű (nem CFD, nem 3D áramlás)
- A 3D vizualizáció forgástest közelítés, nem valódi CAD geometria
- Égési kémia egyszerűsített (kerozin → CO₂ + H₂O, CEA-alapú)
- Mechanikai veszteségek (csapágy, tömítés) nem modellezve

---

## 9. Hivatkozások

- [pyCycle GitHub](https://github.com/OpenMDAO/pyCycle)
- [pyCycle NASA NTRS](https://ntrs.nasa.gov/citations/20200001542)
- [EASA CFM56-5B típusbizonyítvány](https://www.easa.europa.eu/en/document-library/type-certificates/engine-cs-e/easae003-cfm-international-sa-cfm56-5band5c-series)
- [ICAO Kibocsátási Adatbázis](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank)
- [Aircraft Commerce CFM56-5A/5B specifikáció](https://www.aircraft-commerce.com/wp-content/uploads/aircraft-commerce-docs1/Aircraft%20guides/CFM56-5A-5B/ISSUE%2050-CFM56-5A-5B%20SPECS.pdf)
