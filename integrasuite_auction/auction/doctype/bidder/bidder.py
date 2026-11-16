# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Bidder(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.allowed_to_transact_with.allowed_to_transact_with import AllowedToTransactWith
		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
		from erpnext.selling.doctype.customer_credit_limit.customer_credit_limit import CustomerCreditLimit
		from erpnext.selling.doctype.sales_team.sales_team import SalesTeam
		from erpnext.selling.doctype.supplier_number_at_customer.supplier_number_at_customer import SupplierNumberAtCustomer
		from erpnext.utilities.doctype.portal_user.portal_user import PortalUser
		from frappe.types import DF

		account_manager: DF.Link | None
		accounts: DF.Table[PartyAccount]
		bidder_cid: DF.Data
		bidder_display_name: DF.Data | None
		bidder_group: DF.Link | None
		bidder_name: DF.Data
		bidder_type: DF.Literal["Company", "Individual", "Partnership"]
		companies: DF.Table[AllowedToTransactWith]
		contact_no: DF.Data | None
		country: DF.Link | None
		credit_limits: DF.Table[CustomerCreditLimit]
		customer_details: DF.Text | None
		customer_pos_id: DF.Data | None
		customer_primary_address: DF.Link | None
		customer_primary_contact: DF.Link | None
		default_bank_account: DF.Link | None
		default_commission_rate: DF.Float
		default_currency: DF.Link | None
		default_price_list: DF.Link | None
		default_sales_partner: DF.Link | None
		disabled: DF.Check
		dn_required: DF.Check
		dzongkhag: DF.Link | None
		email_id: DF.ReadOnly | None
		first_name: DF.ReadOnly | None
		gender: DF.Link | None
		gewog: DF.Link | None
		image: DF.AttachImage | None
		industry: DF.Link | None
		is_frozen: DF.Check
		is_internal_customer: DF.Check
		language: DF.Link | None
		last_name: DF.ReadOnly | None
		lead_name: DF.Link | None
		loyalty_program: DF.Link | None
		loyalty_program_tier: DF.Data | None
		market_segment: DF.Link | None
		mobile_no: DF.ReadOnly | None
		naming_series: DF.Literal["BID-.YYYY.-"]
		opportunity_name: DF.Link | None
		payment_terms: DF.Link | None
		portal_users: DF.Table[PortalUser]
		primary_address: DF.TextEditor | None
		prospect_name: DF.Link | None
		represents_company: DF.Link | None
		sales_team: DF.Table[SalesTeam]
		so_required: DF.Check
		supplier_numbers: DF.Table[SupplierNumberAtCustomer]
		tax_category: DF.Link | None
		tax_id: DF.Data | None
		tax_withholding_category: DF.Link | None
		tax_withholding_group: DF.Link | None
		territory: DF.Link | None
		village: DF.Link | None
		website: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.bidder_display_name = (
				f"{self.bidder_name or self.name} "
				f"({self.bidder_cid or 'No CID'})"
			)
