// Mobile Menu Toggle
document.querySelector('.mobile-menu')?.addEventListener('click', ()=>{
    document.querySelector('.nav-links').classList.toggle('active');
});

// Close flash messages
document.querySelectorAll('.close-flash').forEach(button => {
    button.addEventListener('click', (e) => {
        e.target.parentElement.style.display = 'none';
    });
});

// Auto-hide flash message after 5 seconds
setTimeout(() => {
    document.querySelectorAll('.flash-succes, .flash-danger').forEach(e1=> {
        e1.style.display = 'none';
    });
},5000);

// Form validation
document.querySelector('form[action="/pay"]')?.addEventListener('submit',(e)=> {
    const phone = document.getElementById('phone').value;
    if (!phone.match(/^254[17]\d{8}$/)) {
        e.preventDefault();
        alert('Please enter a valid phone number in the format 25')
    }
})