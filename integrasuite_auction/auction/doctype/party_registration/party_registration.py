
# # Copyright (c) 2026, ttpl and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.model.document import Document
# from frappe.utils import flt, getdate, today


# class PartyRegistration(Document):
#     # begin: auto-generated types
#     # This code is auto-generated. Do not modify anything in this block.

#     from typing import TYPE_CHECKING

#     if TYPE_CHECKING:
#         from frappe.types import DF

#         amended_from: DF.Link | None
#         auction_location: DF.Link
#         auction_season: DF.Data
#         branch: DF.Link
#         contact_no: DF.Data | None
#         country: DF.Data | None
#         dzongkhag: DF.Data | None
#         gewog: DF.Data | None
#         mode_of_payment: DF.Link | None
#         mode_of_paymentsecurity_deposit: DF.Link | None
#         naming_series: DF.Literal["REG-.YYYY.-.#####"]
#         party: DF.DynamicLink
#         party_cid: DF.Data | None
#         party_name: DF.Data | None
#         party_type: DF.Literal["Grower", "Bidder"]
#         reference_date: DF.Date | None
#         reference_date_copy: DF.Date | None
#         reference_number: DF.Data | None
#         reference_number_copy: DF.Data | None
#         registration_date: DF.Date
#         registration_fee: DF.Currency
#         registration_fee_je: DF.Link | None
#         remarks: DF.SmallText | None
#         security_deposit: DF.Currency
#         security_deposit_je: DF.Link | None
#         village: DF.Data | None
#     # end: auto-generated types

#     def validate(self):
#         self.fetch_party_details()

#     def fetch_party_details(self):

#         if not self.party or not self.party_type:
#             self.clear_party_details()
#             return

#         if self.party_type == "Grower":

#             if not frappe.db.exists("Grower", self.party):
#                 frappe.throw(f"Grower {self.party} does not exist.")

#             grower = frappe.get_doc("Grower", self.party)

#             # Fetch Grower details
#             self.party_name = grower.get("grower_name")
#             self.party_cid = grower.get("grower_cid")

#             # Fetch Grower address
#             self.country = grower.get("country")
#             self.dzongkhag = grower.get("dzongkhag")
#             self.gewog = grower.get("gewog")
#             self.village = grower.get("village")
#             self.contact_no = grower.get("contact_number")
#             self.image = grower.get("image")

#         elif self.party_type == "Bidder":

#             if not frappe.db.exists("Bidder", self.party):
#                 frappe.throw(f"Bidder {self.party} does not exist.")

#             bidder = frappe.get_doc("Bidder", self.party)

#             self.party_name = bidder.get("bidder_name")
#             self.party_cid = (
#                 bidder.get("cid")
#                 or bidder.get("passport_number")
#                 or bidder.get("aadhar_number")
#             )

#             # Clear Grower-specific address
#             self.country = None
#             self.dzongkhag = None
#             self.gewog = None
#             self.village = None
#             self.contact_no = None
#             self.image = None

#     def clear_party_details(self):
#         self.party_name = None
#         self.party_cid = None
#         self.country = None
#         self.dzongkhag = None
#         self.gewog = None
#         self.village = None
#         self.contact_no = None
#         self.image = None

#     def on_submit(self):
#         self.create_registration_fee_je()
#         self.create_security_deposit_je()

#     def on_cancel(self):
#         self.cancel_linked_je("registration_fee_je")
#         self.cancel_linked_je("security_deposit_je")

#     def get_company(self):
#         company = frappe.defaults.get_user_default("Company")

#         if not company:
#             frappe.throw(_("Please set your default Company."))

#         return company

#     def get_payment_account(self, mode_of_payment, company):
#         if not mode_of_payment:
#             frappe.throw(_("Please select a Mode of Payment."))

#         account = frappe.db.get_value(
#             "Mode of Payment Account",
#             {
#                 "parent": mode_of_payment,
#                 "company": company
#             },
#             "default_account"
#         )

#         if not account:
#             frappe.throw(
#                 _("No account configured for Mode of Payment {0} "
#                   "and Company {1}.").format(mode_of_payment, company)
#             )

#         return account

#     def get_chart_account(self, account_name, company):
#         account = frappe.db.get_value(
#             "Account",
#             {
#                 "account_name": account_name,
#                 "company": company,
#                 "is_group": 0,
#                 "disabled": 0
#             },
#             "name"
#         )

#         if not account:
#             frappe.throw(
#                 _("Account {0} not found or disabled for Company {1}.")
#                 .format(account_name, company)
#             )

#         return account

