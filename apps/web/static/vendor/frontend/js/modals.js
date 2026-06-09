// open a dialog identified by the data-modal-open target id
document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-modal-open]");

    if (!trigger) {
        return;
    }

    const modal = document.getElementById(trigger.dataset.modalOpen);

    if (modal && typeof modal.showModal === "function") {
        modal.showModal();
    }
});
