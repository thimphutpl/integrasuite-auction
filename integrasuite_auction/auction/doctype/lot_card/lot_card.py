# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LotCard(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.stock.doctype.purchase_receipt_item.purchase_receipt_item import PurchaseReceiptItem
		from frappe.types import DF

		activity: DF.Data | None
		amended_from: DF.Link | None
		cidpassportaadharcardetc: DF.Data | None
		contact_no: DF.Data | None
		dzongkhag: DF.Link | None
		gewog: DF.Link | None
		grower_name: DF.Data | None
		items: DF.Table[PurchaseReceiptItem]
		location: DF.Link | None
		lot_card_number: DF.Data
		net_total: DF.Currency
		posting_date: DF.Date | None
		remarks: DF.SmallText | None
		total: DF.Currency
		total_net_weight: DF.Float
		total_quantity: DF.Float
		village: DF.Link | None
	# end: auto-generated types

	pass
