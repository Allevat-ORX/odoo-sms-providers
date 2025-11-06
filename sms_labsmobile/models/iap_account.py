# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
import base64

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = 'iap.account'

    provider = fields.Selection(
        selection_add=[('sms_api_labsmobile', 'LabsMobile')],
        ondelete={'sms_api_labsmobile': 'set default'},
    )

    labsmobile_username = fields.Char(
        string="LabsMobile Username",
        help="Your LabsMobile account email"
    )

    labsmobile_token = fields.Char(
        string="LabsMobile API Token",
        help="API Token from LabsMobile dashboard"
    )

    labsmobile_base_url = fields.Char(
        string="LabsMobile Base URL",
        default="https://api.labsmobile.com",
        help="LabsMobile API base URL"
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

    def labsmobile_test_connection(self):
        """Test LabsMobile API connection by checking balance."""
        self.ensure_one()
        if not self.labsmobile_username or not self.labsmobile_token:
            raise UserError(_("Please configure LabsMobile credentials first."))

        try:
            url = f"{self.labsmobile_base_url}/json/balance"
            auth_string = base64.b64encode(
                f"{self.labsmobile_username}:{self.labsmobile_token}".encode()
            ).decode()
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'balance' in data:
                balance = data['balance']
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful!'),
                        'message': _('Balance: %s credits') % balance,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("API Error: %s") % data.get('message', 'Unknown'))

        except Exception as e:
            raise UserError(_("Connection failed: %s") % str(e))

    @api.model
    def create(self, vals_list):
        """Auto-set provider when LabsMobile credentials are provided."""
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('labsmobile_username') and vals.get('labsmobile_token'):
                vals['provider'] = 'sms_api_labsmobile'

            # Auto-uncheck other defaults if this one is marked as default
            if vals.get('is_default_sms'):
                self.search([
                    ('provider', 'like', 'sms_api'),
                    ('is_default_sms', '=', True)
                ]).write({'is_default_sms': False})

        return super().create(vals_list)

    def write(self, vals):
        """Auto-set provider when LabsMobile credentials are updated."""
        if vals.get('labsmobile_username') or vals.get('labsmobile_token'):
            for rec in self:
                if rec.labsmobile_username and rec.labsmobile_token:
                    vals['provider'] = 'sms_api_labsmobile'

        # Auto-uncheck other defaults if this one is marked as default
        if vals.get('is_default_sms'):
            self.search([
                ('provider', 'like', 'sms_api'),
                ('is_default_sms', '=', True),
                ('id', 'not in', self.ids)
            ]).write({'is_default_sms': False})

        return super().write(vals)
