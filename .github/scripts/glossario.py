import re
import json
from pathlib import Path

def extract_glossary_from_latex(latex_content):
    """Estrae termini e definizioni dal file LaTeX del glossario"""
    
    glossary = {}
    
    # Pattern per identificare le sezioni (lettere)
    # Cerca \section{A}, \section{B}, ecc.
    section_pattern = r'\\section\{([A-Z])\}'
    
    # Pattern per gli item: \item \textbf{Termine}: Definizione
    # Supporta anche definizioni su più righe
    item_pattern = r'\\item\s+\\textbf\{([^}]+)\}:\s*(.+?)(?=\\item|\\end\{itemize\}|\\section|$)'
    
    # Trova tutte le sezioni
    sections = list(re.finditer(section_pattern, latex_content))
    
    for i, section_match in enumerate(sections):
        letter = section_match.group(1)
        section_start = section_match.end()
        
        # Determina la fine della sezione corrente
        if i < len(sections) - 1:
            section_end = sections[i+1].start()
        else:
            # Ultima sezione, cerca fine documento
            section_end = latex_content.find(r'\end{document}', section_start)
            if section_end == -1:
                section_end = len(latex_content)
        
        section_content = latex_content[section_start:section_end]
        
        # Trova tutti gli item nella sezione corrente
        items = re.finditer(item_pattern, section_content, re.DOTALL)
        
        terms_in_section = []
        for item_match in items:
            term = item_match.group(1).strip()
            definition = item_match.group(2).strip()
            
            # Pulisci la definizione
            definition = clean_latex_text(definition)
            term = clean_latex_text(term)
            
            terms_in_section.append({
                'term': term,
                'definition': definition
            })
        
        if terms_in_section:
            # Ordina i termini alfabeticamente all'interno della sezione
            terms_in_section.sort(key=lambda x: x['term'].lower())
            glossary[letter] = terms_in_section
    
    return glossary

