
# netbox-portal-access

A **barebones NetBox plugin** to track who has access to which vendor portals (Equinix, DataBank, Zayo, Lumen, etc.), the role they have on that portal, and helpful metadata (MFA, SSO, last reviewed). Starts as **manual entry** and is designed to grow into API-backed sync later.

> Status: **MVP** — models, UI lists/edit forms, and REST API endpoints are included. Expect to iterate.

## Models

- **Portal**: The login surface for a vendor (e.g., *Equinix Customer Portal*, *Zayo Portal*). Links to either `circuits.Provider` (carriers) or `tenancy.Tenant` (DC operators) via a generic relation.
- **VendorRole**: The vendor-labeled role (e.g., “Company Admin”, “Service Desk”) mapped to a normalized category (e.g., `PORTAL_ADMIN`, `LOA_APPROVER`).
- **AccessAssignment**: A user’s access on a specific portal (optionally a contact), with extras like org/account ID, MFA type, SSO, last verified, and expiry.

## Quick start (local dev)

1. **Install into NetBox**  
   On your NetBox host/venv:
   ```bash
   # Option A: install editable from your Git clone
   pip install -e /opt/netbox/netbox-portal-access

   # Option B: via GitHub URL (if the repo is public or has a token)
   pip install git+https://github.com/ds2600/netbox-portal-access.git
   ```

2. **Enable the plugin**  
   In `configuration.py` (or `configuration/plugins.py` for newer NetBox), add:
   ```python
   PLUGINS = ["netbox_portal_access"]

   PLUGINS_CONFIG = {
       "netbox_portal_access": {}
   }
   ```

3. **Migrate & restart**
   ```bash
   # From the NetBox project root
   source /opt/netbox/venv/bin/activate
   python netbox/manage.py migrate
   sudo systemctl restart netbox netbox-rq
   ```

4. **Where to click**
   - In the UI sidebar: **Plugins → Portal Access** to find *Portals*, *Vendor Roles*, and *Access Assignments*.
   - Add **Portals** first (pick the vendor type and ID, then give it a friendly name and URL).
   - Add **Vendor Roles** for each portal and map them to a category.
   - Add **Access Assignments** for your people.

## Data entry tips
- **Vendors**: Use **Circuits → Providers** for carriers (Zayo, Lumen, Cogent) and **Tenancy → Tenants** for data center operators (Equinix, DataBank, Flexential). Copy the object’s ID for `vendor_id`.
- **Categories** enable cross-vendor queries like “who are **all** LOA approvers?”
- Track **`last_verified`** during quarterly access reviews; use **`expires_on`** for contractors.

## REST API
Once the plugin is enabled, endpoints live under `/api/plugins/netbox-portal-access/`:
- `GET /portals/`
- `GET /vendor-roles/`
- `GET /assignments/`

(POST/PUT/PATCH/DELETE are supported for authenticated users with permissions.)

## Permissions
Standard NetBox object permissions apply. Define object-level perms for `Portal`, `VendorRole`, and `AccessAssignment` as needed.

## Roadmap ideas (easy to add later)
- CSV import/export for faster bulk loads
- “Review due” badges & reports (e.g., 90+ days stale)
- Optional link to **contacts.Contact** (currently available via generic relation fields; UI form prefers Users for MVP)
- API adapters (Equinix, Zayo) to sync roles/users to the database
- Attachments for proof (screenshots/CSVs)

## Development
- Requires **NetBox ≥ 3.6** (tested path). On NetBox 4.x, the generic views and tables may have minor API changes — this plugin declares `max_version = "4.0.99"` and is expected to work with early 4.x; adjust as needed.
- Run tests (add your NetBox dev env first):
  ```bash
  pytest -q
  ```

## Uninstall
```bash
pip uninstall netbox-portal-access
# remove from PLUGINS in configuration.py and restart services
```

## License
MIT
