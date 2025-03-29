from apps.shop.enums import PlanFrequencyType
from apps.shop.models import Plan


def populate_plans():
    plans_data = [
        {
            "id": 1,
            "site_id": None,
            "name": "Subscription Plan",
            "tag": "subscription",
            "plan_type": "subscription",
            "gateway": "stripe",
            "external_id": "price_1Q0vLpEUm7G1T8P4H0t5s8RE",
            "currency": "USD",
            "price": 5,
            "credits": 30,
            "frequency_type": PlanFrequencyType.MONTH,
            "frequency_amount": 1,
            "sort_order": 1,
            "featured": False,
            "expire_at": None,
            "expire_after": 30 * 24 * 60 * 60,
            "bonus": 0.0,
            "bonus_expire_after": None,
            "active": True,
            "image": None,
            "description": """<ul class="list-group list-group-flush mb-4">
<li class="list-group-item"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">
                    <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"></path>
                  </svg>&nbsp;<b>Item 1</b></li>
<li class="list-group-item"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">
                    <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"></path>
                  </svg>&nbsp;<b>Item 2</b></li>
<li class="list-group-item"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">
                    <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"></path>
                  </svg>&nbsp;<b>Item 3</b></li>
<li class="list-group-item"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-x text-danger" viewBox="0 0 16 16">
                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"></path>
                  </svg>&nbsp;Item 4</li>
<li class="list-group-item"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-x text-danger" viewBox="0 0 16 16">
                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"></path>
                  </svg>&nbsp;Item 5</li>
<li class="list-group-item"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-x text-danger" viewBox="0 0 16 16">
                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"></path>
                  </svg>&nbsp;Item 6</li></ul>""",
        },
    ]

    for plan_data in plans_data:
        Plan.objects.update_or_create(
            id=plan_data["id"],
            defaults={key: value for key, value in plan_data.items() if key != "id"},
        )


populate_plans()
