document.querySelectorAll('.content-selector').forEach( el => {
    el.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.content-selector').forEach( sel => sel.classList.remove('active'));
        el.classList.add('active');
    })
});

document.querySelectorAll('#documentation .content-selector').forEach( el => {
    el.addEventListener('click', (e) => {
        const targetId = el.getAttribute('aria-controls');
        document.querySelectorAll('#documentation article').forEach( a => a.style.display = 'none');
        document.getElementById(targetId).style.display = 'block';
    });
});

document.querySelector('#documentation .content-selector:first-child').click();

document.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 10) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});