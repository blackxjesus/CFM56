# Szakdolgozat II meghallgatás – felkészülési anyag

> Saját használatra. Ne olvasd fel! Kulcsszavakat tanulj, és minden számot tudj levezetni.
> A bizottság nem a formát nézi, hanem azt, hogy **te magad érted-e** a saját anyagodat.

---

## 0. Őszinte állapotfelmérés (olvasd el először)

**Erős pontok:**
- Működő, verziókezelt (68 commit), tesztelt Python kód; saját szimulációs csomag.
- pyCycle/OpenMDAO (NASA) használata CEA-alapú gáztulajdonságokkal.
- Interaktív A320 E/WD pilótafülke-app (Streamlit): gázkar, ENG MASTER / ENG MODE, élő trendek.
- **Tranziens indítási modell + FADEC-logika + 4 indítási hiba.** Ez a leginkább „saját” kreatív munka – ezt emeld ki.

**Gyenge pontok, amiket egy hozzáértő bizottsági tag meg fog találni** (részletek: 5. fejezet):
1. A HP-tengely teljesítménymérlege **nincs egyensúlyban** (a turbinák PR = 4,0 rögzített bemenet).
2. Az „off-design” valójában **ugyanaz a tervezési pont**, más magasságon/Mach-számon, és a tömegáram rögzített (370 kg/s). Ezért OPR = 26,96 és BPR = 5,5 minden fázisban.
3. A „validált” OPR és BPR **bemenet**, nem eredmény (1,685 × 2,0 × 8,0 = 26,96).
4. A gázkar T4-je nem 1000 K alapjáraton: a FAR-t skálázod, és a tényleges S4 = **1379 K**.
5. A gázkar-eredmények fizikailag nem reálisak: alapjáraton 109 kN tolóerő, és kisebb SFC, mint teljes gáznál.
6. A 133,4 kN **statikus** (Mach 0) érték, te pedig Mach 0,25-ön számolsz (ram drag ≈ 31 kN).
7. Az ideális Brayton-hatásfok a dolgozatban 47 %, OPR = 27-nél valójában **≈ 61 %**.
8. Az irodalomjegyzék néhány tétele pontatlan vagy ellenőrizetlen (lásd 1. fejezet).
9. A dolgozat (.docx) még **nem tartalmazza** az indítási/FADEC modellt és a pilótafülke-appot.

A stratégia: **ne védd a hibát, hanem mutasd meg, hogy te magad találtad meg és érted, miért van.**
Ez a meghallgatáson sokkal többet ér, mint egy „tökéletes” szám, amit nem tudsz megmagyarázni.
3–5 hét van a leadásig, az 1., 2. és 4. pont javítható.

---

## 1. Szakirodalom – „Mit olvasott ebben?”

**Szabály:** csak azt hivatkozd, amit ténylegesen kézben tartottál. Minden forrásnál tudj 2–3 mondatot mondani.

| # | Forrás | Mit kell tudnod róla | Teendő |
|---|--------|----------------------|--------|
| [7] | Mattingly: *Elements of Propulsion* | Turbofan ciklusanalízis, állomásszámozás, tolóerő-egyenlet, TSFC | Olvasd el a turbofan parametrikus ciklusanalízis fejezetet |
| [8] | Çengel–Boles: *Thermodynamics* | Brayton-ciklus, izentropikus hatásfok, T-s diagram | – |
| [9] | Cumpsty–Heyes: *Jet Propulsion* | Tolóerő, propulziós hatásfok, BPR szerepe | – |
| [10] | Walsh–Fletcher: *Gas Turbine Performance* | Design point vs. off-design, jelleggörbék, tranziens | A DOKUMENTACIO.md-ben „5–10 %”, a dolgozatban „10–20 %” eltérés szerepel rá hivatkozva – **nézd meg, mit ír valójában**, vagy vedd ki |
| [14] | Kurzke–Halliwell: *Propulsion and Power* | Teljesítménymodellezés, hűtőlevegő, jelleggörbe-skálázás | – |
| [11] | pyCycle cikk | **Hibás hivatkozás.** A valódi: Hendricks, E. S. – Gray, J. S. (2019): *pyCycle: A Tool for Efficient Optimization of Gas Turbine Engine Cycles.* Aerospace 6(8): 87 (MDPI) | Javítsd |
| [13] | Gray et al. (2019) OpenMDAO | Newton-megoldó, implicit komponensek | – |
| [2] | Aircraft Commerce | A DOKUMENTACIO szerint az 50-es szám a 5A/5B, az 58-as a 7B. A dolgozatban „58: 5B/7B” szerepel | Ellenőrizd |
| [3] | Roux: *Turbofan and Turbojet Engines Database Handbook* | Motoradatok (tömegáram, BPR, OPR) | Innen vedd a tömegáramot |
| [1], [5], [6], [15] | CFM / Airbus / Aviation Week | Nem tudom ellenőrizni, hogy léteznek ezzel a címmel és oldalszámmal | **Keresd meg mindegyiket.** Ha nem találod, cseréld le olyanra, amit megtaláltál |
| – | A320 FCOM / FCTM (indítás) | Az indítási modell számai (16 % gyújtás, 22 % üzemanyag, 50 % indító kiold, 725 °C start EGT limit) | **Vedd fel forrásként** – most nincs hivatkozva |

