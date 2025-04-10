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
