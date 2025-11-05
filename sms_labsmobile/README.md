# LabsMobile SMS Connector for Odoo 18

Send SMS messages directly from Odoo using LabsMobile API.

## Features

- ✅ Full integration with Odoo SMS system
- ✅ Works with all Odoo SMS modules (SMS Marketing, CRM SMS, etc.)
- ✅ Multi-provider support via IAP Alternative Provider
- ✅ Secure credential management
- ✅ Connection testing
- ✅ Automatic failover to other SMS providers
- ✅ Cost-effective SMS sending

## Requirements

- Odoo 18.0
- `iap_alternative_provider` module from OCA
- LabsMobile account with username and API token

## Installation

1. Install `iap_alternative_provider`:
```bash
# Clone OCA server-tools
git clone -b 18.0 https://github.com/OCA/server-tools.git
cp -r server-tools/iap_alternative_provider /path/to/odoo/addons/
```

2. Install this module:
```bash
git clone https://github.com/Allevat-ORX/odoo-labsmobile-sms.git
cp -r odoo-labsmobile-sms /path/to/odoo/addons/sms_labsmobile
```

3. Update apps list in Odoo
4. Install "LabsMobile SMS Connector"

## Configuration

1. Go to **Settings → Technical → IAP → Accounts**
2. Create a new account or edit existing one
3. Set:
   - **Service**: SMS
   - **Provider**: LabsMobile
   - **LabsMobile Username**: Your account email
   - **LabsMobile API Token**: Your API token from LabsMobile dashboard
4. Click **Test Connection** to verify

## Usage

Once configured, all SMS sent from Odoo will automatically use LabsMobile.

## Credits

**Author:** OnRentX - Aleix
**License:** LGPL-3
**Website:** https://tramarental.com
