///////////////////////////////////////////////////////////////////////////////
// FORM
///////////////////////////////////////////////////////////////////////////////

function preventDoubleFormSubmit(form) {
    var submitButton = form.querySelector('[type="submit"]');

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }
}

///////////////////////////////////////////////////////////////////////////////
// SERVICE WORKER
///////////////////////////////////////////////////////////////////////////////

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js');
    });
}
