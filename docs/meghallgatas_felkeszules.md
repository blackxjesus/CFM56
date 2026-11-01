# Szakdolgozat II meghallgatás – felkészülési anyag

> Saját használatra. Ne olvasd fel! Kulcsszavakat tanulj, és minden számot tudj levezetni.
> Állapot: 2026-11-01. Minden szám a jelenlegi modellből való (`data/results.csv`, `data/design_point.pkl`).

---

## 0. Mit néz a bizottság, és hol tartasz

A kiírás szerint a meghallgatás célja annak igazolása, hogy **a dolgozat a saját önálló munkád**. A bizottság (legalább 3 fő, köztük a belső konzulens) öt témát ellenőriz. Ehhez igazodik ez az anyag:

| Bizottsági téma | Példakérdés a kiírásból | Fejezet |
|-----------------|-------------------------|---------|
| Szakirodalom | „Mit olvasott ebben a szakirodalomban?” | 2. |
| Tantárgyi előismeretek | „Mit tanult ezzel kapcsolatban repüléselméletből?” | 3. |
| Kiinduló adatok és forrásuk | „Honnan származik ez az adat? Milyen közelítéssel alkalmazta?” | 4. |
| Módszer | „Milyen más módszert alkalmazhatott volna még?” | 5. |
| Várt és valós eredmények | „Miben mond ellent ez az eredmény az elvárásainak?” | 6. |

További tudnivalók a kiírásból:
- 5 perces, **saját szavas** összefoglaló kell, nem felolvasás. Prezentáció nem szükséges.
- Jegyzet, táblázat és applikáció szabadon használható, sőt bemutatásuk kívánatos (projektor vagy okostábla).
- A forma nem számít. Az számít, hogy **te magad tudod-e értelmezni** a saját anyagaidat.
- Az eredmény a Szakdolgozat II. tárgy záró érdemjegye.

**Erős pontok:**
- Tengely-egyensúllyal zárt tervezési pont: a teljesítménymérleg kézzel is ellenőrizhető.
- Valódi off-design rögzített geometriával: tömegáram, BPR, OPR, N1 és N2 eredmény, nem bemenet.
- Tranziens indítási modell, FADEC-logika, 4 indítási hiba, megrekedési fordulatszámok kézi levezetése.
- Működő app, 97 automatikus teszt, verziókezelés.

**Ahol kérdésre számíthatsz** (részletek a 6. fejezetben):
1. Az SFC 8–17 %-kal nagyobb a közölt értékeknél, miközben a tolóerő +3,7 %.
2. A 63 munkapontból 13 érvénytelen.
3. A földi alapjárat nincs a ciklusmodellben: az indítási modell és a ciklusmodell között szakadék van.
4. A validáció egyik fő forrása a Wikipedia [13].
5. A dolgozatban van néhány szakmai pontatlanság (8. fejezet).

**Az önálló munkáról.** A kiírás kifejezetten a generatív MI miatt vezette be ezt a meghallgatást, a repó 70 commitjából 47-ben pedig Claude társszerzőként szerepel. Ha megmutatod a repót, ez látszik, ezért **mondd el magadtól, pontosan**: mire használtál MI-t, és mi volt a te döntésed. Csak azt állítsd a saját felismerésednek, ami valóban az volt. Ami ebben az anyagban a saját döntésedként szerepel, azt ellenőrizd, és ha nem igaz, fogalmazd át. Tanulni nem a kész válaszokat kell, hanem azt, hogy minden sort meg tudj indokolni.

---

## 1. 5 perces összefoglaló – kulcsszavas vázlat

