# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json

import frappe
from frappe import _, throw
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Abs, CombineDatetime, Sum
from frappe.utils import cint, flt, get_datetime, getdate, nowdate
from pypika import functions as fn

import erpnext
from erpnext.accounts.utils import get_account_currency
from erpnext.assets.doctype.asset.asset import get_asset_account, is_cwip_accounting_enabled
from erpnext.controllers.accounts_controller import merge_taxes
from erpnext.controllers.buying_controller import BuyingController
from erpnext.controllers.mapper import get_qty_already_mapped
from erpnext.stock import get_warehouse_account
from erpnext.stock.doctype.delivery_note.delivery_note import make_inter_company_transaction
from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import StockReservation
from erpnext.stock.serial_batch_bundle import (
	SerialBatchCreation,
	get_batches_from_bundle,
	get_serial_nos_from_bundle,
)

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class LotCard(BuyingController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from integrasuite_auction.auction.doctype.lot_card_item.lot_card_item import LotCardItem

		activity: DF.Data | None
		advance_amount: DF.Currency
		advance_payment_mode: DF.Link | None
		amended_from: DF.Link | None
		apply_discount_on: DF.Literal["", "Grand Total", "Net Total"]
		apply_putaway_rule: DF.Check
		base_grand_total: DF.Currency
		branch: DF.Link
		company: DF.Link | None
		contact_no: DF.Data | None
		conversion_rate: DF.Float
		cost_center: DF.Link | None
		country: DF.Data | None
		currency: DF.Link | None
		dzongkhag: DF.Data | None
		fiscal_year: DF.Link | None
		gewog: DF.Data | None
		grower_advance_je: DF.Link | None
		grower_cid: DF.Data | None
		grower_id: DF.Link
		grower_name: DF.Data | None
		ignore_pricing_rule: DF.Check
		is_return: DF.Check
		is_subcontracted: DF.Check
		items: DF.Table[LotCardItem]
		location: DF.Link | None
		lot_card_number: DF.Data
		net_total: DF.Currency
		pay_grower_advance: DF.Check
		per_billed: DF.Percent
		plc_conversion_rate: DF.Float
		posting_date: DF.Date
		posting_time: DF.Time
		remarks: DF.SmallText | None
		shipping_rule: DF.Link | None
		total: DF.Currency
		total_net_weight: DF.Float
		total_quantity: DF.Float
		village: DF.Data | None
	# end: auto-generated types

	def get_auction_account(self, fieldname):
		settings = frappe.get_single("Auction Accounting Settings")
		account = settings.get(fieldname)

		if not account:
			frappe.throw(
				f"Please configure {fieldname.replace('_', ' ').title()} "
				"in Auction Accounting Settings."
			)

		account_details = frappe.db.get_value(
			"Account",
			account,
			["company", "is_group", "disabled"],
			as_dict=True,
		)

		if not account_details:
			frappe.throw(f"Account {account} does not exist.")

		if account_details.company != self.company:
			frappe.throw(
				f"Account {account} does not belong to company {self.company}."
			)

		if account_details.is_group or account_details.disabled:
			frappe.throw(
				f"Account {account} must be an enabled ledger account."
			)

		return account

	def validate(self):
		self.validate_posting_time()
		#self.validate_posting_date_with_po()
		super().validate()
		self.calculate_lot_totals()

		if self._action != "submit":
			self.set_status()

		
		self.validate_uom_is_integer()
		
		if getdate(self.posting_date) > getdate(nowdate()):
			throw(_("Posting Date cannot be future date"))

		self.get_current_stock()
		self.reset_default_field_value("set_warehouse", "items", "warehouse")
		self.reset_default_field_value("rejected_warehouse", "items", "rejected_warehouse")
		self.reset_default_field_value("set_from_warehouse", "items", "from_warehouse")

	def validate_uom_is_integer(self):
		super().validate_uom_is_integer("uom", ["qty", "received_qty"], "Lot Card Item")
		super().validate_uom_is_integer("stock_uom", "stock_qty", "Lot Card Item")

	def on_submit(self):
		super().on_submit()

		# Check for Approving Authority
		frappe.get_cached_doc("Authorization Control").validate_approving_authority(
			self.doctype, self.company, self.base_grand_total
		)

		
		self.update_stock_ledger()
		self.create_lot_card_gl_entries()
		self.create_grower_advance_je()
	
	def on_cancel(self):
		self.cancel_lot_card_gl_entries()
		# Cancel the Journal Entry for the grower advance if the Lot Card is cancelled.
		self.cancel_grower_advance_je()
		super().on_cancel()

	
		self.update_stock_ledger()
	
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)
		

	def before_cancel(self):
		super().before_cancel()
		#self.remove_amount_difference_with_purchase_invoice()

	# def calculate_lot_totals(self):
	# 	total_quantity = 0
	# 	total_net_weight = 0

	# 	for row in self.items:
	# 		qty = flt(row.qty)
	# 		stock_qty = qty * flt(row.conversion_factor)

	# 		row.stock_qty = stock_qty

	# 		# Assumes weight_per_unit is the weight per Stock UOM.
	# 		row.total_weight = flt(
	# 			stock_qty * flt(row.weight_per_unit),
	# 			row.precision("total_weight"),
	# 		)

	# 		total_quantity += qty
	# 		total_net_weight += row.total_weight

	# 	self.total_quantity = flt(
	# 		total_quantity,
	# 		self.precision("total_quantity"),
	# 	)
	# 	self.total_net_weight = flt(
	# 		total_net_weight,
	# 		self.precision("total_net_weight"),
	# 	)
    #Added by me 
	def calculate_taxes_and_totals(self):
		if self.get("taxes") is None:
			self.set("taxes", [])

		super().calculate_taxes_and_totals()


	def update_status(self, status):
		self.set_status(update=True, status=status)
		self.notify_update()
		clear_doctype_notifications(self)

	def create_grower_advance_je(self):
		if not self.pay_grower_advance:
			return

		# Prevent duplicate Journal Entries.
		if self.grower_advance_je:
			existing_je = frappe.get_doc(
				"Journal Entry", self.grower_advance_je
			)

			if existing_je.docstatus in (0, 1):
				return

			frappe.throw(
				f"Grower Advance Journal Entry {self.grower_advance_je} "
				"has been cancelled."
			)

		if flt(self.advance_amount) <= 0:
			frappe.throw("Please enter a valid Grower Advance Amount.")

		if not self.advance_payment_mode:
			frappe.throw("Please select the Advance Payment Mode.")

		# Read the account from Auction Accounting Settings.
		grower_payable_account = self.get_auction_account(
			"grower_payable_account"
		)

		# Select Cash/Bank through the chosen Mode of Payment.
		payment_account = frappe.db.get_value(
			"Mode of Payment Account",
			{
				"parent": self.advance_payment_mode,
				"company": self.company,
			},
			"default_account",
		)

		if not payment_account:
			frappe.throw(
				f"No account is configured for Mode of Payment "
				f"{self.advance_payment_mode} in company {self.company}."
			)

		account_type = frappe.db.get_value(
			"Account", payment_account, "account_type"
		)

		if account_type not in ("Cash", "Bank"):
			frappe.throw(
				f"{payment_account} must be a Cash or Bank account."
			)

		amount = flt(self.advance_amount)

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.company = self.company
		je.posting_date = self.posting_date or frappe.utils.nowdate()
		je.user_remark = f"Grower advance against Lot Card {self.name}"

		# Debit the selected grower's payable.
		je.append("accounts", {
			"account": grower_payable_account,
			"party_type": "Grower",
			"party": self.grower_id,
			"debit_in_account_currency": amount,
			"debit": amount,
		})

		# Credit the selected Cash/Bank account.
		je.append("accounts", {
			"account": payment_account,
			"credit_in_account_currency": amount,
			"credit": amount,
		})

		# Save as Draft.
		je.insert(ignore_permissions=True)

		self.db_set("grower_advance_je", je.name)		
	# Cancel the Grower Advance Journal Entry if it exists and is submitted.
	def cancel_grower_advance_je(self):
		if not self.grower_advance_je:
			return

		je = frappe.get_doc(
			"Journal Entry", self.grower_advance_je
		)

		if je.docstatus == 1:
			je.cancel()

		elif je.docstatus == 0:
			frappe.throw(
				f"Grower Advance Journal Entry {je.name} is still in Draft."
			)
	

	def create_lot_card_gl_entries(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		from erpnext.accounts.utils import get_fiscal_year

		company_currency = frappe.get_cached_value(
			"Company", self.company, "default_currency"
		)

		if (
			self.currency != company_currency
			or flt(self.conversion_rate) != 1
		):
			frappe.throw(
				"This Lot Card posting supports company currency only."
			)

		amount = flt(
			sum(
				flt(row.qty) * flt(row.rate)
				for row in self.items
			),
			self.precision("base_grand_total"),
		)

		if amount <= 0:
			frappe.throw("Lot Card item value must be greater than zero.")

		warehouse_account = self.get_auction_account(
			"warehouse_account"
		)
		grower_payable_account = self.get_auction_account(
			"grower_payable_account"
		)

		# Amounts below use company currency for both GL and account currency.
		for account in (warehouse_account, grower_payable_account):
			account_currency = frappe.db.get_value(
				"Account", account, "account_currency"
			)

			if account_currency != company_currency:
				frappe.throw(
					f"Account {account} must use {company_currency}."
				)

		fiscal_year = get_fiscal_year(
			self.posting_date,
			company=self.company,
		)[0]

		common = {
			"company": self.company,
			"posting_date": self.posting_date,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"fiscal_year": fiscal_year,
			"cost_center": self.cost_center,
			"is_opening": "No",
		}

		gl_entries = [
			frappe._dict({
				**common,
				"account": warehouse_account,
				"debit": amount,
				"debit_in_account_currency": amount,
				"credit": 0,
				"credit_in_account_currency": 0,
				"against": grower_payable_account,
			}),
			frappe._dict({
				**common,
				"account": grower_payable_account,
				"party_type": "Grower",
				"party": self.grower_id,
				"debit": 0,
				"debit_in_account_currency": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"against": warehouse_account,
			}),
		]

		make_gl_entries(gl_entries, merge_entries=False)


	def cancel_lot_card_gl_entries(self):
		from erpnext.accounts.general_ledger import make_reverse_gl_entries

		make_reverse_gl_entries(
			voucher_type=self.doctype,
			voucher_no=self.name,
		)

	@frappe.whitelist()
	def calculate_lot_totals(self):
		total_quantity = 0
		total_net_weight = 0
		total_amount = 0

		for row in self.items:
			qty = flt(row.qty)
			rate = flt(row.rate)

			# Item amount = quantity × rate.
			row.amount = flt(
				qty * rate,
				row.precision("amount"),
			)

			row.stock_qty = (
				qty * flt(row.conversion_factor)
			)

			row.total_weight = flt(
				row.stock_qty * flt(row.weight_per_unit),
				row.precision("total_weight"),
			)

			total_quantity += qty
			total_net_weight += row.total_weight
			total_amount += row.amount

		self.total_quantity = flt(
			total_quantity,
			self.precision("total_quantity"),
		)

		self.total_net_weight = flt(
			total_net_weight,
			self.precision("total_net_weight"),
		)

		self.total = flt(
			total_amount,
			self.precision("total"),
		)

		self.net_total = self.total

		# Current flow uses company currency with exchange rate 1.
		self.base_grand_total = flt(
			self.total * flt(self.conversion_rate),
			self.precision("base_grand_total"),
		)

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.stock_entry_type = "Material Transfer"
		target.purpose = "Material Transfer"
		target.set_missing_values()

	def update_item(source_doc, target_doc, source_parent):
		if source_doc.serial_and_batch_bundle:
			serial_nos = get_serial_nos_from_bundle(source_doc.serial_and_batch_bundle)
			if serial_nos:
				serial_nos = "\n".join(serial_nos)

			batches = get_batches_from_bundle(source_doc.serial_and_batch_bundle)
			if batches:
				if len(batches) == 1:
					target_doc.use_serial_batch_fields = 1
					target_doc.batch_no = next(iter(batches))
				elif not serial_nos:
					cls_obj = SerialBatchCreation(
						{
							"type_of_transaction": "Outward",
							"serial_and_batch_bundle": source_doc.serial_and_batch_bundle,
							"item_code": source_doc.item_code,
							"warehouse": source_doc.warehouse,
						}
					)

					cls_obj.duplicate_package()

					target_doc.serial_and_batch_bundle = cls_obj.serial_and_batch_bundle

			if serial_nos:
				target_doc.use_serial_batch_fields = 1
				target_doc.serial_no = serial_nos

	doclist = get_mapped_doc(
		"Lot Card",
		source_name,
		{
			"Lot Card": {
				"doctype": "Stock Entry",
			},
			"Lot Card Item": {
				"doctype": "Stock Entry Detail",
				"field_map": {
					"warehouse": "s_warehouse",
					"parent": "reference_purchase_receipt",
					"batch_no": "batch_no",
				},
				"postprocess": update_item,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist


