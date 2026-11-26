# 重訓課表網站

Strength training exercise library + session schedule — content in
`content/exercises.yaml` and `content/sessions.yaml`, rendered by `build.py`
into a static site and deployed to GitHub Pages.

## 本機建置

```bash
pip install -r requirements.txt
python3 build.py --output-dir public
```