1. **Téma (30 s):** CFM56-5B, A320-család; cél a ciklus megértése szimulációval, üzemeltetési (pilótafülke) szemlélettel.
2. **Tervezési pont (1 perc):** pyCycle/OpenMDAO, kéttengelyes turbofan, CEA-gáztulajdonságok. Bemenet: 370 kg/s, BPR 5,5, OPR 27, T4 1700 K. A FAR a T4-et, a turbina-PR-ek a tengely-egyensúlyt zárják. Eredmény: 138,3 kN, 10,84 g/(kN·s).
3. **Off-design (1 perc):** rögzített geometria, 3 repülési fázis, 21 gázkarállás, 63 pont, VBV-ütemezés. Felszállás 113,7 kN (a ram drag miatt), utazás kb. 22 kN-nál SFC 17,41.
4. **Indítás és FADEC (1,5 perc):** tehetetlenségi ODE, szekvencia, 4 hiba tünetei, detektálás.
5. **App és ellenőrzés (30 s):** E/WD, tesztek, kézi mérleg.
6. **Kritikus értékelés (30 s):** SFC-eltérés oka, érvénytelen pontok, alapjárati szakadék, hűtőlevegő.

Gyakorolj stopperrel, hangosan, 2–3 alkalommal.

---

## 2. Szakirodalom – „Mit olvasott ebben?”

**Szabály:** csak azt hivatkozd, amit ténylegesen kézben tartottál, és mindegyikről tudj 2–3 mondatot mondani. Ez a rész a tiéd: **egyetlen forrást sem tudtam ellenőrizni helyetted**, és azt sem, hogy olvastad-e.

| # | Forrás | Mit kell tudnod róla | Teendő |
|---|--------|----------------------|--------|
| [4] | Mattingly: *Elements of Propulsion* | Turbofan ciklusanalízis, állomásszámozás, tolóerő, TSFC | Olvasd el a turbofan parametrikus ciklusanalízist |
| [5] | Çengel–Boles: *Thermodynamics* | Brayton-ciklus, izentropikus hatásfok, T-s diagram | – |
| [6] | Cumpsty–Heyes: *Jet Propulsion* | Tolóerő, propulziós hatásfok, BPR szerepe | – |
| [7] | Walsh–Fletcher: *Gas Turbine Performance* | Design és off-design, jelleggörbék, tranziens | Olvasd el az off-design fejezetet |
| [11] | Kurzke–Halliwell: *Propulsion and Power* | Teljesítménymodellezés, hűtőlevegő, jelleggörbe-skálázás | – |
| [8] | Hendricks–Gray (2019), *Aerospace* 6(8):87 | A pyCycle módszere, CEA-alapú termodinamika | Olvasd el, nyílt hozzáférésű |
| [9] | pyCycle repó | A `high_bypass_turbofan` mintapélda, ezt követi a modell | Tudd, miben tér el tőle: VBV, nincs hűtőlevegő |
| [10] | Gray et al. (2019) OpenMDAO | Newton-megoldó, implicit komponensek | – |
| [14] | EASA TCDS E.003 | Tolóerő, N1/N2 és EGT-határok, fokozatszám | Keresd meg benne a saját számaidat |
| [2] | Aircraft Commerce No. 50 | -5A/-5B specifikációk, EGT margin, /P és /3 változatok | Ellenőrizd az oldalszámot |
| [13] | Wikipedia: CFM56 | Tömegáram-tartomány, SFC-értékek | **Gyenge forrás, és erre épül a validáció.** Keress elsődleges forrást |
| [15] | Airbus FCOM | Indítási küszöbök, alapjárati értékek | **A dolgozat is jelzi:** a kiadás és a fejezet pontosítandó |
| [3] | ICAO Emissions Databank | LTO-ciklus, alapjárati fogyasztás | Nézd meg a -5B1 sorát |
| [1], [12] | CFM-kiadványok | Történet, LEAP | **Keresd meg.** Ha nem találod, cseréld le |

Ezeket a tényállításokat is ellenőrizd, mert rákérdezhetnek:
- „több mint 20 000 darab” a CFM56-5B-ből. Valószínűleg a teljes CFM56-családra igaz, nem a -5B-re.
- CFM56-5A „1987-ben állt szolgálatba”. Nézd meg, hogy ez a tanúsítás vagy a forgalomba állás éve.

---

## 3. Előismeretek – képletek a saját számaiddal

Ezeket tudd **táblán, fejből** levezetni. Tervezési pont: 288,2 K és 101,3 kPa belépés, FAR = 0,02632.

