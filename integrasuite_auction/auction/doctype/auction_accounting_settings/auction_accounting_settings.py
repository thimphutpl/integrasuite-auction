# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AuctionAccountingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank_account: DF.Link
		bidder_receivable_account: DF.Link
		cash_account: DF.Link
		commission_income_account: DF.Link
		company: DF.Link
		consignment_asset_account: DF.Link
		consignment_control_account: DF.Link
		grower_advances_account: DF.Link
		registration_fee_income_account: DF.Link
		security_deposit_liability_account: DF.Link
	# end: auto-generated types

	pass
