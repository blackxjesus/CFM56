# Szakdolgozat II meghallgatás – felkészülési jegyzet

> Ezt a jegyzetet magamnak írtam, nem felolvasásra. Kulcsszavakat tanulok, és minden számot le akarok tudni vezetni.
> 2026-11-02-i állapot, a számokat a jelenlegi modellből vettem (`data/results.csv`, `data/design_point.pkl`).

---

## 0. Mit néz a bizottság, és hol tartok

A kiírás szerint azt kell igazolnom, hogy **a dolgozat a saját önálló munkám**. A bizottságban legalább 3 fő ül, köztük a belső konzulensem. Öt témát néznek, ehhez igazítottam ezt a jegyzetet:

| Bizottsági téma | Példakérdés a kiírásból | Fejezet |
|-----------------|-------------------------|---------|
| Szakirodalom | „Mit olvasott ebben a szakirodalomban?” | 2. |
| Tantárgyi előismeretek | „Mit tanult ezzel kapcsolatban repüléselméletből?” | 3. |
| Kiinduló adatok és forrásuk | „Honnan származik ez az adat? Milyen közelítéssel alkalmazta?” | 4. |
| Módszer | „Milyen más módszert alkalmazhatott volna még?” | 5. |
| Várt és valós eredmények | „Miben mond ellent ez az eredmény az elvárásainak?” | 6. |

Amit még kiírtam magamnak a kiírásból:
- 5 perces összefoglalót kell tartanom **saját szavaimmal**, nem felolvasva. Prezentáció nem kell.
- Használhatok jegyzetet, táblázatot és az appot, sőt érdemes bemutatnom őket (projektor / okostábla).
- A forma nem számít, az igen, hogy **értem-e** a saját anyagomat.
- Ebből lesz a Szakdolgozat II. jegyem.

**Amire építhetek:**
- A tervezési pontot tengely-egyensúllyal zártam, a teljesítménymérleg kézzel is kijön.
- Valódi off-design számítást csináltam rögzített geometriával: tömegáram, BPR, OPR, N1, N2 eredmény, nem bemenet.
- Megírtam a tranziens indítási modellt, a FADEC-logikát és 4 indítási hibát, a megrekedési fordulatszámokat kézzel is levezettem.
- Van működő appom, 109 automatikus tesztem, és verziókezelést használtam.

**Amire szerintem rákérdeznek** (részletek a 6. fejezetben):
1. Az SFC 8–17 %-kal nagyobb a közölt értékeknél, a tolóerő viszont +3,7 %.
2. A 63 munkapontomból 13 érvénytelen.
3. A földi alapjárat nincs benne a ciklusmodellemben, szakadék van az indítási modell és a ciklusmodell között.
4. A validációm egyik fő forrása a Wikipedia [13].
5. Maradt pár szakmai pontatlanság a dolgozatomban (8. fejezet).

**MI-használat.** A meghallgatást a generatív MI miatt vezették be. A repómban a 76 commitból 53-ban Claude társszerzőként szerepel (2026-11-02), és ez látszik, ha megmutatom. Ezt magamtól mondom el: mire használtam MI-t, és mi volt az én döntésem. Csak azt mondom a saját ötletemnek, ami tényleg az volt. Nem a válaszokat tanulom be, hanem hogy minden sort meg tudjak indokolni.

---

## 1. Az 5 perces összefoglalóm vázlata

1. **Téma (30 s):** CFM56-5B, A320-család. A célom a ciklus megértése volt szimulációval, üzemeltetési (pilótafülke) szemmel.
2. **Tervezési pont (1 perc):** pyCycle/OpenMDAO, kéttengelyes turbofan, CEA-gáztulajdonságok. Bemenet: 370 kg/s, BPR 5,5, OPR 27, T4 1700 K. A FAR a T4-et, a turbina-PR-ek a tengely-egyensúlyt zárják. Eredmény: 138,3 kN, 10,84 g/(kN·s).
3. **Off-design (1 perc):** rögzített geometria, 3 repülési fázis, 21 gázkarállás, 63 pont, VBV-ütemezés. Felszállás 113,7 kN (ram drag), utazás kb. 22 kN-nál SFC 17,41.
4. **Indítás és FADEC (1,5 perc):** tehetetlenségi ODE, szekvencia, 4 hiba tünetei, detektálás.
5. **App és ellenőrzés (30 s):** E/WD, tesztek, kézi mérleg.
6. **Kritikus értékelés (30 s):** SFC-eltérés oka, érvénytelen pontok, alapjárati szakadék, hűtőlevegő.

