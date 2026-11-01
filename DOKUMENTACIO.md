# CFM56 Hajtómű Termodinamikai Modell — Projektdokumentáció

**Szakdolgozat:** CFM56-5B repülőgéphajtómű termodinamikai ciklus-analízise Python alapú szimulációval
**Intézmény:** Nyíregyházi Egyetem, Műszaki és Agrártudományi Intézet
**Hajtómű:** CFM International CFM56-5B (vizsgált változat: -5B1)
**Dokumentáció állapota:** 2026-11-01. A számok forrása a `data/results.csv` és a `data/design_point.pkl`.

---

## 1. Projekt áttekintés

A projekt a CFM56-5B kétáramú turbofan hajtómű Python alapú szimulációja. Három részből áll:

1. **Stacioner ciklusmodell** (pyCycle): tengely-egyensúllyal zárt tervezési pont statikus felszállásra, és valódi off-design számítás rögzített geometriával.
2. **Tranziens indítási modell** (tiszta Python): redukált rendű HP-tengely modell, FADEC-logika, négy indítási hiba.
3. **Interaktív pilótafülke-alkalmazás** (Streamlit): kattintható ENG panel, élő E/WD, trendek, ciklusdiagramok.

---

## 2. Szoftverek és eszközök

Két függőségfájl van. A `requirements-sim.txt` a teljes, rögzített környezet (szimuláció, tesztek, app). A `requirements.txt` csak az app csomagjait tartalmazza, ezt telepíti a Streamlit Cloud, mert az app nem használ pyCycle-t.

| Eszköz | Verzió | Szerep |
|--------|--------|--------|
| Python | 3.12 | Futtatókörnyezet |
| om-pycycle | 4.4.0 | NASA gázturbina-ciklusmodell |
| OpenMDAO | 3.45.2 | Implicit megoldó keretrendszer |
| NumPy | 2.2.6 | Numerika. **A pyCycle 4.4.0 NumPy 2.3+ alatt hibával leáll** |
| Streamlit | 1.66.1 | Alkalmazás. **Legalább 1.50 kell** a `width='stretch'` miatt |
| Matplotlib | 3.11.2 | 2D diagramok |
| Plotly | 7.1.0 | Trendek és 3D modell |
| Pillow, streamlit-image-coordinates | 13.0.0, 0.4.1 | Kattintható ENG panel |

