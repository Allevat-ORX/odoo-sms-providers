# -*- coding: utf-8 -*-
from odoo import fields, models, _
import logging
import requests
import hashlib
import hmac
import base64
from urllib.parse import urlencode, quote

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
        results = []

        for sms in self:
            try:
                result = sms._send_zadarma_sms(iap_account)
                results.append(result)
            except Exception as e:
                _logger.error(f"Zadarma SMS error for {sms.number}: {e}")
                results.append({
                    'uuid': sms.uuid,
                    'state': 'server_error',
                    'credit': 0
                })

        self._postprocess_iap_sent_sms(
            results,
            unlink_failed=unlink_failed,
            unlink_sent=unlink_sent
        )

    def _send_zadarma_sms(self, iap_account):
        """Send single SMS via Zadarma API."""
        self.ensure_one()

        if not self.number:
            return {
                'uuid': self.uuid,
                'state': 'wrong_number_format',
                'credit': 0
            }

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
                return {
                    'uuid': self.uuid,
                    'state': 'success',
                    'credit': data.get('messages', 1)
                }
            else:
                error_msg = data.get('message', 'Unknown error')
                _logger.error(f"Zadarma API error: {error_msg}")
                return {
                    'uuid': self.uuid,
                    'state': 'server_error',
                    'credit': 0
                }

        except requests.exceptions.Timeout:
            _logger.error("Zadarma API timeout")
            return {
                'uuid': self.uuid,
                'state': 'server_error',
                'credit': 0
            }
        except Exception as e:
            _logger.exception(f"Zadarma SMS exception: {e}")
            return {
                'uuid': self.uuid,
                'state': 'server_error',
                'credit': 0
            }