Stopperrel, hangosan elmondom 2–3-szor.

---

## 2. Szakirodalom – „Mit olvasott ebben?”

Csak azt hivatkozom, ami tényleg a kezemben volt, és mindegyikről tudnom kell 2–3 mondatot mondani.

| # | Forrás | Miről szól | Mit csinálok vele |
|---|--------|------------|--------|
| [4] | Mattingly: *Elements of Propulsion* | Turbofan ciklusanalízis, állomásszámozás, tolóerő, TSFC | Elolvasom a turbofan parametrikus ciklusanalízist |
| [5] | Çengel–Boles: *Thermodynamics* | Brayton-ciklus, izentropikus hatásfok, T-s diagram | – |
| [6] | Cumpsty–Heyes: *Jet Propulsion* | Tolóerő, propulziós hatásfok, BPR szerepe | – |
| [7] | Walsh–Fletcher: *Gas Turbine Performance* | Design és off-design, jelleggörbék, tranziens | Elolvasom az off-design fejezetet |
| [11] | Kurzke–Halliwell: *Propulsion and Power* | Teljesítménymodellezés, hűtőlevegő, jelleggörbe-skálázás | – |
| [8] | Hendricks–Gray (2019), *Aerospace* 6(8):87 | A pyCycle módszere, CEA-alapú termodinamika | Elolvasom, nyílt hozzáférésű |
| [9] | pyCycle repó | `high_bypass_turbofan` mintapélda, erre épül a modellem | Tudom, miben tér el: VBV, nincs hűtőlevegő |
| [10] | Gray et al. (2019) OpenMDAO | Newton-megoldó, implicit komponensek | – |
| [14] | EASA TCDS E.003 | Tolóerő, N1/N2 és EGT-határok, fokozatszám | Megkeresem benne a saját számaimat |
| [2] | Aircraft Commerce No. 50 | -5A/-5B specifikációk, EGT margin, /P és /3 változatok | Ellenőrzöm az oldalszámot |
| [13] | Wikipedia: CFM56 | Tömegáram-tartomány, SFC-értékek | **Gyenge forrás, pedig erre épül a validációm.** Keresek elsődleges forrást |
| [15] | Airbus FCOM | Indítási küszöbök, alapjárati értékek | A dolgozatban is jeleztem: a kiadást és a fejezetet pontosítom |
| [3] | ICAO Emissions Databank | LTO-ciklus, alapjárati fogyasztás | Megnézem a -5B1 sorát |
| [1], [12] | CFM-kiadványok | Történet, LEAP | Megkeresem, ha nincs meg, lecserélem |

Ezeket a tényállításokat is ellenőrzöm, mert rákérdezhetnek:
- „több mint 20 000 darab” a CFM56-5B-ből: ez szerintem a teljes CFM56-családra igaz, nem a -5B-re.
- CFM56-5A „1987-ben állt szolgálatba”: megnézem, hogy ez a tanúsítás vagy a forgalomba állás éve.

---

## 3. Előismeretek – képletek a saját számaimmal

Ezeket táblán, fejből le kell tudnom vezetni. Tervezési pont: 288,2 K és 101,3 kPa belépés, FAR = 0,02632.

**Ideális Brayton-hatásfok**
η_th = 1 − OPR^(−(γ−1)/γ) = 1 − 26,96^(−0,2857) ≈ **0,61**. A valós ennél jóval kisebb.

**Kompresszió összesített izentropikus hatásfoka**
T_3s = 288,2 · 26,96^0,2857 ≈ 738,5 K → η_c = (738,5 − 288,2)/(795,8 − 288,2) ≈ **0,887**. Stimmel a megadott 0,87–0,89 értékekkel.

