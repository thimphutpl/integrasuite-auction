// // Copyright (c) 2026, ttpl and contributors
// // For license information, please see license.txt

// // frappe.ui.form.on("Party Registration", {
// // 	refresh(frm) {

// // 	},
// // });


// frappe.ui.form.on("Party Registration", {

//     party_type: function(frm) {
//         frm.set_value("party", null);
//         clear_party_details(frm);
//     },

//     party: function(frm) {
//         if (frm.doc.party && frm.doc.party_type) {
//             fetch_party_details(frm);
//         }
//     },

//     refresh: function(frm) {
//         // Populate details for an already selected party
//         if (frm.doc.party && frm.doc.party_type) {
//             fetch_party_details(frm);
//         }
//     }
// });


// function clear_party_details(frm) {
//     const fields = [
//         "party_name",
//         "party_cid",
//         "country",
//         "dzongkhag",
//         "gewog",
//         "village",
//         "contact_no",
//         "image"
//     ];

//     fields.forEach(field => frm.set_value(field, ""));
// }


// // function fetch_party_details(frm) {
// //     frappe.call({
// //         method: "integrasuite_auction.auction.doctype.party_registration.party_registration.get_party_details",

// //         args: {
// //             party_type: frm.doc.party_type,
// //             party: frm.doc.party
// //         },

// //         callback: function(r) {
// //             if (r.message) {
// //                 frm.set_value("party_name", r.message.party_name || "");
// //                 frm.set_value("party_cid", r.message.party_cid || "");
// //                 frm.set_value("country", r.message.country || "");
// //                 frm.set_value("dzongkhag", r.message.dzongkhag || "");
// //                 frm.set_value("gewog", r.message.gewog || "");
// //                 frm.set_value("village", r.message.village || "");
// //                 frm.set_value("contact_no", r.message.contact_no || "");
// //                 frm.set_value("image", r.message.image || "");

// //             }
// //         }
// //     });
// // }



// function fetch_party_details(frm) {
//     frappe.call({
//         method: "integrasuite_auction.auction.doctype.party_registration.party_registration.get_party_details",
//         args: {
//             party_type: frm.doc.party_type,
//             party: frm.doc.party
//         },
//         callback: function(r) {
//             if (r.message) {
//                 frm.set_value("party_name", r.message.party_name || "");
//                 frm.set_value("party_cid", r.message.party_cid || "");
//                 frm.set_value("country", r.message.country || "");
//                 frm.set_value("dzongkhag", r.message.dzongkhag || "");
//                 frm.set_value("gewog", r.message.gewog || "");
//                 frm.set_value("village", r.message.village || "");
//                 frm.set_value("contact_no", r.message.contact_no || "");

//                 // Display the original party photograph
//                 // Clear the previous image first
//             frm.fields_dict.image.$wrapper.empty();

//             // Display the newly selected party photograph
//             const image_url = r.message?.image;

//             if (image_url) {
//                 frm.fields_dict.image.$wrapper.html(`
//                     <img src="${frappe.utils.escape_html(image_url)}"
//                         style="
//                             width: 180px;
//                             height: 180px;
//                             object-fit: cover;
//                             border-radius: 5px;
//                         ">
//                 `);
//             }
//             }
//         }
//     });
// }


// Copyright (c) 2026, ttpl and contributors
// For license information, please see license.txt

const registration_party_fields = [
    "party_name",
    "party_cid",
    "country",
    "dzongkhag",
    "gewog",
    "village",
    "contact_no"
];

frappe.ui.form.on("Party Registration", {
    async onload(frm) {
        if (frm.is_new() && !frm.doc.company) {
            const company =
                frappe.defaults.get_user_default("Company");

            if (company) {
                await frm.set_value("company", company);
            }
        }
    },

    async party_type(frm) {
        if (frm.doc.docstatus !== 0) return;

        await frm.set_value("party", null);
        await clear_registration_party_details(frm);
    },

    async party(frm) {
        if (frm.doc.docstatus !== 0) return;

        await clear_registration_party_details(frm);

        if (frm.doc.party && frm.doc.party_type) {
            await fetch_registration_party_details(frm);
        }
    },

    refresh(frm) {
        if (frm.doc.party && frm.doc.party_type) {
            return fetch_registration_party_details(frm, true);
        }

        render_registration_party_image(frm, null);
    }
});

async function clear_registration_party_details(frm) {
    const values = {};

    registration_party_fields.forEach((fieldname) => {
        values[fieldname] = "";
    });

    await frm.set_value(values);
    render_registration_party_image(frm, null);
}

function render_registration_party_image(frm, image_url) {
    const field = frm.fields_dict.image;

    if (!field || !field.$wrapper) return;

    field.$wrapper.empty();

    if (!image_url) return;

    $("<img>")
        .attr("src", image_url)
        .attr("alt", __("Party photograph"))
        .css({
            width: "180px",
            height: "180px",
            "object-fit": "cover",
            "border-radius": "5px"
        })
        .appendTo(field.$wrapper);
}

async function fetch_registration_party_details(
    frm,
    image_only = false
) {
    const party_type = frm.doc.party_type;
    const party = frm.doc.party;
    const document_name = frm.doc.name;

    if (!party_type || !party) return;

    const response = await frappe.call({
        method:
            "integrasuite_auction.auction.doctype.party_registration.party_registration.get_party_details",
        args: {
            party_type: party_type,
            party: party
        }
    });

    // Ignore a response for an earlier selection or document.
    if (
        frm.doc.name !== document_name ||
        frm.doc.party_type !== party_type ||
        frm.doc.party !== party
    ) {
        return;
    }

    const details = response.message;

    if (!details) return;

    if (!image_only && frm.doc.docstatus === 0) {
        const values = {};

        registration_party_fields.forEach((fieldname) => {
            values[fieldname] = details[fieldname] || "";
        });

        await frm.set_value(values);
    }

    render_registration_party_image(frm, details.image);
}