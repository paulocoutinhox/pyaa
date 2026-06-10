const disableSubmit = (form) => {
    const button = form.querySelector('[type="submit"]');

    if (button) {
        button.disabled = true;
        button.innerHTML =
            '<span class="loading loading-spinner loading-sm"></span>';
    }
};

// prevent double submission on forms that opt in via data-prevent-double-submit
document.addEventListener("submit", (event) => {
    const form = event.target;

    if (
        form instanceof HTMLFormElement &&
        form.hasAttribute("data-prevent-double-submit")
    ) {
        disableSubmit(form);
    }
});