**Magáram és tüzelőanyag**
ṁ_core = 370/(1 + 5,5) = 56,9 kg/s → ṁ_f = 0,02632 · 56,9 ≈ **1,50 kg/s**

**Teljesítménymérleg (ez a legjobb kézi bizonyíték)**

| Tengely | Felvett | Leadott |
|---------|---------|---------|
| HP | HPC: 56,9 · (514,8 − 122,0) = **22,36 MW** | HPT: 58,4 · (501,6 − 118,8) = **22,36 MW** |
| LP | Fan: 370 · (37,9 + 14,4) = 19,35 MW; LPC: 56,9 · (122,0 − 37,9) = 4,78 MW; együtt **24,13 MW** | LPT: 58,4 · (118,8 + 294,2) = **24,13 MW** |

**Tolóerő statikusan:** Fg = 138,41 kN = mag 42,32 kN + bypass 96,09 kN
- Mag: **fojtott**, M = 1,0, Ps = 143,7 kPa, V = 592 m/s, A = 0,182 m². Impulzus 58,4 · 592 = 34,6 kN + nyomáserő (143,7 − 101,3) kPa · 0,182 m² = 7,7 kN → 42,3 kN.
- Bypass: nem fojtott, M = 0,90, V = 308 m/s. 313,1 · 308 = 96,3 kN, Cv = 0,9975 veszteséggel 96,1 kN.

**Ram drag Mach 0,25-ön:** V0 ≈ 85 m/s → 381,4 · 85 ≈ **32,5 kN**. Fn = 146,1 − 32,5 = 113,7 kN

**SFC átváltás:** 1 lb/(lbf·h) ≈ 28,3 g/(kN·s). Vagyis 10,84 g/(kN·s) ≈ 0,38; 17,41 ≈ 0,61; a közölt 15,4 ≈ 0,54 lb/(lbf·h).

**Összhatásfok utazáskor** (Fn = 21,7 kN, ṁ_f = 0,378 kg/s, V_0 ≈ 231 m/s, LHV ≈ 43 MJ/kg):
η_0 = F·V_0/(ṁ_f·LHV) = 5,0 MW / 16,3 MW ≈ **0,31**

**Ezeket még átnézem:**
- Izentropikus hatásfok kompresszorra és turbinára: miért fordított a tört.
- Propulziós hatásfok: η_p = 2/(1 + V_j/V_0). Ezért jó a nagy BPR. Termikus × propulziós = összhatásfok.
- ISA: T = 288,15 − 6,5·h [km] 11 km-ig; 35 000 ft ≈ 218,85 K, ≈ 23,8 kPa.
- Össz- és statikus állapot: T_t = T·(1 + (γ−1)/2·M²). Mach 0,78-on 218,85 K → 245,5 K.
- Kompresszor-jelleggörbe: nyomásviszony, korrigált tömegáram, korrigált fordulatszám, pompázshatár, R-line.
- Mi a VBV, és miért nyit részterhelésen.
- Fojtott fúvócső: kritikus nyomásviszony ≈ 1,85–1,9. A mag 2,62-vel fojtott, a bypass 1,68-cal nem.
- Kéttengelyes felépítés: fan + LPC + LPT az LP, HPC + HPT a HP tengelyen.
- Miért az N2-t forgatja az indítómotor: az AGB a HP tengelyről hajtódik.
- FADEC: tüzelőanyag-adagolás, indítási szekvencia, határérték-felügyelet.
- A CFM56 elsődleges tolóerő-paramétere az **N1**, nem az EPR. Ezért az app nem EPR-t mutat, hanem a P8/P2 nyomásviszonyt (mag-fúvócső / belépő teljes nyomás), ez csak számított kijelzés.

**Miért csökken S3→S4 között az entalpia (514,8 → 501,6), ha a gáz melegszik?** Mert a CEA abszolút entalpiát számol, amiben benne van a képződési entalpia is, az égés pedig megváltoztatja az összetételt. Fajlagos munkaként csak azonos összetételű különbségek értelmezhetők.

---

## 4. Kiinduló adatok – „Honnan van ez a szám? Milyen közelítéssel?”

