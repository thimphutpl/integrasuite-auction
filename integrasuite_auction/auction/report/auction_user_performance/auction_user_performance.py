
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})

    columns = get_columns()
    data = get_data(filters)

    chart = get_chart(data)
    report_summary = get_summary(data)

    return columns, data, None, chart, report_summary



def get_columns():
    return [
        {
            "label": _("Invoice Creator"),
            "fieldname": "owner",
            "fieldtype": "Link",
            "options": "User",
            "width": 200,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "full_name",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": _("Cash Sales"),
            "fieldname": "cash_sales",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 130,
        },
        {
            "label": _("Cash Commission"),
            "fieldname": "cash_commission",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        },
        {
            "label": _("Credit Sales"),
            "fieldname": "credit_sales",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 130,
        },
        {
            "label": _("Credit Commission"),
            "fieldname": "credit_commission",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150,
        },
        {
            "label": _("Bank Transfer Sales"),
            "fieldname": "bank_sales",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150,
        },
        {
            "label": _("Bank Transfer Commission"),
            "fieldname": "bank_commission",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 170,
        },
        {
            "label": _("Total Sales"),
            "fieldname": "total_sales",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        },
        {
            "label": _("Total Commission"),
            "fieldname": "total_commission",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150,
        },
        {
            "label": _("Total Invoices"),
            "fieldname": "total_invoices",
            "fieldtype": "Int",
            "width": 110,
        },
    ]

def get_data(filters):
    conditions = ["si.docstatus = 1"]
    values = {}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.to_date

    if filters.get("user"):
        conditions.append("u.name = %(user)s")
        values["user"] = filters.user

    if filters.get("currency"):
        conditions.append("si.currency = %(currency)s")
        values["currency"] = filters.currency

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            u.name AS owner,
            u.full_name,
            si.currency,

            -- Cash
            COALESCE(SUM(
                CASE
                    WHEN si.commission_payment_mode = 'Cash'
                    THEN si.grand_total ELSE 0
                END
            ), 0) AS cash_sales,

            COALESCE(SUM(
                CASE
                    WHEN si.commission_payment_mode = 'Cash'
                    THEN si.commission_amount ELSE 0
                END
            ), 0) AS cash_commission,

            -- Credit (blank payment mode)
            COALESCE(SUM(
                CASE
                    WHEN IFNULL(si.commission_payment_mode, '') = ''
                    THEN si.grand_total ELSE 0
                END
            ), 0) AS credit_sales,

            COALESCE(SUM(
                CASE
                    WHEN IFNULL(si.commission_payment_mode, '') = ''
                    THEN si.commission_amount ELSE 0
                END
            ), 0) AS credit_commission,

            -- Bank Transfer
            COALESCE(SUM(
                CASE
                    WHEN si.commission_payment_mode = 'Bank transfer'
                    THEN si.grand_total ELSE 0
                END
            ), 0) AS bank_sales,

            COALESCE(SUM(
                CASE
                    WHEN si.commission_payment_mode = 'Bank transfer'
                    THEN si.commission_amount ELSE 0
                END
            ), 0) AS bank_commission,

            -- Overall totals
            COALESCE(SUM(si.grand_total), 0) AS total_sales,

            COALESCE(SUM(si.commission_amount), 0)
                AS total_commission,

            COUNT(si.name) AS total_invoices

        FROM `tabUser` u

        LEFT JOIN `tabAuction Invoice` si
            ON si.owner = u.name
            AND {where_clause}

        WHERE u.enabled = 1
          AND u.user_type = 'System User'

        GROUP BY
            u.name,
            u.full_name,
            si.currency

        ORDER BY
            total_commission DESC,
            total_sales DESC
        """,
        values,
        as_dict=True,
    )

def get_chart(data):
    # Do not compare monetary values from different currencies.
    currencies = {row.currency for row in data}

    if not data or len(currencies) != 1:
        return None

    return {
        "data": {
            "labels": [
                row.full_name or row.owner
                for row in data[:10]
            ],
            "datasets": [
                {
                    "name": _("Total Commission"),
                    "values": [
                        flt(row.total_commission)
                        for row in data[:10]
                    ],
                },
                {
                    "name": _("Total Sales"),
                    "values": [
                        flt(row.total_sales)
                        for row in data[:10]
                    ],
                },
            ],
        },
        "type": "bar",
        "fieldtype": "Currency",
    }


def get_summary(data):
    currencies = {row.currency for row in data}

    if not data or len(currencies) != 1:
        return []

    currency = next(iter(currencies))

    return [
        {
            "value": sum(row.total_invoices for row in data),
            "indicator": "Blue",
            "label": _("Total Invoices"),
            "datatype": "Int",
        },
        {
            "value": sum(flt(row.total_sales) for row in data),
            "indicator": "Blue",
            "label": _("Total Sales"),
            "datatype": "Currency",
            "currency": currency,
        },
        {
            "value": sum(flt(row.total_commission) for row in data),
            "indicator": "Green",
            "label": _("Total Commission"),
            "datatype": "Currency",
            "currency": currency,
        },
    ]
