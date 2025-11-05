# Zadarma SMS Connector for Odoo 18

Send SMS messages directly from Odoo using Zadarma API.

## Features

- ✅ Full integration with Odoo SMS system
- ✅ Works with all Odoo SMS modules (SMS Marketing, CRM SMS, etc.)
- ✅ Multi-provider support via IAP Alternative Provider
- ✅ Secure credential management
- ✅ Connection testing
- ✅ Automatic failover to other SMS providers

## Requirements

- Odoo 18.0
- `iap_alternative_provider` module from OCA
- Zadarma API account with User Key and Secret Key

## Installation

1. Install `iap_alternative_provider`:
```bash
# Clone OCA server-tools
git clone -b 18.0 https://github.com/OCA/server-tools.git
cp -r server-tools/iap_alternative_provider /path/to/odoo/addons/
```

2. Install this module:
```bash
git clone https://github.com/tu-usuario/odoo-zadarma-sms.git
cp -r odoo-zadarma-sms /path/to/odoo/addons/sms_zadarma
```

3. Update apps list in Odoo
4. Install "Zadarma SMS Connector"

## Configuration

1. Go to **Settings → Technical → IAP → Accounts**
2. Create a new account or edit existing one
3. Set:
   - **Service**: SMS
   - **Provider**: Zadarma
   - **Zadarma User Key**: Your API user key
   - **Zadarma Secret Key**: Your API secret key
4. Click **Test Connection** to verify

## Usage

Once configured, all SMS sent from Odoo will automatically use Zadarma:

### Send SMS from Contacts
1. Open a contact with mobile number
2. Click **Send SMS**
3. Type message and send

### SMS Marketing
1. Go to **SMS Marketing**
2. Create campaign
3. Messages will be sent via Zadarma

### CRM SMS
1. Open lead/opportunity
2. Click **Send SMS**
3. Message delivered via Zadarma

## Troubleshooting

### SMS not sending

Check logs:
```bash
grep -i zadarma /var/log/odoo/odoo.log
```

Common issues:
- Invalid credentials → Verify User Key and Secret Key
- No credit → Check balance at https://my.zadarma.com
- Wrong phone format → Use international format: +1234567890

## Technical Details

- Uses official Zadarma PHP SDK signature method
- Automatic HMAC-SHA1 signature generation
- Full compatibility with IAP Alternative Provider framework
- Supports batch SMS sending

## Credits

**Author:** OnRentX - Aleix
**License:** LGPL-3
**Website:** https://tramarental.com

Based on the IAP Alternative Provider framework by OCA.

## Support

For issues or questions:
1. Check Odoo logs
2. Verify Zadarma account has sufficient balance
3. Ensure phone numbers are in international format
4. Open an issue on GitHub
