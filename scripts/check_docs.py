import re
import sys
import subprocess
import os
import glob

def calculate_gulpease(text):
    # 1. ANALISI SOLO DEL CONTENUTO (Ignora il preambolo)
    if "\\begin{document}" in text:
        text = text.split("\\begin{document}")[1]
    if "\\end{document}" in text:
        text = text.split("\\end{document}")[0]

    # 2. RIMOZIONE SEZIONE RIFERIMENTI (Come richiesto)
    text = re.sub(r'\\subsection\{Riferimenti\}.*?(?=\\section|$)', '', text, flags=re.DOTALL)

    # 3. TRATTAMENTO LINK E URL (Prima che vengano "smontati")
    # Estrae il testo visibile dai link ed elimina l'URL
    text = re.sub(r'\\href\{.*?\}\{([\s\S]*?)\}', r'\1', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'7zpus\.swe@gmail\.com', '', text)

    # 4. GESTIONE PUNTI ELENCO E DUE PUNTI (Richiesta specifica)
    # Sostituisce i ":" con "." nella frase che precede un elenco 
    text = re.sub(r':\s*(?=\\begin\{(?:itemize|enumerate)\})', '. ', text)
    
    # Gestione interna agli \item: trasforma i ":" in "." e aggiunge il punto finale
    def clean_items(match):
        item_content = match.group(1)
        # Sostituisce i due punti con punti fermi all'interno del punto elenco
        item_content = item_content.replace(':', '.')
        # Assicura che il punto elenco termini con un punto
        if not item_content.strip().endswith('.'):
            item_content = item_content.strip() + '.'
        return item_content + ' '

    text = re.sub(r'\\item\s+([\s\S]*?)(?=\\item|\\end\{itemize\}|\\end\{enumerate\})', clean_items, text)

    # 5. ESTRAZIONE TITOLI CON PUNTO (Fondamentale per il punteggio)
    # Aggiunge un punto dopo ogni titolo [cite: 66, 74]
    text = re.sub(r'\\(?:section|subsection|subsubsection|subsubsubsection|paragraph|caption)\*?(?:\[.*?\])?\{([\s\S]*?)\}', r'\1. ', text)

    # 6. RIMOZIONE COMMENTI E AMBIENTI NON TESTUALI
    text = re.sub(r'(?<!\\)%.*', '', text)
    for env in ['tabular', 'table', 'figure', 'adjustwidth', 'spacing', 'center', 'tcolorbox', 'longtable']:
        text = re.sub(r'\\begin\{' + env + r'\}.*?\\end\{' + env + r'\}', '', text, flags=re.DOTALL)

    # 7. ESTRAZIONE TESTO DA COMANDI NIDIFICATI (ul, textbf, glossario)
    # Rimuove il comando ma salva il contenuto 
    text = re.sub(r'\\(?:textbf|textit|glossario|ul|ped)\{([\s\S]*?)\}', r'\1', text)

    # 8. RIMOZIONE COMANDI LATEX RESIDUI E PULIZIA CARATTERI
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[.*?\])?(?:\{.*?\})?', ' ', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)

    # Sostituisce trattini e parentesi con spazi per non incollare le parole [cite: 104]
    text = re.sub(r'[\\/()\[\]\-_]', ' ', text)
    text = re.sub(r'[0-9]*/[0-9]*/[0-9]*','', text)
    
    # Mantieni solo lettere, numeri e punteggiatura terminativa
    clean_text = re.sub(r'[^\w\s\.\,\!\?\'\’]', '', text, flags=re.UNICODE)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    print(clean_text)

    # 9. CALCOLO METRICHE
    words_list = re.findall(r'\w+', clean_text)
    words = len(words_list) or 1
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