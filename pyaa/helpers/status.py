class StatusHelper:
    STATUS_COLORS = {
        "initial": {
            "hex": "#007bff",
            "bs": "primary",
            "text": "#ffffff",
        },  # blue with white text
        "analysis": {
            "hex": "#ffc107",
            "bs": "warning",
            "text": "#000000",
        },  # yellow with black text
        "active": {
            "hex": "#28a745",
            "bs": "success",
            "text": "#ffffff",
        },  # green with white text
        "suspended": {
            "hex": "#fd7e14",
            "bs": "orange",
            "text": "#ffffff",
        },  # orange with white text
        "canceled": {
            "hex": "#dc3545",
            "bs": "danger",
            "text": "#ffffff",
        },  # red with white text
        "failed": {
            "hex": "#910000",
            "bs": "danger",
            "text": "#ffffff",
        },  # dark red with white text
        "charged-back": {
            "hex": "#6c757d",
            "bs": "secondary",
            "text": "#ffffff",
        },  # gray with white text
        "rejected": {
            "hex": "#ff0000",
            "bs": "danger",
            "text": "#ffffff",
        },  # red with white text
        "refunded": {
            "hex": "#825690",
            "bs": "purple",
            "text": "#ffffff",
        },  # purple with white text
        "approved": {
            "hex": "#28a745",
            "bs": "success",
            "text": "#ffffff",
        },  # green with white text
        "inactive": {
            "hex": "#6c757d",
            "bs": "secondary",
            "text": "#ffffff",
        },  # gray with white text
        "closed": {
            "hex": "#343a40",
            "bs": "dark",
            "text": "#ffffff",
        },  # dark gray with white text
        "sold": {
            "hex": "#ffc107",
            "bs": "warning",
            "text": "#000000",
        },  # gold with black text
        "unapproved": {
            "hex": "#dc3545",
            "bs": "danger",
            "text": "#ffffff",
        },  # red with white text
        "expired": {
            "hex": "#910000",
            "bs": "danger",
            "text": "#ffffff",
        },  # dark red with white text
    }

    STATUS_PATTERNS = {
        "success": {
            "patterns": ["completed", "succeeded", "paid", "created"],
            "colors": {
                "hex": "#28a745",
                "bs": "success",
                "text": "#ffffff",
            },  # green with white text
        },
        "updated": {
            "patterns": ["updated", "finalized"],
            "colors": {
                "hex": "#ffc107",
                "bs": "warning",
                "text": "#000000",
            },  # yellow with black text
        },
        "info": {
            "patterns": ["attached"],
            "colors": {
                "hex": "#007bff",
                "bs": "primary",
                "text": "#ffffff",
            },  # blue with white text
        },
        "refunded": {
            "patterns": ["refunded"],
            "colors": {
                "hex": "#825690",
                "bs": "purple",
                "text": "#ffffff",
            },  # purple with white text
        },
        "error": {
            "patterns": ["deleted"],
            "colors": {
                "hex": "#dc3545",
                "bs": "danger",
                "text": "#ffffff",
            },  # red with white text
        },
    }

    CREDIT_TYPE_COLORS = {
        "paid": {
            "hex": "#28a745",
            "bs": "success",
            "text": "#ffffff",
        },  # green
        "bonus": {
            "hex": "#ffc107",
            "bs": "warning",
            "text": "#000000",
        },  # yellow
        None: {
            "hex": "#6c757d",
            "bs": "secondary",
            "text": "#ffffff",
        },  # gray
    }

    @staticmethod
    def get_status_color(status: str, style="hex") -> dict:
        if not status:
            status = "unknown"
        else:
            status = status.lower()

        # first check exact matches
        if status in StatusHelper.STATUS_COLORS:
            colors = StatusHelper.STATUS_COLORS[status]
            return {
                "bg": colors[style],
                "text": colors["text"],
            }

        # then check pattern-based matches
        for _, pattern_data in StatusHelper.STATUS_PATTERNS.items():
            for pattern in pattern_data["patterns"]:
                if pattern in status:
                    colors = pattern_data["colors"]
                    return {
                        "bg": colors[style],
                        "text": colors["text"],
                    }

        # default fallback
        return {
            "bg": "#000000" if style == "hex" else "dark",
            "text": "#ffffff",
        }

    @staticmethod
    def get_credit_type_color(credit_type: str, style="hex") -> dict:
        credit_type = credit_type.lower() if credit_type else None

        colors = StatusHelper.CREDIT_TYPE_COLORS.get(
            credit_type, StatusHelper.CREDIT_TYPE_COLORS[None]
        )

        return {
            "bg": colors.get(style, "#6c757d"),
            "text": colors["text"],
        }