| Adat | Érték | Honnan |
|------|-------|--------|
| Referencia-tolóerő | 133,45 kN (-5B1) | EASA TCDS. **Statikus** érték, a statikus modellel kell összevetni |
| BPR | 5,5 | Nyilvános összesítő adat [13]. Tervezési **bemenet** |
| OPR | 27 | **Saját felvétel**, a fan/LPC/HPC PR szorzata |
| Fan / LPC / HPC PR | 1,685 / 2,0 / 8,0 | **Saját felvétel**, valós komponens-PR nem publikus |
| Hatásfokok | 0,87–0,90 | Tipikus szakirodalmi értékek [4], [7], nem CFM-adat |
| T4 | 1700 K | **Saját becslés**, a CFM56-5B értéke nem publikus |
| Tömegáram | 370 kg/s | A 368–439 kg/s tartományból [13]. Tervezési **bemenet** |
| FAR | 0,0263 | **Eredmény**, a balance adja a T4-ből |
| HPT / LPT PR | 2,665 / 3,745 | **Eredmény**, a tengely-egyensúlyból |
| Égőtéri nyomásveszteség | 3 % | Tipikus érték |
| Fúvócső Cv | 0,9999 / 0,9975 | A pyCycle mintapéldából vettem át. Ellenőrzöm, hogy meg tudjam indokolni |
| Jelleggörbék | AXI5, LPCMap, HPCMap, HPTMap, LPTMap | pyCycle mintagörbék, a tervezési pontra skálázva. **Nem CFM56-mérés** |
| 100 % fordulatszám | N1 5000, N2 14 460 1/min | TCDS: 5200 = 104 %, 15 183 = 105 % |
| VBV-ütemezés | 1650 K felett zárt, 1000 K-nél 30 % | **Saját egyszerűsítés.** A valódi FADEC a korrigált N2-ből vezérli |
| Gázkar | T4 = 1000 + 7 · gázkar% | **Saját leképezés.** A valódi kar N1-célt ad a FADEC-nek |
| Gáztulajdonságok | CEA, Jet-A(g) | Hőmérséklet- és összetételfüggő |
| Entrópia a T-s diagramon | cp = 1,005; R = 0,287 | Kalorikusan tökéletes gáz, magas T-n pontatlan |
| Indítási paraméterek | I = 10, k_d = 1, Q_0 = 40 | **Normalizált, hangolt**, nem fizikai mértékegységű |
| Alapjárat | N2 60 %, N1 19 %, EGT 450 °C | Üzemeltetési értékek [15], pontosítandó |
| Alapjárati FF | 600 kg/h | **Hangolt, forrás nélkül.** Összevetem az ICAO alapjárati adatával, szerintem túl nagy |
| Start EGT-határ | 725 °C | EASA TCDS [14] |
| Light-off N2 | 18 % | Egyszerűsítés: valós gyújtás ~16 %, HP tüzelőanyag-szelep ~22 % [15] |
| Indító kioldás | 50 % N2 | [15] |

Ezt ki kell tudnom mondani: **a BPR, OPR, T4 és a tervezési tömegáram egyezése nem validálás**, mert ezek bemenetek. Az off-design pontokban viszont már eredmények.

---

## 5. Módszer – „Milyen más módszert alkalmazhatott volna?”

**Stacioner ciklusanalízis, alternatívák:**
- **Kézi vagy táblázatos 0D számítás** (Mattingly): átlátható, de konstans cp, és nincs off-design.
- **GasTurb** (Kurzke): oktatásban, iparban elterjedt, kész jelleggörbék. Fizetős, zárt.
- **NPSS** (NASA/SwRI): ipari standard, nem szabadon elérhető.
- **GSP** (NLR): objektumorientált, tranziens is.

**Tranziens, alternatívák:**
- **T-MATS** (NASA, MATLAB/Simulink): dinamikus modell szabályozókkal.
- **Komponensszintű modell** idle alá extrapolált jelleggörbékkel: ott a jelleggörbék nem ismertek.
- **Adatvezérelt modell** QAR/FDR-felvételekből: ehhez nem volt adatom.

