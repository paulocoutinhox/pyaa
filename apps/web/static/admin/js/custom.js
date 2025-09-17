// functions
function removeMasksFromInputs(form) {
    $(form).find(':input[class*="-mask"]').unmask();
}

// ready
(function ($) {
    $(() => {
        // add code after page loaded
    });
})(window.$ || window.jQuery || (window.django && window.django.jQuery));

