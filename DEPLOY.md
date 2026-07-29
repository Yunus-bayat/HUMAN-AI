# HUMAN-AI Anket — Render ile Yayinlama

## On hazirlik

1. GitHub reposu olusturun ve projeyi push edin.
2. Asagidaki dosyalar repoda olmali:
   - `data/raw_repos/selected_dataset.json`
   - `data/refactored/refactored_dataset.json` (52 kod, 3 LLM)
3. `.env` dosyasini **asla** push etmeyin.

Yerelde veri kontrolu:

```bash
python experiments/check_refactor_status.py
```

## Render adimlari

1. [render.com](https://render.com) → Sign up (GitHub ile)
2. **New +** → **Blueprint** → GitHub reposunu secin
3. `render.yaml` otomatik okunur → **Apply**
4. Deploy bitince URL: `https://human-ai-survey-xxxx.onrender.com`

Manuel kurulum isterseniz:

- **New Web Service** → repo sec
- **Build:** `pip install -r requirements.txt`
- **Start:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Environment:** `FLASK_SECRET_KEY` = rastgele uzun string (Render otomatik uretebilir)

## Paylasilacak linkler

| Sayfa | URL |
|-------|-----|
| Anket | `https://SIZIN-URL/` |
| Sonuclar | `https://SIZIN-URL/stats` |

## Notlar

- **Ucretsiz plan:** ~15 dk kullanilmazsa uyku moduna gecer; ilk tiklamada 30–60 sn acilabilir.
- **Sonuclar** sunucuda `data/results/` altinda tutulur; redeploy sonrasi silinebilir (ucretsiz disk gecici).
- API key gerekmez (anket sadece onceden uretilmis refaktor verisini kullanir).

## Yerelde production testi

```bash
pip install gunicorn
gunicorn wsgi:app --bind 127.0.0.1:5000
```
