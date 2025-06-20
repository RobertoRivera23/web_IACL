
window.addEventListener('scroll', function() {
    const nav = document.getElementById('mainNav');
    if (window.scrollY > 50) { // Ajusta este valor según necesites
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});

// Detecta scroll y aplica efecto
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    const nav = document.getElementById('mainNav');
    
    if (currentScroll > lastScroll && currentScroll > 100) {
        // Scroll hacia abajo
        nav.style.transform = 'translateY(-100%)';
    } else {
        // Scroll hacia arriba
        nav.style.transform = 'translateY(0)';
    }
    lastScroll = currentScroll;
});