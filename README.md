# Battleship

A Battleship game with a Python/FastAPI server, React web frontend, and Kotlin Android app.

Requires Python 3, Node.js/npm, and Android Studio for the Android app.

**1. Start the server** (from the repo root):

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On Windows, activate with `.venv\Scripts\activate` instead.

**2. Start the web app** in another terminal, from the repo root:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Select a player, click enemy tiles to fire, and use Reset for a new game.

**3. Run Android:** Open `android/` in Android Studio, let Gradle sync, and click Run. Keep the server running, enter its address in the app, and tap Load:

- Emulator: `http://10.0.2.2:8000`
- Phone on the same Wi-Fi: `http://<your-computer-IP>:8000`

The Android app currently displays Player A's board.
