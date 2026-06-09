// server provided configuration read from the document root element
export const language = document.documentElement.lang || "";

export const cookieConsentVersion =
    document.documentElement.dataset.cookieConsentVersion || "1";
