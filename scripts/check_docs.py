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
    for env in ['tabular', 'table', 'figure', 'adjustwidth', 'spacing', 'center', 'tcolorbox']:
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
    letters = sum(len(w) for w in words_list)
    
    index = 89 - 10 * (letters / words) + 300 * (sentences / words)
    return index, clean_text

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
    """
    Controlla gli errori ortografici usando due aspell separati:
    1. Aspell italiano con whitelist personale
    2. Aspell inglese per le parole non italiane
    Restituisce una lista di tuple (parola, riga, contesto) per ogni errore
    """
    try:
        if not text.strip():
            return []
        
        # Run aspell Italian with whitelist
        p_it = subprocess.Popen(
            ["aspell", "list", "--lang=it", "--encoding=utf-8", "--personal=./scripts/aspell_whitelist.pws"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out_it, _ = p_it.communicate(input=text.encode('utf-8'))
        errors_it = set(w.strip() for w in out_it.decode('utf-8').splitlines() if w.strip())
        
        # Run aspell English
        p_en = subprocess.Popen(
            ["aspell", "list", "--lang=en", "--encoding=utf-8"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out_en, _ = p_en.communicate(input=text.encode('utf-8'))
        errors_en = set(w.strip() for w in out_en.decode('utf-8').splitlines() if w.strip())
        
        # Only words not recognized in EITHER language are errors (intersection)
        error_words = errors_it & errors_en
        
        if not error_words:
            print(f"Parole non riconosciute: 0")
            return []
        
        # Find line and context for each error
        lines = text.split('\n')
        error_details = []
        
        for word in error_words:
            # Case-insensitive search
            word_pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                if word_pattern.search(line):
                    # Extract context (up to 60 chars around the word)
                    match = word_pattern.search(line)
                    start = max(0, match.start() - 30)
                    end = min(len(line), match.end() + 30)
                    context = line[start:end].strip()
                    if start > 0:
                        context = '...' + context
                    if end < len(line):
                        context = context + '...'
                    error_details.append((word, line_num, context))
                    break  # Only report first occurrence
        
        print(f"Parole non riconosciute: {len(error_details)}")
        return error_details
    except Exception as e:
        print(f"⚠️ Errore durante lo spellcheck: {e}")
        return []

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
        score, clean_text = calculate_gulpease(content)
        print(f"Indice Gulpease: {score:.2f}")
        if score < 60:
            print(f"❌ ERRORE: Leggibilità insufficiente (< 60)")
            overall_success = False
        else:
            print("Leggibilità: OK")

        # 3. SPELLCHECK
        errors = check_spelling(clean_text)
        if errors:
            for word, line_num, context in errors:
                print(f"  Riga {line_num}: '{word}' in \"{context}\"")
                parole_errate_totali.add(word)
            overall_success = False
        else:
            print("Spellcheck: OK")

    if not overall_success:
        print("\n" + "="*60)
        print("❌ UNO O PIÙ CONTROLLI FALLITI - IL MERGE È BLOCCATO")
        print("="*60)
        if parole_errate_totali:
            print(f"\nRiepilogo parole errate ({len(parole_errate_totali)}):")
            for word in sorted(parole_errate_totali):
                print(f"  • {word}")
        print()
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("✓ TUTTI I CONTROLLI PASSATI CON SUCCESSO!")
        print("="*60)

if __name__ == "__main__":
    main()