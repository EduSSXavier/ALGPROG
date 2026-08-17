// Marcação do link ativo ao rolar
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section, div[id]');
    const navLinks = document.querySelectorAll('.sidebar a');
    let current = '';
    sections.forEach(sec => {
    if (scrollY >= sec.offsetTop - 150) current = sec.getAttribute('id');
    });
    navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === `#${current}`) link.classList.add('active');
    });
});

// Exibir/ocultar menu lateral
const btnmenu = document.querySelector('#btn_menu');
btnmenu.addEventListener('click', () =>  {
    const menu = document.querySelector('#menu');
    menu.classList.toggle('visivel');
    if (menu.classList.contains('visivel')) {
        menu.style = 'display: none;';
    } else {
        menu.style = 'display: block;';
    }
});

// Exibir/ocultar respostas dos exercícios
document.querySelectorAll('.toggle_resposta').forEach(btn => {
    btn.addEventListener('click', function() {
        const resposta = this.nextElementSibling;
        const icone = this.querySelector('.material-icons-round');

        resposta.classList.toggle('mostrando');
        
        if (resposta.classList.contains('mostrando')) {
            icone.textContent = 'keyboard_arrow_up';
            this.innerHTML = '<span class="material-icons-round">keyboard_arrow_up</span> Ocultar resposta';
        } else {
            icone.textContent = 'keyboard_arrow_down';
            this.innerHTML = '<span class="material-icons-round">keyboard_arrow_down</span> Mostrar resposta';
        }
    });
});