**Ideális Brayton-hatásfok**
η_th = 1 − OPR^(−(γ−1)/γ) = 1 − 26,96^(−0,2857) ≈ **0,61**. A valós ennél lényegesen kisebb.

**Kompresszió összesített izentropikus hatásfoka**
T3s = 288,2 · 26,96^0,2857 ≈ 738,5 K → η_c = (738,5 − 288,2)/(795,8 − 288,2) ≈ **0,887**. Összhangban van a megadott 0,87–0,89 értékekkel.

**Magáram és tüzelőanyag**
ṁ_core = 370/(1 + 5,5) = 56,9 kg/s → ṁ_f = 0,02632 · 56,9 ≈ **1,50 kg/s**

**Teljesítménymérleg (a legjobb kézi bizonyíték)**

| Tengely | Felvett | Leadott |
|---------|---------|---------|
| HP | HPC: 56,9 · (514,8 − 122,0) = **22,36 MW** | HPT: 58,4 · (501,6 − 118,8) = **22,36 MW** |
| LP | Fan: 370 · (37,9 + 14,4) = 19,35 MW; LPC: 56,9 · (122,0 − 37,9) = 4,78 MW; együtt **24,13 MW** | LPT: 58,4 · (118,8 + 294,2) = **24,13 MW** |

**Tolóerő statikusan:** Fg = 138,41 kN = mag 42,32 kN + bypass 96,09 kN
- Mag: **fojtott**, M = 1,0, Ps = 143,7 kPa, V = 592 m/s, A = 0,182 m². Impulzus 58,4 · 592 = 34,6 kN + nyomáserő (143,7 − 101,3) kPa · 0,182 m² = 7,7 kN → 42,3 kN.
- Bypass: nem fojtott, M = 0,90, V = 308 m/s. 313,1 · 308 = 96,3 kN, a Cv = 0,9975 veszteséggel 96,1 kN.

**Ram drag Mach 0,25-ön:** V0 ≈ 85 m/s → 381,4 · 85 ≈ **32,5 kN**. Fn = 146,1 − 32,5 = 113,7 kN

**SFC átváltás:** 1 lb/(lbf·h) ≈ 28,3 g/(kN·s). Tehát 10,84 g/(kN·s) ≈ 0,38; 17,41 ≈ 0,61; a közölt 15,4 ≈ 0,54 lb/(lbf·h).

**Összhatásfok utazáskor** (Fn = 21,7 kN, ṁ_f = 0,378 kg/s, V0 ≈ 231 m/s, LHV ≈ 43 MJ/kg):
η_0 = F·V0/(ṁ_f·LHV) = 5,0 MW / 16,3 MW ≈ **0,31**

**Még ezekre készülj:**
- Izentropikus hatásfok kompresszorra és turbinára: miért fordított a tört.
- Propulziós hatásfok: η_p = 2/(1 + V_j/V_0). Ezért jó a nagy BPR. Termikus × propulziós = összhatásfok.
- ISA: T = 288,15 − 6,5·h [km] 11 km-ig; 35 000 ft ≈ 218,85 K, ≈ 23,8 kPa.
- Össz- és statikus állapot: T_t = T·(1 + (γ−1)/2·M²). Mach 0,78-on 218,85 K → 245,5 K.
- Kompresszor-jelleggörbe: nyomásviszony, korrigált tömegáram, korrigált fordulatszám, pompázshatár, R-line.
- Mi a VBV, és miért nyit részterhelésen.
- Fojtott fúvócső: kritikus nyomásviszony ≈ 1,85–1,9. A mag 2,62-vel fojtott, a bypass 1,68-cal nem.
- Kéttengelyes felépítés: fan + LPC + LPT az LP, HPC + HPT a HP tengelyen.
- Miért az N2-t forgatja az indítómotor: az AGB a HP tengelyről hajtódik.
- FADEC feladata: tüzelőanyag-adagolás, indítási szekvencia, határérték-felügyelet.
- A CFM56 elsődleges tolóerő-paramétere az **N1**, nem az EPR. A modell EPR-je csak számított kijelzés.

