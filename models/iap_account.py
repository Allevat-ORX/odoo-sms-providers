# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
import hashlib
import hmac
import base64
from urllib.parse import urlencode

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = 'iap.account'

    provider = fields.Selection(
        selection_add=[('sms_api_zadarma', 'Zadarma')],
        ondelete={'sms_api_zadarma': 'set default'},
    )

    zadarma_user_key = fields.Char(
        string="Zadarma User Key",
        help="Your Zadarma API User Key"
    )
    zadarma_secret_key = fields.Char(
        string="Zadarma Secret Key",
        help="Your Zadarma API Secret Key"
    )
    zadarma_base_url = fields.Char(
        string="Zadarma Base URL",
        default="https://api.zadarma.com",
        help="Zadarma API base URL"
    )

    is_default_sms = fields.Boolean(
        string="Default SMS Provider",
        default=False,
        help="Use this provider by default for sending SMS"
    )

    @api.model
    def _get_sms_account(self):
        """Get SMS account with priority: 1) Default marked, 2) Lowest ID."""
        # First, try to get account marked as default
        default_account = self.search([
            ('provider', 'like', 'sms_api'),
            ('is_default_sms', '=', True),
        ], limit=1)

        if default_account:
            _logger.info(f"Using default SMS provider: {default_account.provider} (ID: {default_account.id})")
            return default_account

        # Fallback: get lowest ID (original behavior)
        fallback_account = self.search([
            ('provider', 'like', 'sms_api'),
        ], order='id asc', limit=1)

        if fallback_account:
            _logger.info(f"Using fallback SMS provider (lowest ID): {fallback_account.provider} (ID: {fallback_account.id})")
            return fallback_account

        # Last resort: default IAP SMS account
        return self.get("sms")

    def zadarma_test_connection(self):
        """Test Zadarma API connection."""
        self.ensure_one()
        if not self.zadarma_user_key or not self.zadarma_secret_key:
            raise UserError(_("Please configure Zadarma credentials first."))

        try:
            method = "/v1/info/balance/"
            params = {'format': 'json'}
            signature = self._generate_zadarma_signature(method, params)

            # Use default urlencode for consistency with signature generation
            url = f"{self.zadarma_base_url}{method}?{urlencode(params)}"
            headers = {'Authorization': f'{self.zadarma_user_key}:{signature}'}

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'success':
                balance = data.get('balance', 0)
                currency = data.get('currency', 'USD')
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful!'),
                        'message': _('Balance: %s %s') % (balance, currency),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("API Error: %s") % data.get('message', 'Unknown'))

        except Exception as e:
            raise UserError(_("Connection failed: %s") % str(e))

    def _generate_zadarma_signature(self, method, params):
        """Generate Zadarma API signature (matches Python SDK)."""
        sorted_items = sorted(params.items())
        # Use default urlencode (+ for spaces) to match requests library encoding
        params_string = urlencode(sorted_items)
        md5_hash = hashlib.md5(params_string.encode()).hexdigest()
        string_to_sign = method + params_string + md5_hash
        hmac_hex = hmac.new(
            self.zadarma_secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha1
        ).hexdigest()
        return base64.b64encode(hmac_hex.encode()).decode()

    @api.model
    def create(self, vals_list):
        """Auto-set provider when Zadarma credentials are provided."""
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('zadarma_user_key') and vals.get('zadarma_secret_key'):
                vals['provider'] = 'sms_api_zadarma'

            # Auto-uncheck other defaults if this one is marked as default
            if vals.get('is_default_sms'):
                self.search([
                    ('provider', 'like', 'sms_api'),
                    ('is_default_sms', '=', True)
                ]).write({'is_default_sms': False})

        return super().create(vals_list)

    def write(self, vals):
        """Auto-set provider when Zadarma credentials are provided."""
        if vals.get('zadarma_user_key') or vals.get('zadarma_secret_key'):
            for rec in self:
                if rec.zadarma_user_key and rec.zadarma_secret_key:
                    vals['provider'] = 'sms_api_zadarma'

        # Auto-uncheck other defaults if this one is marked as default
        if vals.get('is_default_sms'):
            self.search([
                ('provider', 'like', 'sms_api'),
                ('is_default_sms', '=', True),
                ('id', 'not in', self.ids)
            ]).write({'is_default_sms': False})

        return super().write(vals)