Fejlesztéshez külön: `pytest` (tesztek), `python-docx` (dokumentum-generálás), `jupyter` (notebookok).

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-sim.txt
.venv/bin/pip install pytest python-docx
.venv/bin/python -m streamlit run app.py
```

Ismert korlát: a Streamlit jelzi, hogy a `st.components.v1.html` kivezetésre kerül (`st.iframe` a helyettesítője). Az 1.66.1 verzióval még működik, ezért ez a felső határ mindkét fájlban.

---

## 3. Projekt struktúra

```
Engine/Engine/
├── app.py                     # Streamlit pilótafülke-alkalmazás
├── precompute.py              # 63 off-design pont kiszámítása a data/ mappába
├── generate_thesis.py         # A dolgozat .docx generátora
├── engine/
│   ├── cfm56.py               # Paraméterek, CFM56Cycle, CFM56MultiPoint, VBV-ütemezés
│   ├── simulation.py          # run_design_point(), OffDesignSolver, run_off_design()
│   ├── results.py             # EngineResults, StationData, StartTransient
│   ├── start_transient.py     # Indítási plant-modell és simulate_start()
│   ├── fadec.py               # ENG MODE / MASTER / BLEED → vezérlőparancsok
│   ├── playback.py            # Lejátszás és pilótafülke-állapotgép
│   └── trend.py               # Folytonos trend elsőrendű késleltetéssel
├── visualization/
│   ├── ewd.py                 # A320 E/WD kijelző (SVG)
│   ├── airbus_panel.py        # Kattintható ENG panel
│   ├── ecam.py                # EPR-számítás, ECAM-segédfüggvények
│   ├── start_plot.py          # Trendgrafikonok
│   ├── station_diagram.py     # 2D állomás-diagram
│   ├── ts_diagram.py          # T-s diagram
│   └── model_3d.py            # 3D forgástest
├── data/
│   ├── lookup.pkl             # 63 EngineResults az apphoz
│   ├── design_point.pkl       # Tervezési pont
│   └── results.csv            # Ugyanezek táblázatban
├── notebooks/                 # 01–04: tervezési pont, off-design, vizualizáció, gázkar
├── scripts/                   # Parancssoros futtatás, felkészítő .docx generálása
├── tests/                     # 97 pytest-teszt
├── docs/
│   ├── meghallgatas_felkeszules.md
│   └── superpowers/           # Tervek és specifikációk
├── CFM56_szakdolgozat.docx    # A dolgozat
├── meghallgatas_felkeszules.docx
├── DOKUMENTACIO.md            # Ez a fájl
├── README.md
├── requirements.txt          # Csak az app (Streamlit Cloud)
└── requirements-sim.txt      # Teljes rögzített környezet
```

---

## 4. Modellbemenetek és CFM56-5B adatok

### 4.1 Tervezési bemenetek

Ezek a modell bemenetei, ezért egyezésük az irodalommal **nem validálás**.

| Paraméter | Érték | Eredet |
|-----------|-------|--------|
| BPR | 5,5 | Nyilvános összesítő adat |
| Tömegáram | 370 kg/s | Nyilvános tartomány: 368–439 kg/s |
| OPR | 27 (számítva 26,96) | Saját felvétel |
| Fan / LPC / HPC PR | 1,685 / 2,0 / 8,0 | Saját felvétel, a szorzatuk adja az OPR-t |
| T4 | 1700 K | Saját becslés, a gyártói érték nem publikus |
| Hatásfok: fan / LPC / HPC / HPT / LPT | 0,89 / 0,89 / 0,87 / 0,89 / 0,90 | Tipikus szakirodalmi értékek |
| Égőtéri nyomásveszteség | 3 % | Tipikus érték |
| Fúvócső Cv: mag / bypass | 0,9999 / 0,9975 | Modellbemenet |

### 4.2 Hivatkozási adatok

| Adat | Érték | Forrás |
|------|-------|--------|
| Felszállási tolóerő (-5B1), statikus | 133,45 kN | EASA TCDS E.003 |
| Tolóerő-tartomány | 96,1–142,3 kN | EASA TCDS E.003 |
| EGT-határ, felszállás / indítás | 950 °C / 725 °C | EASA TCDS E.003 |
| Legnagyobb N1 / N2 | 5200 1/min (104 %) / 15 183 1/min (105 %) | EASA TCDS E.003 |
| Statikus SFC | 9,25–10,02 g/(kN·s) | Wikipedia, elsődleges forrással kiváltandó |
| Utazó SFC (-5B4) | 15,4 g/(kN·s) | Wikipedia, elsődleges forrással kiváltandó |

### 4.3 Állomások

| Kód | Elnevezés |
|-----|-----------|
| S0 | Szabad levegő |
| S2 | Levegőbevezető kimenet |
| S21 | Ventilátor kimenet |
| S25 | LPC kimenet |
| S3 | HPC kimenet |
| S4 | Égéstér kimenet |
| S45 | HPT kimenet |
| S5 | LPT kimenet (a modell EGT-je) |
| S8 | Mag-fúvócső |
| S18 | Bypass-fúvócső |

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
- [Academia.edu — CFM56-3 hajtómű leírás](https://www.academia.edu/31930244/CFM56_3_Turbofan_Engine_Description)
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
- [Smithsonian — CFM56-2 hajtómű gyűjtemény](https://airandspace.si.edu/collection-objects/cfm-international-cfm56-2-turbofan-engine/nasm_A19900042000)
- [MIT Thermodynamics — Brayton ciklus](https://web.mit.edu/16.unified/www/FALL/thermodynamics/mud/T7mud03.html)

A dolgozat hivatkozási listája a `generate_thesis.py` végén található. Az ellenőrzési teendőket a felkészítő 2. fejezete tartalmazza.

---

## 6. Ciklusmodell

### 6.1 Tervezési pont

Tengerszinti statikus felszállás (Mach ≈ 0, a modellben 0,001 a szingularitás elkerülésére).
A ciklust három implicit egyensúly zárja:

| Ismeretlen | Feltétel |
|------------|----------|
| FAR | Égéstér-kilépő hőmérséklet = T4 |
| HPT PR | HP tengely nettó teljesítménye = 0 |
| LPT PR | LP tengely nettó teljesítménye = 0 |

### 6.2 Off-design

A `CFM56MultiPoint` a tervezési pontból rögzíti a fúvócső-keresztmetszeteket és a jelleggörbe-skálázást. Ismeretlenek:

| Ismeretlen | Feltétel |
|------------|----------|
| FAR | T4 = gázkar szerinti célérték |
| W (tömegáram) | Mag-fúvócső terület = tervezési |
| BPR | Bypass-fúvócső terület = tervezési |
| N1, N2 | Tengely-egyensúly |

A tömegáram, BPR, OPR, N1 és N2 tehát eredmény. Az `OffDesignSolver` kis lépésekben halad (legfeljebb 2500 ft, 0,05 Mach, 50 K), és minden pontot ellenőriz: T4-cél, tengelymérleg, mag-fúvócső nyomása.

**Érvényesség:** egy pont érvénytelen, ha az R-line kilép a jelleggörbéből (fan 1,0–2,6; LPC és HPC 1,0–3,0), vagy N1 > 104 %, N2 > 105 %. Az érvénytelen pontok megmaradnak, de jelölve vannak, és az app figyelmeztet rájuk.

**VBV:** T4 ≥ 1650 K felett zárt, 1000 K-ig lineárisan 30 %-ra nyit. Ez a korrigált N2 szerinti FADEC-vezérlés egyszerűsítése.

**Gázkar:** T4 = 1000 + 7 · gázkar% [K], 5 %-os lépésekben. A 0 % **nem földi alapjárat**, hanem kis részterhelés.

### 6.3 Repülési fázisok

| Fázis | Magasság | Mach |
|-------|----------|------|
| Tervezési pont | 0 ft | ≈ 0 |
| Felszállás | 0 ft | 0,25 |
| Emelkedés | 15 000 ft | 0,50 |
| Utazás | 35 000 ft | 0,78 |

---

## 7. Eredmények

### 7.1 Tervezési pont

| Paraméter | Érték |
|-----------|-------|
| Nettó tolóerő | 138,3 kN |
| Bruttó tolóerő | 138,4 kN (bypass 96,1 + mag 42,3) |
| SFC | 10,84 g/(kN·s) |
| Tüzelőanyag | 1,50 kg/s |
| FAR | 0,0263 |
| HPT / LPT PR | 2,665 / 3,745 |
| OPR / BPR | 26,96 / 5,50 |
| EGT (S5) | 798 °C |
| Mag-fúvócső | Fojtott, M = 1,0, Ps = 143,7 kPa |
| Bypass-fúvócső | Nem fojtott, M = 0,90 |

| Állomás | Tt [K] | Pt [kPa] | h [kJ/kg] |
|---------|--------|----------|-----------|
| S0 | 288,2 | 101,3 | −14,4 |
| S2 | 288,2 | 101,3 | −14,4 |
| S21 | 340,1 | 170,7 | 37,9 |
| S25 | 423,2 | 341,5 | 122,0 |
| S3 | 795,8 | 2731,7 | 514,8 |
| S4 | 1700,0 | 2649,8 | 501,6 |
| S45 | 1404,7 | 994,5 | 118,8 |
| S5 | 1071,3 | 265,6 | −294,2 |
| S8 | 1071,3 | 265,6 | −294,2 |
| S18 | 340,1 | 170,7 | 37,9 |

**Teljesítménymérleg:** HPC 22,36 MW = HPT 22,36 MW; fan 19,35 MW + LPC 4,78 MW = LPT 24,13 MW.

### 7.2 Off-design

| Fázis | T4 [K] | ṁ [kg/s] | Fn [kN] | Ram drag [kN] | SFC [g/(kN·s)] | OPR | BPR | N1 / N2 [%] | Tüzelőanyag [kg/s] | Érvényes |
|-------|--------|----------|---------|---------------|----------------|-----|-----|-------------|--------------------|----------|
| Felszállás | 1700 | 381,4 | 113,7 | 32,5 | 13,44 | 26,42 | 5,55 | 100,2 / 100,3 | 1,53 | igen |
| Emelkedés | 1700 | 264,9 | 69,0 | 42,7 | 16,10 | 29,44 | 5,37 | 101,8 / 99,0 | 1,11 | igen |
| Utazás, teljes gáz | 1700 | 152,3 | 36,1 | 35,2 | 18,80 | 33,59 | 5,11 | 107,1 / 97,8 | 0,68 | nem |
| Utazás, legnagyobb érvényes | 1490 | 139,4 | 25,5 | 32,3 | 17,48 | 24,74 | 5,56 | 91,7 / 91,9 | 0,45 | igen |
| Utazás, kb. 22 kN | 1420 | 133,7 | 21,7 | 30,9 | 17,41 | 22,02 | 5,64 | 89,6 / 90,2 | 0,38 | igen |

### 7.3 Gázkar felszállásnál (0 ft, Mach 0,25)

| Gázkar [%] | T4 [K] | Fn [kN] | FF [kg/h] | SFC [g/(kN·s)] | N1 [%] | N2 [%] | OPR | BPR | EGT [°C] | VBV [%] | Érvényes |
|------------|--------|---------|-----------|----------------|--------|--------|-----|-----|----------|---------|----------|
| 0 | 1000 | 14,9 | 899 | 16,82 | 75,7 | 83,4 | 7,78 | 5,08 | 374 | 30 | nem |
| 10 | 1070 | 21,2 | 1139 | 14,90 | 80,2 | 85,3 | 9,14 | 5,23 | 405 | 27 | igen |
| 25 | 1175 | 32,9 | 1565 | 13,23 | 84,1 | 88,0 | 11,25 | 5,50 | 456 | 22 | igen |
| 50 | 1350 | 57,3 | 2536 | 12,29 | 90,2 | 92,3 | 15,62 | 5,71 | 553 | 14 | igen |
| 75 | 1525 | 84,8 | 3847 | 12,61 | 95,2 | 96,4 | 20,77 | 5,70 | 672 | 6 | igen |
| 100 | 1700 | 113,7 | 5499 | 13,44 | 100,2 | 100,3 | 26,42 | 5,55 | 798 | 0 | igen |

### 7.4 Érvényességi tartomány

A 63 pontból 50 érvényes.

| Fázis | Érvényes gázkar | Érvénytelen pontok | Ok |
|-------|-----------------|--------------------|-----|
| Felszállás | 10–100 % | 2 | Fan off map |
| Emelkedés | 15–100 % | 3 | Fan off map |
| Utazás | 10–70 % | 8 | Fan off map (0, 5 %); LPC off map (75–100 %); N1 > 104 % (95–100 %) |

### 7.5 Összevetés irodalmi adatokkal

| Paraméter | Irodalmi | Szimulált | Eltérés |
|-----------|----------|-----------|---------|
| Statikus tolóerő [kN] | 133,4 | 138,3 | +3,7 % |
| Statikus SFC [g/(kN·s)] | 9,25–10,02 | 10,84 | +8…+17 % |
| Utazó SFC [g/(kN·s)], Fn ≈ 22 kN | 15,4 | 17,41 | +13 % |
| N1 / N2 felszállásnál [%] | ≈ 100 | 100,2 / 100,3 | – |

A tolóerő többlete mellett az SFC is nagyobb, tehát a modell ciklusa kevésbé hatékony a valódinál. Legvalószínűbb ok a becsült OPR és a becsült hatásfokok. A modell kalibrálatlan.

### 7.6 Ismert korlátok

- Nincs turbinahűtő-levegő, beépítési és mechanikai veszteség.
- A jelleggörbék pyCycle mintagörbék, nem CFM56-mérések.
- A földi alapjárat a jelleggörbéken kívül esik.
- A gázkar T4-et állít, a valódi FADEC N1-et vezérel és korlátoz.
- A modell EGT-je az S5 (LPT kilépő), a valódi EGT mérési pontja a T49.5, ezért közvetlenül nem hasonlítható össze.
- A T-s diagram entrópiája konstans cp-vel számolt közelítés.

---

## 8. Hajtóműindítás és indítási hibák (tranziens modell)

Tisztán Python alapú, nincs pyCycle-függősége, ezért élőben fut az alkalmazásban.

### 8.1 Architektúra

| Réteg | Fájl | Felelősség |
|-------|------|------------|
| Plant | `engine/start_transient.py` | HP-tengely ODE, empirikus EGT-, FF- és N1-összefüggések |
| FADEC, pilótafülke | `engine/fadec.py` | Kezelőszervek és N2 → indítószelep, tüzelőanyag, gyújtás |
| Meghajtó | `simulate_start()` | Időléptetés, hibadetektálás, `StartTransient` idősor |

### 8.2 Fizikai modell

```
I · dN2/dt = Q_indító + Q_turbina − Q_ellenállás

