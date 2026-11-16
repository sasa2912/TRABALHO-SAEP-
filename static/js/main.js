
function abrirModalReagendar(id, dataAtual, horaAtual, petNome, tutorNome) {
    const modal = document.getElementById('modalReagendar');
    if (!modal) return;
    
    document.getElementById('modalAgendamentoId').innerText = '#' + id;
    document.getElementById('modalInfoPaciente').innerText = petNome + ' (Tutor: ' + tutorNome + ')';
    document.getElementById('inputNovaData').value = dataAtual;
    document.getElementById('inputNovaHora').value = horaAtual;
    
    const form = document.getElementById('formReagendar');
    form.action = '/agendamentos/' + id + '/atualizar-data';
    
    modal.style.display = 'flex';
}

function fecharModalReagendar() {
    const modal = document.getElementById('modalReagendar');
    if (modal) modal.style.display = 'none';
}

function toggleCpfVisibility(btn, originalMasked, decryptedCpf) {
    const span = btn.previousElementSibling;
    if (span.innerText === originalMasked) {
        span.innerText = decryptedCpf;
        btn.innerText = 'Ocultar';
        btn.classList.add('btn-warning');
        btn.classList.remove('btn-outline');
    } else {
        span.innerText = originalMasked;
        btn.innerText = 'Revelar';
        btn.classList.remove('btn-warning');
        btn.classList.add('btn-outline');
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('modalReagendar');
    if (modal && event.target === modal) {
        modal.style.display = 'none';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const cpfInputs = document.querySelectorAll('.mask-cpf');
    cpfInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            let v = e.target.value.replace(/\D/g, '');
            if (v.length > 11) v = v.slice(0, 11);
            if (v.length > 9) {
                v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
            } else if (v.length > 6) {
                v = v.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
            } else if (v.length > 3) {
                v = v.replace(/(\d{3})(\d{1,3})/, '$1.$2');
            }
            e.target.value = v;
        });
    });
});
