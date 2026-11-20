const auction_can_view_all =
    frappe.session.user === "Administrator" ||
    frappe.user.has_role("System Manager") ||
    frappe.user.has_role("Auction Manager");

frappe.query_reports["Auction User Performance"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "view",
            label: __("View"),
            fieldtype: "Select",
            options: ["Detailed", "Summary by User"].join("\n"),
            default: "Detailed"
        },
        {
            fieldname: "created_by",
            label: __("Created By"),
            fieldtype: "Link",
            options: "User",
            default: auction_can_view_all ? "" : frappe.session.user,
            read_only: !auction_can_view_all
        },
        {
            fieldname: "bidder",
            label: __("Bidder"),
            fieldtype: "Link",
            options: "Bidder"
        },
        {
            fieldname: "lot_card",
            label: __("Lot Card"),
            fieldtype: "Link",
            options: "Lot Card"
        }
    ],

    // Show a negative grower net in red so problem invoices stand out.
    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data && column.fieldname === "grower_net" && flt(data.grower_net) < 0) {
            value = `<span style="color: var(--red-600); font-weight: 600;">${value}</span>`;
        }
        return value;
    }
};