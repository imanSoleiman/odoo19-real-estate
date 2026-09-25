from odoo import api, fields, models
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"
    
    _check_price = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be strictly positive.",
    )

    price = fields.Float()

    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
    )
    property_type_id = fields.Many2one(
        "estate.property.type",
        related="property_id.property_type_id",
        store=True,
    )
    validity = fields.Integer(
        default=7,
    )

    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            create_date = (
                fields.Date.to_date(record.create_date)
                if record.create_date
                else fields.Date.today()
            )

            record.date_deadline = fields.Date.add(
                create_date,
                days=record.validity,
            )


    def _inverse_date_deadline(self):
        for record in self:
            create_date = (
                fields.Date.to_date(record.create_date)
                if record.create_date
                else fields.Date.today()
            )

            if record.date_deadline:
                record.validity = (
                    record.date_deadline - create_date
                ).days
                
    def action_accept(self):
        for record in self:
            if (
                record.date_deadline
                and record.date_deadline < fields.Date.today()
            ):
                raise UserError(
                    "You cannot accept an expired offer."
                )

            other_accepted_offer = record.property_id.offer_ids.filtered(
                lambda offer: offer.status == "accepted"
                and offer.id != record.id
            )

            if other_accepted_offer:
                raise UserError(
                    "Another offer has already been accepted for this property."
                )

            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = "offer_accepted"

        return True


    def action_refuse(self):
        for record in self:
            record.status = "refused"

        return True
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = self.env["estate.property"].browse(
                vals["property_id"]
            )

            if property_id.offer_ids:
                highest_offer = max(
                    property_id.offer_ids.mapped("price")
                )

                if vals["price"] < highest_offer:
                    raise UserError(
                        "The offer price must be higher than "
                        "the existing offers."
                    )

            property_id.state = "offer_received"

        return super().create(vals_list)