// Funciones JavaScript para la aplicación Parqueadero UAN

// Función para formatear números con separador de miles
function formatCurrency(number) {
    return new Intl.NumberFormat('es-CO', { 
        style: 'currency', 
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(number);
}

// Función para formatear la fecha y hora
function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('es-CO', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para calcular el tiempo transcurrido
function calculateElapsedTime(startTime, currentTime) {
    const start = new Date(startTime);
    const current = new Date(currentTime);
    const diffInMs = current - start;
    const diffInHours = diffInMs / (1000 * 60 * 60);
    
    const hours = Math.floor(diffInHours);
    const minutes = Math.floor((diffInHours - hours) * 60);
    
    return `${hours}h ${minutes}m`;
}

// Función para calcular el monto a pagar
function calculatePayment(startTime, currentTime, ratePerHour) {
    const start = new Date(startTime);
    const current = new Date(currentTime);
    const diffInMs = current - start;
    const diffInHours = diffInMs / (1000 * 60 * 60);
    
    // Redondear hacia arriba para fracciones de hora
    const hoursToCharge = Math.ceil(diffInHours);
    
    return hoursToCharge * ratePerHour;
}

// Inicialización cuando el documento está listo
$(document).ready(function() {
    // Convertir inputs de placa a mayúsculas
    $('input[name="placa"]').on('input', function() {
        $(this).val($(this).val().toUpperCase());
    });
    
    // Inicializar tooltips de Bootstrap
    $('[data-toggle="tooltip"]').tooltip();
    
    // Validar formularios antes de enviar
    $('form').on('submit', function() {
        return validateForm(this);
    });
    
    // Confirmar acciones importantes
    $('.confirm-action').on('click', function(e) {
        if (!confirm('¿Está seguro de realizar esta acción?')) {
            e.preventDefault();
        }
    });
    
    // Auto-dismiss de alertas después de 5 segundos
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
});

// Función para validar formularios
function validateForm(form) {
    let isValid = true;
    
    // Validar campos requeridos
    $(form).find('[required]').each(function() {
        if ($(this).val() === '') {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    // Validación específica para campos numéricos
    $(form).find('input[type="number"]').each(function() {
        const min = $(this).attr('min');
        const max = $(this).attr('max');
        const val = parseFloat($(this).val());
        
        if (min && val < parseFloat(min)) {
            isValid = false;
            $(this).addClass('is-invalid');
        } else if (max && val > parseFloat(max)) {
            isValid = false;
            $(this).addClass('is-invalid');
        }
    });
    
    return isValid;
}
