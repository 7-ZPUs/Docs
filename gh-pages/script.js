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

const verbaliBaseUrls = {
    interni: 'https://cdn.jsdelivr.net/gh/7-zpus/Docs@main/1_Candidatura/Verbali/Verbali%20Interni/',
    esterni: 'https://cdn.jsdelivr.net/gh/7-zpus/Docs@main/1_Candidatura/Verbali/Verbali%20Esterni/',
};

document.querySelectorAll('a[data-base][data-file]').forEach((link) => {
    const baseKey = link.dataset.base;
    const fileName = link.dataset.file;
    const baseUrl = verbaliBaseUrls[baseKey];

    if (!baseUrl || !fileName) {
        return;
    }

    const formattedFileName = fileName
        .split('/')
        .map((segment) => encodeURIComponent(segment))
        .join('/');

    link.href = `${baseUrl}${formattedFileName}`;
});
