import frappe
from frappe import _
from frappe.utils import flt, formatdate, getdate

# Roles that may see every user's invoices. Replace "Auction Manager"
# with your actual manager role.
MANAGER_ROLES = {"System Manager", "Auction Manager"}

DETAILED = "Detailed"
BY_USER = "Summary by User"

INVOICE_FIELDS = [
    "name",
    "posting_date",
    "lot_card",
    "bidder",
    "bidder_name",
    "total_qty",
    "total",
    "commission_amount",
    "unloading_charges",
    "currency",
    "owner",
]


def execute(filters=None):
    filters = frappe._dict(filters or {})
    validate_filters(filters)

    company_currency = frappe.get_cached_value(
        "Company", filters.company, "default_currency"
    )
    can_view_all = user_can_view_all()

    invoices = get_invoices(filters, can_view_all, company_currency)
    users = aggregate_by_user(invoices)

    if filters.get("view") == BY_USER:
        columns = get_user_columns()
        data = users
    else:
        columns = get_invoice_columns()
        data = invoices

    chart = get_chart(invoices, company_currency)
    report_summary = get_report_summary(invoices, company_currency)

    return columns, data, None, chart, report_summary


# --------------------------------------------------------------------------
# Validation and permissions
# --------------------------------------------------------------------------

def validate_filters(filters):
    if not filters.company:
        frappe.throw(_("Please select a Company."))

    if not filters.from_date or not filters.to_date:
        frappe.throw(_("Please select From Date and To Date."))

    if getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("From Date cannot be after To Date."))


def user_can_view_all():
    user = frappe.session.user
    if user == "Administrator":
        return True
    return bool(MANAGER_ROLES & set(frappe.get_roles(user)))


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

def get_invoices(filters, can_view_all, company_currency):
    invoice_filters = {
        "company": filters.company,
        "docstatus": 1,
        "posting_date": ["between", [filters.from_date, filters.to_date]],
    }

    # Ownership is enforced here, never trusted from the browser.
    if can_view_all:
        if filters.get("created_by"):
            invoice_filters["owner"] = filters.created_by
    else:
        invoice_filters["owner"] = frappe.session.user

    for fieldname in ("bidder", "lot_card"):
        if filters.get(fieldname):
            invoice_filters[fieldname] = filters.get(fieldname)

    # get_list applies document-level permissions on top of the filters.
    rows = frappe.get_list(
        "Auction Invoice",
        filters=invoice_filters,
        fields=INVOICE_FIELDS,
        order_by="posting_date desc, creation desc",
        page_length=0,
    )

    full_names = get_full_names({row.owner for row in rows})

    for row in rows:
        row.currency = row.currency or company_currency
        row.owner_name = full_names.get(row.owner) or row.owner
        row.grower_net = (
            flt(row.total)
            - flt(row.commission_amount)
            - flt(row.unloading_charges)
        )
        row.commission_percent = percent(row.commission_amount, row.total)

    return rows


def get_full_names(users):
    if not users:
        return {}

    # Reading names of users who already appear in the permitted data.
    return {
        d.name: d.full_name
        for d in frappe.get_all(
            "User",
            filters={"name": ["in", list(users)]},
            fields=["name", "full_name"],
        )
    }


def aggregate_by_user(invoices):
    grouped = {}

    for row in invoices:
        entry = grouped.setdefault(
            row.owner,
            frappe._dict(
                owner=row.owner,
                owner_name=row.owner_name,
                invoice_count=0,
                total_qty=0.0,
                total=0.0,
                commission_amount=0.0,
                unloading_charges=0.0,
                grower_net=0.0,
                currency=row.currency,
            ),
        )
        entry.invoice_count += 1
        entry.total_qty += flt(row.total_qty)
        entry.total += flt(row.total)
        entry.commission_amount += flt(row.commission_amount)
        entry.unloading_charges += flt(row.unloading_charges)
        entry.grower_net += flt(row.grower_net)

    result = sorted(grouped.values(), key=lambda d: d.total, reverse=True)

    for entry in result:
        entry.avg_invoice_value = (
            entry.total / entry.invoice_count if entry.invoice_count else 0
        )
        entry.commission_percent = percent(entry.commission_amount, entry.total)

    return result


def percent(part, whole):
    return flt(part) / flt(whole) * 100 if flt(whole) else 0.0


# --------------------------------------------------------------------------
# Columns
# --------------------------------------------------------------------------

def currency_col(label, fieldname, width=140):
    return {
        "label": _(label),
        "fieldname": fieldname,
        "fieldtype": "Currency",
        "options": "currency",
        "width": width,
    }