A dolgozat egyes állításainak is nézz utána, mert rákérdezhetnek: „több mint 20 000 darab”, „a légi forgalom 30 %-a”, „180 perces ETOPS”, „172 kg/s tömegáram” (a kódban 370 kg/s!).

---

## 2. Előismeretek – képletek a saját számaiddal

Ezeket tudd **táblán, fejből** levezetni. A saját eredményeidből jönnek, és jól mutatják a megértést.

**Ideális Brayton-hatásfok**
η_th = 1 − OPR^(−(γ−1)/γ) = 1 − 26,96^(−0,2857) ≈ **0,61**
(A dolgozatban 47 % szerepel – javítsd. A valós ≈ 40–45 % az irreverzibilitások miatt.)

**Kompresszor összesített izentropikus hatásfoka a saját táblázatodból**
T3s = T2 · OPR^0,2857 = 291,8 · 2,563 ≈ 747,9 K
η_c = (T3s − T2)/(T3 − T2) = (747,9 − 291,8)/(804,9 − 291,8) ≈ **0,889**
→ Konzisztens a megadott 0,87–0,89 értékekkel. Jó bemutatni.

**Magáram és tüzelőanyag**
ṁ_core = 370/(1 + 5,5) ≈ 56,9 kg/s; ṁ_f = FAR · ṁ_core = 0,027 · 56,9 ≈ **1,54 kg/s** ✔ (egyezik a szimulációval)

**Tolóerő** (dolgozat 2.4):
Fn = ṁ_c·V8 + ṁ_b·V18 − ṁ_0·V0 + (P8 − P0)·A8 + (P18 − P0)·A18
Ram drag Mach 0,25-ön: V0 ≈ 85 m/s → ṁ·V0 ≈ 370 · 85 ≈ **31 kN**

**SFC mértékegységek**
1 lb/(lbf·h) ≈ 28,3 g/(kN·s). A te 0,0135 kg/(kN·s) = 13,5 g/(kN·s) ≈ 0,48 lb/(lbf·h).

**Még ezekre készülj:**
- Izentropikus hatásfok definíciója kompresszorra és turbinára, és hogy miért más.
- Propulziós hatásfok: η_p = 2/(1 + V_j/V_0) → ezért jó a nagy BPR (nagy tömegáram, kis kiáramlási sebesség).
- Termikus × propulziós = összhatásfok.
- ISA: T = 288,15 − 6,5·h [km] 11 km-ig; 35 000 ft ≈ 218,8 K, ≈ 23,8 kPa.
- Össznyomás és statikus nyomás, torlóponti állapot.
- Kompresszor-jelleggörbe: nyomásviszony – korrigált tömegáram – fordulatszám, pompázs határ.
- Kéttengelyes felépítés: fan + LPC + LPT az LP tengelyen, HPC + HPT a HP tengelyen.
- Miért az N2-t forgatja az indítómotor (az AGB a HP tengelyen van).
- EGT: a CFM56-on az LPT-nél mérik (a te modelledben S5 ≈ LPT kilépő).
- FADEC feladata: tüzelőanyag-adagolás, indítási szekvencia, határérték-felügyelet.