#     def create_journal_entry(
#         self,
#         amount,
#         mode_of_payment,
#         credit_account,
#         link_field,
#         description
#     ):
#         amount = flt(amount)

#         # Do not create a JE for zero or negative amounts.
#         if amount <= 0:
#             return

#         # Prevent duplicate Journal Entries.
#         existing_je = self.get(link_field)

#         if existing_je:
#             je_status = frappe.db.get_value(
#                 "Journal Entry", existing_je, "docstatus"
#             )

#             if je_status == 1:
#                 return

#             if je_status == 0:
#                 frappe.throw(
#                     _("Journal Entry {0} is already created but not submitted.")
#                     .format(existing_je)
#                 )

#         company = self.get_company()

#         debit_account = self.get_payment_account(
#             mode_of_payment, company
#         )

#         # Validate that both accounts belong to the same company.
#         for account in (debit_account, credit_account):
#             account_company = frappe.db.get_value(
#                 "Account", account, "company"
#             )
#             if account_company != company:
#                 frappe.throw(_("Account {0} does not belong to Company {1}.")
#                     .format(account, company)
#                 )

#         je = frappe.new_doc("Journal Entry")
#         je.voucher_type = "Journal Entry"
#         je.company = company
#         je.posting_date = getdate(
#             self.registration_date or today()
#         )
#         je.user_remark = (
#             f"{description} for Party Registration {self.name}. "
#             f"Party: {self.party_name} ({self.party_type}). "
#             f"Party ID: {self.party}."
#         )

#         # Debit: Bank or Cash account from Mode of Payment.
#         je.append("accounts", {
#             "account": debit_account,
#             "debit_in_account_currency": amount,
#             "credit_in_account_currency": 0
#         })

#         # Credit: Income or Liability account.
#         je.append("accounts", {
#             "account": credit_account,
#             "debit_in_account_currency": 0,
#             "credit_in_account_currency": amount
#         })

#         je.insert(ignore_permissions=True)
#         je.submit()

#         # Save the generated JE reference in Party Registration.
#         self.db_set(link_field, je.name, update_modified=False)

#         return je.name

#     def create_registration_fee_je(self):
#         amount = flt(self.registration_fee)

#         if amount <= 0:
#             return

#         company = self.get_company()

#         income_account = self.get_chart_account(
#             "Service", company
#         )

#         self.create_journal_entry(
#             amount=amount,
#             mode_of_payment=self.mode_of_payment,
#             credit_account=income_account,
#             link_field="registration_fee_je",
#             description="Registration Fee Receipt"
#         )

#     def create_security_deposit_je(self):
#         amount = flt(self.security_deposit)

#         if amount <= 0:
#             return

#         company = self.get_company()

#         liability_account = self.get_chart_account(
#             "Customer Advances", company
#         )

#         self.create_journal_entry(
#             amount=amount,
#             mode_of_payment=self.mode_of_paymentsecurity_deposit,
#             credit_account=liability_account,
#             link_field="security_deposit_je",
#             description="Security Deposit Receipt"
#         )

#     def cancel_linked_je(self, link_field):
#         je_name = self.get(link_field)

#         if not je_name:
#             return

#         je = frappe.get_doc("Journal Entry", je_name)

#         if je.docstatus == 1:
#             je.cancel()


# @frappe.whitelist()
# def get_party_details(party_type, party):

#     if party_type == "Grower":
#         grower = frappe.get_doc("Grower", party)

#         return {
#             "party_name": grower.get("grower_name"),
#             "party_cid": grower.get("grower_cid"),
#             "country": grower.get("country"),
#             "dzongkhag": grower.get("dzongkhag"),
#             "gewog": grower.get("gewog"),
#             "village": grower.get("village"),
#             "contact_no": grower.get("contact_number"),
#             "image": grower.get("image")
#         }

#     elif party_type == "Bidder":
#         bidder = frappe.get_doc("Bidder", party)

#         return {
#             "party_name": bidder.get("bidder_name"),
#             "party_cid": (
#                 bidder.get("cid")
#                 or bidder.get("passport_number")
#                 or bidder.get("aadhar_number")
#             ),
#             "country": None,
#             "dzongkhag": None,
#             "gewog": None,
#             "village": None,
#             "contact_no": None,
#             "image": None
#         }

#     frappe.throw("Invalid Party Type")



# Copyright (c) 2026, ttpl and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


DETAIL_FIELDS = (
    "party_name",
    "party_cid",
    "country",
    "dzongkhag",
    "gewog",
    "village",
    "contact_no",
)