**Miért csökken S3→S4 között az entalpia (514,8 → 501,6), ha a gáz melegszik?** Mert a CEA abszolút entalpiát számol, amely tartalmazza a képződési entalpiát, és az égés megváltoztatja az összetételt. Ezért csak azonos összetételű különbségek értelmezhetők fajlagos munkaként.

---

## 4. Kiinduló adatok – „Honnan van ez a szám? Milyen közelítéssel?”

| Adat | Érték | Eredet – amit mondhatsz |
|------|-------|--------------------------|
| Referencia-tolóerő | 133,45 kN (-5B1) | EASA TCDS. **Statikus** érték, ezért a statikus modellel kell összevetni |
| BPR | 5,5 | Nyilvános összesítő adat [13]. Tervezési **bemenet** |
| OPR | 27 | **Saját felvétel**, a fan/LPC/HPC PR szorzata adja |
| Fan / LPC / HPC PR | 1,685 / 2,0 / 8,0 | **Saját felvétel**, valós komponens-PR nem publikus |
| Hatásfokok | 0,87–0,90 | Tipikus szakirodalmi értékek [4], [7], nem CFM-adat |
| T4 | 1700 K | **Saját becslés**, a CFM56-5B értéke nem publikus |
| Tömegáram | 370 kg/s | A 368–439 kg/s tartományból [13]. Tervezési **bemenet** |
| FAR | 0,0263 | **Eredmény**, a balance adja a T4-ből |
| HPT / LPT PR | 2,665 / 3,745 | **Eredmény**, a tengely-egyensúly adja |
| Égőtéri nyomásveszteség | 3 % | Tipikus érték |
| Fúvócső Cv | 0,9999 / 0,9975 | A pyCycle mintapéldából átvett érték. Ellenőrizd, és tudd megindokolni |
| Jelleggörbék | AXI5, LPCMap, HPCMap, HPTMap, LPTMap | pyCycle mintagörbék, a tervezési pontra skálázva. **Nem CFM56-mérés** |
| 100 % fordulatszám | N1 5000, N2 14 460 1/min | TCDS: 5200 = 104 %, 15 183 = 105 % |
| VBV-ütemezés | 1650 K felett zárt, 1000 K-nél 30 % | **Saját egyszerűsítés.** A valódi FADEC a korrigált N2-ből vezérli |
| Gázkar | T4 = 1000 + 7 · gázkar% | **Saját leképezés.** A valódi kar N1-célt ad a FADEC-nek |
| Gáztulajdonságok | CEA, Jet-A(g) | Hőmérséklet- és összetételfüggő |
| Entrópia a T-s diagramon | cp = 1,005; R = 0,287 | Kalorikusan tökéletes gáz, magas T-n pontatlan |
| Indítási paraméterek | I = 10, k_d = 1, Q_0 = 40 | **Normalizált, hangolt**, nem fizikai mértékegységű |
| Alapjárat | N2 60 %, N1 19 %, EGT 450 °C | Üzemeltetési értékek [15], pontosítandó |
| Alapjárati FF | 600 kg/h | **Hangolt érték, forrás nélkül.** Vesd össze az ICAO alapjárati adatával, mert valószínűleg túl nagy |
| Start EGT-határ | 725 °C | EASA TCDS [14] |
| Light-off N2 | 18 % | Egyszerűsítés: a valós gyújtás ~16 %, a HP tüzelőanyag-szelep ~22 % [15] |
| Indító kioldás | 50 % N2 | [15] |

Fontos különbség, amit tudj kimondani: **a BPR, OPR, T4 és tervezési tömegáram egyezése nem validálás**, mert ezek bemenetek. Off-design pontokban már eredmények.

---

## 5. Módszer – „Milyen más módszert alkalmazhatott volna?”

**Stacioner ciklusanalízis alternatívái:**
- **Kézi vagy táblázatos 0D számítás** (Mattingly): átlátható, de konstans cp és off-design nélkül.
- **GasTurb** (Kurzke): oktatásban és iparban elterjedt, kész jelleggörbékkel. Fizetős, zárt.
- **NPSS** (NASA/SwRI): ipari standard, nem szabadon elérhető.
- **GSP** (NLR): objektumorientált, tranziens is.