**Miért ezt választottam:**
- A pyCycle ingyenes, nyílt és Python, így össze tudtam kötni saját vizualizációval és appal, és implicit balance-okkal zárható a ciklus.
- Az indítást külön modellben írtam meg, mert idle alatt nincs jelleggörbe, és élőben kell futnia. A célom a **jelenségek és tünetek** bemutatása volt, nem a pontos számok.

**Numerika:**
- Cikluszárás: OpenMDAO Newton-megoldó, `BalanceComp`. Tervezésnél FAR → T4, HPT PR → HP pwr_net = 0, LPT PR → LP pwr_net = 0.
- Off-design: FAR → T4; W → mag-fúvócső terület; BPR → bypass-fúvócső terület; N1, N2 → tengely-egyensúly.
- Continuation: a Newton csak közeli kezdőpontból konvergál, ezért legfeljebb 2500 ft / 0,05 Mach / 50 K lépések.
- Minden pontot ellenőriztem: T4-cél, tengelymérleg, jelleggörbe-tartomány, fordulatszám-határ.
- Indítás: I·dN2/dt = Q_indító + Q_turbina − Q_ellenállás, **explicit Euler**, Δt = 0,5 s. Stabil, mert I/k_d = 10 s ≫ 0,5 s. RK4-gyel pontosabb lenne.
- Idle-egyensúly: k_t = k_d · N2_idle, így f_FF = 1-nél dN2/dt = 0 pontosan N2 = 60 %-nál. Ezt le kell tudnom vezetni.
- Trend az appban: elsőrendű késleltetés, τ = 4 s, nem számított tengelydinamika.

**Az indítási hibák kézi levezetése:**
- Nincs tüzelőanyag vagy gyújtás: 40·(1 − N2/50) = N2 → N2 = **22,2 %** (szimuláció: 22,1 %).
- Hung start: 40·(1 − N2/50) + 42 = N2 → N2 = **45,6 %** (szimuláció: 45,5 %). Az 50 % nincs meg, ezért az indító nem old ki.

| Forgatókönyv | Gyökok | Tünet | Jelzés |
|--------------|--------|-------|--------|
| Normál | – | IDLE 60,5 s, EGT-csúcs 633 °C | – |
| Hung | f_FF ≤ 0,7 | N2 45,5 %, N1 12,5 % | HUNG START, 43,5 s |
| Hot | tüzelőanyag × 1,8 | EGT-csúcs 977 °C, **de eléri az alapjáratot** | EGT EXCEEDANCE, 10 s |
| No fuel | szelephiba | N2 22,1 %, EGT 15 °C, FF = 0 | NO LIGHT-OFF, 18,5 s |
| No ignition | gyújtóhiba | N2 22,1 %, EGT 15 °C, FF = 255 kg/h | WET START, 18,5 s |

**Ellenőrzés:** 109 pytest-tesztet írtam, kézzel ellenőriztem a mérleget, és levezettem a megrekedési fordulatszámokat.

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

**Ami az elvárásnak megfelel:**
- A tolóerő és a tömegáram a magassággal csökken.
- Az SFC a repülési sebességgel nő: 10,84 → 13,44 → 17,4.
- Az SFC-görbe U alakú a gázkar függvényében. Minimum felszállásnál 12,28 (55 %), emelkedésnél 15,09 (60 %).
- Az N1 kb. 100 % felszállásnál, pedig ezt nem adtam meg bemenetként.

**Ami ellentmond az elvárásnak, és mit mondok rá:**

**6.1 Több a tolóerő, mégis rosszabb az SFC.** 138,3 kN vs. 133,4 (+3,7 %), de SFC +8…+17 % statikusan, +13 % utazáskor. Hűtőlevegő nélkül a modell felfelé torzítja a tolóerőt, tehát az SFC-eltérés oka inkább a becsült ciklus: OPR 27 és a hatásfokok. Kalibrálást nem végeztem.

**6.2 Miért 113,7 kN felszállásnál, ha 133 kN a névleges?** A 133,4 statikus adat. Mach 0,25-ön kb. 32,5 kN a ram drag. Nem hiba, a két állapot nem hasonlítható össze.

