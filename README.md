# yugi — ASCII art + system stats

Questo repository mostra un ASCII art scelto casualmente e le statistiche di sistema (stile neofetch). Qui trovi istruzioni chiare per far funzionare lo script su un altro PC. I blocchi di codice qui sotto contengono solo comandi copiabili.

## Requisiti

- Linux (o terminale che supporti sequenze ANSI)
- Python 3.8+ (consigliato 3.10+)
- git

## Struttura principale

- `random_art.py` — script principale
- `ascii/` — cartella con i file ASCII art

## Setup — opzioni

Scegli tra due opzioni: virtualenv (raccomandata) oppure Python di sistema.

Opzione A — virtualenv (consigliata)

```bash
git clone <URL_DEL_REPO> ~/yugi
cd ~/yugi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pyfiglet
python random_art.py
```

Note:

- Per eseguire senza attivare la venv:

```bash
./.venv/bin/python random_art.py
```

Opzione B — Python di sistema

```bash
git clone <URL_DEL_REPO> ~/yugi
cd ~/yugi
python3 -m pip install --user pyfiglet
python3 random_art.py
```

## Esecuzione automatica all'apertura del terminale (una sola volta)

Per eseguire lo script una sola volta, prima del primo prompt, aggiungi in fondo a `~/.bashrc` uno degli snippet seguenti.

Se vuoi usare la venv del progetto:

```bash
if [ -f "$HOME/yugi/random_art.py" ]; then
  _yugi_first_prompt(){
    /home/$USER/yugi/.venv/bin/python "$HOME/yugi/random_art.py"
    unset -f _yugi_first_prompt
    PROMPT_COMMAND=''
  }
  PROMPT_COMMAND=_yugi_first_prompt
fi
```

Se preferisci usare il Python di sistema (assicurati di aver fatto `pip3 install --user pyfiglet`):

```bash
if [ -f "$HOME/yugi/random_art.py" ]; then
  _yugi_first_prompt(){
    python3 "$HOME/yugi/random_art.py"
    unset -f _yugi_first_prompt
    PROMPT_COMMAND=''
  }
  PROMPT_COMMAND=_yugi_first_prompt
fi
```

Dopo la modifica, apri un nuovo terminale o esegui:

```bash
source ~/.bashrc
```

## .venv e __pycache__

- `.venv/` è la virtualenv: ambiente Python isolato per il progetto.
- `__pycache__/` contiene bytecode `.pyc` generati da Python e sono rigenerabili.

Consiglio `.gitignore` minimo:

```text
.venv/
__pycache__/
*.pyc
```

## Risoluzione problemi comuni

- Banner figlet non visibile all'avvio: probabilmente lo script è eseguito con il Python di sistema mentre `pyfiglet` è nella venv. Usa lo snippet che chiama `./.venv/bin/python` oppure installa `pyfiglet` a livello utente:

```bash
pip3 install --user pyfiglet
```

- Vedi frammenti `0m` nell'ASCII: qualche file ascii contiene residui di sequenze di colore; prova a rigenerare o correggere il file ASCII.

- Terminale troppo stretto: lo script adatta il layout e stampa le statistiche sotto l'ASCII.