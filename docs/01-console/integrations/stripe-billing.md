# Stripe Billing Integration

This console routes all purchase entry points through Accounts-managed Stripe Checkout:

- `/prices`
- product detail pages
- `/panel/subscription`

The browser reads public plan and `price_id` data from the Accounts billing catalog. It never
stores Stripe keys or calls Stripe directly.

## Configuration ownership

- Accounts billing catalog owns active plan IDs, Price IDs, price, currency and billing cadence.
- Vault injects `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` into Accounts only.
- Portal has no Stripe environment variables and forwards only an allowlisted checkout payload.

## Local Integration Checklist

1. Publish the active Stripe Test Mode Price IDs in the Accounts billing catalog.
2. Start `accounts.svc.plus` with Vault-provided server-side Stripe settings.
3. Start this console with `yarn dev`.
4. Sign in with a normal user account.
5. Open `/prices` or `/panel/subscription` and start checkout.
6. Complete a Stripe test payment.
7. Confirm the browser returns to `/panel/subscription?checkout=success...`.
8. Confirm the subscription record appears in the subscription panel.
9. Open "Manage Stripe billing" and confirm the customer portal opens.

## Expected Flow

1. The console calls `/api/auth/stripe/checkout`.
2. The BFF proxies the request to `accounts.svc.plus` using the current account session.
3. `accounts.svc.plus` creates the Stripe Checkout Session.
4. Stripe redirects back to the console.
5. Stripe webhooks update the account service subscription record.
6. The console reads the final state from `/api/auth/subscriptions`.

## Notes

- The console does not store Stripe secret keys.
- Sensitive payment methods such as crypto QR flows are intentionally removed from the purchase UI.
- Use Stripe test mode first; do not validate this flow against live prices until webhook delivery is confirmed.
