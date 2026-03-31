# Haapsalu Koristuste Haldus

## Üles seadmine Render.com-is (15 minutit)

### Samm 1 — Tee konto
1. Mine aadressile: https://render.com
2. Kliki "Get Started for Free"
3. Registreeru Google kontoga (lihtsaim)

### Samm 2 — Lae kood üles
1. Mine aadressile: https://github.com ja tee tasuta konto
2. Kliki "New repository" → nimeta "haapsalu-majutused" → "Create repository"
3. Kliki "uploading an existing file"
4. Lohista kõik failid sellest ZIP-ist sinna → "Commit changes"

### Samm 3 — Ühenda Render + GitHub
1. Render.com-is kliki "New +" → "Web Service"
2. Vali "Connect a repository" → vali "haapsalu-majutused"
3. Seaded:
   - Name: haapsalu-majutused
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
4. Kliki "Create Web Service"

### Samm 4 — Valmis!
- Render ehitab rakenduse (~2 minutit)
- Saad lingi kujul: https://haapsalu-majutused.onrender.com
- Ava telefonis või arvutis — töötab kohe!

## Kuidas see töötab
- Iga tund loeb server automaatselt Booking.com ja Airbnb kalendrid
- Kui keegi välja registreerub, tekib koristusülesanne automaatselt
- Saad määrata koristaja (Lilia või Gertu) ja saata teavituse
- Märkida koristuse lõpetatuks enne järgmise külalise saabumist

## Uute majutuste lisamine
Ava fail `app.py` ja lisa `PROPERTIES` nimekirja uus rida sama formaadiga.

## Küsimused?
Küsi Claudelt — too see vestlus uuesti üles!
