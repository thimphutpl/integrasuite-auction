# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Grower(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.allowed_to_transact_with.allowed_to_transact_with import AllowedToTransactWith
		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
		from erpnext.buying.doctype.customer_number_at_supplier.customer_number_at_supplier import CustomerNumberAtSupplier
		from erpnext.utilities.doctype.portal_user.portal_user import PortalUser
		from frappe.types import DF

		accounts: DF.Table[PartyAccount]
		allow_purchase_invoice_creation_without_purchase_order: DF.Check
		allow_purchase_invoice_creation_without_purchase_receipt: DF.Check
		companies: DF.Table[AllowedToTransactWith]
		contact_number: DF.Data | None
		country: DF.Link | None
		customer_numbers: DF.Table[CustomerNumberAtSupplier]
		default_bank_account: DF.Link | None
		default_currency: DF.Link | None
		default_price_list: DF.Link | None
		disabled: DF.Check
		dzongkhag: DF.Link | None
		email_id: DF.ReadOnly | None
		gender: DF.Link | None
		gewog: DF.Link | None
		grower_cid: DF.Data | None
		grower_display_name: DF.Data | None
		grower_name: DF.Data
		hold_type: DF.Literal["", "All", "Invoices", "Payments"]
		image: DF.AttachImage | None
		is_frozen: DF.Check
		is_internal_supplier: DF.Check
		is_transporter: DF.Check
		language: DF.Link | None
		mobile_no: DF.ReadOnly | None
		naming_series: DF.Literal["GRO-.YYYY.-"]
		on_hold: DF.Check
		payment_terms: DF.Link | None
		portal_users: DF.Table[PortalUser]
		prevent_pos: DF.Check
		prevent_rfqs: DF.Check
		primary_address: DF.TextEditor | None
		release_date: DF.Date | None
		represents_company: DF.Link | None
		supplier_details: DF.Text | None
		supplier_group: DF.Link | None
		supplier_primary_address: DF.Link | None
		supplier_primary_contact: DF.Link | None
		supplier_type: DF.Literal["Company", "Individual", "Partnership"]
		tax_category: DF.Link | None
		tax_id: DF.Data | None
		tax_withholding_category: DF.Link | None
		tax_withholding_group: DF.Link | None
		village: DF.Link | None
		warn_pos: DF.Check
		warn_rfqs: DF.Check
		website: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.grower_display_name = (
			f"{self.grower_name or self.name} "
			f"({self.grower_cid or 'No CID'})"
		)
