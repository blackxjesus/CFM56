"""
Generates the CFM56-5B thesis as a properly formatted Word document.
Requirements: python-docx
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ────────────────────────────────────────────────────────────
section = doc.sections[0]
section.left_margin   = Cm(3)
section.right_margin  = Cm(2)
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)

# ── Base font (Times New Roman 12pt) ────────────────────────────────────────
style = doc.styles['Normal']
font  = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
pf = style.paragraph_format
pf.line_spacing = Pt(18)   # ~1.5×12pt
pf.space_after  = Pt(0)

def set_font(run, bold=False, italic=False, size=12):
    run.font.name  = 'Times New Roman'
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic

def heading1(text):
    """Main chapter heading — bold 14pt, new page via page break."""
    doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run(text)
    set_font(run, bold=True, size=14)
    return p

def heading2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    set_font(run, bold=True, size=12)
    return p

def heading3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    set_font(run, bold=True, italic=True, size=12)
    return p

def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.5)
    p.paragraph_format.line_spacing      = Pt(18)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_font(run)
    return p

def caption_fig(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_font(run, size=10)
    return p

def caption_tab(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, bold=True, size=10)
    return p

# ═══════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(72)
r = p.add_run('NYÍREGYHÁZI EGYETEM')
set_font(r, bold=True, size=14)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Műszaki és Agrártudományi Intézet')
set_font(r, size=12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Repülőmérnöki alapképzési szak')
set_font(r, size=12)

doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('CFM56-5B REPÜLŐGÉPHAJTÓMŰ TERMODINAMIKAI\nCIKLUS-ANALÍZISE PYTHON ALAPÚ SZIMULÁCIÓVAL')
set_font(r, bold=True, size=16)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('SZAKDOLGOZAT')
set_font(r, bold=True, size=14)

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Készítette: Mohamed Ziad\nRepülőmérnöki alapszak, VI. félév')
set_font(r, size=12)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Nyíregyháza, 2026')
set_font(r, size=12)

# ═══════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (manual)
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('TARTALOMJEGYZÉK')
set_font(r, bold=True, size=14)
doc.add_paragraph()

toc_entries = [
    ('BEVEZETÉS', '1'),
    ('1. A CFM56-5B HAJTÓMŰ ISMERTETÉSE', '3'),
    ('   1.1. Történeti áttekintés', '3'),
    ('   1.2. Műszaki jellemzők és alkalmazások', '5'),
    ('   1.3. Kétáramú sugárhajtómű működési elve', '7'),
    ('2. TERMODINAMIKAI ALAPOK', '10'),
    ('   2.1. A Brayton-ciklus elmélete', '10'),
    ('   2.2. Kompresszor és turbina termodinamikája', '13'),
    ('   2.3. Égéstér és hőmérséklet-szabályozás', '16'),
    ('   2.4. Fúvócső és tolóerő-generálás', '18'),
    ('3. A SZIMULÁCIÓ MÓDSZERTANA', '21'),
    ('   3.1. NASA pyCycle keretrendszer', '21'),
    ('   3.2. A szimulációs modell felépítése', '23'),
    ('   3.3. Repülési állapotok és bemeneti paraméterek', '26'),
    ('4. SZIMULÁCIÓS EREDMÉNYEK', '29'),
    ('   4.1. Tervezési pont analízis — statikus felszállás', '29'),
    ('   4.2. Off-design analízis — három repülési fázis', '33'),
    ('   4.3. Gázkar-szimuláció eredményei', '37'),
    ('   4.4. T-s diagram elemzése', '40'),
    ('5. HAJTÓMŰINDÍTÁS ÉS INDÍTÁSI HIBÁK TRANZIENS MODELLJE', '44'),
    ('   5.1. A modell célja és felépítése', '44'),
    ('   5.2. A nagynyomású tengely dinamikája', '45'),
    ('   5.3. FADEC-logika és indítási szekvencia', '47'),
    ('   5.4. Az indítási hibák modellezése és eredményei', '48'),
    ('   5.5. Interaktív pilótafülke-alkalmazás', '51'),
    ('6. EREDMÉNYEK ÉRTÉKELÉSE ÉS KÖVETKEZTETÉSEK', '53'),
    ('   6.1. A szimulációs eredmények validálása', '53'),
    ('   6.2. Tolóerő és tüzelőanyag-fogyasztás összefüggése', '56'),
    ('   6.3. Fejlesztési javaslatok', '58'),
    ('ÖSSZEFOGLALÁS', '61'),
    ('IRODALOMJEGYZÉK', '63'),
    ('HALLGATÓI NYILATKOZAT', '65'),
]

for entry, page in toc_entries:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(18)
    tab_stop = p.paragraph_format.tab_stops
    run = p.add_run(entry)
    set_font(run, bold=('.' not in entry.split()[0] and entry[0].isupper() and '   ' not in entry))
    run2 = p.add_run(f'\t{page}')
    set_font(run2)

# ═══════════════════════════════════════════════════════════════════════════
# BEVEZETÉS
# ═══════════════════════════════════════════════════════════════════════════
heading1('BEVEZETÉS')

body(
    'A modern repülőgép-hajtóművek a mérnöki tudományok egyik legösszetettebb alkotásai, '
    'amelyek a termodinamika, a gázdinamika és az anyagtudomány határterületein működnek. '
    'A kereskedelmi légi közlekedés globális bővülésével egyre nagyobb igény mutatkozik a '
    'hajtóművek hatékonyságának növelésére, tüzelőanyag-fogyasztásának csökkentésére és '
    'a kibocsátási normák teljesítésére.'
)
body(
    'A szakdolgozat tárgya a CFM56-5B kétáramú gázturbinás sugárhajtómű termodinamikai '
    'ciklus-analízise, Python alapú szimulációval. A CFM56-5B az Airbus A320-as '
    'repülőgépcsalád egyik leggyakrabban alkalmazott hajtóműve, amelyből világszerte több '
    'mint 20 000 darabot helyeztek üzembe. Gazdag gyártói dokumentációja és nyilvános '
    'műszaki adatai különösen alkalmassá teszik szimulációs vizsgálatokra.'
)
body(
    'A szimuláció elvégzéséhez a NASA által fejlesztett és nyilvánosan elérhető pyCycle '
    'keretrendszert alkalmaztam, amely CEA-alapú (Chemical Equilibrium with Applications) '
    'termodinamikai számításokat végez az OpenMDAO optimalizálási platformon. Ez a '
    'megközelítés lehetővé teszi, hogy a valóságos gázturbinás ciklus egyenleteit '
    'numerikusan oldjuk meg, figyelembe véve a komponensek hatásfokát és a tényleges '
    'gázösszetételt.'
)
body(
    'A dolgozat célkitűzései a következők: (1) a CFM56-5B tervezési pontjának meghatározása '
    'tengerszinti, statikus felszállási körülmények között; (2) off-design analízis elvégzése '
    'a tervezési ponton rögzített geometriájú hajtóműre három repülési fázisban '
    '(felszállás, emelkedés, utazórepülés); (3) interaktív gázkar-szimulátor fejlesztése, '
    'amely bemutatja a tolóerő és a tüzelőanyag-fogyasztás összefüggését a turbinabemeneti '
    'hőmérséklet függvényében; (4) a termodinamikai ciklus T-s diagramon való ábrázolása '
    'és értékelése; (5) az A320 hajtóműindítási szekvenciájának és négy jellegzetes '
    'indítási hibájának tranziens modellezése a FADEC vezérlési logikájával, '
    'interaktív pilótafülke-alkalmazásban.'
)
body(
    'A szakdolgozat felépítése a követelményeknek megfelelően halad: az elméleti alapok '
    'ismertetése után a szimulációs módszertan, majd a részletes eredmények és azok '
    'értékelése következik. A munka gyakorlati részét a Python-alapú szimulációs kód, '
    'a Jupyter Notebook interaktív elemzések és a vizualizációs eszközök alkotják.'
)

# ═══════════════════════════════════════════════════════════════════════════
# 1. FEJEZET
# ═══════════════════════════════════════════════════════════════════════════
heading1('1. A CFM56-5B HAJTÓMŰ ISMERTETÉSE')

heading2('1.1. Történeti áttekintés')
body(
    'A CFM56 hajtóműcsalád a CFM International vegyesvállalat terméke, amelyet az '
    'amerikai General Electric (GE Aviation) és a francia Safran Aircraft Engines '
    '(korábban SNECMA) alapított 1974-ben. A vegyesvállalat létrehozásának elsődleges '
    'célja egy új, közepes tolóerejű, nagyfokú bypass-arányú gázturbinás sugárhajtómű '
    'fejlesztése volt a polgári repülés számára [1].'
)
body(
    'Az első sorozatgyártású változat, a CFM56-2 1979-ben kapta meg az FAA '
    'típusengedélyét; ezt a DC-8 utasszállító és a KC-135 Stratotanker '
    'újramotorozásához alkalmazták. Az 5-ös sorozat '
    'fejlesztése az 1980-as évek közepén kezdődött az Airbus A320-as programhoz '
    'kapcsolódóan. A CFM56-5A jelölésű alapváltozat 1987-ben állt szolgálatba, '
    'amelyet az A320 sikere nyomán követett a továbbfejlesztett '
    'CFM56-5B változat [2].'
)
body(
    'A CFM56-5B sorozat 1993 óta van forgalomban; az -5A-hoz képest egy negyedik '
    'booster-fokozatot kapott, amely nagyobb magáramot és 32 000 lbf-ig terjedő '
    'tolóerőt tett lehetővé, így az A318, A319, A320 és A321 típusok mindegyikét '
    'hajthatja. A kilenc változat azonos hardverű, a tolóerő-besorolást a FADEC '
    'adatbeviteli dugója határozza meg. A javított teljesítményű /P változatok kb. 3%-kal '
    'kisebb fajlagos tüzelőanyag-fogyasztásúak a korai változatoknál, a 2007-től '
    'gyártott /3 „Tech Insertion” változat pedig áttervezett HPC- és HPT-lapátokkal '
    'tovább csökkenti az SFC-t és a NOx-kibocsátást [2].'
)

heading2('1.2. Műszaki jellemzők és alkalmazások')
body(
    'A CFM56-5B hajtómű kétáramú (turbofan) gázturbinás sugárhajtómű, amelynek '
    'főbb műszaki jellemzői a következők. A típusbizonyítvány szerint a hajtómű '
    'egyfokozatú ventilátorral, négyfokozatú kis nyomású és kilencfokozatú nagy '
    'nyomású kompresszorral, egyfokozatú nagy nyomású és négyfokozatú kis nyomású '
    'turbinával, valamint kétcsatornás FADEC-kel rendelkezik. A felszállási tolóerő '
    'változattól függően 96,1 kN (-5B8) és 142,3 kN (-5B3) között van; a dolgozatban '
    'vizsgált -5B1 változaté 133,45 kN (30 000 lbf), amely az A321-et hajtja [14], [2]. '
    'A bypass-arány (BPR) kb. 5,5, azaz a ventilátoron átáramló levegőből '
    '5,5-szer annyi halad a bypass-csatornán, mint a magáramban [13].'
)

# Table 1
caption_tab('1. táblázat. A CFM56-5B(1) főbb műszaki adatai\nForrás: [14], [2], [13]; saját felvétel')
table = doc.add_table(rows=11, cols=2)
table.style = 'Table Grid'
headers = ['Jellemző', 'Érték']
data = [
    ('Felszállási tolóerő (-5B1)', '133,45 kN (13 345 daN)'),
    ('Fokozatszám', '1 fan + 4 LPC + 9 HPC / 1 HPT + 4 LPT'),
    ('Bypass-arány (BPR)', '≈ 5,5'),
    ('Összesített nyomásviszony (OPR)', '27,0 (saját felvétel)'),
    ('Turbinabemeneti hőmérséklet (T4)', '1700 K (saját becslés)'),
    ('Tömegáram (légbevitel, felszállás)', '368–439 kg/s (változattól függően)'),
    ('EGT-határ: felszállás / indítás (-5B1)', '950 °C / 725 °C'),
    ('Max. fordulatszám N1 / N2', '5200 1/min (104%) / 15 183 1/min (105%)'),
    ('Száraz tömeg (SAC)', '2 454,8 kg'),
    ('Hossz', '2 599,7 mm'),
]
for i, (h, v) in enumerate([(headers[0], headers[1])] + data):
    row = table.rows[i]
    row.cells[0].text = h
    row.cells[1].text = v
    for cell in row.cells:
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                if i == 0:
                    run.font.bold = True

doc.add_paragraph()

body(
    'A hajtómű alkalmazási területei elsősorban a rövidebb és közepes hatótávolságú '
    'útvonalakra tervezett Airbus A320-as repülőgépcsalád tagjai: az A318 (107 utas), '
    'A319 (124 utas), A320 (150 utas) és A321 (180 utas) típusok. Ezek a repülőgépek '
    'a világ leggyakrabban üzemeltetett keskeny törzsű repülőgépei közé tartoznak. '
    '2007-ben a flottában már több mint 2000 -5B/P hajtómű üzemelt [2].'
)
body(
    'Az üzemeltetés szempontjából kulcsfontosságú az EGT-tartalék (EGT margin): '
    'a FADEC a sarokpont-hőmérsékletig (-5B1: 30 °C) tartja a maximális tolóerőt, '
    'efölött a tolóerő csökkentésével állandó EGT-t tart. Az EGT a külső '
    'hőmérséklet 1 °C-os növekedésére kb. 3 °C-kal nő, és a hajtómű kopásával '
    'fokozatosan emelkedik; amikor a tartalék elfogy, a hajtómű műhelyi javításra '
    'szorul [2].'
)

heading2('1.3. Kétáramú sugárhajtómű működési elve')
body(
    'A kétáramú sugárhajtómű (turbofan) a tiszta gázturbinás sugárhajtómű (turbojet) '
    'továbbfejlesztése, amelynek alapelve az, hogy a kompresszorba belépő levegő '
    'egy részét — az ún. bypass-áramot — nem vezeti az égéstérbe, hanem közvetlenül '
    'a magáram körül vezeti el, és a hajtómű hátsó részén bocsátja ki. Ez a megoldás '
    'lényegesen jobb propulziós hatásfokot eredményez szubszonikus sebességtartományban [4].'
)
body(
    'A CFM56-5B kéttengelyes (twin-spool) kialakítású: a kis nyomású (LP) és nagy '
    'nyomású (HP) rendszerek egymástól független tengelyeken forognak, ami rugalmasabb '
    'üzemelést és jobb részteljesítményen mért hatásfokot tesz lehetővé. A levegő '
    'útja a következő főbb komponenseken keresztül vezet: légbevezetők (inlet) → '
    'ventilátor (fan) → kis nyomású kompresszor (LPC) → nagy nyomású kompresszor '
    '(HPC) → égéstér (combustor) → nagy nyomású turbina (HPT) → kis nyomású '
    'turbina (LPT) → fúvócső (nozzle) [4].'
)
body(
    'A ventilátor egyszerre két feladatot lát el: sűríti a magáramot (amely az LPC '
    'felé halad) és felgyorsítja a bypass-áramot, amely közvetlenül tolóerőt termel. '
    'A saját szimulációm szerint a tervezési pontban (statikus felszállás) a bruttó '
    'tolóerő 69%-a (96,1 kN) a bypass-fúvócsőből és 31%-a (42,3 kN) a '
    'mag-fúvócsőből származik (4. fejezet).'
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. FEJEZET
# ═══════════════════════════════════════════════════════════════════════════
heading1('2. TERMODINAMIKAI ALAPOK')

heading2('2.1. A Brayton-ciklus elmélete')
body(
    'A gázturbinás hajtóművek termodinamikai alapja az ún. Brayton-ciklus '
    '(más néven Joule-ciklus), amelyet George Brayton amerikai mérnökről '
    'neveztek el, aki az 1870-es években szabadalmaztatta az első folyamatos '
    'égésen alapuló gépet. A ciklus ideális esetben három fő folyamatból áll: '
    'izentrópikus kompresszió, izobár hőközlés (égés), valamint izentrópikus '
    'expanzió (turbina) [5].'
)
body(
    'A valóságos gázturbinás ciklusban az ideális Brayton-ciklustól való eltérések '
    'a következők miatt lépnek fel: a kompresszorban és turbinában fellépő '
    'irreverzibilis súrlódási veszteségek (alacsonyabb izentrópikus hatásfok), '
    'a nyomásveszteségek az égéstérben és a csövekben, a hőleadás az égéstér '
    'falain keresztül, valamint a hűtőlevegő hatása a turbinalapátokon [6].'
)
body(
    'A termikus hatásfok az ideális Brayton-ciklusban kizárólag a nyomásviszony '
    'függvénye: η_th = 1 – OPR^(–(γ–1)/γ). A CFM56-5B esetében az összesített '
    'nyomásviszony OPR = 27,0, ami γ = 1,4 mellett ideális esetben kb. 61%-os '
    'termikus hatásfoknak felelne meg. A valóságos '
    'hatásfok az említett irreverzibilitások miatt ennél lényegesen kisebb [6].'
)
body(
    'A T-s diagramon (hőmérséklet–specifikus entrópia diagram) a Brayton-ciklus '
    'jellegzetes alakja rajzolódik ki: a kompresszió felfelé haladó görbe '
    '(S2→S3), az égés vízszintes (vagy enyhén jobbra hajló) szakasz (S3→S4), '
    'az expanzió lefelé haladó görbe (S4→S5), majd a hőleadás visszafelé '
    'haladó vonal. A ciklus által bezárt terület arányos a fajlagos munkával [6].'
)

heading2('2.2. Kompresszor és turbina termodinamikája')
body(
    'A kompresszor izentrópikus hatásfoka (η_c) a valóságos és az ideális '
    'kompressziós munka arányaként definiálható. A modellben a ventilátorra '
    'η_fan = 0,89, a kis nyomású kompresszorra η_LPC = 0,89, a nagy nyomású '
    'kompresszorra η_HPC = 0,87 izentropikus hatásfokot vettem fel; ezek a '
    'szakirodalomban tipikus értékek, gyártói adat nem áll rendelkezésre [4], [7].'
)
body(
    'A kompressziós folyamat végén (S3 állomás) a levegő hőmérséklete a '
    'szimulációs eredmények alapján a tervezési pontban 795,8 K, nyomása 2732 kPa. '
    'A nagy nyomású kompresszorban végzett munka jelentős hőmérséklet-emelkedést '
    'okoz: az LPC kimenetétől (S25 = 423,2 K) a HPC kimenetéig (S3 = 795,8 K) '
    'kb. 373 K-es hőmérséklet-növekedés következik be.'
)
body(
    'A turbina izentrópikus hatásfoka (η_t) a valóságos és az ideális expanziós '
    'munka arányaként definiálható. A modellben a nagy nyomású turbinára '
    'η_HPT = 0,89, a kis nyomású turbinára η_LPT = 0,90 értéket vettem fel. A turbinák '
    'jellemzően nagyobb hatásfokúak a kompresszoroknál, mert a gyorsuló (csökkenő '
    'nyomású) áramlásban a határréteg kevésbé hajlamos a leválásra [7].'
)

heading2('2.3. Égéstér és hőmérséklet-szabályozás')
body(
    'Az égéstér (combustion chamber) feladata, hogy a kompresszorból érkező '
    'sűrített levegőt kerosinnel (Jet-A üzemanyaggal) elégesse, és így a gáz '
    'hőmérsékletét a turbinabemeneti hőmérsékletre (T4) emelje. Az égéstér '
    'tüzelőanyag-levegő arányának (FAR – Fuel-to-Air Ratio) szabályozásával '
    'a hajtómű tolóereje folyamatosan változtatható [6].'
)
body(
    'A turbinabemeneti hőmérséklet (T4 vagy TIT – Turbine Inlet Temperature) '
    'a hajtómű legkritikusabb termodinamikai paramétere: minél magasabb, annál '
    'nagyobb a termikus hatásfok és a fajlagos tolóerő. Ugyanakkor a '
    'turbinalapátok hőterhelése is növekszik, ami korlátozza a maximálisan '
    'megengedhető T4 értéket. A CFM56-5B T4 értéke nem publikus; a modellben '
    'felszállásra 1700 K-t becsültem. A hajtómű üzemi hőmérséklet-korlátja a '
    'T49.5 állomáson mért EGT: -5B1 esetén felszálláskor 950 °C, indításkor 725 °C [14].'
)
body(
    'A gázkar (throttle) fizikailag a tüzelőanyag-adagoló szelepet vezérli, '
    'és így szabályozza a FAR értékét, ami közvetlenül meghatározza a T4-et és '
    'ezen keresztül a tolóerőt. A szimulációban a gázkarállást a T4 célértéke '
    'képviseli a T4 = 1000–1700 K tartományban, ahol 1700 K a felszállási '
    '(TOGA – Take-Off/Go-Around) állapot. A T4 = 1000 K alsó határ nem a földi '
    'alapjárat, hanem kis részterhelés: a valódi alapjárat (N1 ≈ 20%) a '
    'rendelkezésre álló kompresszor-jelleggörbék tartományán kívül esik. '
    'Részterhelésen a booster (LPC) munkapontja a pompázs-határ felé tolódik, '
    'ezért a valódi hajtóműben a FADEC által vezérelt változó elvezetésű '
    'szelepek (VBV – Variable Bleed Valve) a booster levegőjének egy részét '
    'elvezetik. Ezen intervallum szimulációs vizsgálatát mutatja be a 4.3. fejezet.'
)

heading2('2.4. Fúvócső és tolóerő-generálás')
body(
    'A tolóerő (thrust) a hajtómű által a kilépő gázáramra alkalmazott impulzus '
    'reakciójaként keletkezik (Newton III. törvénye). A nettó tolóerő a kilépő '
    'és belépő impulzusáramok különbségeként, valamint a fúvócső nyomóerejének '
    'figyelembevételével számítható [4]:'
)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Fn = ṁ_core · V_8 + ṁ_byp · V_18 – (ṁ_core + ṁ_byp) · V_0 + (P_8 – P_0) · A_8 + (P_18 – P_0) · A_18')
set_font(r, italic=True)

body(
    'ahol V_8 és V_18 a mag- és bypass-fúvócsőből kilépő gáz sebessége, V_0 a '
    'repülési sebesség, P_8 és P_18 a fúvócső toroknyomásai, P_0 a szabad '
    'légköri nyomás, A_8 és A_18 a fúvócső torkolatainak keresztmetszetei. '
    'A szimulációban a pyCycle keretrendszer a perf.Fn komponens segítségével '
    'számítja ezt az értéket [8].'
)
body(
    'A fajlagos tüzelőanyag-fogyasztás (SFC – Specific Fuel Consumption) a '
    'tüzelőanyag-fogyasztás és a tolóerő hányadosa: SFC = ṁ_fuel / Fn. '
    'A CFM56-5B esetében a statikus felszállási SFC 9,25–10,02 g/(kN·s), '
    'az utazórepülési SFC pedig kb. 15,4 g/(kN·s) (-5B4 változat) [13]. Az '
    'utazórepülési érték azért nagyobb, mert a repülési sebességgel nő a '
    'belépő impulzusáram (ram drag), így ugyanakkora tüzelőanyag-fogyasztáshoz '
    'kisebb nettó tolóerő tartozik.'
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. FEJEZET
# ═══════════════════════════════════════════════════════════════════════════
heading1('3. A SZIMULÁCIÓ MÓDSZERTANA')

heading2('3.1. NASA pyCycle keretrendszer')
body(
    'A szimulációhoz a NASA Glenn Research Center által fejlesztett pyCycle '
    'keretrendszert alkalmaztam (4.4.0 verzió). A pyCycle egy nyílt forráskódú, '
    'Python alapú gázturbina-ciklus analízis eszköz, amely az OpenMDAO '
    '(Open-source Multidisciplinary Design, Analysis and Optimization) '
    'keretrendszeren épül [9].'
)
body(
    'A pyCycle legfőbb előnye a hagyományos, manuális Brayton-ciklus számításokkal '
    'szemben, hogy CEA-alapú (Chemical Equilibrium with Applications) '
    'termodinamikai adatbázist használ. Ez azt jelenti, hogy a gázok '
    'termodinamikai tulajdonságait (entalpia, entrópia, fajhő) nem konstans '
    'értékként kezeli, hanem a hőmérséklet és nyomás valóságos függvényeként '
    'számítja, figyelembe véve a gázösszetétel változását az égés során [9], [10].'
)
body(
    'Az OpenMDAO keretrendszer implicit egyenletrendszer-megoldó képessége '
    'lehetővé teszi, hogy a hajtómű komponenseinek egymástól függő egyenleteit '
    'iteratív numerikus módszerrel oldja meg. Ez a megközelítés pontosabb '
    'eredményeket ad, mint az egyszerűsített analitikus közelítések, különösen '
    'off-design körülmények között [10].'
)
body(
    'A szimulációs környezet telepítéséhez a következő Python csomagokat '
    'alkalmaztam: om-pycycle 4.4.0, openmdao 3.39, numpy és matplotlib. '
    'A teljes szimulációs kód verziókezelése git rendszerrel történt, és '
    'reprodukálhatóság érdekében a requirements.txt fájlban rögzítettem a '
    'pontos verziókat [INTERNET 1].'
)

heading2('3.2. A szimulációs modell felépítése')
body(
    'A CFM56-5B hajtómű szimulációs modellje az engine/cfm56.py Python modulban '
    'valósul meg. A modell a pyCycle pyc.Cycle osztályából származtatott saját '
    'ciklusosztály (CFM56Cycle), amelynek felépítése a pyCycle nagy bypass-arányú '
    'turbofan mintapéldáját követi [8], és a következő főkomponenseket '
    'tartalmazza: levegőbevezető (inlet), ventilátor (fan), elosztó (splitter), '
    'kis nyomású kompresszor (lpc), VBV-elvezetés (vbv), nagy nyomású '
    'kompresszor (hpc), égéstér (burner), nagy nyomású turbina (hpt), kis '
    'nyomású turbina (lpt), mag- és bypass-fúvócső (core_nozz, byp_nozz), '
    'valamint teljesítményszámító (perf) [INTERNET 1].'
)
body(
    'A tervezési ponthoz tartozó bemeneti paramétereket a CFM56_PARAMS szótár '
    'tartalmazza. A BPR = 5,5 és a 370 kg/s tömegáram nyilvános összesítő adatokon '
    'alapul [13], az OPR = 27,0 és a T4 = 1700 K saját becslés. A komponensenkénti nyomásviszonyok '
    '(PR_fan = 1,685, PR_lpc = 2,0, PR_hpc = 8,0) nem publikusak; ezeket saját '
    'felvétellel úgy választottam meg, hogy szorzatuk az OPR-t adja. Az izentropikus '
    'hatásfokok (0,87–0,90) a szakirodalomban tipikus értékek [4], [7]. Ezek a '
    'mennyiségek a modell bemenetei, ezért velük a modell nem validálható.'
)
body(
    'A tervezési pontban (design mode) a ciklus egyenletrendszerét implicit '
    'egyensúlyi feltételek (OpenMDAO BalanceComp) zárják: (1) a tüzelőanyag-levegő '
    'arány (FAR) addig változik, amíg az égéstér kilépő hőmérséklete el nem éri a '
    'T4 célértéket; (2) a HPT nyomásviszonya addig változik, amíg a HP tengely '
    'nettó teljesítménye nulla (a HPT pontosan meghajtja a HPC-t); (3) az LPT '
    'nyomásviszonya addig változik, amíg az LP tengely nettó teljesítménye nulla '
    '(az LPT meghajtja a ventilátort és az LPC-t). A fúvócsövek a környezeti '
    'statikus nyomásra expandálnak. A tervezési pont a tengerszinti, statikus '
    '(Mach ≈ 0) felszállás, 370 kg/s tömegárammal és T4 = 1700 K-nel.'
)
body(
    'Az off-design számítás (CFM56MultiPoint) a tervezési pontban meghatározott '
    'geometriát – a fúvócsövek torokkeresztmetszetét és a kompresszor- és '
    'turbina-jelleggörbék skálázását – rögzíti. Ekkor a tömegáram, a bypass-arány '
    'és a két tengely fordulatszáma is ismeretlen: a tömegáramot a mag-fúvócső, '
    'a BPR-t a bypass-fúvócső keresztmetszete, a fordulatszámokat a tengelyek '
    'teljesítmény-egyensúlya határozza meg. Így az OPR, a BPR, a tömegáram és az '
    'N1/N2 fordulatszám eredmény, nem bemenet. Az N1 és N2 értékeket a 100%-os '
    'referencia-fordulatszámhoz (5000, illetve 14 460 1/min) viszonyítom; a '
    'típusbizonyítvány szerinti legnagyobb fordulatszám N1 = 5200 1/min (104%) és '
    'N2 = 15 183 1/min (105%) [14]. Ezeket a határokat használom az érvénytelen '
    'munkapontok jelölésére.'
)
body(
    'A Newton-megoldó csak közeli kezdőpontból konvergál megbízhatóan, ezért '
    'minden üzemállapotot kis lépésekben (legfeljebb 2500 ft, 0,05 Mach, 50 K) '
    'közelítek meg az előző konvergált megoldásból (continuation). Minden pont '
    'után ellenőrzöm, hogy a T4 célérték és a tengely-egyensúlyok teljesülnek-e, '
    'illetve hogy a kompresszorok munkapontja a jelleggörbe tartományán belül és '
    'a fordulatszám a megengedett határ alatt van-e; a határon kívüli pontokat '
    'érvénytelennek jelölöm. A részterhelési VBV-elvezetést a T4 függvényében '
    'ütemezem: 1650 K felett zárt, 1000 K-ig lineárisan 30%-ra nyit. A valódi '
    'FADEC a VBV-t a korrigált N2 alapján vezérli; a T4 szerinti ütemezés ennek '
    'egyszerűsítése.'
)
body(
    'A szimuláció végrehajtása az engine/simulation.py modulon keresztül '
    'történik (run_design_point(), OffDesignSolver, run_off_design()). Az '
    'eredményeket az EngineResults adatosztály tartalmazza SI/metrikus '
    'mértékegységekben [INTERNET 1].'
)
body(
    'Az állomásjelölések a következő konvenciót követik: S0 (szabad levegő), '
    'S2 (levegőbevezető kimenet), S21 (ventilátor kimenet), S25 (LPC kimenet), '
    'S3 (HPC kimenet), S4 (égéstér kimenet), S45 (HPT kimenet), S5 (LPT kimenet), '
    'S8 (mag-fúvócső), S18 (bypass-fúvócső). Minden állomásnál a teljes '
    'hőmérséklet (Tt), teljes nyomás (Pt) és fajlagos entalpia (h) értékek '
    'kerülnek rögzítésre.'
)

heading2('3.3. Repülési állapotok és bemeneti paraméterek')
body(
    'A szimulációban három jellegzetes repülési fázist vizsgáltam, amelyek az '
    'Airbus A320-as repülőgép tipikus üzemi körülményeit fedik le. Az ISA '
    '(International Standard Atmosphere) modell alapján meghatározott légköri '
    'paramétereket alkalmazva a hajtómű teljesítménye minden fázisban '
    'reálisan modellezhető.'
)

caption_tab('2. táblázat. A vizsgált repülési fázisok bemeneti paraméterei\nForrás: saját felvétel')
table2 = doc.add_table(rows=5, cols=4)
table2.style = 'Table Grid'
t2_data = [
    ['Repülési fázis', 'Magasság [ft]', 'Magasság [m]', 'Mach-szám'],
    ['Tervezési pont (statikus felszállás)', '0', '0', '≈ 0'],
    ['Felszállás (takeoff)', '0', '0', '0,25'],
    ['Emelkedés (climb)', '15 000', '4 572', '0,50'],
    ['Utazórepülés (cruise)', '35 000', '10 668', '0,78'],
]
for i, row_data in enumerate(t2_data):
    row = table2.rows[i]
    for j, cell_text in enumerate(row_data):
        row.cells[j].text = cell_text
        for para in row.cells[j].paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                if i == 0:
                    run.font.bold = True
doc.add_paragraph()

body(
    'Az utazórepülési magasság (35 000 ft ≈ 10 668 m) esetén az ISA modell '
    'szerinti léghőmérséklet –54,3 °C (218,85 K), a légköri nyomás kb. 23,8 kPa. '
    'Ez a ritka és hideg levegő jelentősen befolyásolja a hajtómű teljesítményét: '
    'a kisebb sűrűség miatt a tömegáram csökken, és a hajtómű alacsonyabb '
    'tolóerőt fejt ki, mint tengerszinten, de a repülőgép kisebb légellenállása miatt '
    'ez elegendő az utazórepülés fenntartásához.'
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. FEJEZET
# ═══════════════════════════════════════════════════════════════════════════
heading1('4. SZIMULÁCIÓS EREDMÉNYEK')

heading2('4.1. Tervezési pont analízis — statikus felszállás')
body(
    'A tervezési pont szimulációja tengerszinti, statikus felszállási körülmények '
    'között (Alt = 0 ft, Mach ≈ 0, T4 = 1700 K, 370 kg/s) a következő főbb '
    'teljesítményparamétereket eredményezte: nettó tolóerő 138,3 kN, fajlagos '
    'tüzelőanyag-fogyasztás SFC = 10,84 g/(kN·s), tüzelőanyag-tömegáram 1,50 kg/s '
    '(FAR = 0,0263). A tengely-egyensúlyból adódó turbina-nyomásviszonyok: '
    'HPT PR = 2,665, LPT PR = 3,745.'
)
body(
    'A teljesítménymérleg az állomás-entalpiákból kézzel is ellenőrizhető. A HP '
    'tengelyen a HPC által felvett teljesítmény ṁ_core·(h3 – h25) = 56,9 kg/s · '
    '392,8 kJ/kg ≈ 22,36 MW, a HPT által leadott (ṁ_core + ṁ_f)·(h4 – h45) ≈ 22,36 MW; '
    'az LP tengelyen a ventilátor és az LPC együttesen 24,13 MW-ot vesz fel, az LPT '
    '24,13 MW-ot ad le. A kompresszió összesített izentropikus hatásfoka az '
    'állomásadatokból η_c = (T3s – T2)/(T3 – T2) ≈ 0,887, összhangban a megadott '
    'komponens-hatásfokokkal.'
)
body(
    'A szimulált statikus tolóerő (138,3 kN) a gyártói 133,4 kN-os statikus '
    'névleges értéknél 3,7%-kal nagyobb. A többlet fő oka, hogy a modell nem '
    'tartalmaz turbinahűtő-levegőt, beépítési és mechanikai veszteségeket: ezek '
    'mindegyike csökkentené a tolóerőt. Fontos, hogy a névleges érték statikus '
    '(Mach 0) adat; Mach 0,25-ön ugyanez a hajtómű csak 113,7 kN nettó tolóerőt ad, '
    'mert a belépő impulzusáram (ram drag) kb. 32,5 kN. A két állapot összevetése '
    'ezért nem lenne helyes.'
)

caption_tab('3. táblázat. Állomásadatok a tervezési pontban (statikus felszállás, T4 = 1700 K)\nForrás: saját szimuláció')
t3_data = [
    ['Állomás', 'Leírás', 'Tt [K]', 'Pt [kPa]', 'h [kJ/kg]'],
    ['S0', 'Szabad levegő', '288,2', '101,3', '–14,4'],
    ['S2', 'Levegőbevezető kimenet', '288,2', '101,3', '–14,4'],
    ['S21', 'Ventilátor kimenet', '340,1', '170,7', '37,9'],
    ['S25', 'LPC kimenet', '423,2', '341,5', '122,0'],
    ['S3', 'HPC kimenet', '795,8', '2731,7', '514,8'],
    ['S4', 'Égéstér kimenet', '1700,0', '2649,8', '501,6'],
    ['S45', 'HPT kimenet', '1404,7', '994,5', '118,8'],
    ['S5', 'LPT kimenet', '1071,3', '265,6', '–294,2'],
    ['S8', 'Mag-fúvócső', '1071,3', '265,6', '–294,2'],
    ['S18', 'Bypass-fúvócső', '340,1', '170,7', '37,9'],
]
table3 = doc.add_table(rows=len(t3_data), cols=5)
table3.style = 'Table Grid'
for i, row_data in enumerate(t3_data):
    row = table3.rows[i]
    for j, cell_text in enumerate(row_data):
        row.cells[j].text = cell_text
        for para in row.cells[j].paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9)
                if i == 0:
                    run.font.bold = True
doc.add_paragraph()

body(
    'Az állomásadatok elemzéséből jól látható a Brayton-ciklus termodinamikai '
    'folyamata. A kompresszió során (S2→S3) a hőmérséklet 288,2 K-ről 795,8 K-re '
    'nő, a nyomás 101,3 kPa-ról 2732 kPa-ra emelkedik (OPR = 26,96). Az égéstérben '
    '(S3→S4) a hőmérséklet 1700 K-re nő, a nyomás a 3%-os égéstéri veszteségnek '
    'megfelelően csökken. A turbinákon (S4→S5) a gáz hőmérséklete 1071 K-re '
    'csökken, miközben pontosan annyi munkát végez, amennyi a kompresszorok '
    'meghajtásához szükséges. Az S2 és S21 közötti entalpia-különbség negatív '
    'előjelű értékei a CEA abszolút entalpia-referenciájából adódnak; a '
    'teljesítménymérleghez csak a különbségek számítanak.'
)

caption_fig('1. ábra. CFM56-5B állomás-diagram a tervezési pontban (saját szimuláció)\nForrás: saját szerkesztés')

heading2('4.2. Off-design analízis — három repülési fázis')
body(
    'Az off-design analízis keretében a hajtómű teljesítményét három repülési '
    'fázisban vizsgáltam: felszállás (0 ft, Mach 0,25), emelkedés (15 000 ft, '
    'Mach 0,50) és utazórepülés (35 000 ft, Mach 0,78). A hajtómű geometriája '
    'minden fázisban a tervezési pontban meghatározott; a tömegáram, a BPR, az OPR '
    'és a fordulatszámok a jelleggörbékből adódnak. Felszállásnál és emelkedésnél '
    'T4 = 1700 K-t alkalmaztam. Utazórepülésnél T4 = 1700 K mellett az N1 107%-ra '
    'nőne és a booster munkapontja a jelleggörbén kívülre kerülne, ezért ott a '
    'legnagyobb érvényes gázkarállást (T4 = 1490 K) tüntetem fel.'
)

caption_tab('4. táblázat. Off-design analízis összefoglaló eredményei\nForrás: saját szimuláció')
t4_data = [
    ['Paraméter', 'Felszállás', 'Emelkedés', 'Utazórepülés'],
    ['Magasság [ft]', '0', '15 000', '35 000'],
    ['Mach-szám [–]', '0,25', '0,50', '0,78'],
    ['T4 [K]', '1700', '1700', '1490'],
    ['Tömegáram [kg/s]', '381,4', '264,9', '139,4'],
    ['Nettó tolóerő [kN]', '113,7', '69,0', '25,5'],
    ['Ram drag [kN]', '32,5', '42,7', '32,3'],
    ['SFC [g/(kN·s)]', '13,44', '16,10', '17,48'],
    ['OPR [–]', '26,42', '29,44', '24,74'],
    ['BPR [–]', '5,55', '5,37', '5,56'],
    ['N1 / N2 [%]', '100,2 / 100,3', '101,8 / 99,0', '91,7 / 91,9'],
    ['Tüzelőanyag [kg/s]', '1,53', '1,11', '0,45'],
]
table4 = doc.add_table(rows=len(t4_data), cols=4)
table4.style = 'Table Grid'
for i, row_data in enumerate(t4_data):
    row = table4.rows[i]
    for j, cell_text in enumerate(row_data):
        row.cells[j].text = cell_text
        for para in row.cells[j].paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                if i == 0:
                    run.font.bold = True
doc.add_paragraph()

body(
    'Az eredmények egyértelműen mutatják, hogy a tolóerő a magassággal és '
    'a Mach-számmal együtt csökken. Nagyobb magasságon a levegő sűrűsége kisebb, '
    'ezért a rögzített geometriájú hajtómű tömegárama felszállásnál 381 kg/s, '
    'emelkedésnél 265 kg/s, utazórepülésnél 139 kg/s. Emellett a repülési '
    'sebességgel a ram drag is nő. Emelkedésnél a hidegebb belépő levegő miatt '
    'a korrigált fordulatszám és az OPR (29,4) nagyobb, mint tengerszinten.'
)
body(
    'A fajlagos tüzelőanyag-fogyasztás (SFC) a repülési sebességgel nő: '
    'felszálláskor 13,44 g/(kN·s), utazórepülésnél 17,48 g/(kN·s). Bár a hidegebb '
    'levegő javítja a termikus hatásfokot, a nagyobb repülési sebesség miatt a '
    'kilépő és belépő sebesség különbsége, így a tömegáramra jutó nettó tolóerő '
    'csökken. Ez megfelel a gyártói adatok trendjének (statikus 9,25–10,02, '
    'utazó 15,4 g/(kN·s) [13]).'
)

caption_fig('2. ábra. T-s diagram a három repülési fázisra (saját szimuláció)\nForrás: saját szerkesztés')

heading2('4.3. Gázkar-szimuláció eredményei')
body(
    'A gázkar (tolóerő-szabályozó) szimulációját a 04_throttle.ipynb Jupyter '
    'Notebook és a Streamlit alkalmazás valósítja meg. A csúszka a gázkar állását '
    '0–100% között változtatja, ahol 0% a T4 = 1000 K részterhelés és 100% a '
    'felszállási T4 = 1700 K: T4 = 1000 + gázkar% × 7 K. Minden gázkarállás '
    'teljes off-design megoldás (5%-os lépésenként előre kiszámítva), a VBV-ütemezéssel '
    'együtt.'
)
body(
    'A gázkar-szimulációból kapott eredmények bemutatják a tolóerő és a '
    'tüzelőanyag-fogyasztás összefüggését a T4 függvényében. Felszállási '
    'körülmények között (Alt = 0 ft, Mach = 0,25) a következő jellegzetes '
    'értékek adódnak:'
)

caption_tab('5. táblázat. Gázkar-szimuláció eredményei felszállásnál\nForrás: saját szimuláció')
t5_data = [
    ['Gázkar [%]', 'T4 [K]', 'Tolóerő [kN]', 'Tüzelőanyag [kg/s]', 'SFC [g/(kN·s)]', 'N1 [%]', 'VBV [%]'],
    ['0*', '1000', '14,9', '0,25', '16,82', '75,7', '30'],
    ['25', '1175', '32,9', '0,44', '13,23', '84,1', '22'],
    ['50', '1350', '57,3', '0,70', '12,29', '90,2', '14'],
    ['75', '1525', '84,8', '1,07', '12,61', '95,2', '6'],
    ['100', '1700', '113,7', '1,53', '13,44', '100,2', '0'],
]
table5 = doc.add_table(rows=len(t5_data), cols=7)
table5.style = 'Table Grid'
for i, row_data in enumerate(t5_data):
    row = table5.rows[i]
    for j, cell_text in enumerate(row_data):
        row.cells[j].text = cell_text
        for para in row.cells[j].paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                if i == 0:
                    run.font.bold = True
body('* A ventilátor munkapontja 0%-nál kissé a jelleggörbe tartományán kívül esik (R-line 2,68 > 2,6).')

body(
    'A gázkar-szimuláció eredményei fontos megfigyelést tesznek lehetővé: '
    'a tolóerő a T4-gyel erősen nemlineárisan nő (14,9 kN-ről 113,7 kN-re), '
    'mert a T4 növelésével a fordulatszám, a tömegáram (197 → 381 kg/s) és az OPR '
    '(7,8 → 26,4) is nő. Az N1 a gázkarral 75,7%-ról 100,2%-ra emelkedik.'
)
body(
    'Az SFC a gázkar függvényében U alakú görbét ír le: minimuma kb. 50%-os '
    'gázkarnál (12,29 g/(kN·s)) van, kis gázon (16,82 g/(kN·s)) és teljes gázon '
    '(13,44 g/(kN·s)) is nagyobb. Kis terhelésen a kis OPR miatt rossz a termikus '
    'hatásfok, és a VBV-n elvezetett levegő sűrítési munkája is elvész; nagy '
    'terhelésen a nagy kiáramlási sebesség rontja a propulziós hatásfokot. Ez '
    'megfelel a gázturbinák ismert részterhelési viselkedésének [7], [11].'
)

caption_fig('3. ábra. Tolóerő és tüzelőanyag-fogyasztás a gázkar függvényében\nForrás: saját szerkesztés')

heading2('4.4. T-s diagram elemzése')
body(
    'A T-s (hőmérséklet–specifikus entrópia) diagram a gázturbinás ciklus '
    'vizuális megjelenítésének egyik legalapvetőbb eszköze. A szimulációból '
    'nyert állomásadatok alapján elkészített T-s diagram bemutatja az összes '
    'vizsgált repülési fázis Brayton-ciklusát egy koordináta-rendszerben.'
)
body(
    'Az entrópia-értékeket az egymást követő állomások között közelítő '
    'formulával számítottam: Δs ≈ cp·ln(T₂/T₁) – R·ln(P₂/P₁), ahol '
    'cp = 1,005 kJ/(kg·K) és R = 0,287 kJ/(kg·K). Ez az összefüggés '
    'kalorikusan tökéletes gázra vonatkozik, ami közelítőleg érvényes a '
    'kompresszor szakaszon, de az égés utáni magas hőmérsékletű tartományban '
    'kevésbé pontos. A pontosabb értékeket a pyCycle CEA-alapú számítása '
    'adja meg [5], [6].'
)
body(
    'A T-s diagramon jól látható a három repülési fázis közötti különbség. '
    'Utazórepülésnél a kb. 219 K statikus hőmérsékletű levegő fékezett '
    'hőmérséklete Mach 0,78-on kb. 245 K, így a kompressziós szakasz a '
    'tengerszintinél (292 K) alacsonyabb hőmérsékletről indul; azonos T4 mellett '
    'tehát nagyobb a ciklus hőmérséklet-'
    'aránya (T4/T2), ami a termikus hatásfokot javítja. Az SFC ennek ellenére '
    'nagyobb utazórepülésnél, mert azt a propulziós hatásfok és a ram drag is '
    'meghatározza (4.2. fejezet).'
)

caption_fig('4. ábra. CFM56-5B T-s diagram három repülési fázisra\nForrás: saját szerkesztés')

# ═══════════════════════════════════════════════════════════════════════════
# 5. FEJEZET — HAJTÓMŰINDÍTÁS
# ═══════════════════════════════════════════════════════════════════════════
heading1('5. HAJTÓMŰINDÍTÁS ÉS INDÍTÁSI HIBÁK TRANZIENS MODELLJE')

heading2('5.1. A modell célja és felépítése')
body(
    'A 3. és 4. fejezet ciklusmodellje stacioner: egy adott üzemállapot '
    'egyensúlyi megoldását adja. A hajtóműindítás ezzel szemben időfüggő folyamat, '
    'amely az alapjárat alatti, a kompresszor-jelleggörbék által nem lefedett '
    'fordulatszám-tartományban zajlik. Ezért az indításhoz külön, redukált rendű '
    'tranziens modellt készítettem, amely tisztán Pythonban, valós időben fut, '
    'és így az interaktív alkalmazásban élőben animálható.'
)
body(
    'A modell három rétegből áll. (1) A „plant” (engine/start_transient.py) a '
    'fizikai folyamatot írja le: a nagynyomású (HP) tengely tehetetlenségi '
    'egyenletét és empirikus EGT-, tüzelőanyag- és N1-összefüggéseket. (2) A FADEC- '
    'és pilótafülke-réteg (engine/fadec.py) a kezelőszervek állásából (ENG MODE, '
    'ENG MASTER, APU BLEED) és a visszacsatolt N2-ből állítja elő a vezérlőparancsokat: '
    'indítószelep, tüzelőanyag, gyújtás. (3) A meghajtó (simulate_start()) '
    'időlépésenként felváltva hívja a FADEC-et és a plant-et, és rögzíti az idősort '
    '(t, N1, N2, EGT, FF, tolóerő, események, hibák). A vezérlő és a szabályozott '
    'szakasz szétválasztása a valódi rendszer felépítését követi, és lehetővé teszi '
    'a hibák injektálását a fizikai rétegben, a detektálásukat pedig a vezérlőben.'
)

heading2('5.2. A nagynyomású tengely dinamikája')
body(
    'Indításkor a pneumatikus indítómotor a segédhajtómű-áttételen keresztül a HP '
    'tengelyt forgatja, ezért a modell állapotváltozója az N2 fordulatszám [%]. '
    'A tengely mozgásegyenlete:'
)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('I · dN2/dt = Q_indító(N2) + Q_turbina(N2) – Q_ellenállás(N2)')
set_font(r, italic=True)
body(
    'ahol az indítómotor nyomatéka Q_indító = Q_0 · k_bleed · (1 – N2/N2_kiold), '
    'amely nyitott indítószelepnél hat és az N2_kiold = 50%-os fordulatszámon '
    'nullára csökken; k_bleed az APU bleed-nyomás rendelkezésre állását skálázza. '
    'A turbina nyomatéka gyújtás (light-off) után Q_turbina = k_t · f_FF(N2), ahol '
    'f_FF a tüzelőanyag-adagolási ütemezés relatív értéke: gyújtáskor 0,35, és '
    'lineárisan nő 1-ig az alapjárati N2 90%-áig. Az ellenállási nyomaték a '
    'kompresszor és a súrlódás hatását összevonva Q_ellenállás = k_d · N2.'
)
body(
    'A paraméterek normalizáltak (I = 10, k_d = 1, Q_0 = 40), nem fizikai '
    'mértékegységűek; értéküket úgy hangoltam, hogy az indítás időbeli lefolyása és '
    'a jellegzetes fordulatszám-pontok valósághűek legyenek. A turbina-erősítést '
    'k_t = k_d · N2_idle választással határoztam meg: ekkor az indítómotor kioldása '
    'után a dN2/dt = 0 egyensúly pontosan N2 = N2_idle = 60%-nál áll be, mert '
    'f_FF = 1 mellett k_t – k_d · N2 = 0. Az időállandó I/k_d = 10 s, ami jóval '
    'nagyobb az explicit Euler-integrálás Δt = 0,5 s lépésközénél, így az integrálás '
    'stabil.'
)
body(
    'Az EGT-t empirikus összefüggés adja: gyújtás előtt a környezeti hőmérséklet '
    '(15 °C), utána egy N2-vel arányosan az alapjárati 450 °C felé növekvő alapszint '
    'és egy gyújtási csúcs összege, amelyet N2 = 25% körüli Gauss-görbe ír le. Az N1 '
    'az N2-t követi: N1 = N1_idle · (N2/N2_idle)^1,5, N1_idle = 19%. Az alapjárati '
    'értékek (N2 ≈ 60%, N1 ≈ 19%, EGT ≈ 450 °C) az A320/CFM56-5B üzemeltetési '
    'adatain alapulnak [15]; az indítási EGT-határ (725 °C) a típusbizonyítványból '
    'származik [14]. Ezek az összefüggések a '
    'jelenségek jellegét adják vissza; pontos számszerű egyezés valódi indítási '
    'felvételek nélkül nem várható el.'
)

heading2('5.3. FADEC-logika és indítási szekvencia')
body(
    'A modell a pilótafülke ENG MODE választókapcsolójának három állását kezeli. '
    'IGN/START állásban, bekapcsolt ENG MASTER és rendelkezésre álló APU bleed '
    'mellett a FADEC automatikus indítást hajt végre: kinyitja az indítószelepet, '
    'majd N2 = 18%-nál tüzelőanyagot ad és bekapcsolja a gyújtást, 50%-nál az '
    'indítószelep zár. NORM állásban a hajtómű nem indul; ez a járó hajtómű '
    'üzemi állása, és indítás közben NORM-ba kapcsolás megszakítja az indítást. '
    'CRANK állásban csak forgatás (dry motoring) történik, tüzelőanyag és gyújtás '
    'nélkül; ez sikertelen indítás után a hajtómű átszellőztetésére szolgál.'
)
body(
    'A valódi A320 automatikus indításánál a gyújtás kb. 16%-os, a HP '
    'tüzelőanyag-szelep nyitása kb. 22%-os N2-nél történik [15]. A modellben ezt '
    'egyetlen, 18%-os light-off ponttá vontam össze, mert a két esemény közötti '
    'rövid időszak a vizsgált hibajelenségeket nem befolyásolja.'
)
body(
    'A normál indítás szimulált eseménysora: STARTER ON (0 s) → IGNITION ON és '
    'LIGHT-OFF (9,0 s, N2 = 18%) → STARTER CUTOUT (31,5 s, N2 = 50%) → IDLE (60,5 s, '
    'N2 = 59,4%, N1 = 18,7%). A gyújtási EGT-csúcs 633 °C (N2 ≈ 26%-nál), ami az '
    '725 °C-os indítási határ alatt marad.'
)

heading2('5.4. Az indítási hibák modellezése és eredményei')
body(
    'Négy indítási hibát modelleztem. Mindegyiknél a fizikai rétegbe egy gyökokot '
    'injektálok, és azt vizsgálom, hogy a modell a jellegzetes tünetet adja-e, '
    'illetve a FADEC felismeri-e. A FADEC a modellben csak detektál és jelez, '
    'automatikusan nem szakítja meg az indítást; a beavatkozás (ENG MASTER OFF, '
    'szükség esetén CRANK-kal átszellőztetés) a személyzet feladata. Ez tervezési '
    'döntés volt, hogy a hibák teljes lefolyása megfigyelhető legyen; a valódi '
    'A320 FADEC földi automatikus indításnál bizonyos hibáknál magától megszakítja '
    'az indítást.'
)

caption_tab('6. táblázat. Indítási hibák: gyökok, tünet és szimulált eredmény\nForrás: saját szimuláció')
t7_data = [
    ['Hiba', 'Injektált gyökok', 'Szimulált tünet', 'FADEC jelzés'],
    ['Hidegfennakadás (hung start)', 'tüzelőanyag-korlát: f_FF ≤ 0,7',
     'N2 45,5%-on megreked, N1 12,5%', 'HUNG START (43,5 s)'],
    ['Melegfennakadás (hot start)', 'tüzelőanyag-többlet: 1,8×',
     'EGT-csúcs 977 °C > 725 °C', 'EGT EXCEEDANCE (10,0 s)'],
    ['Nincs üzemanyag-betáplálás', 'tüzelőanyag-szelep hiba',
     'N2 22,1%, EGT 15 °C, FF = 0', 'NO LIGHT-OFF (18,5 s)'],
    ['Nincs gyújtás (wet start)', 'gyújtóhiba',
     'N2 22,1%, EGT 15 °C, FF = 255 kg/h', 'WET START (18,5 s)'],
]
table7 = doc.add_table(rows=len(t7_data), cols=4)
table7.style = 'Table Grid'
for i, row_data in enumerate(t7_data):
    row = table7.rows[i]
    for j, cell_text in enumerate(row_data):
        row.cells[j].text = cell_text
        for para in row.cells[j].paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9)
                if i == 0:
                    run.font.bold = True
doc.add_paragraph()

body(
    'A megrekedési fordulatszámok a mozgásegyenletből kézzel is levezethetők. '
    'Tüzelőanyag vagy gyújtás hiányában csak az indítómotor forgat: '
    '40 · (1 – N2/50) = N2, amiből N2 = 22,2%. Hidegfennakadásnál az '
    'adagolás 0,7-es korlátja miatt a turbina legfeljebb 60 · 0,7 = 42 egységnyi '
    'nyomatékot ad; mivel az N2 nem éri el az 50%-ot, az indítómotor sem old ki, '
    'így 40 · (1 – N2/50) + 42 = N2, azaz N2 = 45,6%. Mindkét érték egyezik a '
    'szimulációval.'
)
body(
    'A detektálás időzítős logikán alapul. A hung start jelzés akkor aktiválódik, '
    'ha gyújtás után az N2 az alapjárat 95%-a alatt 8 s-on át gyakorlatilag nem '
    'változik. A NO LIGHT-OFF és a WET START jelzés akkor aktiválódik, ha '
    'tüzelőanyag-parancs mellett 10 s-on belül nincs gyújtás; a kettőt a '
    'tüzelőanyag-áram megléte különbözteti meg. Az EGT EXCEEDANCE azonnal jelez, '
    'amint az EGT meghaladja a 725 °C-ot. A nedves indítás veszélye, hogy az '
    'égéstérben felgyűlt tüzelőanyag a következő indítási kísérletnél hirtelen '
    'meggyulladva túlmelegedést okozhat, ezért ilyenkor CRANK üzemű átszellőztetés '
    'szükséges.'
)

heading2('5.5. Interaktív pilótafülke-alkalmazás')
body(
    'A modelleket Streamlit-alapú webes alkalmazásban (app.py) kötöttem össze. '
    'A bal oldalon kattintható A320 ENG panel található (ENG 1 MASTER, ENG MODE '
    'CRANK/NORM/IGN START, APU BLEED) és a hibaforgatókönyv-választó. Az E/WD '
    '(Engine/Warning Display) kijelző valós időben animálja az N1, N2, EGT és FF '
    'értékeket, alatta pedig az események, a FADEC-jelzések és a trenddiagramok '
    'jelennek meg. Stabil alapjárat után a hajtómű a gázkarral a 4.3. fejezet '
    'off-design eredményei felé mozog, tengely-késleltetéssel, folytonos trendként.'
)
body(
    'A két modell kapcsolata korlátozott. Az indítási modell alapjárata '
    '(N1 ≈ 19%) alacsonyabb, mint a ciklusmodell legkisebb érvényes gázkarállása '
    '(T4 = 1000 K, N1 ≈ 76%), mert a földi alapjárat a jelleggörbéken kívül esik. '
    'Az alkalmazásban a kettő közötti átmenet ezért csak szemléltető jellegű. '
    'A modell helyességét a kódhoz tartozó automatikus tesztek (pytest) '
    'ellenőrzik, köztük a négy hiba tüneteit és jelzéseit.'
)

# ═══════════════════════════════════════════════════════════════════════════
# 6. FEJEZET
# ═══════════════════════════════════════════════════════════════════════════
heading1('6. EREDMÉNYEK ÉRTÉKELÉSE ÉS KÖVETKEZTETÉSEK')

heading2('6.1. A szimulációs eredmények validálása')
body(
    'A szimulációs eredmények értékeléséhez az elérhető gyártói és nyilvános '
    'szakirodalmi adatokkal végeztem összehasonlítást. A validálás elsősorban '
    'azokra a mennyiségekre irányult, amelyek a modellben eredményként adódnak '
    '(tolóerő, SFC, fordulatszám). A BPR, az OPR, a T4 és a tervezési tömegáram '
    'a tervezési pont bemenetei, ezért ezek egyezése nem validálás.'
)

caption_tab('7. táblázat. Szimulációs eredmények összehasonlítása irodalmi adatokkal\nForrás: [13]; saját szimuláció')
t6_data = [
    ['Paraméter', 'Irodalmi érték', 'Szimulált érték', 'Eltérés [%]'],
    ['Statikus felszállási tolóerő [kN]', '133,4', '138,3', '+3,7%'],
    ['Statikus felszállási SFC [g/(kN·s)]', '9,25–10,02', '10,84', '+8 … +17%'],
    ['Utazó SFC [g/(kN·s)] (Fn ≈ 22 kN)', '15,4', '17,41', '+13%'],
    ['Tömegáram [kg/s] (bemenet)', '368–439', '370', '–'],
    ['N1 / N2 felszállásnál [%]', '≈ 100', '100,2 / 100,3', '–'],
]
table6 = doc.add_table(rows=len(t6_data), cols=4)
table6.style = 'Table Grid'
for i, row_data in enumerate(t6_data):
    row = table6.rows[i]
    for j, cell_text in enumerate(row_data):
        row.cells[j].text = cell_text
        for para in row.cells[j].paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                if i == 0:
                    run.font.bold = True
doc.add_paragraph()

body(
    'A statikus tolóerő 3,7%-kal nagyobb a gyártói értéknél, az SFC viszont '
    'felszállásnál és utazórepülésnél is 8–17%-kal nagyobb. A két eltérés együtt '
    'arra utal, hogy a modell ciklusa kevésbé hatékony a valódinál. Ennek '
    'legvalószínűbb oka a becsült OPR = 27 és a becsült komponens-hatásfokok: a '
    'nagyobb nyomásviszony a termikus hatásfokot növelné. A hűtőlevegő és a veszteségek elhanyagolása a '
    'tolóerőt ezzel ellentétes irányban, felfelé torzítja. A pontosabb egyezéshez '
    'a komponens-nyomásviszonyok és a hűtőlevegő-arányok együttes kalibrálása '
    'szükséges (6.3. fejezet).'
)
body(
    'A modell belső konzisztenciáját a teljesítménymérleg kézi ellenőrzése '
    '(4.1. fejezet) igazolja. A trendek – a tömegáram és a tolóerő csökkenése a '
    'magassággal, az SFC növekedése a repülési sebességgel, az SFC U alakú '
    'részterhelési görbéje – a fizikai elvárásoknak és a gyártói adatoknak '
    'megfelelnek. Utazórepülésnél T4 ≈ 1500 K felett a modell fordulatszám-túllépést '
    'és jelleggörbén kívüli munkapontot jelez, ami összhangban van azzal, hogy a '
    'valódi hajtóműben a FADEC ott már korlátozza a tolóerőt.'
)

heading2('6.2. Tolóerő és tüzelőanyag-fogyasztás összefüggése')
body(
    'A szimuláció egyik legfontosabb eredménye az, hogy kvantitatívan '
    'megmutatja a tolóerő és a tüzelőanyag-fogyasztás közötti összefüggést '
    'különböző repülési körülmények között. Ez a kapcsolat alapvető fontosságú '
    'a repülési tervezés és az üzemeltetési optimalizálás szempontjából.'
)
body(
    'Az off-design eredmények alapján felszállástól utazórepülésig a '
    'tüzelőanyag-fogyasztás 1,53 kg/s-ről 0,45 kg/s-re csökken, az SFC viszont '
    '13,44-ről 17,48 g/(kN·s)-ra nő. A kisebb abszolút fogyasztás a kisebb '
    'tömegáramból és a kisebb szükséges tolóerőből adódik; a nagy magasságú '
    'utazórepülés gazdaságossága tehát nem a hajtómű kisebb SFC-jéből, hanem a '
    'repülőgép kisebb légellenállásából és nagyobb sebességéből származik.'
)
body(
    'A gázkar-szimuláció eredményei azt mutatják, hogy a T4 = 1000–1700 K '
    'tartományban a hajtómű nemlineárisan viselkedik: az SFC minimuma '
    'részterhelésen, kb. 50%-os gázkarnál van, és kis gázon meredeken nő. '
    'A hajtómű tehát a közepes terhelési tartományban a leggazdaságosabb.'
)
body(
    'Utazórepülésnél a tipikus, kb. 22 kN-os tolóerőigény a gázkar 60%-ának '
    'felel meg (N1 = 89,6%, SFC = 17,41 g/(kN·s)), ami a hajtómű érvényes '
    'működési tartományán belül van.'
)

heading2('6.3. Fejlesztési javaslatok')
body(
    'A szimulációs modell és a vizsgálat eredményei alapján a következő '
    'fejlesztési irányok azonosíthatók a pontosabb és részletesebb elemzés '
    'érdekében.'
)
body(
    'A modell pontosságának növelése érdekében a turbinalapátok hűtőlevegő-rendszerét '
    'célszerű lenne beépíteni. A modern gázturbinákban a kompresszor által kiszívott '
    'levegő 15-20%-a hűtési célokat szolgál. Ennek beépítése a tolóerőt '
    'csökkentené és az SFC-t növelné, ezért csak a komponens-nyomásviszonyok '
    'és hatásfokok egyidejű kalibrálásával javítaná az egyezést. A pyCycle a '
    'kompresszor-elvezetéseket (bleed) és a turbinák hűtőlevegő-bemeneteit '
    'támogatja [8], [9]. Hasonlóan pontosítható a VBV ütemezése, ha a korrigált '
    'N2 függvényében, a FADEC logikájának megfelelően adom meg.'
)
body(
    'A CFM56-5B LEAP-1A utódjának (CFM LEAP-1A) összehasonlító elemzése '
    'további lehetőséget kínál. A LEAP hajtómű OPR-értéke ~40, BPR-értéke '
    '~11, és karbonszálas ventilátor-lapátokat alkalmaz, ami kb. 15%-os '
    'tüzelőanyag-megtakarítást eredményez. A szimulációs keretrendszer '
    'alkalmas lenne erre az összehasonlításra is, és szemléltethetné a '
    'technológiai fejlődés kvantitatív hatásait [12].'
)
body(
    'Az off-design analízis kibővítése egy teljesebb repülési profilra '
    '(gurulás, felszállás, emelkedés több lépcsőben, utazórepülés, '
    'süllyedés, megközelítés, landolás) átfogóbb képet adna a hajtómű '
    'tüzelőanyag-fogyasztásáról egy teljes repülési cikluson át. '
    'Ez a kiterjesztés az ICAO által megkövetelt LTO (Landing and Take-Off) '
    'ciklus emissziós számításaival is összekapcsolható lenne [3].'
)
body(
    'Az indítási modell továbbfejleszthető fizikai mértékegységű paraméterekkel '
    '(tengely-tehetetlenségi nyomaték, indítómotor-jelleggörbe), valódi indítási '
    'felvételekhez való kalibrálással és a FADEC automatikus megszakítási '
    'logikájának beépítésével. Az alapjárati tartomány és a ciklusmodell '
    'összekapcsolásához alacsony fordulatszámra kiterjesztett kompresszor-'
    'jelleggörbék szükségesek.'
)
body(
    'A vizualizációs eszközök továbbfejlesztéseként a 3D forgatható '
    'hajtóműmodell kiegészíthető lenne animált áramlási nyilakkal, amelyek '
    'bemutatják a levegő útját a hajtőmű egyes komponensein keresztül. '
    'Ez oktatási szempontból különösen hasznos lenne, mivel szemléletesebbé '
    'tenné a bypass- és magáram szétválasztását és a turbinák meghajtásának '
    'mechanizmusát.'
)

# ═══════════════════════════════════════════════════════════════════════════
# ÖSSZEFOGLALÁS
# ═══════════════════════════════════════════════════════════════════════════
heading1('ÖSSZEFOGLALÁS')
body(
    'A szakdolgozat a CFM56-5B kétáramú gázturbinás sugárhajtómű termodinamikai '
    'ciklus-analízisét valósította meg Python alapú szimulációval. A vizsgálat '
    'a NASA pyCycle 4.4.0 keretrendszert alkalmazta, amely CEA-alapú '
    'termodinamikai számításokat végez az OpenMDAO optimalizálási platformon.'
)
body(
    'A tengely-egyensúlyokkal zárt tervezési pont statikus felszállásnál 138,3 kN '
    'tolóerőt adott, ami 3,7%-kal nagyobb a gyártói 133,4 kN-nál. A rögzített '
    'geometriájú off-design analízis a tömegáram, a BPR, az OPR és az N1/N2 '
    'változását is eredményként adta: utazórepülésnél a tömegáram kb. 140 kg/s-ra '
    'csökken, az SFC pedig a repülési sebesség miatt nagyobb, mint felszálláskor, '
    'a gyártói adatokkal egyező trenddel.'
)
body(
    'A gázkar-szimulátor bemutatta, hogy T4 = 1000–1700 K között a tolóerő '
    '14,9 kN-ről 113,7 kN-re nő, az SFC minimuma pedig részterhelésen van. '
    'A részterhelési tartomány csak a booster VBV-elvezetésének modellezésével '
    'volt megoldható, ami rámutat e szelepek szerepére a kompresszor pompázs '
    'elleni védelmében.'
)
body(
    'A T-s diagram elemzése szemléletesen megmutatta a Brayton-ciklus '
    'alakulását a különböző repülési fázisokban, és megerősítette az '
    'elméleti termodinamikai összefüggéseket a szimulált numerikus '
    'eredményekkel. A szimulált SFC 8–17%-kal nagyobb a közölt értékeknél, amit '
    'főként a becsült OPR és komponens-hatásfokok magyaráznak.'
)
body(
    'A tranziens indítási modell a HP tengely mozgásegyenletével és a FADEC '
    'vezérlési logikájával visszaadta az A320 automatikus indítási szekvenciáját, '
    'valamint a hidegfennakadás, a melegfennakadás, az üzemanyag-betáplálás hiánya '
    'és a gyújtás hiánya jellegzetes tüneteit; a megrekedési fordulatszámok kézi '
    'levezetése egyezik a szimulációval.'
)
body(
    'A dolgozat eredményei igazolják, hogy a nyílt forráskódú pyCycle '
    'keretrendszer alkalmas a polgári gázturbinás hajtóművek termodinamikai '
    'viselkedésének szimulálására és oktatási célú vizsgálatára. A fejlesztett '
    'Python-alapú szimulációs csomag és a Jupyter Notebook interfész '
    'reprodukálható, bővíthető alapot nyújt további kutatásokhoz.'
)

# ═══════════════════════════════════════════════════════════════════════════
# IRODALOMJEGYZÉK
# ═══════════════════════════════════════════════════════════════════════════
heading1('IRODALOMJEGYZÉK')

references = [
    '[1] CFM INTERNATIONAL (2012): CFM56 Tech Insertion. CFM International technikai kiadványa, Cincinnati, OH.',
    '[2] AIRCRAFT COMMERCE (2007): CFM56-5A/5B series specifications. Owner\'s & Operator\'s Guide: CFM56-5A/-5B. Aircraft Commerce, No. 50 (February/March 2007): 6–9.',
    '[3] ICAO (2017): Aircraft Engine Emissions Databank. International Civil Aviation Organization, Doc 9646.',
    '[4] MATTINGLY, J. D. (2006): Elements of Propulsion: Gas Turbines and Rockets. 2nd ed. AIAA Education Series, Reston, VA.',
    '[5] ÇENGEL, Y. A. – BOLES, M. A. (2019): Thermodynamics: An Engineering Approach. 9th ed. McGraw-Hill, New York.',
    '[6] CUMPSTY, N. A. – HEYES, A. (2015): Jet Propulsion. 3rd ed. Cambridge University Press, Cambridge.',
    '[7] WALSH, P. P. – FLETCHER, P. (2004): Gas Turbine Performance. 2nd ed. Blackwell Science, Oxford.',
    '[8] HENDRICKS, E. S. – GRAY, J. S. (2019): pyCycle: A Tool for Efficient Optimization of Gas Turbine Engine Cycles. Aerospace, 6(8): 87. https://doi.org/10.3390/aerospace6080087',
    '[9] OPENMDAO / NASA GLENN RESEARCH CENTER: pyCycle – Thermodynamic cycle modeling library (forráskód és mintapéldák, 4.4.0). https://github.com/OpenMDAO/pyCycle (letöltés: 2026. szeptember 15.)',
    '[10] GRAY, J. S. et al. (2019): OpenMDAO: An open-source framework for multidisciplinary design, analysis, and optimization. Structural and Multidisciplinary Optimization, 59(4): 1075–1104.',
    '[11] KURZKE, J. – HALLIWELL, I. (2018): Propulsion and Power: An Exploration of Gas Turbine Performance Modeling. Springer, Cham.',
    '[12] CFM INTERNATIONAL (2020): LEAP Engine: Technology and Performance Overview. CFM International, Cincinnati, OH.',
    '[13] WIKIPEDIA: CFM International CFM56 – Specifications (EASA TCDS E.003 és E.066 alapján). https://en.wikipedia.org/wiki/CFM_International_CFM56 (letöltés: 2026. szeptember 15.)',
    '[14] EASA (2023): Type-Certificate Data Sheet No. E.003 for CFM56-5B and CFM56-5C series engines. Issue 06, 9 January 2023. European Union Aviation Safety Agency, Köln.',
    '[15] AIRBUS: A318/A319/A320/A321 Flight Crew Operating Manual (FCOM) – Power Plant: Engine Start; Limitations. Airbus S.A.S., Blagnac. (A felhasznált kiadást és fejezetszámot pontosítani kell.)',
]

doc.add_paragraph()
for ref in references:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(-0.5)
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.line_spacing = Pt(18)
    run = p.add_run(ref)
    set_font(run)

p = doc.add_paragraph()
run = p.add_run('\nINTERNET FORRÁSOK:')
set_font(run, bold=True)

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = Cm(-0.5)
p.paragraph_format.left_indent = Cm(0.5)
run = p.add_run('[INTERNET 1] MOHAMED, Z. (2026): CFM56-5B Thermodynamic Simulation – Python forráskód. '
                'GitHub repository. Letöltés: 2026. május 19.')
set_font(run)

# ═══════════════════════════════════════════════════════════════════════════
# HALLGATÓI NYILATKOZAT
# ═══════════════════════════════════════════════════════════════════════════
heading1('HALLGATÓI NYILATKOZAT')
doc.add_paragraph()
body(
    'Alulírott Mohamed Ziad, a Nyíregyházi Egyetem Műszaki és Agrártudományi '
    'Intézetének repülőmérnöki alapképzési szakos hallgatója kijelentem, hogy '
    'ezt a szakdolgozatot önállóan, konzulensem irányításával készítettem el. '
    'A dolgozatban felhasznált irodalmi forrásokat és adatokat pontosan '
    'megjelöltem, és azokat a tudományos hivatkozás szabályainak megfelelően '
    'idéztem. A dolgozat sem egészében, sem részleteiben nem kerül felhasználásra '
    'más felsőfokú intézménybe benyújtott szakdolgozatban.'
)
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(9)
run = p.add_run('Nyíregyháza, 2026. május')
set_font(run)

doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(9)
run = p.add_run('_________________________')
set_font(run)

p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(9)
run = p.add_run('Mohamed Ziad')
set_font(run)
p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(9)
run = p.add_run('hallgató')
set_font(run)

# ── Save ────────────────────────────────────────────────────────────────────
output_path = '/Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine/CFM56_szakdolgozat.docx'
doc.save(output_path)
print(f'Szakdolgozat elmentve: {output_path}')
