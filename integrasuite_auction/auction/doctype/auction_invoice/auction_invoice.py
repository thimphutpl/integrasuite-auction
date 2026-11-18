# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_company_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.query_builder import DocType
from frappe.query_builder.functions import Abs, Sum
from frappe.utils import cint, flt

from erpnext.accounts.party import CROSS_PARTY_FIELD_NO_MAP, get_due_date
from erpnext.controllers.accounts_controller import _get_taxes_and_charges, merge_taxes
from erpnext.controllers.mapper import get_qty_already_mapped
from erpnext.controllers.selling_controller import SellingController

from integrasuite_auction.auction.doctype.lot_card.lot_card import LotCard

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}

class AuctionInvoice(SellingController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.item_wise_tax_detail.item_wise_tax_detail import ItemWiseTaxDetail
		from erpnext.accounts.doctype.pricing_rule_detail.pricing_rule_detail import PricingRuleDetail
		from erpnext.accounts.doctype.sales_taxes_and_charges.sales_taxes_and_charges import SalesTaxesandCharges
		from erpnext.selling.doctype.sales_team.sales_team import SalesTeam
		from erpnext.stock.doctype.packed_item.packed_item import PackedItem
		from frappe.types import DF
		from integrasuite_auction.auction.doctype.auction_invoice_item.auction_invoice_item import AuctionInvoiceItem

		additional_discount_percentage: DF.Float
		address_display: DF.TextEditor | None
		amended_from: DF.Link | None
		amount_eligible_for_commission: DF.Currency
		apply_discount_on: DF.Literal["", "Grand Total", "Net Total"]
		auto_repeat: DF.Link | None
		base_discount_amount: DF.Currency
		base_grand_total: DF.Currency
		base_in_words: DF.Data | None
		base_net_total: DF.Currency
		base_rounded_total: DF.Currency
		base_rounding_adjustment: DF.Currency
		base_total: DF.Currency
		base_total_taxes_and_charges: DF.Currency
		bidder: DF.Link | None
		bidder_cid: DF.Data | None
		bidder_name: DF.Data | None
		commission_amount: DF.Currency
		commission_payment_mode: DF.Literal["", "Cash", "Bank transfer"]
		commission_percent: DF.Percent
		commission_rate: DF.Float
		company: DF.Link
		company_address: DF.Link | None
		company_address_display: DF.TextEditor | None
		company_contact_person: DF.Link | None
		contact_display: DF.SmallText | None
		contact_email: DF.Data | None
		contact_mobile: DF.SmallText | None
		contact_no: DF.Data | None
		contact_person: DF.Link | None
		conversion_rate: DF.Float
		cost_center: DF.Link | None
		country: DF.Data | None
		currency: DF.Link
		customer_address: DF.Link | None
		customer_group: DF.Link | None
		delivery_trip: DF.Link | None
		disable_rounded_total: DF.Check
		discount_amount: DF.Currency
		dispatch_address: DF.TextEditor | None
		dispatch_address_name: DF.Link | None
		driver: DF.Link | None
		driver_name: DF.Data | None
		dzongkhag: DF.Data | None
		excise_page: DF.Data | None
		gewog: DF.Data | None
		grand_total: DF.Currency
		group_same_items: DF.Check
		ignore_pricing_rule: DF.Check
		in_words: DF.Data | None
		incoterm: DF.Link | None
		installation_status: DF.Literal[None]
		instructions: DF.Text | None
		inter_company_reference: DF.Link | None
		is_internal_customer: DF.Check
		is_return: DF.Check
		issue_credit_note: DF.Check
		item_wise_tax_details: DF.Table[ItemWiseTaxDetail]
		items: DF.Table[AuctionInvoiceItem]
		language: DF.Link | None
		letter_head: DF.Link | None
		lot_card: DF.Link
		lr_date: DF.Date | None
		lr_no: DF.Data | None
		named_place: DF.Data | None
		naming_series: DF.Literal["AUC-INV-.YYYY.-"]
		net_total: DF.Currency
		other_charges_calculation: DF.TextEditor | None
		packed_items: DF.Table[PackedItem]
		per_billed: DF.Percent
		per_installed: DF.Percent
		per_returned: DF.Percent
		plc_conversion_rate: DF.Float
		po_date: DF.Date | None
		po_no: DF.SmallText | None
		posting_date: DF.Date
		posting_time: DF.Time
		price_list_currency: DF.Link | None
		pricing_rules: DF.Table[PricingRuleDetail]
		print_without_amount: DF.Check
		project: DF.Link | None
		represents_company: DF.Link | None
		rounded_total: DF.Currency
		rounding_adjustment: DF.Currency
		sales_partner: DF.Link | None
		sales_team: DF.Table[SalesTeam]
		scan_barcode: DF.Data | None
		select_print_heading: DF.Link | None
		selling_price_list: DF.Link | None
		series_copy: DF.Literal["AUC-INV-.YYYY.-"]
		set_target_warehouse: DF.Link | None
		set_warehouse: DF.Link | None
		shipping_address: DF.TextEditor | None
		shipping_address_name: DF.Link | None
		shipping_rule: DF.Link | None
		status: DF.Literal["", "Draft", "To Bill", "Partially Billed", "Completed", "Return", "Return Issued", "Cancelled", "Closed"]
		tax_category: DF.Link | None
		taxes: DF.Table[SalesTaxesandCharges]
		taxes_and_charges: DF.Link | None
		tc_name: DF.Link | None
		terms: DF.TextEditor | None
		territory: DF.Link | None
		title: DF.Data | None
		total: DF.Currency
		total_commission: DF.Currency
		total_net_weight: DF.Float
		total_qty: DF.Float
		total_taxes_and_charges: DF.Currency
		transporter: DF.Link | None
		transporter_name: DF.Data | None
		unloading_charges: DF.Currency
		utm_campaign: DF.Link | None
		utm_content: DF.Data | None
		utm_medium: DF.Link | None
		utm_source: DF.Link | None
		vehicle_no: DF.Data | None
		village: DF.Data | None
	# end: auto-generated types

    
	@frappe.whitelist()
	def fetch_lot_card_items(self):
		self.check_permission("write")

		if self.docstatus != 0:
			frappe.throw("Items can only be fetched into a draft invoice.")

		if not self.lot_card:
			frappe.throw("Please select a Lot Card.")

		lot = frappe.get_doc("Lot Card", self.lot_card)
		lot.check_permission("read")

		if lot.docstatus != 1 or lot.get("is_return"):
			frappe.throw("Please select a submitted, non-return Lot Card.")

		if not lot.items:
			frappe.throw("The selected Lot Card has no items.")

		if self.company and self.company != lot.company:
			frappe.throw("Lot Card and Auction Invoice must have the same company.")

		self.company = lot.company
		self.currency = lot.currency
		self.conversion_rate = lot.conversion_rate
		self.cost_center = lot.cost_center
		self.ignore_pricing_rule = 1

		self.set("items", [])

		copy_fields = (
			"item_code",
			"item_name",
			"description",
			"qty",
			"uom",
			"stock_uom",
			"conversion_factor",
			"warehouse",
			"weight_per_unit",
			"weight_uom",
			"cost_center",
			"project",
		
		)

		for source in lot.items:
			row = self.append("items", {
				field: source.get(field)
				for field in copy_fields
			})

			row.lot_card_item = source.name
			row.rate = flt(source.rate)
			row.amount = flt(row.qty) * flt(row.rate)

			row.stock_qty = (
				flt(row.qty) * flt(row.conversion_factor)
			)

	def validate_whole_lot(self):
		if not self.lot_card:
			frappe.throw("Please select a Lot Card.")

		# Serialize invoice validation for this Lot Card so two users
		# cannot submit separate invoices for the same lot concurrently.
		frappe.db.sql(
			"select name from `tabLot Card` where name = %s for update",
			(self.lot_card,),
		)

		lot = frappe.get_doc("Lot Card", self.lot_card)
		lot.check_permission("read")

		if lot.docstatus != 1 or lot.get("is_return"):
			frappe.throw("Lot Card must be submitted and must not be a return.")

		if self.company != lot.company:
			frappe.throw("Lot Card and Auction Invoice must have the same company.")

		if self.currency != lot.currency:
			frappe.throw("Lot Card and Auction Invoice must use the same currency.")

		existing_invoice = frappe.db.get_value(
			"Auction Invoice",
			{
				"lot_card": self.lot_card,
				"docstatus": 1,
				"name": ["!=", self.name],
			},
			"name",
		)

		if existing_invoice:
			frappe.throw(
				f"This Lot Card is already invoiced through {existing_invoice}."
			)

		source_rows = {row.name: row for row in lot.items}
		seen = set()

		if not source_rows or len(self.items) != len(source_rows):
			frappe.throw("The invoice must contain every Lot Card item.")

		for row in self.items:
			source = source_rows.get(row.lot_card_item)

			if not source or row.lot_card_item in seen:
				frappe.throw(
					f"Row {row.idx}: Invalid or duplicate Lot Card item reference."
				)

			seen.add(row.lot_card_item)

			for field in ("item_code", "uom", "stock_uom", "warehouse"):
				if row.get(field) != source.get(field):
					frappe.throw(
						f"Row {row.idx}: {field.replace('_', ' ').title()} "
						"must match the Lot Card."
					)

			for field in ("qty", "conversion_factor", "rate"):
				precision = row.precision(field)
				if flt(row.get(field), precision) != flt(
					source.get(field), precision
				):
					frappe.throw(
						f"Row {row.idx}: {field.replace('_', ' ').title()} "
						"cannot be changed."
					)

	def validate(self):
		# self.validate_whole_lot()
		self.validate_posting_time()
		super().validate()
		self.validate_whole_lot()
		self.calculate_item_amounts()#added by me for calculating item amounts
		# self.validate_references()
		#self.set_status()
		# self.so_required()
		#self.validate_proj_cust()
		#self.check_sales_order_on_hold_or_close("against_sales_order")
		self.validate_warehouse()
		self.validate_uom_is_integer("stock_uom", "stock_qty") 
		self.validate_uom_is_integer("uom", "qty")
		# self.validate_with_previous_doc()
		#self.set_serial_and_batch_bundle_from_pick_list()

		#from erpnext.stock.doctype.packed_item.packed_item import make_packing_list

		#make_packing_list(self)
		self.update_current_stock()

		# if not self.installation_status:
		# 	self.installation_status = "Not Installed"

		#self.validate_against_stock_reservation_entries()
		self.reset_default_field_value("set_warehouse", "items", "warehouse")


	def get_auction_account(self, fieldname):
		return LotCard.get_auction_account(self, fieldname)
	
	def validate_warehouse(self):
		super().validate_warehouse()

		for d in self.get_item_list():
			if not d["warehouse"] and frappe.get_cached_value("Item", d["item_code"], "is_stock_item") == 1:
				frappe.throw(_("Warehouse required for stock Item {0}").format(d["item_code"]))

	def update_current_stock(self):
		if not (self.get("_action") and self._action != "update_after_submit"):
			return

		warehouse_item_codes = {}
		for d in self.get("items") + self.get("packed_items"):
			warehouse_item_codes.setdefault(d.warehouse, set()).add(d.item_code)

		if not warehouse_item_codes:
			return

		bin_map = {}
		for warehouse, item_codes in warehouse_item_codes.items():
			for b in frappe.get_all(
				"Bin",
				filters={"item_code": ["in", item_codes], "warehouse": warehouse},
				fields=["item_code", "actual_qty", "projected_qty"],
			):
				bin_map[(b.item_code, warehouse)] = b

		for d in self.get("items"):
			bin_data = bin_map.get((d.item_code, d.warehouse))
			d.actual_qty = bin_data.actual_qty if bin_data else None

		for d in self.get("packed_items"):
			bin_data = bin_map.get((d.item_code, d.warehouse))
			if bin_data:
				d.actual_qty = flt(bin_data.actual_qty)
				d.projected_qty = flt(bin_data.projected_qty)

	def on_submit(self):
		#self.validate_packed_qty()
		#self.update_pick_list_status()
		# self.create_consignment_gl_entries()#Added by me for creating consignment gl entries
		# self.create_commission_gl_entries()
		self.create_auction_gl_entries()

		# Check for Approving Authority
		frappe.get_cached_doc("Authorization Control").validate_approving_authority(
			self.doctype, self.company, self.base_grand_total, self
		)

		# update delivered qty in sales order
		#self.update_prevdoc_status()
		#self.update_billing_status()

		# if not self.is_return:
		# 	#self.check_credit_limit()
		# 	pass
		# elif self.issue_credit_note:
		# 	# self.make_return_invoice()
		# 	pass

		# for table_name in ["items", "packed_items"]:
		# 	if not self.get(table_name):
		# 		continue

		# 	self.make_bundle_for_sales_purchase_return(table_name)
		# 	self.make_bundle_using_old_serial_batch_fields(table_name)

		#self.validate_standalone_serial_nos_customer()
		#self.update_stock_reservation_entries()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		self.update_stock_ledger()
		#self.validate_produced_serial_nos_against_reservation()
		#self.make_gl_entries()
		#self.repost_future_sle_and_gle()

	def on_cancel(self):
		super().on_cancel()
		# self.cancel_consignment_gl_entries()#Added by me for cancelling consignment gl entries
		# self.cancel_commission_gl_entries()
		self.cancel_auction_gl_entries()
		#self.check_sales_order_on_hold_or_close("against_sales_order")
		#self.check_next_docstatus()

		#self.update_prevdoc_status()
		#self.update_billing_status()

		#self.update_stock_reservation_entries()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		self.update_stock_ledger()

		#self.cancel_packing_slips()
		#self.update_pick_list_status()

		#self.make_gl_entries_on_cancel()
		#self.repost_future_sle_and_gle()
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Payment Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)

		#self.delete_auto_created_batches()

	# Added by me for calculating item amounts
	# def calculate_item_amounts(self):
	# 	total_amount = 0

	# 	for row in self.items:
	# 		qty = flt(row.qty)
	# 		rate = flt(row.rate)

	# 		row.amount = flt(qty * rate, row.precision("amount"))
	# 		total_amount += row.amount

	# 	self.total = flt(total_amount, self.precision("total"))
	# 	self.net_total = flt(total_amount, self.precision("net_total"))
	def calculate_item_amounts(self):
		company_currency = frappe.get_cached_value(
			"Company", self.company, "default_currency"
		)

		if (
			self.currency != company_currency
			or flt(self.conversion_rate) != 1
		):
			frappe.throw(
				"This auction posting supports company currency only."
			)

		# This calculation does not include separate taxes or discounts.
		if (
			self.get("taxes")
			or flt(self.get("discount_amount"))
			or flt(self.get("additional_discount_percentage"))
		):
			frappe.throw(
				"Separate taxes and discounts are not supported "
				"in this auction calculation."
			)

		if flt(self.commission_percent) < 0:
			frappe.throw("Commission percentage cannot be negative.")

		if flt(self.unloading_charges) < 0:
			frappe.throw("Unloading charges cannot be negative.")

		total_amount = 0
		total_qty = 0

		for row in self.items:
			row.amount = flt(
				flt(row.qty) * flt(row.rate),
				row.precision("amount"),
			)

			row.base_rate = flt(row.rate)
			row.base_amount = row.amount
			row.net_rate = flt(row.rate)
			row.net_amount = row.amount
			row.base_net_rate = flt(row.rate)
			row.base_net_amount = row.amount

			row.stock_qty = (
				flt(row.qty) * flt(row.conversion_factor)
			)

			total_amount += row.amount
			total_qty += flt(row.qty)

		self.total = flt(
			total_amount, self.precision("total")
		)
		self.net_total = self.total
		self.base_total = self.total
		self.base_net_total = self.total
		self.total_qty = total_qty

		if self.total <= 0:
			frappe.throw("Lot Card item value must be greater than zero.")

		self.commission_amount = flt(
			self.total * flt(self.commission_percent) / 100,
			self.precision("commission_amount"),
		)

		self.unloading_charges = flt(
			self.unloading_charges,
			self.precision("unloading_charges"),
		)

		self.grand_total = flt(
        self.total,
        self.precision("grand_total"),
)
		self.base_grand_total = self.grand_total

		# Keep rounded totals consistent with the custom calculation.
		self.disable_rounded_total = 1
		self.rounding_adjustment = 0
		self.base_rounding_adjustment = 0
		self.rounded_total = self.grand_total
		self.base_rounded_total = self.grand_total

	# def create_consignment_gl_entries(self):
	# 	from erpnext.accounts.general_ledger import make_gl_entries
	# 	from erpnext.accounts.utils import get_fiscal_year

	# 	amount = sum(
	# 		flt(row.qty) * flt(row.rate)
	# 		for row in self.items
	# 	)
	# 	amount = flt(amount, self.precision("grand_total"))

	# 	if amount <= 0:
	# 		frappe.throw(
	# 			"Auction Invoice stock-out value must be greater than zero."
	# 		)

	# 	# Use the existing Lot Card helper.
	# 	asset_account = self.get_auction_account(
	# 		"consignment_asset_account"
	# 	)
	# 	control_account = self.get_auction_account(
	# 		"consignment_control_account"
	# 	)

	# 	fiscal_year = get_fiscal_year(
	# 		self.posting_date,
	# 		company=self.company,
	# 	)[0]

	# 	gl_entries = [
	# 		# Debit Consignment Control.
	# 		{
	# 			"account": control_account,
	# 			"debit": amount,
	# 			"debit_in_account_currency": amount,
	# 			"credit": 0,
	# 			"credit_in_account_currency": 0,
	# 			"against": asset_account,
	# 		},
	# 		# Credit Consignment Asset.
	# 		{
	# 			"account": asset_account,
	# 			"debit": 0,
	# 			"debit_in_account_currency": 0,
	# 			"credit": amount,
	# 			"credit_in_account_currency": amount,
	# 			"against": control_account,
	# 		},
	# 	]

	# 	for entry in gl_entries:
	# 		entry.update({
	# 			"company": self.company,
	# 			"posting_date": self.posting_date,
	# 			"voucher_type": self.doctype,
	# 			"voucher_no": self.name,
	# 			"fiscal_year": fiscal_year,
	# 			"cost_center": self.cost_center,
	# 			"is_opening": "No",
	# 		})

	# 	make_gl_entries(
	# 		[frappe._dict(entry) for entry in gl_entries],
	# 		merge_entries=False,
	# 	)
	
	# def cancel_consignment_gl_entries(self):
	# 	from erpnext.accounts.general_ledger import make_reverse_gl_entries

	# 	accounts = [
	# 		self.get_auction_account("consignment_asset_account"),
	# 		self.get_auction_account("consignment_control_account"),
	# 	]

	# 	gl_entries = frappe.get_all(
	# 		"GL Entry",
	# 		filters={
	# 			"voucher_type": self.doctype,
	# 			"voucher_no": self.name,
	# 			"company": self.company,
	# 			"account": ["in", accounts],
	# 			"is_cancelled": 0,
	# 		},
	# 		fields=["*"],
	# 	)

	# 	if gl_entries:
	# 		make_reverse_gl_entries(gl_entries)

	# def create_commission_gl_entries(self):
	# 	from erpnext.accounts.general_ledger import make_gl_entries
	# 	from erpnext.accounts.utils import get_fiscal_year

	# 	commission_amount = flt(
	# 		flt(self.grand_total) * flt(self.commission_percent) / 100,
	# 		self.precision("commission_amount"),
	# 	)

	# 	if commission_amount <= 0:
	# 		return

	# 	if not self.bidder:
	# 		frappe.throw("Please select a Bidder.")

	# 	payment_mode = self.commission_payment_mode

	# 	if payment_mode == "Cash":
	# 		debit_account = self.get_auction_account("cash_account")
	# 		is_credit_commission = False

	# 	elif payment_mode == "Bank Transfer":
	# 		debit_account = self.get_auction_account("bank_account")
	# 		is_credit_commission = False

	# 	else:
	# 		debit_account = self.get_auction_account(
	# 			"bidder_receivable_account"
	# 		)
	# 		is_credit_commission = True

	# 	income_account = self.get_auction_account(
	# 		"commission_income_account"
	# 	)

	# 	fiscal_year = get_fiscal_year(
	# 		self.posting_date,
	# 		company=self.company,
	# 	)[0]

	# 	debit_entry = {
	# 		"account": debit_account,
	# 		"debit": commission_amount,
	# 		"debit_in_account_currency": commission_amount,
	# 		"credit": 0,
	# 		"credit_in_account_currency": 0,
	# 		"against": income_account,
	# 	}

	# 	# Include bidder details whenever receivables are used.
	# 	if is_credit_commission:
	# 		debit_entry.update({
	# 			"party_type": "Bidder",
	# 			"party": self.bidder,
	# 		})

	# 	gl_entries = [
	# 		debit_entry,
	# 		{
	# 			"account": income_account,
	# 			"debit": 0,
	# 			"debit_in_account_currency": 0,
	# 			"credit": commission_amount,
	# 			"credit_in_account_currency": commission_amount,
	# 			"against": debit_account,
	# 		},
	# 	]

	# 	for entry in gl_entries:
	# 		entry.update({
	# 			"company": self.company,
	# 			"posting_date": self.posting_date,
	# 			"voucher_type": self.doctype,
	# 			"voucher_no": self.name,
	# 			"fiscal_year": fiscal_year,
	# 			"cost_center": self.cost_center,
	# 			"is_opening": "No",
	# 		})

	# 	make_gl_entries(
	# 		[frappe._dict(entry) for entry in gl_entries],
	# 		merge_entries=False,
	# 	)

	# def cancel_commission_gl_entries(self):
	# 	from erpnext.accounts.general_ledger import make_reverse_gl_entries

	# 	if self.commission_payment_mode == "Cash":
	# 		debit_account = self.get_auction_account("cash_account")

	# 	elif self.commission_payment_mode == "Bank Transfer":
	# 		debit_account = self.get_auction_account("bank_account")

	# 	else:
	# 		debit_account = self.get_auction_account(
	# 			"bidder_receivable_account"
	# 		)

	# 	income_account = self.get_auction_account(
	# 		"commission_income_account"
	# 	)

	# 	gl_entries = frappe.get_all(
	# 		"GL Entry",
	# 		filters={
	# 			"voucher_type": self.doctype,
	# 			"voucher_no": self.name,
	# 			"company": self.company,
	# 			"account": ["in", [debit_account, income_account]],
	# 			"is_cancelled": 0,
	# 		},
	# 		fields=["*"],
	# 	)

	# 	if gl_entries:
	# 		make_reverse_gl_entries(gl_entries)
    
	def create_auction_gl_entries(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		from erpnext.accounts.utils import get_fiscal_year

		if not self.bidder:
			frappe.throw("Please select a Bidder.")

		if not self.lot_card:
			frappe.throw("Please select a Lot Card.")

		lot = frappe.get_doc("Lot Card", self.lot_card)

		if not lot.grower_id:
			frappe.throw("Please select a Grower on the Lot Card.")

		warehouse_account = self.get_auction_account(
			"warehouse_account"
		)
		receivable_account = self.get_auction_account(
			"bidder_receivable_account"
		)

		company_currency = frappe.get_cached_value(
			"Company", self.company, "default_currency"
		)

		if (
			self.currency != company_currency
			or flt(self.conversion_rate) != 1
		):
			frappe.throw(
				"This auction posting supports company currency only."
			)

		item_value = flt(
			self.total, self.precision("total")
		)
		commission = flt(
			self.commission_amount,
			self.precision("commission_amount"),
		)
		unloading = flt(
			self.unloading_charges,
			self.precision("unloading_charges"),
		)
		grower_charges = flt(
			commission + unloading,
			self.precision("grand_total"),
		)

		if item_value <= 0:
			frappe.throw("Item value must be greater than zero.")

		if commission < 0 or unloading < 0:
			frappe.throw(
				"Commission and unloading charges cannot be negative."
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

		entries = []

		def add_entry(account, debit=0, credit=0, **extra):
			account_currency = frappe.db.get_value(
				"Account", account, "account_currency"
			)

			if account_currency != company_currency:
				frappe.throw(
					f"Account {account} must use {company_currency}."
				)

			entries.append(frappe._dict({
				**common,
				"account": account,
				"account_currency": account_currency,
				"debit": debit,
				"debit_in_account_currency": debit,
				"credit": credit,
				"credit_in_account_currency": credit,
				**extra,
			}))

		# Bidder pays only the full item value.
		add_entry(
			receivable_account,
			debit=item_value,
			party_type="Bidder",
			party=self.bidder,
			against=warehouse_account,
		)

		# Clear the full Lot Card stock value.
		add_entry(
			warehouse_account,
			credit=item_value,
			against=receivable_account,
		)

		if grower_charges:
			grower_payable_account = self.get_auction_account(
				"grower_payable_account"
			)

			charge_accounts = []

			if commission:
				income_account = self.get_auction_account(
					"commission_income_account"
				)
				charge_accounts.append(income_account)

			if unloading:
				unloading_account = self.get_auction_account(
					"unloading_charges_payable_account"
				)
				charge_accounts.append(unloading_account)

			# Deduct charges from the grower's entitlement.
			add_entry(
				grower_payable_account,
				debit=grower_charges,
				party_type="Grower",
				party=lot.grower_id,
				against=", ".join(charge_accounts),
			)

			if commission:
				add_entry(
					income_account,
					credit=commission,
					against=grower_payable_account,
				)

			if unloading:
				add_entry(
					unloading_account,
					credit=unloading,
					against=grower_payable_account,
				)

		make_gl_entries(entries, merge_entries=False)

	def cancel_auction_gl_entries(self):
		from erpnext.accounts.general_ledger import make_reverse_gl_entries

		entries = frappe.get_all(
			"GL Entry",
			filters={
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"company": self.company,
				"is_cancelled": 0,
			},
			fields=["*"],
		)

		if entries:
			make_reverse_gl_entries(entries)

def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context

	list_context = get_list_context(context)
	list_context.update(
		{
			"show_sidebar": True,
			"show_search": True,
			"no_breadcrumbs": True,
			"title": _("Shipments"),
			"list_template": "templates/includes/list/list.html",
		}
	)
	return list_context

@frappe.whitelist()
def make_auction_invoice(source_name, target_doc=None):
    if not frappe.has_permission("Auction Invoice", "create"):
        frappe.throw(
            "You do not have permission to create an Auction Invoice.",
            frappe.PermissionError,
        )

    lot = frappe.get_doc("Lot Card", source_name)
    lot.check_permission("read")

    if lot.docstatus != 1 or lot.get("is_return"):
        frappe.throw(
            "Please select a submitted, non-return Lot Card."
        )

    existing_invoice = frappe.db.get_value(
        "Auction Invoice",
        {
            "lot_card": lot.name,
            "docstatus": 1,
        },
        "name",
    )

    if existing_invoice:
        frappe.throw(
            f"This Lot Card is already invoiced through {existing_invoice}."
        )

    invoice = frappe.new_doc("Auction Invoice")
    invoice.lot_card = lot.name
    invoice.fetch_lot_card_items()

    return invoice