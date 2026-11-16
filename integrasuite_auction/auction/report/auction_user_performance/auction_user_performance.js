
frappe.query_reports["Auction User Performance"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
        },
        {
            fieldname: "user",
            label: __("Invoice Creator"),
            fieldtype: "Link",
            options: "User",
        },
        {
            fieldname: "currency",
            label: __("Currency"),
            fieldtype: "Link",
            options: "Currency",
        },
    ],
};
