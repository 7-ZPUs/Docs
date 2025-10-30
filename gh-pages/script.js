const tabButtons = document.querySelectorAll('#documentation .content-selector');
const tabPanels = document.querySelectorAll('#documentation [role="tabpanel"]');

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

    const firstTab = tabButtons[0];
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

if (pdfLinks.length && pdfViewerWrapper && pdfViewer && pdfTitle && pdfCloseButton) {
    pdfLinks.forEach((link) => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const pdfPath = link.getAttribute('data-pdf');
            const pdfName = link.textContent;
            
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