def clean_latex_text(text):
    """Rimuove comandi LaTeX e pulisce il testo"""
    
    # Rimuovi \textbf, \textit mantenendo il contenuto
    text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
    
    # Rimuovi link o riferimenti
    text = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\1', text)
    
    # Rimuovi $ per formule matematiche inline
    text = text.replace('$', '')
    
    # Rimuovi backslash residui e graffe singole se non accoppiate
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Pulisci spazi multipli e newline trasformandoli in spazi singoli
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Gestisci caratteri speciali comuni (se non gestiti dall'encoding)
    replacements = {
        '``': '"',
        "''": '"',
        '`': "'",
        '--': '–',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def generate_html(glossary):
    """Genera HTML interattivo compatibile con style.css"""
    
    # Struttura HTML che rispecchia il layout del sito
    html_template = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Glossario di Progetto - 7-ZPUs</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="site-header">
        <div class="header-inner">
            <a href="https://7-zpus.github.io/Docs/" class="logo">
                <img src="assets/imgs/logo-transp-rev.png" alt="Logo ZPUs Engineering Team">
                <!-- <span class="logo-text">7-ZPUs Engineering Team</span> -->
            </a>
            <nav class="site-nav">
                <a href="https://github.com/7-ZPUs">REPOSITORY</a>
                <a href="https://7-zpus.github.io/Docs/#documentation">DOCUMENTAZIONE</a>
                <a href="../gh-pages/glossario.html">GLOSSARIO</a>
                <a href="https://7-zpus.github.io/Docs/#team">TEAM</a>
            </nav>
        </div>
    </header>

    <main>
            <section id="hero" class="hero">
            <div class="hero-content">
                <h1>7-ZPUs Engineering Team</h1>
                <p class="subtitle">SWE Project 2025/2026</p>
                <div class="hero-actions">
                    <a class="button primary" href="https://github.com/7-ZPUs" target="_blank">GitHub — ZPUs Engineering</a>
                    <a class="button ghost" href="#documentation">DOCUMENTAZIONE</a>
                </div>
            </div>
        </section>
        <div class="section-heading">
            <h1>Glossario</h1>
            <p class="subtitle">Terminologia tecnica e definizioni del progetto</p>
        </div>

        <div class="glossary-container">
            
            <div class="glossary-search">
                <input type="text" id="searchInput" class="glossary-search-input" placeholder="Cerca un termine o una definizione...">
            </div>
            
            <nav class="glossary-alphabet-nav" id="alphabetNav">
                </nav>
            
            <div class="glossary-content" id="glossaryContent">
                </div>
        </div>
    </main>

    <footer>
        <p>&copy; 2024 Gruppo 7-ZPUs. Università degli Studi di Padova.</p>
        <p style="opacity: 0.6; font-size: 0.85rem; margin-top: 0.5rem;">Generato automaticamente da LaTeX</p>
    </footer>

    <script>
        // Dati iniettati da Python
        const glossaryData = GLOSSARY_JSON_PLACEHOLDER;
        
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

        // 1. Genera Navigazione Alfabetica
        function generateAlphabetNav() {
            const nav = document.getElementById('alphabetNav');
            nav.innerHTML = ''; // Reset
            
            // Link per "Mostra tutti" (opzionale, qui mettiamo solo lettere)
            
            alphabet.forEach(letter => {
                const link = document.createElement('a');
                link.className = 'glossary-letter-link';
                link.textContent = letter;
                
                // Se la lettera non esiste nei dati, disabilitala
                if (!glossaryData[letter] || glossaryData[letter].length === 0) {
                    link.classList.add('disabled');
                } else {
                    link.href = '#section-' + letter;
                    link.onclick = (e) => {
                        e.preventDefault();
                        scrollToSection(letter);
                    };
                }
                
                nav.appendChild(link);
            });
        }
        
        // 2. Genera Contenuto Glossario
        function generateGlossaryContent(searchTerm = '') {
            const content = document.getElementById('glossaryContent');
            content.innerHTML = '';
            
            let hasResults = false;
            const termLower = searchTerm.toLowerCase();
            
            // Ordina le chiavi (lettere) presenti
            const sortedKeys = Object.keys(glossaryData).sort();
            
            sortedKeys.forEach(letter => {
                const terms = glossaryData[letter];
                
                // Filtra i termini se c'è una ricerca
                const filteredTerms = terms.filter(item => {
                    if (!searchTerm) return true;
                    return item.term.toLowerCase().includes(termLower) || 
                           item.definition.toLowerCase().includes(termLower);
                });
                
                if (filteredTerms.length > 0) {
                    hasResults = true;
                    
                    // Creazione Sezione
                    const section = document.createElement('div');
                    section.className = 'glossary-section';
                    section.id = 'section-' + letter;
                    
                    // Titolo Sezione
                    const title = document.createElement('h2');
                    title.className = 'glossary-section-title';
                    title.textContent = letter;
                    section.appendChild(title);
                    
                    // Wrapper delle Card
                    const termsWrapper = document.createElement('div');
                    termsWrapper.className = 'glossary-terms';
                    
                    filteredTerms.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'glossary-term-card';
                        
                        const nameEl = document.createElement('h3');
                        nameEl.className = 'glossary-term-name';
                        nameEl.innerHTML = highlightText(item.term, searchTerm);
                        
                        const defEl = document.createElement('p');
                        defEl.className = 'glossary-term-definition';
                        defEl.innerHTML = highlightText(item.definition, searchTerm);
                        
                        card.appendChild(nameEl);
                        card.appendChild(defEl);
                        termsWrapper.appendChild(card);
                    });
                    
                    section.appendChild(termsWrapper);
                    content.appendChild(section);
                }
            });
            
            // Messaggio Nessun Risultato
            if (!hasResults) {
                content.innerHTML = `
                    <div class="glossary-no-results">
                        <div class="glossary-no-results-icon">🔍</div>
                        <h3>Nessun risultato trovato</h3>
                        <p>Non abbiamo trovato termini corrispondenti a "<strong>${searchTerm}</strong>"</p>
                    </div>
                `;
            }
            
            // Aggiorna stato attivo nella navigazione
            updateActiveNav();
        }
        
        // Helper: Scroll fluido
        function scrollToSection(letter) {
            const el = document.getElementById('section-' + letter);
            if (el) {
                // Offset per l'header sticky
                const headerOffset = 100;
                const elementPosition = el.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
                
                // Aggiorna visivamente la lettera attiva
                document.querySelectorAll('.glossary-letter-link').forEach(l => l.classList.remove('active'));
                const activeLink = Array.from(document.querySelectorAll('.glossary-letter-link')).find(l => l.textContent === letter);
                if(activeLink) activeLink.classList.add('active');
            }
        }
        
        // Helper: Evidenzia testo cercato
        function highlightText(text, searchTerm) {
            if (!searchTerm) return text;
            // Escape special chars for regex
            const safeTerm = searchTerm.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
            const regex = new RegExp(`(${safeTerm})`, 'gi');
            return text.replace(regex, '<span class="glossary-highlight">$1</span>');
        }
        
        function updateActiveNav() {
             // Semplice logica per rimuovere active se stiamo filtrando
             const searchInput = document.getElementById('searchInput');
             if(searchInput.value.length > 0) {
                 document.querySelectorAll('.glossary-letter-link').forEach(l => l.classList.remove('active'));
             }
        }

        // Event Listeners
        document.getElementById('searchInput').addEventListener('input', (e) => {
            generateGlossaryContent(e.target.value.trim());
        });

        // Init
        generateAlphabetNav();
        generateGlossaryContent();
        
    </script>
</body>
</html>'''

    # Inserisci i dati JSON nel template
    json_data = json.dumps(glossary, ensure_ascii=False)
    final_html = html_template.replace('GLOSSARY_JSON_PLACEHOLDER', json_data)
    
    return final_html

def main():
    # Percorso del file LaTeX di input
    latex_file = Path('../../2_RTB/Glossario.tex')
    
    if not latex_file.exists():
        # Fallback per test o se il file non è nella stessa cartella
        print(f"⚠️  File {latex_file} non trovato. Cerco in sottocartelle comuni...")
        # Esempio: cerca in src/ o docs/ se necessario
        return

    print(f"📖 Lettura di {latex_file}...")
    try:
        latex_content = latex_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Errore nella lettura del file: {e}")
        return

    print("🔍 Estrazione termini...")
    glossary = extract_glossary_from_latex(latex_content)
    
    total_terms = sum(len(terms) for terms in glossary.values())
    print(f"✅ Trovati {total_terms} termini in {len(glossary)} sezioni (lettere).")
    
    print("🎨 Generazione HTML con stile...")
    html_content = generate_html(glossary)
    
    output_file = Path('../../gh-pages/glossario.html')
    output_file.write_text(html_content, encoding='utf-8')
    
    print(f"✨ Successo! File generato: {output_file.absolute()}")
    print("   Assicurati che 'style.css' sia nella stessa cartella del file HTML.")

if __name__ == '__main__':
    main()