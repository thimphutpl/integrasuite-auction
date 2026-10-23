# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PartyRegistration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		auction_location: DF.Link
		auction_season: DF.Data
		branch: DF.Link
		mode_of_payment: DF.Link | None
		party: DF.DynamicLink
		party_cidpassportaadharcardetc: DF.Data | None
		party_name: DF.Data | None
		party_type: DF.Literal["Grower", "Bidder"]
		reference_date: DF.Date | None
		reference_number: DF.Data | None
		registration_date: DF.Date
		registration_fee: DF.Currency
		remarks: DF.SmallText | None
		security_deposit: DF.Currency
	# end: auto-generated types

	pass
