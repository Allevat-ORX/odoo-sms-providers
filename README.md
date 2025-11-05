# Odoo 18 SMS Providers - Multi-Provider SMS Integration

Complete SMS integration for Odoo 18 using multiple providers through IAP Alternative Provider framework.

## 📦 Available Modules

### 1. sms_zadarma_v2
**Zadarma SMS Connector**
- ✅ Full Zadarma API integration
- ✅ HMAC-SHA1 signature authentication
- ✅ Balance checking
- ✅ Tested and working

**Credentials needed:**
- User Key
- Secret Key

**Cost:** ~$0.075 per SMS

### 2. sms_labsmobile
**LabsMobile SMS Connector**
- ✅ Full LabsMobile JSON API integration
- ✅ Basic Auth (username:token)
- ✅ Balance checking
- ✅ Cost-effective option

**Credentials needed:**
- Username (email)
- API Token

**Cost:** More economical than Zadarma

## 🚀 Quick Start

### Requirements
```bash
# Clone OCA server-tools for iap_alternative_provider
git clone -b 18.0 https://github.com/OCA/server-tools.git
cp -r server-tools/iap_alternative_provider /path/to/odoo/addons/
```

### Installation

**Option 1: Zadarma**
```bash
git clone https://github.com/Allevat-ORX/odoo-zadarma-sms.git
cp -r odoo-zadarma-sms /path/to/odoo/addons/sms_zadarma_v2
```

**Option 2: LabsMobile**
```bash
git clone https://github.com/Allevat-ORX/odoo-labsmobile-sms.git
cp -r odoo-labsmobile-sms /path/to/odoo/addons/sms_labsmobile
```

**Install in Odoo:**
1. Update Apps List
2. Install "iap_alternative_provider"
3. Install your chosen SMS provider module
4. Configure credentials in Settings → Technical → IAP → Accounts

## 📋 Configuration

### For Zadarma:
```
Settings → Technical → IAP → Accounts
- Service: SMS
- Provider: Zadarma
- User Key: your_user_key
- Secret Key: your_secret_key
- Test Connection → Should show balance
```

### For LabsMobile:
```
Settings → Technical → IAP → Accounts
- Service: SMS
- Provider: LabsMobile
- Username: your_email@domain.com
- API Token: your_api_token
- Test Connection → Should show balance
```

## 🎯 Features

✅ **Multi-Provider Support**
- Switch between providers easily
- Automatic failover
- No code changes needed

✅ **Full Odoo Integration**
- Works with SMS Marketing
- Works with CRM SMS
- Works with any Odoo SMS feature
- Automatic state tracking (sent/error)

✅ **Production Ready**
- Tested on Odoo 18
- Error handling
- Logging
- Secure credential storage

## 🏗️ Architecture

Both modules use the same architecture:

```
iap_alternative_provider (OCA)
    ↓
sms_zadarma_v2 / sms_labsmobile
    ├── models/
    │   ├── iap_account.py    (Provider registration + credentials)
    │   └── sms_sms.py         (SMS sending logic)
    └── views/
        └── iap_account.xml    (UI for credentials)
```

**Flow:**
1. User creates SMS in Odoo (Contact, CRM, Marketing, etc.)
2. `sms.sms._send()` is called
3. Module checks if provider is configured
4. If yes: Use provider API
5. If no: Use default Odoo IAP
6. SMS state updated automatically

## ⚠️ Known Issues

### LabsMobile + Mexico
**Status:** API accepts messages but SMS do not reach Mexican phone numbers

- ✅ API responds successfully (code: 0)
- ✅ Credits are deducted
- ❌ SMS never delivered to destination
- **Possible causes:**
  - LabsMobile requires specific activation for Mexico
  - Sender ID registration needed for Mexico
  - Account verification required for international SMS
  - Routing issues with Mexican carriers

**Recommendation:** Use **Zadarma** for Mexican numbers (tested and working ✅)

**LabsMobile Support:** Contact LabsMobile support to activate Mexican SMS delivery

---

## 🔧 Troubleshooting

### Zadarma 401 Errors
- Verify User Key and Secret Key
- Check signature generation (should use `+` for spaces, not `%20`)
- Ensure `format=json` parameter is included

### LabsMobile Errors
- Verify username and API token
- Check phone number format (should not include `+`)
- Ensure balance is sufficient

### General Issues
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo.log | grep -i "zadarma\|labsmobile"

# Verify module installed
# In Odoo: Apps → search for module name
```

## 📊 Testing

### Test Connection (UI)
Settings → Technical → IAP → Accounts → Select account → "Test Connection" button

### Test SMS Send (Python)
```python
import xmlrpc.client

url = "https://your-odoo.com"
db = "your_db"
username = "admin"
password = "admin_password"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Create and send SMS
sms_id = models.execute_kw(db, uid, password,
    'sms.sms', 'create',
    [{'number': '+1234567890', 'body': 'Test message'}])

models.execute_kw(db, uid, password,
    'sms.sms', 'send', [[sms_id]])
```

## 🔐 Security

- Credentials stored encrypted in Odoo database
- API tokens never logged
- HTTPS for all API calls
- No credentials in code or config files

## 📝 Credits

**Author:** OnRentX - Aleix
**License:** LGPL-3
**Website:** https://tramarental.com

Based on IAP Alternative Provider framework by OCA.

## 🆘 Support

1. Check module logs in Odoo
2. Verify API credentials in provider dashboard
3. Test API directly with curl/python
4. Open issue on GitHub

## 🔗 Links

- **Zadarma API Docs:** https://zadarma.com/en/support/api/
- **LabsMobile API Docs:** https://apidocs.labsmobile.com/
- **OCA IAP Alternative Provider:** https://github.com/OCA/server-tools
- **Odoo SMS Documentation:** https://www.odoo.com/documentation/18.0/developer/reference/backend/mixins.html#sms-mixin

---

**Last Updated:** 2025-11-05
**Odoo Version:** 18.0
**Status:** ✅ Production Ready
