# Yulong Ye — Academic Page

A clean, buildless academic homepage for Yulong Ye. The page is maintained as
plain HTML, CSS, and JavaScript so that personal information and publications
can be updated without a Jekyll build step.

## Local preview

From this directory, run:

```bash
python3 -m http.server 4173
```

Then open <http://127.0.0.1:4173/>.

## Structure

```text
index.html                         # Page layout, styles, and publication data
assets/profile.jpg                 # Profile photo
data/scholar.json                 # Cached Google Scholar metrics
scripts/update_scholar.py         # Monthly Scholar snapshot updater
.github/workflows/update-scholar.yml
                                    # Scheduled monthly metrics update
tests/test_update_scholar.py      # Updater tests
```

The Scholar workflow runs on the first day of each month and can also be
started manually from GitHub Actions.
