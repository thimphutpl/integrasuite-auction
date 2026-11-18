// Copyright (c) 2026, ttpl and contributors
// For license information, please see license.txt

//cur_frm.add_fetch("customer", "tax_id", "tax_id");

//cur_frm.cscript.tax_table = "Sales Taxes and Charges";

//frappe.provide("erpnext.stock");
//frappe.provide("erpnext.stock.delivery_note");
frappe.provide("erpnext.accounts.dimensions");

erpnext.accounts.taxes.setup_tax_filters("Sales Taxes and Charges");
erpnext.accounts.taxes.setup_tax_validations("Auction Invoice");
erpnext.sales_common.setup_selling_controller();

// frappe.ui.form.on("Auction Invoice", {
//     setup(frm) {
//         frm.set_query("item_code", "items", function () {
//             return {
//                 filters: {
//                     custom_is_auction_item: 1
//                 }
//             };
//         });
//     }
// });

// function calculate_auction_invoice_totals(frm) {
//     let total = 0;

//     (frm.doc.items || []).forEach(function(item) {
//         item.amount = flt(item.qty) * flt(item.rate);
//         total += item.amount;
//     });

//     frm.refresh_field("items");

//     frm.set_value("total", total);
//     frm.set_value("net_total", total);
//     frm.set_value("grand_total", total);

//     let commission = total * flt(frm.doc.commission_percent) / 100;

//     frm.set_value("commission_amount", commission);
// }
function calculate_auction_invoice_totals(frm) {
    // Do not recalculate submitted or cancelled invoices.
    if (frm.doc.docstatus !== 0) return;

    let total = 0;
    let total_qty = 0;

    (frm.doc.items || []).forEach((item) => {
        item.amount = flt(
            flt(item.qty) * flt(item.rate),
            precision("amount", item)
        );

        total += item.amount;
        total_qty += flt(item.qty);
    });

    total = flt(total, precision("total", frm.doc));

    const commission = flt(
        total * flt(frm.doc.commission_percent) / 100,
        precision("commission_amount", frm.doc)
    );

    const unloading = flt(
        frm.doc.unloading_charges,
        precision("unloading_charges", frm.doc)
    );

    // const grand_total = flt(
    //     total + commission + unloading,
    //     precision("grand_total", frm.doc)
    // );
    const grand_total = flt(
    total,
    precision("grand_total", frm.doc));

    frm.refresh_field("items");

    return frm.set_value({
        total: total,
        net_total: total,
        total_qty: total_qty,
        commission_amount: commission,
        grand_total: grand_total
    });
}

frappe.ui.form.on("Auction Invoice Item", {
    qty: function(frm) {
        calculate_auction_invoice_totals(frm);
    },

    rate: function(frm) {
        calculate_auction_invoice_totals(frm);
    }
});

frappe.ui.form.on("Auction Invoice", {
    commission_percent(frm) {
        return calculate_auction_invoice_totals(frm);
    },

    unloading_charges(frm) {
        return calculate_auction_invoice_totals(frm);
    }
});


frappe.ui.form.on("Auction Invoice", {
    refresh(frm) {
        if (frm.is_new() && frm.doc.lot_card) {
            calculate_auction_invoice_totals(frm);}

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("General Ledger"), function () {
                frappe.set_route("query-report", "General Ledger", {
                    company: frm.doc.company,
                    voucher_no: frm.doc.name
                });
            }, __("View"));
        }
    }
});


// frappe.ui.form.on("Auction Invoice Item", {
// 	expense_account: function (frm, dt, dn) {
// 		var d = locals[dt][dn];
// 		frm.update_in_all_rows("items", "expense_account", d.expense_account);
// 	},
// });

frappe.ui.form.on("Auction Invoice", {
    company(frm) {
        erpnext.accounts.dimensions.update_dimension(
            frm, frm.doctype
        );
    }
});
// frappe.ui.form.on("Auction Invoice", {
// 	setup: function (frm) {
// 		if (frm.doc.company) {
// 			frm.trigger("unhide_account_head");
// 		}
// 	},

// 	company: function (frm) {
// 		frm.trigger("unhide_account_head");
// 		erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
// 	},

// 	unhide_account_head: function (frm) {
// 		// unhide expense_account and cost_center if perpetual inventory is enabled in the company
// 		var aii_enabled = erpnext.is_perpetual_inventory_enabled(frm.doc.company);
// 		frm.fields_dict["items"].grid.set_column_disp(["expense_account", "cost_center"], aii_enabled);
// 	},
// });

frappe.ui.form.on("Auction Invoice", {
    setup(frm) {
        frm.set_query("lot_card", () => ({
            filters: {
                docstatus: 1,
                is_return: 0,
                ...(frm.doc.company
                    ? { company: frm.doc.company }
                    : {})
            }
        }));
    },

    async lot_card(frm) {
        // Prevent old items remaining against a different source.
        frm.clear_table("items");
        frm.refresh_field("items");

        if (frm.doc.lot_card) {
            await frm.call({
                method: "fetch_lot_card_items",
                freeze: true,
                freeze_message: __("Fetching complete Lot Card")
            });

            frm.refresh_fields();
        }

        await calculate_auction_invoice_totals(frm);
        frm.dirty();
    },

    refresh(frm) {
        const grid = frm.fields_dict.items.grid;

        grid.cannot_add_rows = true;
        grid.cannot_delete_rows = true;

        [
            "item_code",
            "qty",
            "rate",
            "uom",
            "stock_uom",
            "conversion_factor",
            "warehouse",
            "lot_card_item"
        ].forEach((fieldname) => {
            grid.update_docfield_property(
                fieldname, "read_only", 1
            );
        });

        // grid.update_docfield_property("rate", "read_only", 0);
        grid.refresh();

        frm.set_df_property("scan_barcode", "hidden", 1);
    }
});