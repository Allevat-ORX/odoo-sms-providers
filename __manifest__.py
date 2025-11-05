# -*- coding: utf-8 -*-
{
    'name': "Zadarma SMS Connector",
    'summary': "Send SMS with Zadarma API (Odoo 18)",
    'author': "OnRentX - Aleix",
    'website': "https://tramarental.com",
    'license': 'LGPL-3',
    'category': 'Tools',
    'version': '18.0.1.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'sms',
        'iap_alternative_provider',
        'iap',
    ],
    'external_dependencies': {
        'python': ['requests']
    },
    'data': [
        'views/iap_account.xml',
    ],
}