**Tranziens alternatívái:**
- **T-MATS** (NASA, MATLAB/Simulink): dinamikus modell szabályozókkal.
- **Komponensszintű modell** idle alá extrapolált jelleggörbékkel: a jelleggörbék ott nem ismertek.
- **Adatvezérelt modell** QAR/FDR-felvételekből: ehhez nem volt adat.

**Miért ez lett a választás:**
- pyCycle: ingyenes, nyílt, Python, így saját vizualizációval és appal összeköthető, és implicit balance-okkal zárható a ciklus.
- Az indítás külön modell, mert idle alatt nincs jelleggörbe, és élőben kell futnia. A cél a **jelenségek és a tünetek** bemutatása, nem a pontos számok.

**Numerika:**
- Cikluszárás: OpenMDAO Newton-megoldó, `BalanceComp`. Tervezésnél FAR → T4, HPT PR → HP pwr_net = 0, LPT PR → LP pwr_net = 0.
- Off-design: FAR → T4; W → mag-fúvócső terület; BPR → bypass-fúvócső terület; N1, N2 → tengely-egyensúly.
- Continuation: a Newton csak közeli kezdőpontból konvergál, ezért legfeljebb 2500 ft / 0,05 Mach / 50 K lépések.
- Minden pont ellenőrzött: T4-cél, tengelymérleg, jelleggörbe-tartomány, fordulatszám-határ.
- Indítás: I·dN2/dt = Q_indító + Q_turbina − Q_ellenállás, **explicit Euler**, Δt = 0,5 s. Stabil, mert I/k_d = 10 s ≫ 0,5 s. Pontosabb lenne az RK4.
- Idle-egyensúly: k_t = k_d · N2_idle, ezért f_FF = 1-nél dN2/dt = 0 pontosan N2 = 60 %-nál. Tudd levezetni!
- Trend az appban: elsőrendű késleltetés, τ = 4 s, nem számított tengelydinamika.

**Indítási hibák kézi levezetése:**
- Nincs tüzelőanyag vagy gyújtás: 40·(1 − N2/50) = N2 → N2 = **22,2 %** (szimuláció: 22,1 %).
- Hung start: 40·(1 − N2/50) + 42 = N2 → N2 = **45,6 %** (szimuláció: 45,5 %). Az 50 % nincs elérve, ezért az indító nem old ki.

| Forgatókönyv | Gyökok | Tünet | Jelzés |
|--------------|--------|-------|--------|
| Normál | – | IDLE 60,5 s, EGT-csúcs 633 °C | – |
| Hung | f_FF ≤ 0,7 | N2 45,5 %, N1 12,5 % | HUNG START, 43,5 s |
| Hot | tüzelőanyag × 1,8 | EGT-csúcs 977 °C, **de eléri az alapjáratot** | EGT EXCEEDANCE, 10 s |
| No fuel | szelephiba | N2 22,1 %, EGT 15 °C, FF = 0 | NO LIGHT-OFF, 18,5 s |
| No ignition | gyújtóhiba | N2 22,1 %, EGT 15 °C, FF = 255 kg/h | WET START, 18,5 s |

**Ellenőrzés:** 97 pytest-teszt, kézi mérleg, megrekedési fordulatszámok levezetése.

---

## 6. Várt és valós eredmények

| Fázis | T4 [K] | ṁ [kg/s] | Fn [kN] | Ram drag [kN] | SFC [g/(kN·s)] | OPR | BPR | N1 / N2 [%] | Érvényes? |
|-------|--------|----------|---------|---------------|----------------|-----|-----|-------------|-----------|
| Statikus tervezési pont | 1700 | 370,0 | 138,3 | 0,1 | 10,84 | 26,96 | 5,50 | 100 / 100 | igen |
| Felszállás, M 0,25 | 1700 | 381,4 | 113,7 | 32,5 | 13,44 | 26,42 | 5,55 | 100,2 / 100,3 | igen |
| Emelkedés, 15 000 ft, M 0,50 | 1700 | 264,9 | 69,0 | 42,7 | 16,10 | 29,44 | 5,37 | 101,8 / 99,0 | igen |
| Utazás, 35 000 ft, M 0,78 | 1700 | 152,3 | 36,1 | 35,2 | 18,80 | 33,59 | 5,11 | 107,1 / 97,8 | **nem** |
| Utazás, legnagyobb érvényes | 1490 | 139,4 | 25,5 | 32,3 | 17,48 | 24,74 | 5,56 | 91,7 / 91,9 | igen |
| Utazás, kb. 22 kN | 1420 | 133,7 | 21,7 | 30,9 | 17,41 | 22,02 | 5,64 | 89,6 / 90,2 | igen |