**6.3 Utazáskor T4 = 1700 K-nél N1 = 107 %.** A TCDS-határ 104 %, és az LPC lefut a jelleggörbéről (R-line 112). Az én modellemben a gázkar T4-et állít, a valódi FADEC viszont N1-et vezérel és korlátoz, így a valódi hajtómű ide nem jutna el. Utazásnál az érvényes tartomány 10–70 %.

**6.4 13 érvénytelen pont a 63-ból.**

| Fázis | Érvénytelen gázkarállások | Ok |
|-------|---------------------------|-----|
| Felszállás | 0, 5 % | fan R-line > 2,6 |
| Emelkedés | 0, 5, 10 % | fan R-line > 2,6 |
| Utazás | 0, 5 % és 75–100 % | fan R-line, illetve LPC off map; 95–100 %-nál N1 > 104 % |

Bent hagytam őket az adatsorban, de megjelöltem őket, és az app figyelmeztet rájuk. A 75 % feletti utazási pontok az LPC R-line miatt megbízhatatlanok, ezekre nem hivatkozom.

**6.5 A 0 % gázkar nem alapjárat.** T4 = 1000 K-nél N1 = 75,7 %, tolóerő 14,9 kN (a statikus érték 11 %-a), a valódi alapjárat kb. N1 20 %. Az igazi alapjárat kívül esik a jelleggörbéken, ott a modell nem megbízható.

**6.6 Szakadék az indítás és a ciklusmodell között.** Az indítás N1 ≈ 19 %-nál ér véget, a legalacsonyabb ciklusmodell-pont N1 ≈ 76 %. Az appban a 0 % gázkar alapjárat (az indítás végpontja), 5 % fölött elsőrendű késleltetéssel fut fel a ciklusmodell-pontra, vagyis **ez az átmenet nem fizikai számítás**. Bemutatón ezt még a kérdés előtt kimondom (7. fejezet).

**6.7 Alacsony EGT.** A modell 798 °C-ot ad felszálláskor, a határ 950 °C. Az én modellemben az EGT az **LPT kilépő** (S5) hőmérséklete, a valódi mérés viszont a T49.5 pontban van, az LPT belsejében, ahol a gáz még melegebb. Nem ugyanaz a pont, közvetlenül nem összevethető. Ráadásul az 1700 K is becslés.

**6.8 Light-off után a turbina magától is gyorsítana.** N2 = 18 %-nál a turbina 60 · 0,35 = 21, az ellenállás 18 egység. A valódi hajtómű sokkal később lesz önfenntartó, ezért kell az indító kb. 50 %-ig. Az alak hangolt, nem fizikai.

**6.9 A FADEC nem szakít meg.** A valódi A320 automatikus indításnál földön bizonyos hibáknál magától megszakít. Az én FADEC-em csak detektál, hogy a hiba teljes lefolyása látszódjon. Ezt tudatosan egyszerűsítettem így.

**6.10 „Melegfennakadás”.** A HOT forgatókönyvben a hajtómű nem akad fenn, hanem túlmelegszik és eléri az alapjáratot. Ez *hot start*, nem *hot hang*. Megnézem, milyen elnevezést egyeztettem a konzulensemmel.

**6.11 Miért nagyobb az OPR emelkedésnél, mint felszállásnál?** Emelkedés 29,4, felszállás 26,4. Hidegebb belépő levegő → nagyobb korrigált fordulatszám. Utazáskor 1700 K-nél 33,6 lenne, de az a pont érvénytelen.

---

## 7. A bemutatóm (projektor)

**Pár nappal előtte ezt csinálom:**

```bash
cd Engine/Engine
.venv/bin/python -m streamlit run app.py
```

- **A .venv-ből futtatom.** A gépem alap `python3.12`-jében régi Streamlit van (1.37), azzal az app `TypeError`-ral leáll.
- Az app élőben nem futtatja a pyCycle-t, a `data/lookup.pkl`-ből olvas, ezért gyors.
- Nyilvános link: https://cfm56ziad.streamlit.app. Internet kell hozzá, és ha nem használják, elalszik, ezért előtte felébresztem, és megnézem, hogy betölt-e.
- Készítek **offline tartalékot** (képernyővideó vagy képernyőképek), és kipróbálom a projektor felbontásán.