---

## 3. Kiinduló adatok – „Honnan van ez a szám? Milyen közelítéssel?”

| Adat | Érték | Forrás / közelítés – mit mondj |
|------|-------|---------------------------------|
| BPR | 5,5 | ICAO emissziós adatbázis / EASA típusbizonyítvány |
| OPR | 27 | Aircraft Commerce. **Bemenet**, a fan/LPC/HPC PR szorzata adja |
| Fan / LPC / HPC PR | 1,685 / 2,0 / 8,0 | **Saját felvétel**, hogy a szorzat 27 legyen. Valós komponens-PR nem publikus |
| Hatásfokok | 0,87–0,90 | Tipikus értékek a szakirodalomból (Walsh–Fletcher, Mattingly), nem CFM-adat |
| T4 | ~1700 K | Irodalmi becslés (egy CFM56-3 cikkből). Nem gyártói adat |
| Tömegáram | 370 kg/s | **Nézd meg a Roux-ban.** A dolgozat 1. táblázatában 172 kg/s szerepel – ellentmondás |
| FAR | 0,027 | Úgy választva, hogy T4 ≈ 1700 K legyen |
| HPT / LPT PR | 4,0 / 4,0 | **Rögzített feltevés, nem egyensúlyból számolt** (lásd 5.1) |
| Égőtéri nyomásveszteség | 3 % | Tipikus érték |
| Gáztulajdonságok | CEA | pyCycle, hőmérséklet- és összetételfüggő cp |
| Entrópia a T-s diagramon | cp = 1,005, R = 0,287 | Kalorikusan tökéletes gáz – magas T-n pontatlan (ezt a dolgozat is írja ✔) |
| Gázkar N1/N2 | lineáris becslés | Nem számolt, empirikus. A DOKUMENTACIO és az `ecam.py` más együtthatókat használ (20+0,80x vs. 22+0,78x) |
| Indítási modell paraméterei | inertia = 10, k_drag = 1, starter_torque = 40 | **Normalizált, hangolt paraméterek**, nem fizikai [kg·m²]. Úgy hangoltam őket, hogy az indítási idő és a jellegzetes N2-pontok (light-off, kioldás, idle) valósághűek legyenek |
| Idle N2 / N1 / EGT | 60 % / 19 % / 450 °C | A320 FCOM / üzemeltetési tipikus értékek → hivatkozd |
| Start EGT limit | 725 °C | A320 FCOM (CFM56-5B) |
| Light-off N2 | 18 % | Egyszerűsítés: a valós automatikus indításnál ~16 % gyújtás, ~22 % HP fuel valve. **Tudd elmondani, miért vontad össze** |

---

## 4. Módszertan – „Milyen más módszert alkalmazhatott volna?”

**Stacioner ciklusanalízis alternatívái:**
- **Kézi / táblázatkezelős 0D számítás** (Mattingly parametrikus analízis) – átlátható, de konstans cp.
- **GasTurb** (Kurzke) – ipari-oktatási szabvány, kész jelleggörbék és off-design.
- **NPSS** (NASA/SwRI) – ipari standard, nem ingyenes.
- **GSP** (NLR) – objektumorientált, tranziens is.
- **pyCycle valódi multipoint off-design** – ezt kellett volna (lásd 5.2).

**Tranziens / indítás alternatívái:**
- **T-MATS** (NASA, MATLAB/Simulink) – dinamikus hajtóműmodell, szabályozókkal.
- **Komponensszintű dinamikus modell** jelleggörbékkel, az alacsony fordulatszámú tartomány extrapolálásával – ez nagyon nehéz, mert a jelleggörbék idle alatt nem ismertek. Emiatt választottam a redukált rendű modellt.
- **Adatvezérelt modell** valódi indítási felvételekből (QAR/FDR adatok) – nem fértem hozzá adathoz.

**Miért ezt választottad?** (saját szavaiddal)
- pyCycle: ingyenes, nyílt, NASA-validált, Python → saját vizualizációval és appal összeköthető.
- Tranziens modell tisztán Pythonban: élőben fut a webappban, gyors, átlátható. A cél a **jelenségek és a hibák tüneteinek** bemutatása volt, nem a pontos számok.

