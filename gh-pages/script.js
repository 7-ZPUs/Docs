const tabButtons = document.querySelectorAll(
  "#documentation .content-selector",
);
const tabPanels = document.querySelectorAll('#documentation [role="tabpanel"]');
const pdfBaseUrls = {
  "verbali-interni-candidatura": "assets/1_Candidatura/",
  "verbali-esterni-candidatura": "assets/1_Candidatura/",
  candidatura: "assets/1_Candidatura/",

  "verbali-interni-RTB": "assets/2_RTB/DocumentiInterni/Verbali/",
  "verbali-esterni-RTB": "assets/2_RTB/DocumentiEsterni/Verbali/",
  "documenti-interni-RTB": "assets/2_RTB/DocumentiInterni/",
  "documenti-esterni-RTB": "assets/2_RTB/DocumentiEsterni/",
  "verbali-interni-PB": "assets/3_PB/DocumentiInterni/Verbali/",
  "verbali-esterni-PB": "assets/3_PB/DocumentiEsterni/Verbali/",
  "documenti-interni-PB": "assets/3_PB/DocumentiInterni/",
  "documenti-esterni-PB": "assets/3_PB/DocumentiEsterni/",
};

if (tabButtons.length && tabPanels.length) {
  tabButtons.forEach((button) => {
    button.setAttribute("aria-selected", "false");
    button.setAttribute("tabindex", "-1");

    button.addEventListener("click", () => {
      tabButtons.forEach((btn) => {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
        btn.setAttribute("tabindex", "-1");
      });

      tabPanels.forEach((panel) => {
        panel.style.display = "none";
        panel.setAttribute("hidden", "true");
      });

      const targetId = button.getAttribute("aria-controls");
      const targetPanel = document.getElementById(targetId);

      if (targetPanel) {
        button.classList.add("active");
        button.setAttribute("aria-selected", "true");
        button.removeAttribute("tabindex");

        targetPanel.style.display = "block";
        targetPanel.removeAttribute("hidden");
      }
    });
  });

  const firstTab = tabButtons[0];
  if (firstTab) {
    firstTab.click();
  }
}

document.addEventListener("scroll", () => {
  const header = document.querySelector("header");
  if (window.scrollY > 10) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }
});

const pdfLinks = document.querySelectorAll(".pdf-link");

const encodePath = (value) =>
  value
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");

const resolvePdfUrl = (link) => {
  const baseKey = link.dataset.base;
  const fileName = link.dataset.file;
  const baseUrl = baseKey ? pdfBaseUrls[baseKey] : null;

  if (baseUrl && fileName) {
    return `${baseUrl}${encodePath(fileName)}`;
  }

  const fallbackPdf = link.dataset.pdf || link.getAttribute("href");
  return fallbackPdf && fallbackPdf !== "#" ? fallbackPdf : null;
};

pdfLinks.forEach((link) => {
  const pdfUrl = resolvePdfUrl(link);

  if (pdfUrl) {
    link.setAttribute("href", pdfUrl);
    link.dataset.pdf = pdfUrl;
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");
  }
});
