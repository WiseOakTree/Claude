# Signal-Bot auf einem Server betreiben (24/7)

Anleitung für einen kleinen Linux-VPS (Debian/Ubuntu mit systemd — der Standard
bei günstigen Servern). Ergebnis: Der Bot läuft dauerhaft, startet nach Reboot
oder Absturz automatisch neu, und du bekommst Signale nach Telegram.

> Andere Distribution ohne systemd? Dann `--loop` in `tmux`/`screen` oder per
> Cron (siehe README) starten.

## 1. Einloggen & Grundpakete

```bash
ssh dein-user@dein-server
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
```

## 2. Code holen

Das Repo ist privat — clone es mit deinem GitHub-Zugang (HTTPS-Token oder SSH):

```bash
cd /opt
sudo git clone https://github.com/WiseOakTree/Claude.git prop-bot
sudo chown -R $USER:$USER /opt/prop-bot
cd /opt/prop-bot
```

(Falls der PR noch nicht gemergt ist: `git clone -b claude/crypto-prop-backtester-renko-kdiuz8 ...`)

## 3. Virtuelle Umgebung + Abhängigkeiten

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## 4. Telegram-Daten sicher hinterlegen

Token/Chat-ID kommen **nicht** in eine Datei im Repo, sondern in eine geschützte
Env-Datei:

```bash
sudo tee /etc/prop-signals.env >/dev/null <<'EOF'
TELEGRAM_TOKEN=123456:DEIN_TOKEN
TELEGRAM_CHAT_ID=987654321
EOF
sudo chmod 600 /etc/prop-signals.env
```

Kurzer Testlauf (sollte eine Telegram-Nachricht schicken, falls ein Signal ansteht):

```bash
set -a; source /etc/prop-signals.env; set +a
.venv/bin/python -m prop_backtester.signals --config configs/signals.example.yaml --once
```

## 5. systemd-Service anlegen

```bash
sudo tee /etc/systemd/system/prop-signals.service >/dev/null <<'EOF'
[Unit]
Description=Renko-Reversal Signal-Bot -> Telegram
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/prop-bot
EnvironmentFile=/etc/prop-signals.env
ExecStart=/opt/prop-bot/.venv/bin/python -m prop_backtester.signals \
  --config configs/signals.example.yaml --loop --mode levels \
  --state /opt/prop-bot/signal_state.json
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
```

Passe bei Bedarf `WorkingDirectory`/Pfade an deinen Klon-Ort an.

## 6. Starten & prüfen

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now prop-signals
systemctl status prop-signals --no-pager      # läuft er?
journalctl -u prop-signals -f                 # Live-Logs (Strg+C zum Beenden)
```

Ab jetzt läuft der Bot dauerhaft im Modus **`levels`**: Er schickt dir die
kommenden Trigger-Level mit SL/TP/Size, damit du dort **vorab** Stop-Orders
platzieren kannst. Das ist der einzige Weg, den Backtest-Edge zu erreichen —
Details in [realism.md](realism.md). `signal_state.json` verhindert Doppel-Pings;
gemeldet wird nur, wenn sich die Level ändern.

**Dein Ablauf:** Nachricht kommt → Stop-Order(s) auf die genannten Level legen →
bei Änderungsmeldung Order anpassen. Nicht auf ausgelöste Signale reagieren.

## Anpassen

- **Paare/Einstellungen:** eigene `configs/signals.yaml` anlegen (aus
  `signals.example.yaml`) und im Service statt `signals.example.yaml` eintragen.
  Mehrere Paare: einfach in die `pairs:`-Liste aufnehmen.
- **Update einspielen:**
  ```bash
  cd /opt/prop-bot && git pull && sudo systemctl restart prop-signals
  ```

## Sicherheit

- `/etc/prop-signals.env` mit `chmod 600` schützen (nur root liest den Token).
- Der Bot sendet nur — er hat **keinen** Handelszugriff auf dein Konto. Du
  platzierst die Trades selbst.