**Numerikus módszer:**
- pyCycle: OpenMDAO Newton-megoldó az implicit egyenletrendszerre.
- Indítás: I·dN2/dt = Q_indító + Q_turbina − Q_ellenállás, **explicit Euler**, dt = 0,5 s.
  Várható kérdés: „Stabil ez a lépésköz?” → az időállandó I/k_drag = 10 s ≫ 0,5 s, tehát stabil. Pontosabb lenne az RK4 vagy a `scipy.solve_ivp`.
- Az egyensúly: turbine_gain = k_drag · idle_N2 → dN2/dt = 0 pontosan N2 = idle-nál (ff_frac = 1 esetén). Tudd levezetni!
- Hibadetektálás: időzítős logika (hung start: 8 s-ig nincs N2-növekedés; no light-off / wet start: 10 s-ig nincs gyújtás).
- Tesztek: pytest, ~20 tesztmodul (plant, FADEC, hibák, playback, E/WD).

---

## 5. Várt és valós eredmények – a kritikus kérdések

### 5.1 A HP-tengely teljesítménymérlege (a legfontosabb)

A saját 3. táblázatodból (h értékek, CEA abszolút entalpia):
- HPC felvett teljesítménye: 56,9 · (524,8 − 127,3) ≈ **22,6 MW**
- HPT leadott teljesítménye: 58,4 · (511,0 − (−16,0)) ≈ **30,8 MW**
- → **≈ 8 MW többlet**, a HP tengely nincs egyensúlyban. Az LP tengely nagyjából rendben van (24,5 vs. 23,6 MW).

**Ok:** a `cfm56.py`-ban `hpt.PR = 4.0` és `lpt.PR = 4.0` rögzített bemenet, nincs `Balance`, ami a `hp_shaft.pwr_net = 0` feltételt kikényszerítené. A HPT túl sok energiát von el → kevesebb jut a fúvócsőnek → ez **is** hozzájárul a tolóerő-hiányhoz.

**Javítás (1–2 nap):** a pyCycle `high_bypass_turbofan` példája alapján `om.BalanceComp`:
- `FAR` → cél: T4 = 1700 K (ez egyben megoldja a 4. pontot is),
- `hpt.PR` → cél: `hp_shaft.pwr_net = 0`,
- `lpt.PR` → cél: `lp_shaft.pwr_net = 0`,
- (opcionálisan `W` → cél: Fn = 133,4 kN statikusan).
Ellenőrzés: `prob.get_val('hp_shaft.pwr_net')` legyen ~0.

**Ha nem javítod:** mondd ki, hogy ez a modell egyszerűsítése, és számold ki előttük a fenti mérleget. Ez a „saját munka” legerősebb bizonyítéka.

### 5.2 „Miért ugyanaz az OPR és a BPR mindhárom fázisban?”
Mert a `run_off_design()` minden fázisban **új tervezési pontot** old meg ugyanazokkal a PR és BPR bemenetekkel, és a tömegáram is rögzített 370 kg/s. Valódi off-design-ban a geometria (fúvócsőterület, jelleggörbék) rögzített, és az OPR, BPR, ṁ az üzemállapotból adódik: magasságon a fizikai tömegáram ~1/3-ára esik.
**Javítás:** pyCycle multipoint (`MPhbtf` minta): 1 design pont + off-design pontok `design=False` módban, a design pont területeivel. Ha erre nincs idő: **nevezd át** „parametrikus design-point vizsgálatnak”, és írd le a korlátot.

### 5.3 „Miért kevesebb a tolóerő 14,7 %-kal?”
Sorrendben mondd:
1. **Nem azonos körülmény:** 133,4 kN statikus (Mach 0) érték, a szimuláció Mach 0,25-ön fut → ram drag ≈ 31 kN. **Futtasd le Mach 0-n**, és hasonlítsd azt!
2. A HP-tengely mérlege nincs egyensúlyban (5.1).
3. Hűtőlevegő, beépítési és mechanikai veszteségek nincsenek modellezve.
4. A tömegáram, T4 és a komponens-PR-ek becsültek.
(A dolgozat szerint „a hűtőlevegő miatt kevesebb” – de hűtőlevegő nélkül inkább **több** jönne ki, mert nincs elvont levegő. Erre készülj!)

