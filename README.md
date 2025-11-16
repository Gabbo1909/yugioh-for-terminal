# yugi — ASCII + stats splash

Questo repository mostra un ASCII art scelto casualmente affiancato a statistiche di sistema (stile neofetch). Di seguito le istruzioni per rendere il programma funzionante su un altro PC esattamente come nel tuo.

## Requisiti
- Linux
- Python 3.8+ con `venv` e `pip`
- Terminale che supporti sequenze ANSI (meglio se TrueColor / 24-bit)

## Struttura principale
- `random_art.py` — script principale
- `ascii/` — directory contenente i file ASCII colorati (mantieni i file qui)

## Installazione (consigliata: virtualenv del progetto)
1. Clona il repo:
```bash
git clone <URL_DEL_REPO> yugi
cd yugi

2. Crea e attiva una virtualenv:

python3 -m venv .venv
source .venv/bin/activate

3. Installa la dipendenza opzionale (per il banner figlet):

pip install pyfiglet

4. Rendi eseguibile lo script (opzionale):

chmod +x 



Esecuzione automatica all'apertura del terminale

Per fare in modo che lo script venga eseguito una sola volta, prima del primo prompt, aggiungi questo snippet in fondo a ~/.bashrc (o al file di avvio della tua shell):

Se usi la virtualenv del progetto:
# esegui  una sola volta prima del primo prompt (usa la venv del progetto)
if [ -f "$HOME/yugi/random_art.py" ]; then
  _yugi_first_prompt(){
    /home/$USER/yugi/.venv/bin/python 
    unset -f _yugi_first_prompt
    PROMPT_COMMAND=''
  }
  PROMPT_COMMAND=_yugi_first_prompt
fi

Se non vuoi usare la venv ma hai installato pyfiglet con pip3 --user:

if [ -f "$HOME/yugi/random_art.py" ]; then
  _yugi_first_prompt(){
    python3 "$HOME/yugi/random_art.py"
    unset -f _yugi_first_prompt
    PROMPT_COMMAND=''
  }
  PROMPT_COMMAND=_yugi_first_prompt
fi

Dopo la modifica, apri una nuova finestra del terminale o esegui source ~/.bashrc per testare.