(() => {
    'use strict'

    const STORAGE_KEY = 'cookie-consent'
    const UPDATED_EVENT = 'cookie-consent:updated'

    const ESSENTIAL_CATEGORY = 'essential'
    const ALL_CATEGORIES = ['essential', 'analytics']
    const OPTIONAL_CATEGORIES = ['analytics']

    const version = (window.PYAA_COOKIE_CONSENT_VERSION || '1').toString()

    const readStored = () => {
        try {
            const raw = localStorage.getItem(STORAGE_KEY)
            if (!raw) {
                return null
            }
            const parsed = JSON.parse(raw)
            if (!parsed || parsed.version !== version) {
                return null
            }
            return parsed
        } catch (e) {
            return null
        }
    }

    const writeStored = (categories) => {
        const payload = {
            version: version,
            categories: categories,
            updatedAt: new Date().toISOString(),
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
        return payload
    }

    const normalize = (categories) => {
        const result = { essential: true }
        OPTIONAL_CATEGORIES.forEach((category) => {
            result[category] = Boolean(categories && categories[category])
        })
        return result
    }

    const broadcast = (categories) => {
        const event = new CustomEvent(UPDATED_EVENT, {
            detail: { categories: categories },
        })
        window.dispatchEvent(event)
    }

    const showBanner = () => {
        const banner = document.getElementById('cookie-consent-banner')
        if (banner) {
            banner.classList.remove('hidden')
        }
    }

    const hideBanner = () => {
        const banner = document.getElementById('cookie-consent-banner')
        if (banner) {
            banner.classList.add('hidden')
        }
    }

    const showModal = () => {
        const modal = document.getElementById('cookie-consent-modal')
        if (modal && typeof modal.showModal === 'function') {
            syncModalInputs()
            modal.showModal()
        }
    }

    const closeModal = () => {
        const modal = document.getElementById('cookie-consent-modal')
        if (modal && typeof modal.close === 'function') {
            modal.close()
        }
    }

    const syncModalInputs = () => {
        const current = CookieConsent.getCategories()
        OPTIONAL_CATEGORIES.forEach((category) => {
            const input = document.querySelector(`#cookie-consent-modal [data-category="${category}"]`)
            if (input) {
                input.checked = current[category]
            }
        })
    }

    const collectModalInputs = () => {
        const result = {}
        OPTIONAL_CATEGORIES.forEach((category) => {
            const input = document.querySelector(`#cookie-consent-modal [data-category="${category}"]`)
            result[category] = Boolean(input && input.checked)
        })
        return result
    }

    const persist = (categories) => {
        const normalized = normalize(categories)
        writeStored(normalized)
        broadcast(normalized)
        hideBanner()
        closeModal()
        return normalized
    }

    const CookieConsent = {
        CATEGORIES: ALL_CATEGORIES,
        ESSENTIAL_CATEGORY: ESSENTIAL_CATEGORY,
        UPDATED_EVENT: UPDATED_EVENT,
        hasDecision() {
            return readStored() !== null
        },
        getCategories() {
            const stored = readStored()
            if (!stored) {
                return normalize({})
            }
            return normalize(stored.categories)
        },
        has(category) {
            return this.getCategories()[category] === true
        },
        acceptAll() {
            const result = {}
            OPTIONAL_CATEGORIES.forEach((category) => {
                result[category] = true
            })
            return persist(result)
        },
        rejectAll() {
            const result = {}
            OPTIONAL_CATEGORIES.forEach((category) => {
                result[category] = false
            })
            return persist(result)
        },
        savePreferences() {
            return persist(collectModalInputs())
        },
        openPreferences() {
            showModal()
        },
        closePreferences() {
            closeModal()
        },
    }

    window.CookieConsent = CookieConsent

    window.addEventListener('DOMContentLoaded', () => {
        if (CookieConsent.hasDecision()) {
            broadcast(CookieConsent.getCategories())
        } else {
            showBanner()
        }
    })
})()
