// Copyright (c) 2026, ttpl and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Party Registration", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Party Registration", {

    party_type: function(frm) {
        frm.set_value("party", null);
        clear_party_details(frm);
    },

    party: function(frm) {
        if (frm.doc.party && frm.doc.party_type) {
            fetch_party_details(frm);
        }
    },

    refresh: function(frm) {
        // Populate details for an already selected party
        if (frm.doc.party && frm.doc.party_type) {
            fetch_party_details(frm);
        }
    }
});


function clear_party_details(frm) {
    const fields = [
        "party_name",
        "party_cid",
        "country",
        "dzongkhag",
        "gewog",
        "village",
        "contact_no",
        "image"
    ];

    fields.forEach(field => frm.set_value(field, ""));
}


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
//                 frm.set_value("image", r.message.image || "");

//             }
//         }
//     });
// }



function fetch_party_details(frm) {
    frappe.call({
        method: "integrasuite_auction.auction.doctype.party_registration.party_registration.get_party_details",
        args: {
            party_type: frm.doc.party_type,
            party: frm.doc.party
        },
        callback: function(r) {
            if (r.message) {
                frm.set_value("party_name", r.message.party_name || "");
                frm.set_value("party_cid", r.message.party_cid || "");
                frm.set_value("country", r.message.country || "");
                frm.set_value("dzongkhag", r.message.dzongkhag || "");
                frm.set_value("gewog", r.message.gewog || "");
                frm.set_value("village", r.message.village || "");
                frm.set_value("contact_no", r.message.contact_no || "");

                // Display the original party photograph
                // Clear the previous image first
            frm.fields_dict.image.$wrapper.empty();

            // Display the newly selected party photograph
            const image_url = r.message?.image;

            if (image_url) {
                frm.fields_dict.image.$wrapper.html(`
                    <img src="${frappe.utils.escape_html(image_url)}"
                        style="
                            width: 180px;
                            height: 180px;
                            object-fit: cover;
                            border-radius: 5px;
                        ">
                `);
            }
            }
        }
    });
}
