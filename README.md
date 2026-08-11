# GI Prediction

A static website that predicts the glycemic index (GI) and glycemic load (GL) of a meal
from free-text food descriptions, tuned for South Asian-American diets.

## Architecture

- Static site only (HTML/CSS/JS), no backend, no accounts, no user data collected or transmitted.
- Hosted free on GitHub Pages.
- Food data as an open JSON/CSV file, loaded client-side.
- The prediction model is trained once, offline, in Python (`model/`). Training produces a
  small set of exported coefficients (`model/saved_model/`) that are re-applied in JavaScript
  in the browser — no live model inference on any server.

## Repo layout

- `data/` — raw and processed food/GI datasets, plus a data dictionary.
- `model/` — offline training and evaluation scripts, and the exported model coefficients.
- `parser/` — Python meal-text parser (ported to `site/app.js` in a later phase).
- `site/` — the static site itself.
- `tests/` — regression test suite, one file per project phase.
- `notebooks/` — exploratory analysis.

## Development setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/
```

## License

Code is licensed under the [MIT License](LICENSE). Data is licensed under
[CC-BY-4.0](LICENSE-DATA).
