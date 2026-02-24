const tabButtons = document.querySelectorAll('#documentation .content-selector');
const tabPanels = document.querySelectorAll('#documentation [role="tabpanel"]');
const pdfBaseUrls = {
    'verbali-interni-candidatura': 'assets/pdf/Verbali/Verbali%20Interni/',
    'verbali-esterni-candidatura': 'assets/pdf/Verbali/Verbali%20Esterni/',
    candidatura: 'assets/pdf/',
    'verbali-interni-RTB': 'assets/pdf/Verbali/Verbali%20Interni/',
    'verbali-esterni-RTB': 'assets/pdf/Verbali/Verbali%20Esterni/',
    RTB: 'assets/pdf/',
};

if (tabButtons.length && tabPanels.length) {
    tabButtons.forEach((button) => {
        button.setAttribute('aria-selected', 'false');
        button.setAttribute('tabindex', '-1');

        button.addEventListener('click', () => {
            tabButtons.forEach((btn) => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
                btn.setAttribute('tabindex', '-1');
            });

            tabPanels.forEach((panel) => {
                panel.style.display = 'none';
                panel.setAttribute('hidden', 'true');
            });

            const targetId = button.getAttribute('aria-controls');
            const targetPanel = document.getElementById(targetId);

            if (targetPanel) {
                button.classList.add('active');
                button.setAttribute('aria-selected', 'true');
                button.removeAttribute('tabindex');

                targetPanel.style.display = 'block';
                targetPanel.removeAttribute('hidden');
            }
        });
    });

    const firstTab = tabButtons[1];
    if (firstTab) {
        firstTab.click();
    }
}

document.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 10) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

const pdfLinks = document.querySelectorAll('.pdf-link');
const pdfViewerWrapper = document.getElementById('pdf-viewer-wrapper');
const pdfViewer = document.getElementById('pdf-viewer');
const pdfDownloadLink = document.getElementById('pdf-download-link');
const pdfTitle = document.getElementById('pdf-title');
const pdfCloseButton = document.getElementById('pdf-close-button');

const encodePath = (value) =>
    value
        .split('/')
        .map((segment) => encodeURIComponent(segment))
        .join('/');

const resolvePdfUrl = (link) => {
    const baseKey = link.dataset.base;
    const fileName = link.dataset.file;
    const baseUrl = baseKey ? pdfBaseUrls[baseKey] : null;

    if (baseUrl && fileName) {
        return `${baseUrl}${encodePath(fileName)}`;
    }

    const fallbackPdf = link.getAttribute('data-pdf') || link.getAttribute('href');
    return fallbackPdf && fallbackPdf !== '#' ? fallbackPdf : null;
};

const appendNewTabButton = (link, pdfUrl) => {
    if (!pdfUrl) {
        return;
    }

    const newTabButton = document.createElement('button');
    newTabButton.type = 'button';
    newTabButton.className = 'pdf-open-button';
    newTabButton.setAttribute('aria-label', 'Apri il PDF in una nuova scheda');
    newTabButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="pdf-open-button__icon" aria-hidden="true">
            <path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"></path>
            <path d="m21 3-9 9"></path>
            <path d="M15 3h6v6"></path>
        </svg>
        <span class="pdf-open-button__label">Apri in nuova scheda</span>
    `;
    newTabButton.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        window.open(pdfUrl, '_blank', 'noopener,noreferrer');
    });

    const container = link.closest('.pdf-item');
    if (container) {
        container.appendChild(newTabButton);
    } else {
        link.insertAdjacentElement('afterend', newTabButton);
    }
};

pdfLinks.forEach((link) => {
    const pdfUrl = resolvePdfUrl(link);

    if (pdfUrl) {
        link.setAttribute('href', pdfUrl);
        link.setAttribute('data-pdf', pdfUrl);
    }

    appendNewTabButton(link, pdfUrl);
});

if (pdfLinks.length && pdfViewerWrapper && pdfViewer && pdfDownloadLink && pdfTitle && pdfCloseButton) {
    pdfLinks.forEach((link) => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const pdfPath = link.getAttribute('data-pdf');
            const pdfName = link.textContent;

            if (!pdfPath) {
                return;
            }
            
            pdfViewer.setAttribute('data', pdfPath);
            pdfDownloadLink.setAttribute('href', pdfPath);
            pdfTitle.textContent = pdfName;
            
            pdfViewerWrapper.style.display = 'block';
            pdfViewerWrapper.scrollIntoView({ behavior: 'smooth' });
        });
    });

    pdfCloseButton.addEventListener('click', () => {
        pdfViewerWrapper.style.display = 'none';
    });
}
