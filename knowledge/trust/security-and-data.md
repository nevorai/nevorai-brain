# Security and data
Last checked: 2026-11-07.

## Where data lives
Each business's contacts, chats, files and documents are stored separately and are visible only to that business's logins. Row-level security in the database enforces it.

## Who can see what
Owners see everything in their business. Team members see what the owner allows (for example only their own chats). Nevorai staff do not read customer chats except to fix a problem the business reported.

## AI and your data
Nevorai's AI reads the business's own data (profile, documents, chats) to answer its customers. It is stated in the privacy policy. Nevorai's AI key is on a paid Google project, so prompts are not used to train Google's models.

## Payments
Card and UPI details are handled by Razorpay; Nevorai never sees or stores them. We never ask for OTPs or passwords on WhatsApp.

## Files
Uploads are stored on Cloudflare R2 and served from media.nevorai.com; private files use short-lived signed links.
