const BannerManager = {
    trackViewAccess(token) {
        $.ajax({
            url: '/banner/track-view-access/',
            type: 'POST',
            data: JSON.stringify({
                token: token,
            }),
            contentType: 'application/json',
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
            contentType: 'application/json',
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