**Így megyek végig rajta:**
1. **Normál indítás:** MODE IGN/START → ENG 1 ON. Megmutatom a light-off-ot (9 s), kioldás (31,5 s), IDLE (60,5 s). Sebesség 1/5/10-szeres.
2. **IDLE:** indítás után alapjáraton marad (N1 18,7 %, N2 59,4 %, FF 600 kg/h), az E/WD „IDLE”-t ír, THR, OPR, SFC „---”. A gázkar 5 % fölé → felfut kb. 80 % N1 fölé. **Ezt előre kimondom:** ez a 6.6 pont, a két modell közti szemléltető átmenet; alapjáratra nincs ciklusmodell-megoldás.
3. **Gázkar:** a bal oldali függőleges gázkart (görgetéskor is a helyén marad) 50–100 % között húzom, megmutatom a trendet, utána az állomás- és T-s diagramot és a 3D modellt. Cruise-ra váltok, 75 % fölé húzom, és megmutatom a figyelmeztetést (6.3).
   **3D modell:** áttetsző burkolat, a jelölők a gázkarral változnak (T4 a 4-es állomáson), az égőtér a helyi gázhőmérséklet szerint izzik (a fúvócső csak nagy tolóerőnél, mert ott kisebb a hőmérséklet), a rotor N1-gyel forog. A **Heat map** gombbal a hajtómű részei a gáz helyi hőmérséklete szerint színeződnek (fan kék, égőtér piros, turbinák felé hűl). Indítás közben is nézhető, a görbét a böngésző játssza le. **Elmondom:** a modell szemléltetés (Sketchfab, CC BY 4.0), a számok a szimulációból jönnek; a forgás lelassítva, a jelölők helye közelítő.
4. **Hot start:** ENG 1 OFF, scenario HOT, újraindítás → EGT 977 °C, EGT EXCEEDANCE. Elmagyarázom a gyökokot.
5. **Hung start:** N2 45,5 %-on megreked. Levezetem az egyensúlyt.
6. **Kód:** megmutatom: `engine/start_transient.py` → `dN2_dt()`, `engine/cfm56.py` → `CFM56_PARAMS` és a balance-ok.
7. **Gyors tesztek** (a teljes készlet kb. 2,5 perc, ezért bemutatón csak ezt futtatom, 1 mp alatt lefut):

```bash
.venv/bin/python -m pytest -q -W ignore tests/test_start_plant.py tests/test_start_faults.py tests/test_fadec.py tests/test_simulate_start.py
```

8. **Kézi számítás:** táblán kiszámolom az η_c ≈ 0,887-et és a HP-mérleget.

---

## 8. Amit javítanom kell a dolgozatomban

A dolgozatom számai megegyeznek a jelenlegi modellel. Ezek a szöveges pontatlanságok maradtak, ezeket saját magam írom át.

