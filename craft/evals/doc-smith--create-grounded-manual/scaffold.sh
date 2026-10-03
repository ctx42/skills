#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'EOF_0'
{
  "name": "billing-dashboard",
  "version": "1.4.0",
  "private": true,
  "scripts": { "dev": "vite", "api": "node server/index.js" }
}
EOF_0
cat > README.md <<'EOF_1'
# billing-dashboard

React front end and Express API for the billing dashboard.

## Development

Run `npm install`, then `npm run dev` and `npm run api`.
EOF_1
mkdir -p src/screens
cat > src/screens/InvoiceList.tsx <<'EOF_2'
// Invoices screen: the landing page after sign-in.
export function InvoiceList() {
  return (
    <Page title="Invoices">
      <StatusFilter options={["All", "Open", "Paid", "Overdue"]} />
      <Table columns={["Number", "Issued", "Due", "Amount", "Status"]} source="/api/bills" />
      <Button label="Download PDF" />
    </Page>
  );
}
EOF_2
mkdir -p src/screens
cat > src/screens/InvoiceDetail.tsx <<'EOF_3'
// One invoice with its line items.
export function InvoiceDetail({ id }: { id: string }) {
  return (
    <Page title="Invoice">
      <LineItems source={`/api/bills/${id}`} />
      <Button label="Download PDF" href={`/api/bills/${id}/pdf`} />
      <Button label="Pay now" action={`/api/bills/${id}/pay`} disabledWhen="status === 'Paid'" />
    </Page>
  );
}
EOF_3
mkdir -p src/screens
cat > src/screens/PaymentMethod.tsx <<'EOF_4'
// The card the account is charged with.
export function PaymentMethod() {
  return (
    <Page title="Payment method">
      <CardForm fields={["Card number", "Expiry", "CVC", "Name on card"]} />
      <Button label="Save card" action="PUT /api/payment-method" />
    </Page>
  );
}
EOF_4
mkdir -p src/screens
cat > src/screens/Usage.tsx <<'EOF_5'
// API calls per day in the current billing period.
export function Usage() {
  return (
    <Page title="Usage">
      <BarChart source="/api/usage" x="day" y="calls" />
      <Note text="Usage above your plan's included calls is billed on the next invoice." />
    </Page>
  );
}
EOF_5
mkdir -p server
cat > server/routes.js <<'EOF_6'
// Express routes for the billing dashboard API.
router.get("/api/bills", listBills);             // ?status=open|paid|overdue
router.get("/api/bills/:id", getBill);
router.get("/api/bills/:id/pdf", billPdf);
router.post("/api/bills/:id/pay", payBill);      // charges the saved card
router.put("/api/payment-method", saveCard);     // 402 when the card is declined
router.get("/api/usage", usageThisPeriod);
EOF_6
