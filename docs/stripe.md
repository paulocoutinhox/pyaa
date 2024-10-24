# Stripe

This guide explains how to integrate Stripe as a payment gateway for your application.

## Configuration

To set up Stripe, you need to configure two essential keys:

1. `STRIPE_SECRET_KEY`: Your Stripe account's secret key
2. `STRIPE_WEBHOOK_SECRET`: The secret for verifying webhook events

You can set these keys in one of two ways:

- In the `dev.py` file
- As environment variables

In the Stripe Webhook configuration, select all events from the following categories to receive notifications:

- Charge
- Checkout
- Invoice
- Payment Intent

## Local Testing

To test the Stripe integration locally, you'll need to use the `stripe-cli` tool. Follow these steps:

1. Install the `stripe-cli` tool on your system.
2. Authenticate with your Stripe account using the CLI.

### Setting Up The Webhook Listener

Open a terminal and run the following command to start listening for webhook events:

```
stripe listen --forward-to localhost:8000/shop/webhook/stripe/
```

This command will forward Stripe events to your local development server.

### Simulating A Completed Order

In a separate terminal, you can simulate a completed checkout session using this command:

```
stripe trigger checkout.session.completed --add checkout_session:client_reference_id=[ORDER-TOKEN]
```

Replace `[ORDER-TOKEN]` with your actual order token.

### Resend Events Already Sent Before

In a separate terminal, you can resend events from Stripe webhook panel:

```
stripe events resend [EVENT-ID]
```

Replace `[EVENT-ID]` with your event ID, that start with `evt_`.

## Additional Resources

For more detailed information, consult the following official Stripe documentation:

- [Stripe CLI Overview](https://docs.stripe.com/stripe-cli/overview)
- [Webhooks Documentation](https://docs.stripe.com/webhooks)

These resources provide comprehensive guidance on using the Stripe CLI and working with webhooks in your integration.
