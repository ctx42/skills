---
type: agent
---
Answer each id or path with its document below, verbatim.

For `initiatives/wishlist-v2/srd.md`:

````markdown
# SRD: Wishlist sharing v2

- **Objective:** Let a reader share a wishlist by link.
- **Owners:** Ada Brook (primary), Lev Ortiz (secondary)
- **Initiative:** https://tickets.example.com/browse/BOOK-19
- **Status:** REJECTED
- **Designs:** N/A

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119 and RFC 8174.
````

For `initiatives/gift-cards/srd.md`:

````markdown
# SRD: Gift cards

- **Objective:** Let a reader buy a gift card for a wishlist title.
- **Owners:** Ada Brook (primary), Lev Ortiz (secondary)
- **Initiative:** https://tickets.example.com/browse/BOOK-10
- **Status:** ACCEPTED
- **Designs:** N/A

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119 and RFC 8174.
````

For `kb/wishlists.md`:

````markdown
---
title: Wishlists
attested: 2026-09-02
srd_ref: wishlist-v2, gift-cards
last_verified: 2026-09-20
---

# Wishlists

## Shared wishlist links

> Not in the platform docs. Attested wishlist-v2 interview 2026-09-02.

A reader can create a read-only link to one wishlist. The link never expires.

## Wishlist visibility

> Not in the platform docs. Attested wishlist-v2 interview 2026-09-02; gift-cards
> interview 2026-09-20.

A wishlist is private until its owner shares it.

## Wishlist size limit

> Not in the platform docs. Attested wishlist-v2 interview 2026-09-02.

A wishlist holds at most 200 titles.

## Gift wrap

> Not in the platform docs. Attested gift-cards interview 2026-09-20.

A gift card bought for a wishlist title can be gift-wrapped.

## Provenance

Where each section of this page comes from.

| Section               | Source                             |
|-----------------------|------------------------------------|
| Shared wishlist links | wishlist-v2 interview              |
| Wishlist visibility   | wishlist-v2, gift-cards interviews |
| Wishlist size limit   | wishlist-v2 interview              |
| Gift wrap             | gift-cards interview               |
````

For `kb/_inbox.md`:

````markdown
---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox
````

For any other id answer {"error":"document not found"}.
