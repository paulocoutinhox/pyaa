const BannerManager = {
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (typeof window.PYAA_LANGUAGE !== 'undefined') {
            headers['Accept-Language'] = window.PYAA_LANGUAGE;
        }

        return headers;
    },
    trackViewAccess(token) {
        $.ajax({
            url: '/banner/track-view-access/',
            type: 'POST',
            data: JSON.stringify({
                token: token,
            }),
            headers: this.getHeaders(),
            dataType: 'json'
        });
    },
    trackClickAccess(token, url, external) {
        $.ajax({
            url: '/banner/track-click-access/',
            type: 'POST',
            data: JSON.stringify({
                token: token,
            }),
            headers: this.getHeaders(),
            dataType: 'json',
            success: () => {
                if (url) {
                    if (external) {
                        window.open(url, '_blank');
                    } else {
                        window.location.href = url;
                    }
                }
            },
            error: () => {
                if (url) {
                    if (external) {
                        window.open(url, '_blank');
                    } else {
                        window.location.href = url;
                    }
                }
            }
        });
    }
};
