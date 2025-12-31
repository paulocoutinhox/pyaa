import pytest
from django.contrib.sites.models import Site

from apps.shop.enums import PaymentGateway, PlanFrequencyType, PlanType
from apps.shop.models import Plan


@pytest.fixture
def site(db):
    return Site.objects.get_current()


@pytest.fixture
def stripe_plan(site):
    return Plan.objects.create(
        site=site,
        name="Stripe Plan",
        tag="stripe-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        external_id="ext_stripe_123",
        currency="USD",
        price=9.99,
        credits=100,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        active=True,
    )


@pytest.fixture
def inactive_plan(site):
    return Plan.objects.create(
        site=site,
        name="Inactive Plan",
        tag="inactive-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=5.99,
        credits=50,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        active=False,
    )


def test_list_all_plans(client, stripe_plan, inactive_plan):
    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_list_plans_filter_by_gateway_stripe(client, stripe_plan):
    response = client.get(f"/api/shop/plan?gateway={PaymentGateway.STRIPE.value}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["gateway"] == PaymentGateway.STRIPE.value
    assert data[0]["name"] == "Stripe Plan"


def test_list_plans_filter_by_active(client, stripe_plan, inactive_plan):
    response = client.get("/api/shop/plan?active=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["active"] is True
    assert data[0]["name"] == "Stripe Plan"


def test_list_plans_filter_by_inactive(client, stripe_plan, inactive_plan):
    response = client.get("/api/shop/plan?active=false")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["active"] is False
    assert data[0]["name"] == "Inactive Plan"


def test_list_plans_filter_by_site(client, site, stripe_plan):
    response = client.get(f"/api/shop/plan?site={site.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_list_plans_multiple_filters(client, site, stripe_plan):
    response = client.get(
        f"/api/shop/plan?gateway={PaymentGateway.STRIPE.value}&active=true&site={site.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["gateway"] == PaymentGateway.STRIPE.value
    assert data[0]["active"] is True


def test_plan_schema_includes_all_fields(client, stripe_plan):
    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    plan = data[0]

    assert "name" in plan
    assert "tag" in plan
    assert "planType" in plan
    assert "gateway" in plan
    assert "externalId" in plan
    assert "currency" in plan
    assert "price" in plan
    assert "credits" in plan
    assert "frequencyType" in plan
    assert "frequencyAmount" in plan
    assert "featured" in plan
    assert "bonus" in plan
    assert "image" in plan
    assert "sortOrder" in plan
    assert "description" in plan
    assert "active" in plan
    assert "createdAt" in plan
    assert "updatedAt" in plan


def test_plan_external_id_field(client, stripe_plan):
    response = client.get(f"/api/shop/plan?gateway={PaymentGateway.STRIPE.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["externalId"] == "ext_stripe_123"


def test_list_plans_empty_result(client):
    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_plans_invalid_site_filter(client, stripe_plan):
    response = client.get("/api/shop/plan?site=99999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_list_plans_order_by_sort_order(client, site):
    plan1 = Plan.objects.create(
        site=site,
        name="Z Plan",
        tag="z-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=9.99,
        credits=100,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        sort_order=2,
        active=True,
    )
    plan2 = Plan.objects.create(
        site=site,
        name="A Plan",
        tag="a-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=9.99,
        credits=100,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        sort_order=1,
        active=True,
    )

    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["sortOrder"] == 1
    assert data[0]["name"] == "A Plan"
    assert data[1]["sortOrder"] == 2
    assert data[1]["name"] == "Z Plan"


def test_list_plans_order_by_name_when_sort_order_equal(client, site):
    plan1 = Plan.objects.create(
        site=site,
        name="Zebra Plan",
        tag="zebra-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=9.99,
        credits=100,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        sort_order=0,
        active=True,
    )
    plan2 = Plan.objects.create(
        site=site,
        name="Apple Plan",
        tag="apple-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=9.99,
        credits=100,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        sort_order=0,
        active=True,
    )

    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Apple Plan"
    assert data[1]["name"] == "Zebra Plan"


def test_plan_without_external_id(client, site):
    plan = Plan.objects.create(
        site=site,
        name="No External ID Plan",
        tag="no-ext-plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=9.99,
        credits=100,
        frequency_type=PlanFrequencyType.MONTH,
        frequency_amount=1,
        active=True,
    )

    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["externalId"] is None


def test_plan_with_all_optional_fields_null(client, site):
    plan = Plan.objects.create(
        site=site,
        name="Minimal Plan",
        tag="minimal-plan",
        plan_type=PlanType.CREDIT_PURCHASE,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=5.99,
        active=True,
    )

    response = client.get("/api/shop/plan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["externalId"] is None
    assert data[0]["credits"] is None
    assert data[0]["frequencyType"] is None
    assert data[0]["bonus"] is None
    assert data[0]["description"] is None
