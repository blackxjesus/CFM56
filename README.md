# CFM56-5B Termodinamikai Szimuláció

BSc szakdolgozat — Nyíregyházi Egyetem

**Cím:** CFM56-5B repülőgéphajtómű termodinamikai ciklus-analízise Python alapú szimulációval

**Élő alkalmazás:** https://cfm56ziad.streamlit.app

A részletes projektdokumentáció a [DOKUMENTACIO.md](DOKUMENTACIO.md), a meghallgatási
felkészítő a [docs/meghallgatas_felkeszules.md](docs/meghallgatas_felkeszules.md) fájlban van.
Közérthető, „konyhanyelvű” leírás a hajtómű és a modell működéséről:
[docs/hajtomu_konyhanyelven.docx](docs/hajtomu_konyhanyelven.docx).

## Telepítés

Python 3.12 ajánlott. A `requirements-sim.txt` a teljes környezet: a verziói rögzítettek, mert a pyCycle 4.4.0 nem fut NumPy 2.3+ alatt. A `requirements.txt` csak az apphoz kell, ezt telepíti a Streamlit Cloud.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-sim.txt
.venv/bin/pip install pytest python-docx   # tesztek és dokumentum-generálás
```

## Futtatás

```bash
.venv/bin/python -m streamlit run app.py        # pilótafülke-alkalmazás
.venv/bin/python -m pytest -q -W ignore         # 103 teszt, kb. 2,5 perc
.venv/bin/python precompute.py                  # data/ újraszámítása
.venv/bin/python scripts/run_design.py          # tervezési pont
.venv/bin/python scripts/run_off_design.py      # off-design
.venv/bin/python scripts/build_hearing_docx.py  # felkészítő .docx a .md-ből
.venv/bin/jupyter notebook notebooks/           # külön telepítendő: pip install jupyter
```

## Struktúra

- `app.py` — Streamlit pilótafülke-alkalmazás
- `engine/` — pyCycle ciklusmodell, off-design megoldó, indítási modell, FADEC
- `visualization/` — E/WD, ENG panel, 2D diagramok, 3D hajtómű-nézet (`engine3d/`: CFM56-5B modell, CloudHubOmniTeam, Sketchfab, CC BY 4.0)
- `data/` — előre kiszámolt eredmények
- `notebooks/` — Jupyter analízis
- `scripts/` — parancssoros futtatás
- `tests/` — pytest-tesztek
- `docs/` — felkészítő, közérthető hajtómű-leírás, tervek és specifikációk
- `generate_thesis.py` — a dolgozat `.docx` generátora