def hidden_currency_col():
    return {
        "label": _("Currency"),
        "fieldname": "currency",
        "fieldtype": "Link",
        "options": "Currency",
        "hidden": 1,
    }


def get_invoice_columns():
    return [
        {"label": _("Posting Date"), "fieldname": "posting_date",
         "fieldtype": "Date", "width": 110},
        {"label": _("Auction Invoice"), "fieldname": "name",
         "fieldtype": "Link", "options": "Auction Invoice", "width": 190},
        {"label": _("Lot Card"), "fieldname": "lot_card",
         "fieldtype": "Link", "options": "Lot Card", "width": 170},
        {"label": _("Bidder"), "fieldname": "bidder",
         "fieldtype": "Link", "options": "Bidder", "width": 170},
        {"label": _("Bidder Name"), "fieldname": "bidder_name",
         "fieldtype": "Data", "width": 180},
        {"label": _("Total Quantity"), "fieldname": "total_qty",
         "fieldtype": "Float", "width": 120},
        currency_col("Sales Value", "total"),
        currency_col("Commission", "commission_amount", 130),
        {"label": _("Commission %"), "fieldname": "commission_percent",
         "fieldtype": "Percent", "width": 110},
        currency_col("Unloading Charges", "unloading_charges", 150),
        currency_col("Grower Net Before Advance", "grower_net", 200),
        {"label": _("Created By"), "fieldname": "owner",
         "fieldtype": "Link", "options": "User", "width": 200},
        {"label": _("Creator Name"), "fieldname": "owner_name",
         "fieldtype": "Data", "width": 160},
        hidden_currency_col(),
    ]


def get_user_columns():
    return [
        {"label": _("User"), "fieldname": "owner",
         "fieldtype": "Link", "options": "User", "width": 220},
        {"label": _("Name"), "fieldname": "owner_name",
         "fieldtype": "Data", "width": 180},
        {"label": _("Invoices"), "fieldname": "invoice_count",
         "fieldtype": "Int", "width": 90},
        {"label": _("Total Quantity"), "fieldname": "total_qty",
         "fieldtype": "Float", "width": 120},
        currency_col("Sales Value", "total"),
        currency_col("Avg Invoice Value", "avg_invoice_value", 150),
        currency_col("Commission", "commission_amount", 130),
        {"label": _("Commission %"), "fieldname": "commission_percent",
         "fieldtype": "Percent", "width": 110},
        currency_col("Unloading Charges", "unloading_charges", 150),
        currency_col("Grower Net Before Advance", "grower_net", 200),
        hidden_currency_col(),
    ]


# --------------------------------------------------------------------------
# Chart and summary
# --------------------------------------------------------------------------

def get_chart(invoices, currency):
    """Daily trend of sales value and commission."""
    if not invoices:
        return None

    daily = {}
    for row in invoices:
        day = daily.setdefault(
            getdate(row.posting_date), {"total": 0.0, "commission": 0.0}
        )
        day["total"] += flt(row.total)
        day["commission"] += flt(row.commission_amount)

    dates = sorted(daily)

    return {
        "data": {
            "labels": [formatdate(d) for d in dates],
            "datasets": [
                {"name": _("Sales Value"),
                 "values": [daily[d]["total"] for d in dates]},
                {"name": _("Commission"),
                 "values": [daily[d]["commission"] for d in dates]},
            ],
        },
        "type": "line",
        "fieldtype": "Currency",
        "options": "currency",
        "currency": currency,
    }


def get_report_summary(invoices, currency):
    def total_of(field):
        return sum(flt(row.get(field)) for row in invoices)

    sales = total_of("total")
    commission = total_of("commission_amount")

    return [
        {"label": _("Invoices"), "value": len(invoices),
         "datatype": "Int", "indicator": "Blue"},
        {"label": _("Sales Value"), "value": sales,
         "datatype": "Currency", "currency": currency, "indicator": "Green"},
        {"label": _("Commission Income"), "value": commission,
         "datatype": "Currency", "currency": currency, "indicator": "Blue"},
        {"label": _("Avg Commission %"), "value": percent(commission, sales),
         "datatype": "Percent", "indicator": "Blue"},
        {"label": _("Unloading Charges"), "value": total_of("unloading_charges"),
         "datatype": "Currency", "currency": currency, "indicator": "Orange"},
        {"label": _("Grower Net Before Advance"), "value": total_of("grower_net"),
         "datatype": "Currency", "currency": currency, "indicator": "Green"},
    ]