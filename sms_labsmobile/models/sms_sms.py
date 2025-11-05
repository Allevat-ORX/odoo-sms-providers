# -*- coding: utf-8 -*-
from odoo import fields, models, _
import logging
import requests
import base64
import json

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    labsmobile_message_id = fields.Char(
        string="LabsMobile Message ID",
        readonly=True,
        copy=False
    )

    def _is_sent_with_labsmobile(self):
        """Check if SMS should be sent via LabsMobile."""
        iap_account = self.env['iap.account']._get_sms_account()
        return bool(
            iap_account and
            iap_account.labsmobile_username and
            iap_account.labsmobile_token and
            iap_account.provider == 'sms_api_labsmobile'
        )

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        """Override to use LabsMobile for SMS sending."""
        if not self._is_sent_with_labsmobile():
            return super()._send(
                unlink_failed=unlink_failed,
                unlink_sent=unlink_sent,
                raise_exception=raise_exception
            )

        # Send via LabsMobile
        iap_account = self.env['iap.account']._get_sms_account()

        for sms in self:
            try:
                success = sms._send_labsmobile_sms(iap_account)
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
                _logger.error(f"LabsMobile SMS error for {sms.number}: {e}")
                sms.write({'state': 'error', 'failure_type': 'sms_server'})
                if raise_exception:
                    raise
                if unlink_failed:
                    sms.unlink()

        return True

    def _send_labsmobile_sms(self, iap_account):
        """Send single SMS via LabsMobile API. Returns True if successful, False otherwise."""
        self.ensure_one()

        if not self.number:
            _logger.error(f"SMS {self.id}: No phone number provided")
            return False

        url = f"{iap_account.labsmobile_base_url}/json/send"
        auth_string = base64.b64encode(
            f"{iap_account.labsmobile_username}:{iap_account.labsmobile_token}".encode()
        ).decode()

        headers = {
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/json'
        }

        # LabsMobile JSON format
        payload = {
            "message": self.body,
            "recipient": [
                {"msisdn": self.number.replace('+', '')}  # LabsMobile expects numbers without +
            ]
        }

        try:
            _logger.info(f"Sending SMS to {self.number} via LabsMobile")

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # LabsMobile response format: {"code": "0", "message": "Successfully sent"}
            if data.get('code') == '0' or data.get('code') == 0:
                _logger.info(f"SMS sent successfully to {self.number}")
                # Store message ID if available
                if data.get('messageId'):
                    self.write({'labsmobile_message_id': str(data['messageId'])})
                return True
            else:
                error_msg = data.get('message', 'Unknown error')
                _logger.error(f"LabsMobile API error: {error_msg}")
                return False

        except requests.exceptions.Timeout:
            _logger.error(f"LabsMobile API timeout for {self.number}")
            return False
        except Exception as e:
            _logger.exception(f"LabsMobile SMS exception for {self.number}: {e}")
            return False
