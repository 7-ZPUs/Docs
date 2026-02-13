import re
import sys
import subprocess
import os
import glob

def calculate_gulpease(text):
    # Rimuove i comandi LaTeX per analizzare solo il testo "pulito"
    # Rimuove il contenuto delle tabelle LaTeX (da \begin{tabular} a \end{tabular})
    clean_text = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', '', text, flags=re.DOTALL)
    clean_text = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'[0-9]*/[0-9]*/[0-9]*','', clean_text) # Rimuove date
    clean_text = re.sub(r'[\[\{\<].*?[\]\}\>]', '', clean_text, flags=re.DOTALL) # Rimuove contenuto tra parentesi quadre, graffe e angolari
    clean_text = re.sub(r'(\\item\s+.*?)([\.])(?=\s*\\item|\s*\\end)',r'\1', clean_text, flags=re.DOTALL) # Rimuove punto a fine item se presente
    clean_text = re.sub(r'(\\item\s+.*?)(?=\s*\\item|\s*\\end)', r'\1.', clean_text, flags=re.DOTALL) # Aggiunge punto a fine item se non presente
    clean_text = re.sub(r'\\[a-zA-Z]+(\{.*?\})?|%.*', '', clean_text) # Rimuove comandi e commenti
    clean_text = re.sub(r'7zpus\.swe@gmail\.com', '', clean_text) # Rimuove email
    #clean_text = re.sub(r'\s+', ' ', clean_text) # Sostituisce spazi multipli con uno singolo
    #clean_text = re.sub(r'\n{2,}', '', clean_text) # Rimuove nuove linee
    #clean_text = re.sub(r'\?{2,}', '', clean_text) # Rimuove sequenze di punti interrogativi
    # Mantiene solo lettere (inclusi accenti), numeri, spazi e punteggiatura base
    clean_text = re.sub(r'[^\w\s\.\,\!\?\'\’]', '', clean_text, flags=re.UNICODE) # Rimuove caratteri speciali
    #print(clean_text)
    
    sentences = len(re.findall(r'[.!?]+', clean_text)) or 1
    words = len(re.findall(r'\w+', clean_text)) or 1
    letters = len(re.findall(r'[a-zA-Z]', clean_text))
    
    # Formula Gulpease
    index = 89 - 10 * (letters / words) + 300 * (sentences / words)
    return index

def check_latex(filepath):
    # Compilazione veloce (draftmode) per verificare la sintassi
    filepath_dir = os.path.dirname(filepath) or '.'
    filepath_name = os.path.basename(filepath)
    
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-draftmode", filepath_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=filepath_dir
    )
    print(result.stdout)
    return result.returncode == 0

def check_spelling(text):
    # Usa aspell con dizionario italiano
    # Se esiste un file 'whitelist.txt', lo usa come dizionario personale
    cmd = ['aspell','-t', '-l', 'it', 'list']
    if os.path.exists('scripts/aspell_whitelist.txt'):
        cmd.append('--personal=./scripts/aspell_whitelist.txt')
        
    process = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    stdout, _ = process.communicate(input=text)
    return set(stdout.split())

def main():
    # Prende i file passati come argomenti (es. da glob nello yaml)
    files = []
    for arg in sys.argv[1:]:
        files.extend(glob.glob(arg, recursive=True))

    if not files:
        print("⚠️ Nessun file .tex trovato per l'analisi.")
        return

    overall_success = True
    parole_errate_totali = set()
    
    for f in files:
        print(f"\n--- Analisi file: {f} ---")
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            print(f"❌ Impossibile leggere il file: {e}")
            overall_success = False
            continue

        # 1. LATEX CHECK
        if check_latex(f):
            print("Compilazione LaTeX: OK")
        else:
            print("❌ ERRORE: Il file LaTeX non compila!")
            overall_success = False

        # 2. GULPEASE CHECK
        score = calculate_gulpease(content)
        print(f"Indice Gulpease: {score:.2f}")
        if score < 60:
            print(f"❌ ERRORE: Leggibilità insufficiente (< 60)")
            overall_success = False
        else:
            print("Leggibilità: OK")

        # 3. SPELLCHECK
        errors = check_spelling(content)
        if errors:
            print(f"❌ ERRORE: Trovati {len(errors)} errori di spelling.")
            parole_errate_totali.update(errors)
            overall_success = False
        else:
            print("Spellcheck: OK")

    if not overall_success:
        print("\nUno o più controlli falliti. Il merge è bloccato.")
        parole_errate = '\n'.join(list(parole_errate_totali))
        print(f"Parole errate totali trovate: \n{parole_errate}\n")
        sys.exit(1)
    else:
        print("\nTutti i controlli passati con successo!")

if __name__ == "__main__":
    main()