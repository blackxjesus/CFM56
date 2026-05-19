# CFM56-5B Termodinamikai Szimuláció

BSc szakdolgozat — Nyíregyházi Egyetem

**Cím:** CFM56-5B repülőgéphajtómű termodinamikai ciklus-analízise Python alapú szimulációval

## Telepítés
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Futtatás
```bash
python scripts/run_design.py
python scripts/run_off_design.py
jupyter notebook notebooks/
```

## Struktúra
- `engine/` — pyCycle wrapper, CFM56 modell
- `visualization/` — 2D/3D diagramok
- `notebooks/` — Jupyter analízis
- `scripts/` — parancssoros futtatás
