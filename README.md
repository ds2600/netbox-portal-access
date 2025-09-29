
# netbox-portal-access

## Installation 

1. **Install into NetBox**  
   On your NetBox venv:
   ```bash
   pip install --no-cache-dir git+https://github.com/ds2600/netbox-portal-access.git
   ```

2. **Generate a Fernet key**
    ```bash
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```

3. **Enable the plugin**  
   In `configuration.py` (or `configuration/plugins.py` for newer NetBox), add:
   ```python
   PLUGINS = ["netbox_portal_access"]

   PLUGINS_CONFIG = {
       "netbox_portal_access": {
            "fernet_key": "PASTE_KEY_HERE",
        }
   }
   ```

4. **Migrate & restart**
   ```bash
   # From the NetBox project root
   source /opt/netbox/venv/bin/activate
   python netbox/manage.py migrate
   sudo systemctl restart netbox netbox-rq
   ```

## Roadmap ideas (easy to add later)
- CSV import/export for faster bulk loads
- “Review due” badges & reports (e.g., 90+ days stale)
- Optional link to **contacts.Contact** (currently available via generic relation fields; UI form prefers Users for MVP)
- API adapters (Equinix, Zayo) to sync roles/users to the database
- Attachments for proof (screenshots/CSVs)

## License
MIT