def read_party_details(party_type, party):
    if party_type not in ("Grower", "Bidder"):
        frappe.throw(_("Invalid Party Type."))

    if not party:
        frappe.throw(_("Please select a Party."))

    doc = frappe.get_doc(party_type, party)
    doc.check_permission("read")

    if party_type == "Grower":
        return {
            "party_name": doc.get("grower_name"),
            "party_cid": doc.get("grower_cid"),
            "country": doc.get("country"),
            "dzongkhag": doc.get("dzongkhag"),
            "gewog": doc.get("gewog"),
            "village": doc.get("village"),
            "contact_no": doc.get("contact_number"),
            "image": doc.get("image"),
        }

    # Retains the Bidder field mapping from your original code.
    return {
        "party_name": doc.get("bidder_name"),
        "party_cid": (
            doc.get("cid")
            or doc.get("passport_number")
            or doc.get("aadhar_number")
        ),
        "country": None,
        "dzongkhag": None,
        "gewog": None,
        "village": None,
        "contact_no": None,
        "image": doc.get("image"),
    }


class PartyRegistration(Document):
    def validate(self):
        if not self.company:
            frappe.throw(_("Please select a Company."))

        if not self.party_type or not self.party:
            frappe.throw(_("Please select Party Type and Party."))

        details = read_party_details(self.party_type, self.party)

        for fieldname in DETAIL_FIELDS:
            self.set(fieldname, details.get(fieldname))

        for amount_field, payment_field in (
            ("registration_fee", "mode_of_payment"),
            ("security_deposit", "mode_of_paymentsecurity_deposit"),
        ):
            amount = flt(
                self.get(amount_field),
                self.precision(amount_field),
            )
            self.set(amount_field, amount)

            if amount < 0:
                frappe.throw(
                    _("{0} cannot be negative.").format(
                        self.meta.get_label(amount_field)
                    )
                )

            if amount > 0 and not self.get(payment_field):
                frappe.throw(
                    _("Please select {0}.").format(
                        self.meta.get_label(payment_field)
                    )
                )

    def on_submit(self):
        self.create_registration_fee_je()
        self.create_security_deposit_je()

    def on_cancel(self):
        self.cancel_linked_je("registration_fee_je")
        self.cancel_linked_je("security_deposit_je")

    def get_company(self):
        if not self.company:
            frappe.throw(_("Please select a Company."))

        return self.company

    def validate_account(self, account, payment_account=False):
        company = self.get_company()

        details = frappe.db.get_value(
            "Account",
            account,
            [
                "company",
                "is_group",
                "disabled",
                "account_type",
                "account_currency",
            ],
            as_dict=True,
        )

        if not details:
            frappe.throw(
                _("Account {0} does not exist.").format(account)
            )

        if details.company != company:
            frappe.throw(
                _("Account {0} does not belong to Company {1}.")
                .format(account, company)
            )

        if details.is_group or details.disabled:
            frappe.throw(
                _("Account {0} must be an enabled ledger account.")
                .format(account)
            )

        company_currency = frappe.get_cached_value(
            "Company", company, "default_currency"
        )

        if details.account_currency != company_currency:
            frappe.throw(
                _("Account {0} must use company currency {1}.")
                .format(account, company_currency)
            )

        if payment_account and details.account_type not in ("Cash", "Bank"):
            frappe.throw(
                _("Payment account {0} must be Cash or Bank.")
                .format(account)
            )

        return details

    def get_settings_account(self, fieldname):
        settings = frappe.get_single("Auction Accounting Settings")
        account = settings.get(fieldname)

        if not account:
            frappe.throw(
                _("Please configure {0} in Auction Accounting Settings.")
                .format(fieldname.replace("_", " ").title())
            )

        self.validate_account(account)
        return account

    def get_payment_account(self, mode_of_payment):
        if not mode_of_payment:
            frappe.throw(_("Please select a Mode of Payment."))

        account = frappe.db.get_value(
            "Mode of Payment Account",
            {
                "parent": mode_of_payment,
                "company": self.get_company(),
            },
            "default_account",
        )

        if not account:
            frappe.throw(
                _("No account configured for Mode of Payment {0} "
                  "and Company {1}.")
                .format(mode_of_payment, self.company)
            )

        self.validate_account(account, payment_account=True)
        return account

    def create_journal_entry(
        self,
        amount,
        mode_of_payment,
        credit_account,
        link_field,
        description,
        reference_number=None,
        reference_date=None,
    ):
        amount = flt(amount)

        if amount <= 0:
            return

        existing_je = self.get(link_field)

        if existing_je:
            existing = frappe.db.get_value(
                "Journal Entry",
                existing_je,
                ["docstatus", "company"],
                as_dict=True,
            )

            if (
                existing
                and existing.docstatus == 1
                and existing.company == self.company
            ):
                return existing_je

            frappe.throw(
                _("Journal Entry reference {0} already exists. "
                  "Please resolve its status before proceeding.")
                .format(existing_je)
            )

        company = self.get_company()
        debit_account = self.get_payment_account(mode_of_payment)
        self.validate_account(credit_account)

        if debit_account == credit_account:
            frappe.throw(
                _("Payment and credit accounts must be different.")
            )

        cost_center = None

        if self.get("branch"):
            cost_center = frappe.db.get_value(
                "Branch", self.branch, "cost_center"
            )

        if not cost_center:
            cost_center = frappe.get_cached_value(
                "Company", company, "cost_center"
            )

        if cost_center:
            cost_center_company = frappe.db.get_value(
                "Cost Center", cost_center, "company"
            )

            if cost_center_company != company:
                frappe.throw(
                    _("Cost Center {0} does not belong to Company {1}.")
                    .format(cost_center, company)
                )

        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = company
        je.posting_date = getdate(self.registration_date or today())

        je.user_remark = (
            f"{description} for Party Registration {self.name}. "
            f"Party: {self.party_name} ({self.party_type}). "
            f"Party ID: {self.party}."
        )

        if reference_number:
            je.cheque_no = reference_number
            je.cheque_date = getdate(
                reference_date or self.registration_date or today()
            )

        debit_row = {
            "account": debit_account,
            "debit_in_account_currency": amount,
            "credit_in_account_currency": 0,
        }

        credit_row = {
            "account": credit_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": amount,
        }

        if cost_center:
            debit_row["cost_center"] = cost_center
            credit_row["cost_center"] = cost_center

        je.append("accounts", debit_row)
        je.append("accounts", credit_row)

        # Preserves your existing automatic posting behaviour.
        je.insert(ignore_permissions=True)
        je.submit()

        self.db_set(link_field, je.name, update_modified=False)

        return je.name

    # def create_registration_fee_je(self):
    #     if flt(self.registration_fee) <= 0:
    #         return

    #     income_account = self.get_settings_account(
    #         "registration_fee_income_account"
    #     )

    #     self.create_journal_entry(
    #         amount=self.registration_fee,
    #         mode_of_payment=self.mode_of_payment,
    #         credit_account=income_account,
    #         link_field="registration_fee_je",
    #         description="Registration Fee Receipt",
    #         reference_number=self.reference_number,
    #         reference_date=self.reference_date,
    #     )

    # def create_security_deposit_je(self):
    #     if flt(self.security_deposit) <= 0:
    #         return

    #     liability_account = self.get_settings_account(
    #         "security_deposit_liability_account"
    #     )

    #     self.create_journal_entry(
    #         amount=self.security_deposit,
    #         mode_of_payment=self.mode_of_paymentsecurity_deposit,
    #         credit_account=liability_account,
    #         link_field="security_deposit_je",
    #         description="Security Deposit Receipt",
    #         reference_number=self.reference_number_copy,
    #         reference_date=self.reference_date_copy,
    #     )

    def create_registration_fee_je(self):
        if flt(self.registration_fee) <= 0:
            return

        income_account = self.get_settings_account(
            "registration_fee_income_account"
        )

        self.create_journal_entry(
            amount=self.registration_fee,
            mode_of_payment=self.mode_of_payment,
            credit_account=income_account,
            link_field="registration_fee_je",
            description="Registration Fee Receipt",
            reference_number=self.reference_number,
            reference_date=self.reference_date,
        )


    def create_security_deposit_je(self):
        if flt(self.security_deposit) <= 0:
            return

        liability_account = self.get_settings_account(
            "security_deposit_liability_account"
        )

        self.create_journal_entry(
            amount=self.security_deposit,
            mode_of_payment=self.mode_of_paymentsecurity_deposit,
            credit_account=liability_account,
            link_field="security_deposit_je",
            description="Security Deposit Receipt",
            reference_number=self.reference_number_copy,
            reference_date=self.reference_date_copy,
        )


    def cancel_linked_je(self, link_field):
        je_name = self.get(link_field)

        if not je_name:
            return

        je = frappe.get_doc("Journal Entry", je_name)

        if je.company != self.company:
            frappe.throw(
                _("Linked Journal Entry {0} belongs to another company.")
                .format(je.name)
            )

        if je.docstatus == 1:
            je.cancel()

        elif je.docstatus == 0:
            frappe.throw(
                _("Linked Journal Entry {0} is in Draft. "
                  "Resolve it before cancelling this registration.")
                .format(je.name)
            )


@frappe.whitelist()
def get_party_details(party_type, party):
    return read_party_details(party_type, party)