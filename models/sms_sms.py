# -*- coding: utf-8 -*-
from odoo import fields, models, _
import logging
import requests
import hashlib
import hmac
import base64
from urllib.parse import urlencode

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    zadarma_message_id = fields.Char(
        string="Zadarma Message ID",
        readonly=True,
        copy=False
    )

    def _is_sent_with_zadarma(self):
        """Check if SMS should be sent via Zadarma."""
        iap_account = self.env['iap.account']._get_sms_account()
        return bool(
            iap_account and
            iap_account.zadarma_user_key and
            iap_account.zadarma_secret_key and
            iap_account.provider == 'sms_api_zadarma'
        )

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        """Override to use Zadarma for SMS sending."""
        if not self._is_sent_with_zadarma():
            return super()._send(
                unlink_failed=unlink_failed,
                unlink_sent=unlink_sent,
                raise_exception=raise_exception
            )

        # Send via Zadarma
        iap_account = self.env['iap.account']._get_sms_account()

        for sms in self:
            try:
                success = sms._send_zadarma_sms(iap_account)
                if success:
                    sms.write({'state': 'sent'})
                    _logger.info(f"SMS {sms.id} marked as sent")
                    if unlink_sent:
                        sms.unlink()
                else:
                    sms.write({'state': 'error', 'failure_type': 'sms_server'})
                    if unlink_failed:
                        sms.unlink()
            except Exception as e:
                _logger.error(f"Zadarma SMS error for {sms.number}: {e}")
                sms.write({'state': 'error', 'failure_type': 'sms_server'})
                if raise_exception:
                    raise
                if unlink_failed:
                    sms.unlink()

        return True

    def _send_zadarma_sms(self, iap_account):
        """Send single SMS via Zadarma API. Returns True if successful, False otherwise."""
        self.ensure_one()

        if not self.number:
            _logger.error(f"SMS {self.id}: No phone number provided")
            return False

        method = "/v1/sms/send/"
        params = {
            'number': self.number,
            'message': self.body,
            'format': 'json'
        }

        try:
            signature = iap_account._generate_zadarma_signature(method, params)
            url = f"{iap_account.zadarma_base_url}{method}"
            headers = {'Authorization': f'{iap_account.zadarma_user_key}:{signature}'}

            _logger.info(f"Sending SMS to {self.number} via Zadarma")

            response = requests.post(url, data=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'success':
                _logger.info(f"SMS sent successfully to {self.number}")
                return True
            else:
                error_msg = data.get('message', 'Unknown error')
                _logger.error(f"Zadarma API error: {error_msg}")
                return False

        except requests.exceptions.Timeout:
            _logger.error(f"Zadarma API timeout for {self.number}")
            return False
        except Exception as e:
            _logger.exception(f"Zadarma SMS exception for {self.number}: {e}")
            return False
