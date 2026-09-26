# Odoo 19 Real Estate Management

A complete **Real Estate Management application for Odoo 19 Community**, developed as part of a technical assessment.

The project is based on the Odoo Server Framework 101 Real Estate tutorial and extends it with additional business functionality, workflow validation, automatic references, offer expiration protection, commission calculation, role-based Agent/Manager security, and accounting integration.

The goal of the project is to demonstrate practical understanding of the Odoo framework, Python models, ORM relationships, XML views, security, QWeb/Kanban, inheritance, PostgreSQL-backed business logic, and integration between Odoo modules.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Assessment Scope](#assessment-scope)
- [Main Modules](#main-modules)
- [Main Features](#main-features)
- [Property Workflow](#property-workflow)
- [Offer Workflow](#offer-workflow)
- [Accounting Integration](#accounting-integration)
- [Custom Features Added](#custom-features-added)
- [Odoo Concepts Used](#odoo-concepts-used)
- [Data Model and Relationships](#data-model-and-relationships)
- [Project Structure](#project-structure)
- [Development Environment](#development-environment)
- [Installation on Windows](#installation-on-windows)
- [Odoo Configuration](#odoo-configuration)
- [Database Setup](#database-setup)
- [Installing the Modules](#installing-the-modules)
- [Running and Updating the Project](#running-and-updating-the-project)
- [Testing the Application](#testing-the-application)
- [Business Rules and Validation](#business-rules-and-validation)
- [Views and User Interface](#views-and-user-interface)
- [Security](#security)
- [Git and GitHub Workflow](#git-and-github-workflow)
- [Troubleshooting](#troubleshooting)
- [Important Technical Notes](#important-technical-notes)
- [Possible Future Improvements](#possible-future-improvements)
- [Author](#author)

---

# Project Overview

The application manages the main workflow of a real estate business.

A user can:

1. Create a property.
2. Assign a property type and tags.
3. Add property details.
4. Receive offers from customers.
5. Compare offers.
6. Accept or refuse offers.
7. Assign the buyer automatically after accepting an offer.
8. Calculate the final selling price.
9. Calculate the agency commission.
10. Mark the property as sold.
11. Automatically create a customer invoice in Odoo Invoicing.

The final workflow is:

```text
Create Property
      ↓
Automatic Property Reference
      ↓
Receive Offer
      ↓
Offer Received
      ↓
Accept Valid Offer
      ↓
Buyer Assigned
Selling Price Assigned
      ↓
Offer Accepted
      ↓
Commission Calculated
      ↓
Mark Property as Sold
      ↓
Customer Invoice Created
```

---

# Assessment Scope

The technical assessment required:

- Understanding the Odoo ERP framework.
- Building the Real Estate module on Odoo 19 Community.
- Completing the official Real Estate tutorial concepts.
- Adding new functionality to the created module.
- Understanding the code well enough to explain it during a technical/oral discussion.

The final implementation contains both the original tutorial functionality and additional custom features.

---

# Main Modules

The project contains two Odoo addons.

```text
estate/
estate_account/
```

## `estate`

The main Real Estate application.

It contains:

- Property management
- Property types
- Property tags
- Offers
- Buyers
- Salespersons
- Property states
- Computed fields
- Business constraints
- Search views
- List views
- Form views
- Kanban/QWeb view
- Role-based security
- Agent and Manager access levels
- Record rules for salesperson-specific property visibility
- Automatic property references
- Commission calculation
- Offer expiration protection

## `estate_account`

A bridge module between the Real Estate application and Odoo Invoicing.

It depends on:

```python
["estate", "account"]
```

It extends `estate.property` and creates a customer invoice when a property is sold.

---

# Main Features

## Property Management

Each property can contain:

- Unique reference
- Name
- Description
- Postcode
- Availability date
- Property type
- Tags
- Salesperson
- Buyer
- Expected price
- Best offer
- Selling price
- Commission rate
- Commission amount
- Bedrooms
- Living area
- Garden area
- Total area
- Number of facades
- Garage
- Garden
- Garden orientation
- Current workflow state

---

## Property Types

Properties can be classified using property types such as:

```text
Apartment
House
Villa
```

Property types can also display related offers through a statistic button.

---

## Property Tags

Properties can contain multiple tags.

Example:

```text
Cozy
Renovated
Luxury
Sea View
```

Tags use Odoo's `many2many_tags` widget and can support colors.

---

## Buyers and Salespersons

The project uses two different Odoo models:

```text
res.partner
res.users
```

### Buyer

The buyer is stored using:

```python
buyer_id = fields.Many2one("res.partner")
```

`res.partner` represents contacts/customers.

### Salesperson

The salesperson is stored using:

```python
salesperson_id = fields.Many2one("res.users")
```

`res.users` represents internal Odoo users.

The default salesperson is the currently logged-in user.

---

# Property Workflow

The property uses a `state` Selection field.

The main states are:

```text
New
Offer Received
Offer Accepted
Sold
Canceled
```

Normal workflow:

```text
New
 ↓
Offer Received
 ↓
Offer Accepted
 ↓
Sold
```

Alternative workflow:

```text
New
 ↓
Canceled
```

The state is displayed in the form header using the Odoo `statusbar` widget.

Example:

```xml
<field
    name="state"
    widget="statusbar"
    statusbar_visible="new,offer_received,offer_accepted,sold"
/>
```

---

# Offer Workflow

Each property can receive multiple offers.

An offer contains:

- Price
- Partner
- Property
- Property type
- Validity
- Deadline
- Status

Offer statuses are:

```text
Accepted
Refused
```

The deadline is computed from the creation date and the validity period.

Example:

```text
Create Date: September 25
Validity: 7 days
Deadline: October 2
```

The deadline also has an inverse method, so changing the deadline can update the validity.

---

## Accepting an Offer

When an offer is accepted, the application performs the following actions:

```text
Offer Status = Accepted
Buyer = Offer Partner
Selling Price = Offer Price
Property State = Offer Accepted
```

The core logic is implemented in the offer model.

---

## Refusing an Offer

When an offer is refused:

```text
Offer Status = Refused
```

The property itself remains available unless another business rule changes its state.

---

# Accounting Integration

The accounting integration is implemented in:

```text
estate_account/models/estate_property.py
```

The module inherits from:

```python
_inherit = "estate.property"
```

When `action_sold()` is executed, the module first verifies that the current user has write access to the property and then creates a customer invoice.

```python
self.check_access("write")
self.env["account.move"].sudo().create(...)
```

The explicit access check protects the Real Estate record, while the controlled `sudo()` call allows an authorized Real Estate user to generate the invoice without granting general Accounting permissions.

The invoice type is:

```python
"move_type": "out_invoice"
```

This means:

```text
Customer Invoice
```

---

## What the Invoice Contains

The invoice contains two lines:

```text
Property Commission
Administrative Fees
```

The invoice does **not** represent the full property selling price.

It represents the fees charged by the real estate agency.

Example:

```text
Selling Price:              95,000
Commission Rate:                 6%
Commission Amount:           5,700
Administrative Fees:          100
---------------------------------
Invoice Total:               5,800
```

The selling price remains visible on the Real Estate property record.

---

## Invoice States

The invoice follows Odoo's standard accounting workflow.

```text
Draft
 ↓
Posted
 ↓
Paid
```

### Draft

The invoice has been created but is not yet officially posted in accounting.

### Posted

The invoice has been validated and posted to the accounting system.

Example invoice number:

```text
INV/2026/00010
```

### Paid

The invoice has been registered as paid.

Important:

```text
Posted ≠ Paid
```

Posting validates the invoice. Payment is a separate step.

---

# Custom Features Added

The original tutorial was extended with custom functionality.

## 1. Automatic Property Reference

Every new property receives a unique reference.

Example:

```text
PROP-00001
PROP-00002
PROP-00003
```

The feature uses:

```text
ir.sequence
```

The sequence is defined in:

```text
estate/data/estate_property_sequence.xml
```

The property model overrides `create()` using:

```python
@api.model_create_multi
```

The sequence is requested with:

```python
self.env["ir.sequence"].next_by_code("estate.property")
```

A sequence can contain gaps. For example, if `PROP-00001` was generated during testing and the record was later deleted, the next record can correctly become:

```text
PROP-00002
```

Odoo sequences do not normally reuse consumed numbers.

---

## 2. Expired Offer Protection

An expired offer cannot be accepted.

The application compares:

```text
Offer Deadline
```

with:

```text
Today's Date
```

Logic:

```text
Deadline < Today
      ↓
Offer Expired
      ↓
Accept Blocked
```

The user receives:

```text
You cannot accept an expired offer.
```

This validation is implemented inside `action_accept()`.

---

## 3. Single Accepted Offer Protection

Only one offer can be accepted for a property.

Before accepting a new offer, the system searches for another accepted offer.

If one already exists, the system raises an error:

```text
Another offer has already been accepted for this property.
```

Other offers can remain stored in the system, but a second accepted offer is blocked.

---

## 4. Commission Rate and Commission Amount

The property model includes:

```text
Commission Rate (%)
Commission Amount
```

Default commission rate:

```text
6%
```

The commission amount is computed automatically:

```text
Commission Amount
=
Selling Price × Commission Rate / 100
```

Example:

```text
Selling Price:       100,000
Commission Rate:           6%
Commission Amount:     6,000
```

The accounting module then uses the computed commission amount instead of hardcoding:

```python
selling_price * 0.06
```

This improves maintainability and makes the business rule visible in the Real Estate application.

---

## 5. Agent and Manager Role-Based Security

The Real Estate application includes two business roles:

```text
Agent
Manager
```

### Agent

An Agent represents a real estate salesperson.

Agents can:

- Access the Real Estate application
- See properties assigned to themselves
- See unassigned properties
- Manage offers for properties they are allowed to access
- Read Property Types and Tags

Agents cannot:

- See properties assigned to another agent
- Access the Real Estate Settings menu
- Modify Property Types or Tags
- Update or install Odoo modules

### Manager

A Real Estate Manager has broader access.

Managers can:

- See all Real Estate properties
- Manage all offers
- Access Real Estate Settings
- Create, edit, and delete Property Types
- Create, edit, and delete Tags

The Real Estate Manager role is separate from the global Odoo Administrator role. Module installation and module upgrades remain system-administration operations.

### Access Rights and Record Rules

Model-level permissions are defined in:

```text
estate/security/ir.model.access.csv
```

Security groups and record rules are defined in:

```text
estate/security/security.xml
```

The Agent property rule allows access to:

```text
salesperson_id = current user
OR
salesperson_id is empty
```

This means an Agent can work with their own properties and unassigned properties, but cannot access another agent's assigned properties.

The Manager role has unrestricted access to Real Estate property records.

### Secure Invoice Creation

An Agent should not need general Accounting permissions simply to complete a property sale.

The accounting integration therefore verifies write access to the property before creating the invoice with controlled elevated access:

```python
self.check_access("write")
self.env["account.move"].sudo().create(...)
```

This keeps the Real Estate permission check in place while allowing the system to generate the required invoice.

---

# Odoo Concepts Used

The project demonstrates the following Odoo concepts.

## Models

Examples:

```text
estate.property
estate.property.type
estate.property.tag
estate.property.offer
```

---

## Basic Fields

Examples:

```python
fields.Char
fields.Text
fields.Integer
fields.Float
fields.Boolean
fields.Date
fields.Selection
```

---

## Relational Fields

### Many2one

Many records can reference one record.

Example:

```python
property_type_id = fields.Many2one(
    "estate.property.type"
)
```

Many properties can have the same property type.

### One2many

One record can display many related records.

Example:

```python
offer_ids = fields.One2many(
    "estate.property.offer",
    "property_id"
)
```

One property can contain many offers.

### Many2many

Many records can be connected to many records.

Example:

```python
tag_ids = fields.Many2many(
    "estate.property.tag"
)
```

One property can have many tags and one tag can belong to many properties.

---

## Computed Fields

Examples:

```text
Total Area
Best Offer
Commission Amount
```

Computed fields use:

```python
@api.depends(...)
```

Example:

```python
@api.depends("selling_price", "commission_rate")
def _compute_commission_amount(self):
    ...
```

---

## Onchange

The garden feature uses:

```python
@api.onchange("garden")
```

When Garden is enabled:

```text
Garden Area = 10
Garden Orientation = North
```

When Garden is disabled:

```text
Garden Area = 0
Garden Orientation = Empty
```

`onchange` mainly controls interactive form behavior in the user interface.

---

## SQL Constraints

The project uses database-level constraints.

Examples:

```text
Expected Price > 0
Selling Price >= 0
Offer Price > 0
```

---

## Python Constraints

A Python constraint prevents the selling price from being lower than 90% of the expected price.

Example:

```text
Expected Price = 100,000
Minimum Allowed Selling Price = 90,000
```

A selling price such as:

```text
85,000
```

is rejected.

---

## `@api.ondelete`

Deletion is restricted using:

```python
@api.ondelete(at_uninstall=False)
```

Only properties in these states can be deleted:

```text
New
Canceled
```

---

## Model Inheritance

The accounting module uses:

```python
_inherit = "estate.property"
```

This extends the existing property model without creating a new model.

The project also extends:

```text
res.users
```

to display assigned properties on internal user records.

---

## `super()`

The accounting integration extends the original `action_sold()` behavior and keeps the existing parent behavior using `super()`.

This allows the accounting module to add invoice creation without replacing the original Real Estate logic completely.

---

# Data Model and Relationships

Conceptual relationship:

```text
res.users
   │
   │ salesperson_id
   ▼
estate.property
   │
   ├──────── property_type_id ───────► estate.property.type
   │
   ├──────── tag_ids ◄───────────────► estate.property.tag
   │
   ├──────── buyer_id ───────────────► res.partner
   │
   │
   └──────── offer_ids
              │
              ▼
      estate.property.offer
              │
              └──────── partner_id ──► res.partner
```

Important database concept:

The physical foreign key for a One2many relationship exists on the corresponding Many2one field.

Example:

```text
estate.property.offer.property_id
```

links an offer to a property.

---

# Project Structure

```text
odoo19-real-estate/
│
├── estate/
│   ├── __init__.py
│   ├── __manifest__.py
│   │
│   ├── data/
│   │   └── estate_property_sequence.xml
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── estate_property.py
│   │   ├── estate_property_offer.py
│   │   ├── estate_property_tag.py
│   │   ├── estate_property_type.py
│   │   └── res_users.py
│   │
│   ├── security/
│   │   ├── security.xml
│   │   └── ir.model.access.csv
│   │
│   └── views/
│       ├── estate_property_views.xml
│       ├── estate_property_offer_views.xml
│       ├── estate_property_tag_views.xml
│       ├── estate_property_type_views.xml
│       ├── res_users_views.xml
│       └── estate_menus.xml
│
├── estate_account/
│   ├── __init__.py
│   ├── __manifest__.py
│   │
│   └── models/
│       ├── __init__.py
│       └── estate_property.py
│
└── .gitignore
```

---

# Development Environment

The project was developed and tested with:

```text
Operating System: Windows 11 Pro
Odoo: Odoo 19 Community
PostgreSQL: PostgreSQL
Database: estate_dev
Odoo URL: http://localhost:8069
```

Local Odoo installation used during development:

```text
C:\Program Files\Odoo 19.0.20260923\
```

Odoo configuration:

```text
C:\Program Files\Odoo 19.0.20260923\server\odoo.conf
```

Custom addons:

```text
C:\odoo\custom_modules
```

---

# Installation on Windows

## 1. Install Odoo 19 Community

Install Odoo 19 Community for Windows.

A typical installation path is:

```text
C:\Program Files\Odoo 19.0.20260923\
```

The installation includes the Odoo server and a compatible Python environment.

---

## 2. Install PostgreSQL

Odoo uses PostgreSQL as its database.

Verify that PostgreSQL is running before starting Odoo.

pgAdmin can be used to inspect the database, tables, rows, and relationships.

---

## 3. Prepare the Custom Addons Folder

Create:

```text
C:\odoo\custom_modules
```

Place the two modules directly inside:

```text
C:\odoo\custom_modules\
├── estate\
└── estate_account\
```

Each Odoo addon must contain its own:

```text
__manifest__.py
```

---

# Odoo Configuration

Open:

```text
C:\Program Files\Odoo 19.0.20260923\server\odoo.conf
```

Ensure `addons_path` contains both the standard Odoo addons path and the custom addons folder.

Example:

```ini
addons_path = c:\program files\odoo 19.0.20260923\server\odoo\addons,c:\odoo\custom_modules
```

Important:

Odoo does not search arbitrary nested folders recursively.

With this configuration, addons should be directly inside:

```text
C:\odoo\custom_modules
```

like:

```text
estate
estate_account
```

---

# Database Setup

Open the database manager:

```text
http://localhost:8069/web/database/manager
```

Create or select a database.

The development database used for this project was:

```text
estate_dev
```

After entering the database:

1. Enable Developer Mode.
2. Open Apps.
3. Update the Apps List if necessary.
4. Search for the Real Estate module.

---

# Installing the Modules

Install:

```text
Real Estate
```

Then install:

```text
Real Estate Accounting
```

The accounting module declares:

```python
"depends": ["estate", "account"]
```

Therefore Odoo ensures the required dependencies are installed.

The Odoo `account` module provides the Invoicing/accounting models used by the integration.

---

# Running and Updating the Project

The Odoo service used during development is:

```text
odoo-server-19.0
```

## Restart Odoo

Run PowerShell or Command Prompt as Administrator:

```powershell
net stop odoo-server-19.0
net start odoo-server-19.0
```

---

## When a Restart Is Needed

Restart Odoo after changing Python code.

Examples:

```text
models/estate_property.py
models/estate_property_offer.py
estate_account/models/estate_property.py
```

Python files are loaded by the Odoo server process, so the service must be restarted to load new Python logic.

---

## When a Module Upgrade Is Needed

Upgrade the module after changes involving:

- New model fields
- XML views
- Security files
- Data XML
- Manifest changes
- Database schema changes

Example:

```text
Apps
→ Real Estate
→ Upgrade
```

For the accounting module:

```text
Apps
→ Real Estate Accounting
→ Upgrade
```

A common development workflow is:

```text
Save Code
   ↓
Restart Odoo
   ↓
Upgrade Module
   ↓
Refresh Browser
   ↓
Test
```

---

# Testing the Application

A complete end-to-end test can be performed as follows.

## Test 1: Property Creation

Create a property:

```text
Name: Beirut Apartment
Expected Price: 100,000
```

Expected result:

```text
Reference: PROP-0000X
State: New
Commission Rate: 6%
Commission Amount: 0
```

---

## Test 2: Create an Offer

Create:

```text
Offer: 95,000
Partner: Customer
```

Expected result:

```text
Best Offer: 95,000
State: Offer Received
```

---

## Test 3: Accept the Offer

Click:

```text
Accept
```

Expected result:

```text
Offer Status: Accepted
Buyer: Offer Partner
Selling Price: 95,000
State: Offer Accepted
Commission Amount: 5,700
```

---

## Test 4: Expired Offer

Create or edit an offer so its deadline is before today's date.

Click:

```text
Accept
```

Expected result:

```text
You cannot accept an expired offer.
```

---

## Test 5: Second Accepted Offer

Try to accept another offer for a property that already has an accepted offer.

Expected result:

```text
Another offer has already been accepted for this property.
```

---

## Test 6: Sell the Property

After a valid offer is accepted, click:

```text
Sold
```

Expected result:

```text
Property State: Sold
```

A customer invoice should be created automatically.

---

## Test 7: Verify Invoice

Open:

```text
Invoicing
→ Customers
→ Invoices
```

Example with:

```text
Selling Price = 95,000
Commission Rate = 6%
```

Expected invoice:

```text
Property Commission     5,700
Administrative Fees       100
--------------------------------
Total                   5,800
```

---

## Test 8: Invalid Workflow

Try:

```text
Canceled Property → Sold
```

Expected:

```text
Blocked
```

Try:

```text
Sold Property → Cancel
```

Expected:

```text
Blocked
```

---

## Test 9: Agent Access

Create two properties:

```text
Property A → Salesperson = Agent A
Property B → Salesperson = Agent B
```

Login as Agent A.

Expected result:

```text
Property A visible
Property B hidden
Real Estate Settings hidden
```

An unassigned property should also remain visible to Agent A.

---

## Test 10: Manager Access

Login as a Real Estate Manager.

Expected result:

```text
All properties visible
All offers accessible
Real Estate Settings visible
Property Types editable
Tags editable
```

The Manager role should be tested separately from the global Odoo Administrator role.

---

# Business Rules and Validation

The final project includes the following rules.

| Rule | Behavior |
|---|---|
| Expected price | Must be greater than 0 |
| Selling price | Cannot be negative |
| Selling price threshold | Cannot be below 90% of expected price |
| Offer price | Must be greater than 0 |
| New offer | Cannot be lower than the current highest offer |
| Expired offer | Cannot be accepted |
| Accepted offers | Only one accepted offer per property |
| Canceled property | Cannot be sold |
| Sold property | Cannot be canceled |
| Property deletion | Only New or Canceled properties can be deleted |
| Property reference | Generated automatically using `ir.sequence` |
| Commission amount | Computed from selling price and commission rate |
| Agent property access | Own and unassigned properties only |
| Manager property access | All Real Estate properties |
| Real Estate Settings | Manager only |

---

# Views and User Interface

The project uses several Odoo view types.

## List View

The list view displays multiple properties and uses decorations.

Examples:

```text
Offer Received / Offer Accepted → success decoration
Offer Accepted → bold
Sold → muted
```

The list can display:

- Reference
- Name
- Postcode
- Bedrooms
- Living area
- Expected price
- Selling price
- Commission rate
- Commission amount
- Property type
- Tags

---

## Form View

The form view contains:

- Header buttons
- Status bar
- Basic property information
- Pricing information
- Commission information
- Property details
- Garden information
- Description tab
- Other Info tab
- Offers tab

---

## Search View

The search view supports:

- Name
- Postcode
- Expected price
- Bedrooms
- Minimum living area
- Available filter
- Group by postcode

The Available filter includes properties with these states:

```text
New
Offer Received
```

---

## Kanban and QWeb

The property Kanban view uses QWeb.

QWeb is Odoo's XML templating engine.

The Kanban view can:

- Show property cards
- Display expected price
- Display best offer conditionally
- Display selling price conditionally
- Display tags
- Group properties by property type

Example configuration:

```xml
<kanban
    default_group_by="property_type_id"
    records_draggable="false"
>
```

This groups cards by property type and prevents moving cards between groups using drag-and-drop.

---

# Security

The project uses both model-level access rights and record-level security.

Security groups and record rules are defined in:

```text
estate/security/security.xml
```

Model permissions are defined in:

```text
estate/security/ir.model.access.csv
```

The application contains two Real Estate roles:

```text
Agent
Manager
```

## Agent

An Agent can work with:

```text
Their own properties
Unassigned properties
Offers related to accessible properties
```

An Agent cannot see properties assigned to another agent.

The Settings menu is hidden from Agents.

Property Types and Tags are readable by Agents but configuration changes are reserved for Managers.

## Manager

A Manager can:

```text
See all properties
Manage all offers
Access Real Estate Settings
Manage Property Types
Manage Tags
```

## Access Control Layers

Odoo CRUD permissions are:

```text
Create
Read
Update
Delete
```

In `ir.model.access.csv` they correspond to:

```text
perm_create
perm_read
perm_write
perm_unlink
```

Record rules then restrict which individual records a user can access.

The Agent property rule is based on the assigned salesperson:

```text
salesperson_id = current user
OR
salesperson_id is empty
```

The Manager role can access all Real Estate property records.

The Real Estate Manager role does not replace the global Odoo Administrator role. System operations such as module installation and module upgrades remain restricted to Odoo administrators.

---

# Git and GitHub Workflow

The repository contains both addons:

```text
estate/
estate_account/
```

Recommended `.gitignore`:

```gitignore
__pycache__/
*.pyc
*.pyo
*.log
.env
.vscode/
odoo.conf
```

Do not commit:

- Odoo passwords
- PostgreSQL passwords
- `odoo.conf`
- Database backups containing sensitive information
- Python cache files
- Local logs

---

## Typical Git Workflow

Check changes:

```powershell
git status
```

Add only this project:

```powershell
git add estate estate_account .gitignore
```

Commit:

```powershell
git commit -m "Add custom real estate assessment features"
```

Push:

```powershell
git push origin main
```

Verify:

```powershell
git status
```

Expected final result:

```text
nothing to commit, working tree clean
```

---

# Troubleshooting

This section documents important development issues encountered while building the project and the corresponding solutions.

## Module Does Not Appear in Apps

Check:

```ini
addons_path
```

The folder containing the addon must be included.

For this project:

```ini
c:\odoo\custom_modules
```

Then:

1. Restart Odoo.
2. Update Apps List.
3. Search again.

---

## Python Change Does Not Appear

Python files are loaded when the Odoo server starts.

After changing Python:

```powershell
net stop odoo-server-19.0
net start odoo-server-19.0
```

Then retest.

---

## New Field Does Not Appear

If a field was added to Python but not visible:

1. Ensure it is added to the correct XML form/list view.
2. Restart Odoo.
3. Upgrade the module.

Example:

```xml
<field name="commission_rate"/>
<field name="commission_amount"/>
```

Adding a field only to the List view does not automatically display it in the Form view.

---

## Kanban Option Does Not Appear

Ensure the window action contains:

```xml
<field name="view_mode">list,kanban,form</field>
```

Then upgrade the module.

---

## Kanban Is Not Grouped by Property Type

Ensure the Kanban root contains:

```xml
<kanban
    default_group_by="property_type_id"
    records_draggable="false"
>
```

---

## Property Stays on "Offer Received" After Accept

The offer acceptance method must update the property state:

```python
record.property_id.state = "offer_accepted"
```

Accepting an offer should also set:

```python
record.property_id.buyer_id = record.partner_id
record.property_id.selling_price = record.price
```

---

## Accepted Offer Is Green but State Does Not Change

This means the offer status changed but the property workflow state was not updated.

The solution is the same:

```python
record.property_id.state = "offer_accepted"
```

Restart Odoo after changing Python.

---

## Invoice Is Not Created After Clicking Sold

Check that:

```text
estate_account/__init__.py
```

contains:

```python
from . import models
```

and:

```text
estate_account/models/__init__.py
```

contains:

```python
from . import estate_property
```

Also verify the manifest dependencies:

```python
"depends": ["estate", "account"]
```

Restart Odoo after Python changes.

---

## Invoice Is Created but Shows Only Commission

This is expected.

The invoice represents the real estate agency's charges:

```text
Commission
+
Administrative Fee
```

The full property selling price remains in the Real Estate property record.

---

## Invoice Is Draft

This is also expected.

The custom code creates a Draft invoice.

Normal workflow:

```text
Draft
→ Posted
→ Paid
```

---

## Deadline Calculation Error Between Datetime and Date

`create_date` is a Datetime field while `date_deadline` is a Date field.

Convert the creation date before date arithmetic:

```python
create_date = (
    fields.Date.to_date(record.create_date)
    if record.create_date
    else fields.Date.today()
)
```

This prevents mixing incompatible date and datetime types.

---

## XML Model Name Errors

Technical XML values such as model names and `res_model` should be written cleanly without accidental whitespace.

Correct:

```xml
<field name="model">res.users</field>
```

Correct:

```xml
<field name="res_model">estate.property.offer</field>
```

Avoid inserting unwanted spaces/newlines inside technical values.

---

## Access Denied

Verify:

```text
security/ir.model.access.csv
```

and confirm the model has appropriate permissions for:

```text
base.group_user
```

Also remember:

```text
res.users
```

represents local Odoo users.

A local user created in:

```text
Settings
→ Users & Companies
→ Users
```

is not automatically an account on `odoo.com`.

---

## PostgreSQL Authentication Error

If Odoo reports a PostgreSQL authentication error such as:

```text
fe_sendauth: no password supplied
```

verify the database configuration in:

```text
odoo.conf
```

and ensure the configured PostgreSQL role and authentication settings match the running PostgreSQL server.

Do not commit database credentials to GitHub.

---

## Git Warns About an Embedded Repository

If Git displays:

```text
warning: adding embedded git repository
```

there is another `.git` folder inside a folder being added.

The final project repository should contain normal project folders such as:

```text
estate/
estate_account/
```

without unintended nested Git repositories.

---

## `cd custom modules` Fails in PowerShell

A path containing spaces must be quoted.

Example:

```powershell
cd "custom modules"
```

The actual project folder is:

```powershell
cd C:\odoo\custom_modules
```

because the folder name uses an underscore.

---

# Important Technical Notes

## Odoo ORM

The project uses Odoo's ORM instead of manually writing SQL for normal application operations.

Example:

```python
self.env["account.move"].create(...)
```

The ORM translates model operations into PostgreSQL operations and applies Odoo business logic and security.

---

## Model-to-Table Mapping

An Odoo model such as:

```python
_name = "estate.property"
```

normally maps to a PostgreSQL table similar to:

```text
estate_property
```

Odoo also creates standard fields such as:

```text
id
create_uid
write_uid
create_date
write_date
```

---

## XML Views vs Python Models

Python defines:

```text
Data
Business Logic
Validation
Computed Fields
Actions
```

XML defines:

```text
How the user sees and interacts with that data
```

Example:

```text
Python field exists
+
XML field added to form
=
Field visible in the interface
```

---

## QWeb vs HTML

QWeb is not HTML itself.

QWeb is Odoo's XML templating engine.

A QWeb template can contain:

- QWeb directives
- Odoo fields
- HTML elements such as `div`, `span`, and `strong`

Example:

```xml
<t t-name="card">
    <div>
        <strong>
            <field name="name"/>
        </strong>
    </div>
</t>
```

---

## `type="object"` vs `type="action"`

### `type="object"`

Calls a Python method on the current model.

Example:

```xml
<button
    name="action_sold"
    type="object"
/>
```

### `type="action"`

Executes an Odoo action.

Example:

```text
Opening another list/form window
```

---

## `res.partner` vs `res.users`

Use:

```text
res.partner
```

for:

```text
Customers
Contacts
Buyers
```

Use:

```text
res.users
```

for:

```text
Internal Odoo users
Salespersons
Administrators
```

---

# Possible Future Improvements

These are possible extensions and are **not required for the current assessment**.

- Property images
- Offer expiration cron automation
- Email notifications
- PDF property reports
- Automated tests
- Dashboard and statistics
- Commission configuration by property type
- Multiple commission rules
- Offer history/reporting
- Additional accounting configuration

---

# Final Assessment Checklist

The implemented project currently covers:

```text
Odoo 19 Setup                     ✅
PostgreSQL Database               ✅
Custom Addons Path                ✅
Real Estate Module                ✅
Property Model                    ✅
Property Types                    ✅
Property Tags                     ✅
Offers                            ✅
Relational Fields                 ✅
Computed Fields                   ✅
Onchange                          ✅
SQL Constraints                   ✅
Python Constraints                ✅
Delete Protection                 ✅
Actions                           ✅
State Workflow                    ✅
Security Access                   ✅
Agent Role                        ✅
Manager Role                      ✅
Role-Based Record Rules           ✅
Salesperson Property Visibility   ✅
Manager-Only Settings             ✅
Secure Invoice Permission Flow    ✅
List View                         ✅
Form View                         ✅
Search View                       ✅
Kanban / QWeb                     ✅
Model Inheritance                 ✅
res.users Extension               ✅
Accounting Integration            ✅
Automatic Invoice Creation        ✅
Automatic Property Reference      ✅
Expired Offer Protection          ✅
Single Accepted Offer Protection  ✅
Commission Calculation            ✅
Git / GitHub                      ✅
```

---

# Author

**Iman Soleiman**

Odoo 19 Real Estate Management  
Technical Assessment Project