### 5.4 „Miért ilyen kicsi az alapjárati tolóerő-csökkenés? (109 → 114 kN)”
Mert a gázkar csak a FAR-t változtatja, a tömegáram és a nyomásviszonyok rögzítettek. Valóságban alapjáraton a fordulatszám, a tömegáram és az OPR is leesik, az idle tolóerő a maximumnak csak kb. 5–7 %-a. Ráadásul „0 %”-nál a T4 nem 1000 K, hanem **1379 K** (a FAR skálázás nem egyenes arányban adja a T4-et).

### 5.5 „Miért kisebb alapjáraton az SFC?” / „Miért kisebb utazáskor az SFC?”
- **Alapjárat:** a valóságban alapjáraton **nagyobb** az SFC (rossz részterhelési hatásfok). A modellben azért jön ki kisebbnek, mert a tolóerő szinte nem változik, az üzemanyag viszont igen. A dolgozat magyarázata („jobb a kompresszor hatásfoka 1000 K-en”) **nem helyes**: a hatásfokok a modellben konstans bemenetek. **Javítsd a szöveget.**
- **Utazás:** a valós CFM56-5B TSFC utazáskor (~0,55 lb/lbf/h) **nagyobb**, mint statikusan felszálláskor, mert nő a repülési sebesség (ram drag, propulziós hatásfok). A modelled az ellenkezőjét adja, mert a fizikai tömegáram rögzített. Mondd ki: „Ez ellentmond az elvárásnak, és a rögzített tömegáramú design-point megközelítés következménye.” (Pont ez az, amit a bizottság kérdezni szokott: „Miben mond ellent az eredmény az elvárásainak?”)

### 5.6 EGT anomália
A DOKUMENTACIO 9.5 táblázatában 75 %-nál EGT = 754 °C, 100 %-nál 717 °C – ez nem monoton. A friss `lookup.pkl` szerint S5 100 %-nál 990 K = 717 °C. Nézd meg, a 75 %-os érték régi futásból maradt-e, és tedd rendbe.

### 5.7 Indítási modell – ezek az erősségeid
Várt = kapott, és tudod az okát:
- **Normál:** STARTER ON → IGNITION → LIGHT-OFF (18 %) → STARTER CUTOUT (50 %) → IDLE (60 %).
- **Hung (hideg fennakadás):** ff_cap = 0,7 → a turbinanyomaték nem elég, N2 ≈ 45 %-on beáll (Q_turbina = Q_ellenállás egyensúly alacsonyabb N2-n).
- **Hot start:** fuel_mult = 1,8 → EGT csúcs > 725 °C.
- **No fuel:** csak az indító forgat, N2 ≈ 22 %, EGT = környezeti, FF = 0.
- **No ignition (wet start):** FF > 0, de nincs gyújtás → nedves indítás.
- A FADEC **csak detektál**, nem abortál automatikusan. Tudd megindokolni, és tudd, hogy a valós A320 auto-start FADEC **automatikusan megszakít** a földön (hot/hung start, no light-off). Ez tervezési döntés volt: a hibák tüneteinek bemutatása és a személyzeti beavatkozás.
- Korlát: az N1 = idle_N1 · (N2/idle)^1,5 és az EGT Gauss-csúcs **empirikus alakfüggvény**, nem fizikai számítás.

---

## 6. 5 perces összefoglaló – kulcsszavas vázlat (ne szó szerint)