**Ami megfelel az elvárásnak:**
- A tolóerő és a tömegáram a magassággal csökken.
- Az SFC a repülési sebességgel nő: 10,84 → 13,44 → 17,4.
- Az SFC-görbe U alakú a gázkar függvényében. Minimum felszállásnál 12,28 (55 %), emelkedésnél 15,09 (60 %).
- Az N1 kb. 100 % felszállásnál, amit a modell nem kapott bemenetként.

**Ami ellentmond az elvárásnak, és amit mondhatsz:**

**6.1 Több a tolóerő, mégis rosszabb az SFC.** 138,3 kN a 133,4-del szemben (+3,7 %), de SFC +8…+17 % statikusan, +13 % utazáskor. Hűtőlevegő nélkül a modell felfelé torzítja a tolóerőt, tehát az SFC-eltérés oka inkább a becsült ciklus: az OPR 27 és a hatásfokok. Kalibrálás nem történt.

**6.2 Miért 113,7 kN a felszállásnál, ha 133 kN a névleges?** Mert 133,4 statikus adat. Mach 0,25-ön kb. 32,5 kN a ram drag. Az érték nem hiba, a két állapot nem hasonlítható össze.

**6.3 Utazáskor T4 = 1700 K-nél N1 = 107 %.** A TCDS-határ 104 %, és az LPC lefut a jelleggörbéről (R-line 112). A modellben a gázkar T4-et állít, a valódi FADEC viszont N1-et vezérel és korlátoz, ezért a valódi hajtómű ide nem jutna el. Utazásnál az érvényes tartomány 10–70 %.

**6.4 13 érvénytelen pont a 63-ból.**

| Fázis | Érvénytelen gázkarállások | Ok |
|-------|---------------------------|-----|
| Felszállás | 0, 5 % | fan R-line > 2,6 |
| Emelkedés | 0, 5, 10 % | fan R-line > 2,6 |
| Utazás | 0, 5 % és 75–100 % | fan R-line, illetve LPC off map; 95–100 %-nál N1 > 104 % |

Ezek megmaradtak az adatsorban, de meg vannak jelölve, és az app figyelmeztet rájuk. A 75 %-os és annál nagyobb gázkarállású utazási pontok az LPC R-line miatt megbízhatatlanok, az eredményeidben ne hivatkozz rájuk.

**6.5 A 0 % gázkar nem alapjárat.** T4 = 1000 K-nél N1 = 75,7 %, tolóerő 14,9 kN (a statikus érték 11 %-a), a valódi alapjárat kb. N1 20 %. Az igazi alapjárat a jelleggörbék tartományán kívül van, ezért ott a modell nem ad megbízható eredményt.

**6.6 Szakadék az indítás és a ciklusmodell között.** Az indítás N1 ≈ 19 %-nál ér véget, a legalacsonyabb ciklusmodell-pont N1 ≈ 76 %. Az app ezt elsőrendű késleltetéssel köti össze, tehát **ez az átmenet nem fizikai számítás**. A bemutatón ezt mondd ki, mielőtt megkérdezik (7. fejezet).

**6.7 Az EGT alacsony.** A modell 798 °C-ot ad felszálláskor a 950 °C-os határ mellett. A modell EGT-je az **LPT kilépő** (S5) hőmérséklete, a valódi mérés viszont a T49.5 pont, az LPT belsejében, ahol a gáz még melegebb. Tehát a kettő nem azonos pont, ezért nem hasonlítható össze közvetlenül. Emellett a 1700 K is becslés.

