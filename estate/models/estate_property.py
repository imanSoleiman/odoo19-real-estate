from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)",
        "The expected price must be strictly positive.",
    )

    _selling_price_sql_constraint = models.Constraint(
        "CHECK(selling_price >= 0)",
        "The selling price must be positive.",
    )

    reference = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    name = fields.Char(
        required=True,
    )

    description = fields.Text()

    postcode = fields.Char()

    date_availability = fields.Date(
        copy=False,
        default=lambda self: fields.Date.add(
            fields.Date.today(),
            months=3,
        ),
    )

    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type",
    )

    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tags",
    )

    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
    )

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
    )

    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    expected_price = fields.Float(
        required=True,
    )

    selling_price = fields.Float(
        readonly=True,
        copy=False,
    )

    best_price = fields.Float(
        compute="_compute_best_price",
        string="Best Offer",
    )

    commission_rate = fields.Float(
        string="Commission Rate (%)",
        default=6.0,
    )

    commission_amount = fields.Float(
        string="Commission Amount",
        compute="_compute_commission_amount",
    )

    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )

    total_area = fields.Integer(
        compute="_compute_total_area",
        string="Total Area",
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (
                record.living_area + record.garden_area
            )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(
                record.offer_ids.mapped("price"),
                default=0.0,
            )

    @api.depends("selling_price", "commission_rate")
    def _compute_commission_amount(self):
        for record in self:
            record.commission_amount = (
                record.selling_price
                * record.commission_rate
                / 100
            )

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise UserError(
                    "A canceled property cannot be sold."
                )

            record.state = "sold"

        return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError(
                    "A sold property cannot be canceled."
                )

            record.state = "canceled"

        return True

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(
                record.selling_price,
                precision_digits=2,
            ):
                continue

            minimum_price = record.expected_price * 0.90

            if (
                float_compare(
                    record.selling_price,
                    minimum_price,
                    precision_digits=2,
                )
                < 0
            ):
                raise ValidationError(
                    "The selling price cannot be lower than "
                    "90% of the expected price."
                )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_canceled(self):
        for record in self:
            if record.state not in ("new", "canceled"):
                raise UserError(
                    "You cannot delete a property that is "
                    "not New or Canceled."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = (
                    self.env["ir.sequence"].next_by_code(
                        "estate.property"
                    )
                    or "New"
                )

        return super().create(vals_list)