1. **Téma, motiváció (30 s):** CFM56-5B, A320, legelterjedtebb hajtómű; cél: ciklus megértése szimulációval + üzemeltetési (pilótafülke) szemlélet.
2. **Stacioner modell (1 perc):** pyCycle/OpenMDAO, kéttengelyes turbofan, komponensek, CEA, bemeneti adatok és forrásuk.
3. **Eredmények (1 perc):** állomásadatok, T-s diagram, OPR/T4/tolóerő; 14,7 % eltérés – és **mi az oka** (Mach 0,25, tengelymérleg, egyszerűsítések).
4. **Tranziens indítás + FADEC (1,5 perc):** tehetetlenségi ODE, indítási szekvencia, 4 hiba és tüneteik, detektálás.
5. **App és validáció (30 s):** E/WD, tesztek, verziókezelés.
6. **Kritikus értékelés és folytatás (30 s):** tengelyegyensúly, valódi off-design, hűtőlevegő, alapjárati modell összekötése a pyCycle-lel.

Gyakorolj stopperrel, hangosan, 2–3 alkalommal.

---

## 7. Bemutató forgatókönyv (projektor)

Előtte: `streamlit run app.py` fusson már, a böngésző legyen nyitva, és legyen **offline tartalék** (képernyővideó vagy képernyőképek), ha nincs internet vagy leáll.

1. **App – normál indítás:** ENG MODE IGN/START → MASTER ON → mutasd az E/WD-n a light-off-ot, az indító kioldását és az idle-t. Közben mondd a számokat.
2. **Hot start** → EGT piros, EGT EXCEEDANCE. Magyarázd a gyökokot.
3. **Hung start** → N2 megreked. Magyarázd az egyensúlyt az ODE-ből.
4. **Gázkar + ciklusanalízis** → állomás-diagram, T-s diagram, 3D modell.
5. **Kód:** `engine/start_transient.py` → `dN2_dt()` (az egyenlet 1:1-ben látszik), `engine/cfm56.py` → `CFM56_PARAMS`.
6. **Tesztek:** `pytest -q` a terminálban.
7. **Kézi számítás** (papír/tábla): η_c ≈ 0,889 és a HP teljesítménymérleg.

---

## 8. Teendőlista a meghallgatásig

**Kötelező (a meghallgatás előtt):**
- [ ] Minden hivatkozást megkeresni; a [11]-et javítani; amit nem találsz, cserélni.
- [ ] Tömegáram-ellentmondás (172 vs. 370 kg/s) – forrásból eldönteni.
- [ ] Ideális Brayton-hatásfok: 47 % → 61 %.
- [ ] Az SFC-magyarázatok átírása (5.5).
- [ ] Minden képletet és számot fejből levezetni (2. fejezet).
- [ ] Az app fusson egy friss gépen is (`requirements.txt`-ből a pyCycle hiányzik – a lookup.pkl előre kiszámolt, ezt tudd elmondani).
- [ ] 5 perces összefoglaló gyakorlása.

**Erősen ajánlott (3–5 hét alatt a végleges dolgozathoz):**
- [ ] Balance-ok a pyCycle modellbe (T4 cél, tengelyek pwr_net = 0) → újrafuttatás.
- [ ] Mach 0 statikus futtatás és összehasonlítás a 133,4 kN-nal.
- [ ] Valódi off-design (multipoint), vagy a fejezet átnevezése és a korlát leírása.
- [ ] Új fejezet a dolgozatba: tranziens indítás, FADEC, indítási hibák, pilótafülke-app.
- [ ] Az ellentmondó táblázatok egységesítése (climb 10 000 vs. 15 000 ft; cruise tolóerő 52,4 vs. 49,5 kN; N1/N2 képletek).
- [ ] A dolgozat szövegét saját szavaiddal átírni. Minden mondatot meg kell tudnod védeni.

---

## 9. Gyors válaszok nehéz helyzetekre

- **„Ezt nem tudom.”** → „Ezt nem vizsgáltam, de úgy közelíteném meg, hogy…” – mondj egy módszert.
- **„Ez hibás.”** → „Igen, ezt én is észrevettem: az oka … a végleges dolgozatban így javítom: …”
- **„Honnan van ez?”** → mondd meg őszintén, ha becsült/hangolt érték, és mi alapján hangoltad.
- **„Használt MI-t?”** → Légy őszinte arról, mire használtál eszközöket (pl. kódolási segítség), és mutasd meg, hogy **te döntöttél** a modellről, a feltevésekről, és te érted és ellenőrizted az eredményt. A kézi ellenőrző számítások (η_c, tengelymérleg, ram drag) pont ezt bizonyítják.