**6.8 Light-off után a turbina önmagában is gyorsítana.** N2 = 18 %-nál a turbina 60 · 0,35 = 21, az ellenállás 18 egység. A valódi hajtómű ennél jóval később válik önfenntartóvá, ezért kell az indító kb. 50 %-ig. Az alak hangolt, nem fizikai.

**6.9 A FADEC nem szakít meg.** A valódi A320 automatikus indításnál földön bizonyos hibáknál magától megszakít. Itt csak detektál, hogy a hiba teljes lefolyása látható legyen. Ez tudatos egyszerűsítés.

**6.10 A „melegfennakadás” elnevezés.** A HOT forgatókönyvben a hajtómű nem akad fenn, hanem túlmelegszik és eléri az alapjáratot. Ez *hot start*, nem *hot hang*. Nézd meg a konzulenseddel egyeztetett megnevezést.

**6.11 Miért nagyobb az OPR emelkedésnél, mint felszállásnál?** Az emelkedési OPR 29,4, a felszállási 26,4. A hidegebb belépő levegő miatt nagyobb a korrigált fordulatszám. Utazáskor 1700 K-nél 33,6 lenne, de az a pont érvénytelen.

---

## 7. Bemutató forgatókönyv (projektor)

**Előkészítés, napokkal előtte:**

```bash
cd Engine/Engine
.venv/bin/python -m streamlit run app.py
```

- **A .venv környezetet használd.** A gép alap `python3.12` környezete régi Streamlitet tartalmaz (1.37), amellyel az app `TypeError`-ral leáll.
- Az app élőben nem futtatja a pyCycle-t, a `data/lookup.pkl`-ből olvas. Ettől gyors, ezt tudd elmondani.
- Nyilvános link: https://cfm56ziad.streamlit.app. Internetet igényel, és használat nélkül elalszik, ezért a bemutató előtt ébreszd fel, és nézd meg, hogy betölt-e.
- Legyen **offline tartalék** (képernyővideó vagy képernyőképek), és próbáld ki a projektor felbontásán.

**Menet:**
1. **Normál indítás:** MODE IGN/START → ENG 1 ON. Mutasd a light-off-ot (9 s), a kioldást (31,5 s), az IDLE-t (60,5 s). A sebesség 1/5/10-szeres.
2. **Figyelem:** IDLE után az E/WD magától kb. 76 % N1-re fut fel, és megjelenik az érvénytelen pont figyelmeztetése, mert a csúszka 0 %-on áll, ami nem alapjárat. **Mondd ki előre:** ez a 6.6 pont, a két modell közti szemléltető átmenet.
3. **Gázkar:** csúszka 50–100 %, trend, majd állomás- és T-s diagram, 3D modell. Válts Cruise-ra, és húzd 75 % fölé: mutasd a figyelmeztetést (6.3).
4. **Hot start:** ENG 1 OFF, scenario HOT, újraindítás → EGT 977 °C, EGT EXCEEDANCE. Magyarázd a gyökokot.
5. **Hung start:** N2 45,5 %-on megreked. Vezesd le az egyensúlyt.
6. **Kód:** `engine/start_transient.py` → `dN2_dt()`, `engine/cfm56.py` → `CFM56_PARAMS` és a balance-ok.
7. **Tesztek gyorsan** (a teljes készlet kb. 2,5 perc, ezért bemutatón csak ez, 1 másodperc alatt fut):

```bash
.venv/bin/python -m pytest -q -W ignore tests/test_start_plant.py tests/test_start_faults.py tests/test_fadec.py tests/test_simulate_start.py
```

8. **Kézi számítás a táblán:** η_c ≈ 0,887 és a HP-mérleg.

---

## 8. Javítandó a dolgozatban

A dolgozat számai megegyeznek a jelenlegi modellel. Ezek a szöveges pontatlanságok maradtak. Szándékosan nem írtam át őket, mert a dolgozat szövegét neked kell megvédened.

