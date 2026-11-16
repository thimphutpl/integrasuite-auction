// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.stock");

cur_frm.cscript.tax_table = "Purchase Taxes and Charges";

erpnext.accounts.taxes.setup_tax_filters("Purchase Taxes and Charges");
erpnext.accounts.taxes.setup_tax_validations("Lot Card");
erpnext.buying.setup_buying_controller();


frappe.ui.form.on("Lot Card", {
    refresh(frm) {
        frm.set_query("item_code", "items", () => ({
            filters: {
                custom_is_auction_item: 1
            }
        }));
    },

    onload_post_render(frm) {
        frm.set_query("item_code", "items", () => ({
            filters: {
                custom_is_auction_item: 1
            }
        }));
    }
});

frappe.ui.form.on("Lot Card", {
	setup: (frm) => {
		frm.set_query("taxes_and_charges", function () {
			return {
				filters: { company: frm.doc.company },
			};
		});
	},
	onload: function (frm) {
		erpnext.queries.setup_queries(frm, "Warehouse", function () {
			return erpnext.queries.warehouse(frm.doc);
		});
	},


	company: function (frm) {
		frm.trigger("toggle_display_account_head");
		erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
	},

	toggle_display_account_head: function (frm) {
		var enabled = erpnext.is_perpetual_inventory_enabled(frm.doc.company);
		frm.fields_dict["items"].grid.set_column_disp(["cost_center"], enabled);
	},
});

erpnext.stock.PurchaseReceiptController = class PurchaseReceiptController extends (
	erpnext.buying.BuyingController
) {
	setup(doc) {
		this.setup_accounting_dimension_triggers();
		this.setup_posting_date_time_check();
		super.setup(doc);

		this.frm.set_query("expense_account", "items", () => {
			return {
				query: "erpnext.controllers.queries.get_expense_account",
				filters: {
					company: this.frm.doc.company,
					disabled: 0,
				},
			};
		});
	}
    apply_pricing_rule(item, calculate_taxes_and_totals) {
    // Lot Card does not use ERPNext Pricing Rules.
    if (this.frm.doc.doctype === "Lot Card") {
        if (calculate_taxes_and_totals) {
            this.calculate_taxes_and_totals();
        }
        return;
    }

    return super.apply_pricing_rule(item, calculate_taxes_and_totals);
}

	refresh() {
		//var me = this;
		super.refresh();
		
		erpnext.accounts.ledger_preview.show_accounting_ledger_preview(this.frm);
		erpnext.accounts.ledger_preview.show_stock_ledger_preview(this.frm);

		if (this.frm.doc.docstatus > 0) {
			this.show_stock_ledger();
			//removed for temporary
			this.show_general_ledger();

				}	}

	items_add(doc, cdt, cdn) {
		const row = frappe.get_doc(cdt, cdn);
		const field_copy = ["expense_account", "cost_center"];
		if (doc.project) {
			frappe.model.set_value(cdt, cdn, "project", doc.project);
		} else {
			field_copy.push("project");
		}
		this.frm.script_manager.copy_from_first_row("items", row, field_copy);
	}
};

// frappe.provide("erpnext.buying");
