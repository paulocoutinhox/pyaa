// clears all descendant fields when a parent field changes
(function ($) {
    $(() => {
        // stores parent and child relation
        const depMap = new Map();

        // tracks observed elements
        const watched = new WeakMap();

        // gets prefix from input name
        function getPrefix(el, parentName) {
            if (typeof el.getFormPrefix === 'function') return el.getFormPrefix();
            const name = el.getAttribute('name') || '';
            return name.endsWith(parentName) ? name.slice(0, -parentName.length) : '';
        }

        // clears a field value
        function clearByFullName(fullName) {
            const el = document.querySelector(`[name="${fullName}"]`);
            if (!el) return;
            if (window.jQuery && window.jQuery.fn && window.jQuery(el).data('select2')) {
                window.jQuery(el).val(null).trigger('change');
            } else {
                el.value = '';
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }

        // clears children recursively
        function clearDescendants(prefix, parentName) {
            const kids = depMap.get(parentName);
            if (!kids) return;
            for (const child of kids) {
                clearByFullName(`${prefix}${child}`);
                clearDescendants(prefix, child);
            }
        }

        // runs when a parent changes
        function onParentChange(el, parentName) {
            const prefix = getPrefix(el, parentName);
            clearDescendants(prefix, parentName);
        }

        // observes changes without events
        function watchElement(el, parentName) {
            if (watched.has(el)) return;
            watched.set(el, el.value);
            const mo = new MutationObserver(() => {
                const last = watched.get(el);
                const cur = el.value;
                if (cur !== last) {
                    watched.set(el, cur);
                    onParentChange(el, parentName);
                }
            });
            mo.observe(el, { attributes: true, childList: true, subtree: true });
        }

        // attaches observer to all parents
        function scanAndBind() {
            for (const parent of depMap.keys()) {
                document
                    .querySelectorAll(`select[name$="${parent}"], input[name$="${parent}"]`)
                    .forEach(el => watchElement(el, parent));
            }
        }

        // listens to native change
        document.addEventListener('change', e => {
            const t = e.target;
            if (!t || !t.name) return;
            for (const parent of depMap.keys()) {
                if (t.name.endsWith(parent)) {
                    onParentChange(t, parent);
                    break;
                }
            }
        }, true);

        // rebinds on new nodes
        const addObs = new MutationObserver(scanAndBind);
        addObs.observe(document.documentElement, { childList: true, subtree: true });

        // registers one parent and one child
        window.bindSelectDependentClear = function (parentName, childName) {
            if (!depMap.has(parentName)) depMap.set(parentName, new Set());
            depMap.get(parentName).add(childName);
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', scanAndBind, { once: true });
            } else {
                scanAndBind();
            }
        };

        // registers a chain of parents and children
        window.bindSelectDependentClear = function (names) {
            for (let i = 0; i < names.length - 1; i++) {
                window.bindSelectDependentClear(names[i], names[i + 1]);
            }
        };
    });
})(window.$ || window.jQuery || (window.django && window.django.jQuery));