| Fejezet | Mostani szöveg | Probléma | Javítás iránya |
|---------|----------------|----------|----------------|
| Bevezetés | „több mint 20 000 darabot” a -5B-ből | Valószínűleg a családra igaz | Forrásból ellenőrizni |
| 2.1 | A ciklus „három fő folyamatból áll” | A zárt ideális ciklus négy folyamat | Hozzávenni az izobár hőelvonást |
| 2.1 | Az égés „vízszintes” szakasz a T-s diagramon | Az izobár hőközlés emelkedő görbe, T és s is nő. A kompresszió és expanzió közel függőleges | Átírni |
| 2.3 | A gázkar „fizikailag a tüzelőanyag-adagoló szelepet vezérli” | Az A320-on a kar a FADEC-nek ad parancsot, N1-célt | Pontosítani |
| 3.1 | openmdao 3.39, „pontos verziók” | Mostantól rögzítve: openmdao 3.45.2, numpy 2.2.6 | Frissíteni |
| 3.2 | „A fúvócsövek a környezeti statikus nyomásra expandálnak” | A mag fojtott (M = 1, Ps = 143,7 kPa), nyomáserő keletkezik. A 2.4 tolóerő-képlete ezt jól tartalmazza | Pontosítani |
| 4.1 | Az „entalpia-különbség negatív előjelű értékei” | Nem a különbség, hanem egyes állomások abszolút h-ja negatív | Pontosítani, kiegészíteni a 3. fejezet S3→S4 magyarázatával |
| 5.5 | „legkisebb érvényes gázkarállása (T4 = 1000 K, N1 ≈ 76 %)” | A 0 % és 5 % érvénytelen. A legkisebb érvényes felszállásnál 10 %: 1070 K, N1 80,2 % | Javítani |
| 5.4 | „melegfennakadás” | Lásd 6.10 | Megnevezés egyeztetése |
| 6.1 | Az EGT nincs értékelve | S5 és T49.5 eltérése | Kiegészíteni 6.7 alapján |
| Nyilatkozat | „2026. május” | Elavult dátum | Leadáskor frissíteni |

A dolgozatot a `generate_thesis.py` generálja. Ha a `.docx`-et kézzel szerkeszted, ne futtasd újra, mert felülírja.

---

## 9. Teendőlista a meghallgatásig

**Kötelező:**
- [ ] Minden hivatkozást kézbe venni; amit nem találsz, cserélni (2. fejezet).
- [ ] A Wikipedia [13] SFC-adatait elsődleges forrással kiváltani vagy alátámasztani.
- [ ] Az FCOM [15] kiadását és fejezetét pontosítani.
- [ ] A 8. fejezet pontjait saját szavaiddal javítani.
- [ ] Az alapjárati 600 kg/h-t az ICAO-adattal összevetni.
- [ ] Minden képletet fejből levezetni (3. fejezet).
- [ ] 5 perces összefoglaló gyakorlása.
- [ ] Bemutató végigpróbálása a `.venv`-ből, offline tartalék elkészítése.
- [ ] Átgondolni, pontosan mire használtál MI-t, és hogyan mondod el (0. fejezet).

**Ajánlott, ha marad idő:**
- [ ] A dolgozat szövegét végig saját szavaiddal átírni. Minden mondatot meg kell tudnod védeni.
- [ ] Kalibrálás: az OPR és a hatásfokok hatása az SFC-eltérésre.
- [ ] Hűtőlevegő beépítése.

---

## 10. Gyors válaszok nehéz helyzetekre

- **„Ezt nem tudom.”** → „Ezt nem vizsgáltam, de úgy közelíteném meg, hogy…”, és mondj egy módszert.
- **„Ez hibás.”** → „Igen, az oka …, és a végleges dolgozatban így javítom: …”
- **„Honnan van ez?”** → Mondd meg őszintén, ha becsült vagy hangolt érték, és mi alapján.
- **„Használt MI-t?”** → Igen, és mondd el pontosan, mire. Mutasd meg, hogy érted és ellenőrizted az eredményt: a kézi számítások (η_c, tengelymérleg, ram drag, megrekedési N2) erre valók. Olyat ne állíts, ami nem igaz.