Q_indító    = Q_0 · k_bleed · (1 − N2 / N2_kiold)    nyitott szelepnél
Q_turbina   = k_t · f_FF(N2)                         light-off után
Q_ellenállás = k_d · N2
k_t         = k_d · N2_idle                          → egyensúly N2 = 60 %-nál
```

I = 10, k_d = 1, Q_0 = 40, N2_kiold = 50 %. A paraméterek normalizáltak és hangoltak, nem fizikai mértékegységűek. Integrálás: explicit Euler, Δt = 0,5 s; az időállandó 10 s.

Az f_FF gyújtáskor 0,35, és lineárisan nő 1-ig az alapjárati N2 90 %-áig.
EGT: alapszint a 450 °C felé, plusz Gauss-csúcs N2 = 25 % körül.
N1 = 19 % · (N2/60)^1,5.
Az EGT, az FF és az N1 empirikus alakfüggvény, nem fizikai számítás.

### 8.3 Indítási szekvencia

`STARTER ON (0 s) → IGNITION ON, LIGHT-OFF (9,0 s, N2 18 %) → STARTER CUTOUT (31,5 s, N2 50 %) → IDLE (60,5 s, N2 59,4 %, N1 18,7 %)`

EGT-csúcs: 633 °C. A valós ~16 %-os gyújtást és ~22 %-os tüzelőanyag-nyitást a modell egyetlen 18 %-os pontba vonja össze.

| ENG MODE | Viselkedés |
|----------|------------|
| IGN/START | Automatikus indítás, ha ENG MASTER ON és van APU bleed |
| NORM | Nem indít. Indítás közben megszakítja, járó hajtóműnél üzemi állás |
| CRANK | Csak forgatás, tüzelőanyag és gyújtás nélkül |

### 8.4 Indítási hibák

| Hiba | Injektált gyökok | Tünet | FADEC-jelzés |
|------|------------------|-------|--------------|
| Hidegfennakadás (HUNG) | `ff_cap = 0,7` | N2 45,5 %, N1 12,5 %, FF 420 kg/h | HUNG START, 43,5 s |
| Melegindítás (HOT) | `fuel_mult = 1,8` | EGT-csúcs 977 °C, eléri az alapjáratot | EGT EXCEEDANCE, 10,0 s |
| Nincs üzemanyag (NO_FUEL) | Szelephiba | N2 22,1 %, EGT 15 °C, FF = 0 | NO LIGHT-OFF, 18,5 s |
| Nincs gyújtás (NO_IGNITION) | Gyújtóhiba | N2 22,1 %, EGT 15 °C, FF = 255 kg/h | WET START, 18,5 s |

A FADEC **csak detektál**, automatikusan nem szakít meg. Detektálás: hung start 8 s N2-változás nélkül, no light-off és wet start 10 s gyújtás nélkül, EGT azonnal 725 °C felett.

Kézi ellenőrzés: 40·(1 − N2/50) = N2 → 22,2 %; 40·(1 − N2/50) + 42 = N2 → 45,6 %.

---

## 9. Pilótafülke-alkalmazás

Indítás: `.venv/bin/python -m streamlit run app.py`

Az app a `data/lookup.pkl`-ből olvas, tehát futás közben nem old meg ciklust. A pyCycle a `precompute.py` futtatásához kell.

**Nyilvános elérés:** https://cfm56ziad.streamlit.app — az app Streamlit Community Cloudon fut, a GitHub-repó webhookja (`share.streamlit.io/hook`) pushkor értesíti a szolgáltatást. Az ingyenes appok használat nélkül elalszanak, ezért bemutató előtt érdemes megnyitni.

**Állapotok:** OFF → STARTING → RUNNING, sikertelen indításnál FAULT.

| Elem | Működés |
|------|---------|
| ENG panel | Kattintható kép: ENG 1, MODE (CRANK / NORM / IGN/START), APU BLEED |
| Scenario | NORMAL, HUNG, HOT, NO_FUEL, NO_IGNITION. Járó hajtóműnél váltva újraindít |
| Speed | 1, 5 vagy 10-szeres szimulációs idő |
| E/WD | N1, EGT, N2, FF. RUNNING állapotban EPR, OPR, SFC, tolóerő is |
| Engine trends | N1/N2, EGT, FF az idő függvényében |
| Cycle analysis | Repülési fázis, gázkar, paraméterek, állomástábla, állomás- és T-s diagram, 3D modell |

**Az indítás és a ciklusmodell kapcsolata:** az indítás N1 ≈ 19 %-on ér véget, a legalacsonyabb ciklusmodell-pont N1 ≈ 76 %. RUNNING állapotban az E/WD elsőrendű késleltetéssel (τ = 4 s szimulációs idő) a kiválasztott gázkarpont felé mozog, ezért IDLE után 0 % gázkarnál is felfut kb. 76 % N1-re. Ez szemléltető átmenet, nem fizikai számítás.

---

## 10. Tesztek

`.venv/bin/python -m pytest -q -W ignore` — 97 teszt, kb. 2,5 perc. Utoljára futtatva 2026-11-01-én: 97 sikeres.

| Terület | Modulok | Tesztek |
|---------|---------|---------|
| Ciklusmodell | `test_cfm56`, `test_cycle_balance`, `test_simulation`, `test_results` | 23 |
| Indítás és FADEC | `test_start_plant`, `test_start_faults`, `test_fadec`, `test_simulate_start`, `test_start_anchor`, `test_start_results` | 35 |
| App-logika | `test_cockpit_logic`, `test_playback`, `test_trend` | 19 |
| Megjelenítés | `test_airbus_panel`, `test_ecam`, `test_ewd`, `test_start_plot`, `test_visualization` | 20 |

---

## 11. Karbantartás

Ha a modell vagy az adat változik, ezeket együtt kell frissíteni:

1. `precompute.py` futtatása, ez frissíti a `data/` mappát.
2. Ez a fájl, 7. fejezet.
3. `docs/meghallgatas_felkeszules.md`, majd `scripts/build_hearing_docx.py`.
4. `generate_thesis.py`, ha a dolgozat számai is érintettek.

A commit-történet a `git log` paranccsal érhető el.
