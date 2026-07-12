import streamlit as st

def validate_payment_fields(method, fields):
    if method == "Card":
        name = fields.get("name", "")
        card_number = fields.get("card_number", "")
        expiry = fields.get("expiry", "")
        cvv = fields.get("cvv", "")
        if not name or not card_number or not expiry or not cvv:
            return False, "Please fill all card details."
        if len(card_number) != 16 or not card_number.isdigit():
            return False, "Invalid card number."
        if len(cvv) != 3 or not cvv.isdigit():
            return False, "Invalid CVV."
        return True, ""
    if method == "UPI":
        upi_id = fields.get("upi_id", "")
        if not upi_id or "@" not in upi_id:
            return False, "Invalid UPI ID."
        return True, ""
    if method == "Net Banking":
        bank = fields.get("bank_name", "")
        if not bank:
            return False, "Select a bank."
        return True, ""
    if method == "Wallet":
        wallet = fields.get("wallet_type", "")
        if not wallet:
            return False, "Select a wallet."
        return True, ""
    return False, "Select a payment method."

def render_payment_notice():
    st.info("Complete payment to confirm your ticket.")