| Fejezet | Mostani szöveg | Probléma | Mit csinálok |
|---------|----------------|----------|----------------|
| Bevezetés | „több mint 20 000 darabot” a -5B-ből | Valószínűleg a családra igaz | Forrásból ellenőrzöm |
| 2.1 | A ciklus „három fő folyamatból áll” | A zárt ideális ciklus négy folyamat | Hozzáveszem az izobár hőelvonást |
| 2.1 | Az égés „vízszintes” szakasz a T-s diagramon | Az izobár hőközlés emelkedő görbe, T és s is nő. A kompresszió és expanzió közel függőleges | Átírom |
| 2.3 | A gázkar „fizikailag a tüzelőanyag-adagoló szelepet vezérli” | Az A320-on a kar a FADEC-nek ad parancsot, N1-célt | Pontosítom |
| 3.1 | openmdao 3.39, „pontos verziók” | Most már rögzítve: openmdao 3.45.2, numpy 2.2.6 | Frissítem |
| 3.2 | „A fúvócsövek a környezeti statikus nyomásra expandálnak” | A mag fojtott (M = 1, Ps = 143,7 kPa), nyomáserő keletkezik. A 2.4 tolóerő-képlete ezt jól tartalmazza | Pontosítom |
| 4.1 | Az „entalpia-különbség negatív előjelű értékei” | Nem a különbség, hanem egyes állomások abszolút h-ja negatív | Pontosítom, és kiegészítem a 3. fejezet S3→S4 magyarázatával |
| 5.5 | „legkisebb érvényes gázkarállása (T4 = 1000 K, N1 ≈ 76 %)” | A 0 % és 5 % érvénytelen. A legkisebb érvényes felszállásnál 10 %: 1070 K, N1 80,2 % | Javítom |
| 5.4 | „melegfennakadás” | Lásd 6.10 | Egyeztetem az elnevezést |
| 6.1 | Az EGT nincs értékelve | S5 és T49.5 eltérése | Kiegészítem a 6.7 alapján |
| Nyilatkozat | „2026. május” | Elavult dátum | Leadáskor frissítem |
| 7. fejezet (továbbfejlesztés) | „3D forgatható hajtóműmodell” | Az app már valódi CFM56-5B glTF-modellt mutat, a szimulációhoz kötve. Idegen modell, forrásmegjelölés kötelező | Leírom a 3D nézetet, hivatkozom a modellt (CloudHubOmniTeam, Sketchfab, CC BY 4.0), a „NEO” szót kerülöm |

A dolgozatomat a `generate_thesis.py` generálja. Ha a `.docx`-et kézzel szerkesztem, utána nem futtatom újra, mert felülírja.

---

## 9. Teendőim a meghallgatásig

**Kötelező:**
- [ ] Minden hivatkozást kézbe veszek, amit nem találok, lecserélem (2. fejezet).
- [ ] A Wikipedia [13] SFC-adatait elsődleges forrással kiváltom vagy alátámasztom.
- [ ] Pontosítom az FCOM [15] kiadását és fejezetét.
- [ ] Átírom a 8. fejezet pontjait.
- [ ] Összevetem az alapjárati 600 kg/h-t az ICAO-adattal.
- [ ] Minden képletet fejből levezetek (3. fejezet).
- [ ] Átolvasom a `docs/hajtomu_konyhanyelven.docx`-et: ahol nem tudom saját szavaimmal elmondani, azt alaposabban megnézem.
- [ ] Gyakorlom az 5 perces összefoglalót.
- [ ] Végigpróbálom a bemutatót a `.venv`-ből, és elkészítem az offline tartalékot.
- [ ] Átgondolom, pontosan mire használtam MI-t, és hogyan mondom el (0. fejezet).

**Ha marad idő:**
- [ ] A dolgozatom szövegét végig saját szavaimmal átírom, hogy minden mondatát meg tudjam védeni.
- [ ] Kalibrálok: megnézem az OPR és a hatásfokok hatását az SFC-eltérésre.
- [ ] Beépítem a hűtőlevegőt.

---

## 10. Gyors válaszaim nehéz helyzetekre

- **„Ezt nem tudom.”** → „Ezt nem vizsgáltam, de úgy közelíteném meg, hogy…”, és mondok egy módszert.
- **„Ez hibás.”** → „Igen, az oka …, és a végleges dolgozatban így javítom: …”
- **„Honnan van ez?”** → Őszintén megmondom, ha becsült vagy hangolt érték, és mi alapján.
- **„A 3D modellt maga készítette?”** → Nem: Sketchfab-modell (CloudHubOmniTeam, CC BY 4.0), az app ki is írja. Az enyém a szimulációhoz kötés: jelölők a T, P, h értékekkel, T4/EGT szerinti izzás, a hőtérkép (az állomások közti lineáris gázhőmérséklet a tengely mentén, shaderben számolva), N1 szerinti forgás, az indítási görbe lejátszása.
- **„Használt MI-t?”** → Igen, és elmondom pontosan, mire. Megmutatom, hogy értem és ellenőriztem az eredményt: erre valók a kézi számítások (η_c, tengelymérleg, ram drag, megrekedési N2).
