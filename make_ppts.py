#!/usr/bin/env python3
"""Generate Review 2 and Review 3 PPTX decks for the DBMS project."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import os

OUT_DIR = "presentations"
os.makedirs(OUT_DIR, exist_ok=True)

NAVY   = RGBColor(0x0E, 0x1A, 0x2B)
BLUE   = RGBColor(0x1F, 0x6F, 0xEB)
CYAN   = RGBColor(0x35, 0xC4, 0xD5)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xF2, 0xF5, 0xFA)
GREY   = RGBColor(0x5A, 0x64, 0x73)
GREEN  = RGBColor(0x1E, 0xA9, 0x7A)
AMBER  = RGBColor(0xE8, 0xA0, 0x20)

SW, SH = Inches(13.333), Inches(7.5)

def base(prs, title, kicker):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = LIGHT
    bg.line.fill.background(); bg.shadow.inherit = False
    bar = s.shapes.add_shape(1, 0, 0, SW, Inches(1.15))
    bar.fill.solid(); bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background(); bar.shadow.inherit = False
    acc = s.shapes.add_shape(1, 0, Inches(1.15), SW, Pt(4))
    acc.fill.solid(); acc.fill.fore_color.rgb = CYAN
    acc.line.fill.background(); acc.shadow.inherit = False
    tf = bar.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.55); tf.margin_top = Inches(0.12)
    p = tf.paragraphs[0]; r = p.add_run(); r.text = kicker
    r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = CYAN
    p2 = tf.add_paragraph(); r2 = p2.add_run(); r2.text = title
    r2.font.size = Pt(26); r2.font.bold = True; r2.font.color.rgb = WHITE
    return s

def bullets(s, items, left=0.6, top=1.5, width=12.1, height=5.6, size=16, gap=6):
    # cap the box so it never reaches the footer band (footer sits at y=6.95)
    if top + height > 5.35:
        height = 5.35 - top
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for item in items:
        if isinstance(item, tuple):
            text, lvl = item
        else:
            text, lvl = item, 0
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = lvl
        p.space_after = Pt(gap)
        r = p.add_run()
        r.text = ("• " if lvl == 0 else "– ") + text if text else ""
        r.font.size = Pt(size if lvl == 0 else size - 2)
        r.font.color.rgb = NAVY if lvl == 0 else GREY
        if text and text.endswith(":") and lvl == 0:
            r.font.bold = True
    return tb

def cards(s, cards_def, top=1.6, height=2.4):
    n = len(cards_def)
    gap = 0.25
    w = (12.13 - gap * (n - 1)) / n
    for i, (head, body, color) in enumerate(cards_def):
        x = 0.6 + i * (w + gap)
        box = s.shapes.add_shape(1, Inches(x), Inches(top), Inches(w), Inches(height))
        box.fill.solid(); box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = RGBColor(0xDD, 0xE4, 0xEE); box.shadow.inherit = False
        tf = box.text_frame; tf.word_wrap = True
        tf.margin_left = Inches(0.15); tf.margin_top = Inches(0.12)
        p = tf.paragraphs[0]; r = p.add_run(); r.text = head
        r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = color
        p2 = tf.add_paragraph(); r2 = p2.add_run(); r2.text = body
        r2.font.size = Pt(11.5); r2.font.color.rgb = GREY

def table(s, rows, cols_data, top=1.5, left=0.6, width=12.1, col_w=None, fsize=11.5, height=None):
    rows_n = len(rows) + 1
    shp = s.shapes.add_table(rows_n, len(cols_data), Inches(left), Inches(top),
                             Inches(width), Inches(0.4 * rows_n))
    t = shp.table
    if col_w:
        total = sum(col_w)
        for i, cw in enumerate(col_w):
            t.columns[i].width = Emu(int(Inches(width) * cw / total))
    for j, h in enumerate(cols_data):
        c = t.cell(0, j); c.text = h
        c.fill.solid(); c.fill.fore_color.rgb = NAVY
        pr = c.text_frame.paragraphs[0]; pr.runs[0].font.size = Pt(fsize)
        pr.runs[0].font.bold = True; pr.runs[0].font.color.rgb = WHITE
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = str(val)
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if i % 2 else RGBColor(0xEA, 0xF0, 0xF9)
            pr = c.text_frame.paragraphs[0]; pr.runs[0].font.size = Pt(fsize)
            pr.runs[0].font.color.rgb = NAVY
    return t

def footer(s, text):
    tb = s.shapes.add_textbox(Inches(0.6), Inches(6.95), Inches(12.1), Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    r = p.add_run(); r.text = text
    r.font.size = Pt(10); r.font.color.rgb = GREY

def title_slide(prs, review_no, review_title, subtitle):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background(); bg.shadow.inherit = False
    mono = s.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(1.6), Inches(1.3))
    p = mono.text_frame.paragraphs[0]; r = p.add_run(); r.text = "DB"
    r.font.size = Pt(48); r.font.bold = True; r.font.color.rgb = CYAN
    tag = s.shapes.add_textbox(Inches(0.6), Inches(2.0), Inches(12.1), Inches(0.5))
    p = tag.text_frame.paragraphs[0]; r = p.add_run()
    r.text = f"DBMS PROJECT REPORT   ·   REVIEW {review_no}"
    r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = CYAN
    tt = s.shapes.add_textbox(Inches(0.6), Inches(2.5), Inches(12.1), Inches(1.7))
    tf = tt.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = review_title
    r.font.size = Pt(40); r.font.bold = True; r.font.color.rgb = WHITE
    st = s.shapes.add_textbox(Inches(0.6), Inches(4.0), Inches(12.1), Inches(0.6))
    p = st.text_frame.paragraphs[0]; r = p.add_run(); r.text = subtitle
    r.font.size = Pt(17); r.font.color.rgb = RGBColor(0xB9, 0xC6, 0xD8)
    who = s.shapes.add_textbox(Inches(0.6), Inches(5.4), Inches(12.1), Inches(1.6))
    tf = who.text_frame
    for i, (k, v) in enumerate([("PRESENTED BY", "Jampana Naga Satya Sai Rishvarma"),
                                ("STUDENT ID", "25WU0102105"),
                                ("PROGRAM", "B.Tech CSE (AI & ML)  ·  Woxsen University, Hyderabad")]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = f"{k}   {v}"
        r.font.size = Pt(13); r.font.bold = (i == 0)
        r.font.color.rgb = WHITE if i == 0 else RGBColor(0xB9, 0xC6, 0xD8)
    return s

# ================================================================
# REVIEW 2
# ================================================================
prs = Presentation()
prs.slide_width = SW; prs.slide_height = SH

title_slide(prs, 2,
            "Design, Implementation Progress &\nPrototype Demonstration",
            "Software License & Subscription Management System — Relational Database (MySQL 8)")

# Agenda
s = base(prs, "Agenda", "REVIEW 2")
cards(s, [
    ("01 · Design", "Finalized 3NF relational schema, integrity constraints and business-rule enforcement at the database level.", BLUE),
    ("02 · Implementation Progress", "Schema built and populated in MySQL 8; views, triggers and stored procedures implemented and verified.", CYAN),
    ("03 · Prototype Demonstration", "Working prototype walkthrough — allocation, expiry, compliance and cost reports.", GREEN),
], top=2.0, height=3.2)
footer(s, "Software License & Subscription Management System · Review 2")

# Finalized design
s = base(prs, "Finalized Relational Design — 3NF", "DESIGN")
bullets(s, [
    "12 tables across 4 modules: Procurement · Licensing · Organization · Compliance",
    "All transitive and partial dependencies removed; every non-key attribute depends on the key only",
    "Primary keys on every table; 10 foreign keys with ON UPDATE CASCADE / ON DELETE RESTRICT (or CASCADE for owned data)",
    "ENUM domains lock status and category values; UNIQUE constraints on license_key, emails, hostnames and invoice numbers",
], size=15, gap=10)
table(s, [
    ["Procurement", "VENDOR, SOFTWARE_PRODUCT, PURCHASE, RENEWAL"],
    ["Licensing", "LICENSE, LICENSE_TYPE, SUBSCRIPTION"],
    ["Organization", "DEPARTMENT, APP_USER, DEVICE"],
    ["Compliance", "ALLOCATION, COMPLIANCE_CHECK"],
], ["Module", "Tables"], top=4.1, height=1.8, col_w=[1, 3])
footer(s, "Single source of truth for the full license lifecycle: purchase → allocation → renewal → retirement")

# Business rules
s = base(prs, "Design Decisions — Business Rules in the Schema", "DESIGN")
table(s, [
    ["BR-01 / BR-02", "License must be ACTIVE and allocation date within validity", "Trigger BEFORE INSERT on ALLOCATION"],
    ["BR-03", "Seats allocated ≤ seats purchased per license", "Trigger counts active allocations vs total_seats"],
    ["BR-04", "Allocation period must be valid (return ≥ allocation)", "CHECK constraint + BEFORE UPDATE trigger"],
    ["Integrity", "Reclaim workflow sets status on return", "BEFORE UPDATE trigger sets RECLAIMED"],
    ["ACID", "Allocate / reclaim / renew run as transactions", "Stored procedures with COMMIT / ROLLBACK"],
], ["Rule", "Meaning", "Database Enforcement"], top=1.7, col_w=[1.2, 2.4, 2.6], fsize=12.5)
footer(s, "Rules are enforced at the database level, so no application layer can bypass them")

# Implementation stack
s = base(prs, "Implementation — Architecture & Stack", "IMPLEMENTATION PROGRESS")
cards(s, [
    ("Data Layer · MySQL 8", "12-table schema in database license_mgmt; 6 reporting views; 4 triggers; 4 stored procedures; CHECK & UNIQUE constraints.", BLUE),
    ("Scripts Delivered", "01_schema.sql · 02_seed.sql · 03_views_reports.sql · 04_procedures.sql · 05_demo_queries.sql + README with build steps.", CYAN),
    ("Verification Harness", "Schema, seed data, all views and the seat-limit trigger executed end-to-end; over-allocation attempt correctly rejected.", GREEN),
], top=1.8, height=2.6)
bullets(s, [
    "Seed dataset: 4 vendors, 6 products, 5 departments, 8 users, 6 purchases (₹3.18L), 6 licenses, 8 allocations",
    "Include realistic edge cases: reclaimed seats, expired licenses and inactive users for compliance testing",
], top=4.8, size=14)

# Progress table
s = base(prs, "Implementation Progress — Milestones vs Review 1 Plan", "IMPLEMENTATION PROGRESS")
table(s, [
    ["Normalize & implement 3NF schema", "DONE", "12 tables, PK/FK, CHECK + UNIQUE constraints"],
    ["Core database & CRUD operations", "DONE", "Seed data loaded; INSERT/UPDATE/DELETE flows validated"],
    ["Monitoring & compliance", "DONE", "Expiry monitor, compliance sweep procedure, reclaim workflow"],
    ["Reports & decision support", "DONE", "6 views: utilization, department, expiry, compliance, spend, renewals"],
    ["Testing, security & deployment", "IN PROGRESS", "Negative tests passing; RBAC & backup docs planned for Review 3"],
], ["Review 1 Planned Milestone", "Status", "Evidence"], top=1.8, col_w=[2.2, 0.9, 3.4], fsize=12.5)
footer(s, "All four Review 1 milestones for design & implementation are complete; testing wraps up before Review 3")

# Prototype demo 1
s = base(prs, "Prototype Demonstration — Monitoring & Compliance", "PROTOTYPE DEMO")
cards(s, [
    ("v_expiry_monitor", "Bands every license: EXPIRED / CRITICAL <30d / WARNING <90d / OK, with days-to-expiry computed in SQL.", AMBER),
    ("v_compliance_violations", "Flags EXPIRED_LICENSE, UNASSIGNED_DEVICE and USER_INACTIVE across all active allocations.", AMBER),
    ("sp_run_compliance_check", "Sweeps every active allocation and writes dated audit rows into COMPLIANCE_CHECK.", AMBER),
], top=1.8, height=2.7)
bullets(s, [
    "Demo query set: EXPIRED + WARNING licenses, compliance findings, dated audit trail (FR04 · FR05)",
    "Live check: 4 licenses past validity correctly flagged; audit rows persisted with check date and status",
], top=4.9, size=14)

# Prototype demo 2
s = base(prs, "Prototype Demonstration — Workflows & Reports", "PROTOTYPE DEMO")
table(s, [
    ["Allocate license", "CALL sp_allocate_license(3, 4, 4, ...)", "Seat granted; utilization view updates (FR02)"],
    ["Over-allocation blocked", "INSERT beyond seats → SIGNAL", "BR-03 trigger aborts with clear error (FR02)"],
    ["Reclaim license", "CALL sp_reclaim_license(8, ...)", "Seat returned, status RECLAIMED (FR03)"],
    ["Renew license", "CALL sp_renew_license(3, 50000, ...)", "Renewal row + validity extended atomically (FR06)"],
    ["Utilization & spend", "v_license_utilization · v_vendor_spend", "Seats free %, lifetime vendor spend (FR07)"],
], ["Workflow", "Command", "Result"], top=1.8, col_w=[1.6, 2.4, 2.9], fsize=12.5)
footer(s, "Every functional requirement FR01–FR08 now has a working database-backed path")

# Next steps
s = base(prs, "Remaining Plan — Toward Review 3", "NEXT STEPS")
cards(s, [
    ("Testing & Hardening", "Edge-case suite: boundary seats, concurrent allocation, cascade behaviour; record pass/fail evidence.", BLUE),
    ("Security & Access", "Role-based access for IT Admin, Procurement, Compliance; restrict license keys to authorized roles.", CYAN),
    ("Documentation", "Final report: schema diagrams, README, user guide, test results and deployment notes.", GREEN),
], top=2.0, height=3.0)
footer(s, "Review 3 will present the finished system: final demonstration + complete documentation")

prs.save(os.path.join(OUT_DIR, "ppt_review2.pptx"))

# ================================================================
# REVIEW 3
# ================================================================
prs = Presentation()
prs.slide_width = SW; prs.slide_height = SH

title_slide(prs, 3,
            "Final Project Demonstration &\nDocumentation",
            "Software License & Subscription Management System — Complete Delivered Product (MySQL 8)")

s = base(prs, "Agenda", "REVIEW 3")
cards(s, [
    ("01 · Final Demonstration", "End-to-end product walkthrough — every FR01–FR08 requirement executed live on the built database.", BLUE),
    ("02 · Business Rule Validation", "Negative tests proving integrity is enforced at the database level, not in the application.", CYAN),
    ("03 · Documentation", "Complete deliverables: SQL build scripts, README, test evidence and user guide.", GREEN),
], top=2.0, height=3.2)
footer(s, "Software License & Subscription Management System · Review 3")

s = base(prs, "Delivered System — Requirements Coverage", "FINAL DELIVERY")
table(s, [
    ["FR01", "Record purchases", "PURCHASE rows with vendor/product/cost; UNIQUE invoice numbers", "✅"],
    ["FR02", "Allocate licenses", "sp_allocate_license + seat-limit trigger", "✅"],
    ["FR03", "Reclaim licenses", "sp_reclaim_license sets RECLAIMED via return date", "✅"],
    ["FR04", "Monitor expiry", "v_expiry_monitor with CRITICAL/WARNING/EXPIRED bands", "✅"],
    ["FR05", "Compliance checks", "v_compliance_violations + sp_run_compliance_check audit trail", "✅"],
    ["FR06", "Renewals & cost", "sp_renew_license, v_upcoming_renewals, renewal spend in v_vendor_spend", "✅"],
    ["FR07", "Utilization reports", "v_license_utilization, v_department_allocations", "✅"],
    ["FR08", "Search & audit history", "Allocation lifecycle query by user/license with full history", "✅"],
], ["Req", "Requirement", "Implemented As", "Done"], top=1.7, col_w=[0.6, 1.8, 3.6, 0.5], fsize=11.5)
footer(s, "All eight functional requirements from the Review 1 SRS are implemented and demonstrated")

s = base(prs, "Final Demonstration — Live Walkthrough", "FINAL DEMONSTRATION")
cards(s, [
    ("Act 1 · Data Foundation", "Build database from 5 SQL scripts; show schema, seed data and referential integrity across 12 tables.", BLUE),
    ("Act 2 · Lifecycle Workflows", "Purchase → allocate → reclaim → renew executed as ACID transactions via stored procedures.", CYAN),
    ("Act 3 · Insight & Audit", "Utilization, expiry, compliance, vendor-spend and upcoming-renewal reports; compliance sweep audit trail.", GREEN),
], top=1.8, height=2.7)
bullets(s, [
    "Demo script 05_demo_queries.sql runs 12 numbered demonstrations in sequence — repeatable and self-contained",
    "Sample results shown in review: JetBrains ₹1.7L lifetime spend; Office 365 at 8% utilization; 4 expired licenses flagged",
], top=4.9, size=14)

s = base(prs, "Implementation — Architecture & Build", "IMPLEMENTATION")
cards(s, [
    ("Database Layer · MySQL 8", "12-table 3NF schema (license_mgmt): PK/FK graph, CHECK & UNIQUE constraints, ENUM domains, 4 triggers enforcing BR-01…BR-04 on every write.", BLUE),
    ("Logic Layer · SQL Objects", "6 reporting views (utilization, department, expiry, compliance, vendor spend, renewals) + 5 stored procedures: allocate, reclaim, renew, compliance sweep, status sync — all ACID.", CYAN),
    ("Application Layer · Streamlit", "Python UI over the same views and procedures; dual engine (MySQL or bundled SQLite demo) so the prototype runs with zero external setup.", GREEN),
], top=1.6, height=2.25)
table(s, [
    ["sql/01_schema.sql", "DDL: 12 tables, constraints, triggers"],
    ["sql/02_seed.sql", "4 vendors, 6 products, 8 users, 6 purchases (₹3.18L), 8 allocations"],
    ["sql/03_views_reports.sql", "6 reporting views incl. effective-status expiry monitor"],
    ["sql/04_procedures.sql", "5 transactional stored procedures"],
    ["sql/05_demo_queries.sql", "12-step repeatable demonstration script"],
    ["app.py + crud.py + db.py", "Streamlit UI, CRUD diff-engine, dual-engine connection"],
    ["data/app.db + scripts/", "SQLite demo mirror (identical schema, views, triggers)"],
], ["Artifact", "Contents"], top=4.15, col_w=[1.6, 3.2], fsize=10)
footer(s, "Full source of truth: every artifact is versionable plain text — schema, rules, data and UI")

s = base(prs, "Implementation — Module Breakdown", "IMPLEMENTATION")
table(s, [
    ["Procurement", "VENDOR · SOFTWARE_PRODUCT · PURCHASE · RENEWAL", "CRUD forms + renewal workflow extends license validity atomically"],
    ["Licensing", "LICENSE · LICENSE_TYPE · SUBSCRIPTION", "Unique license keys, seat counts, validity windows, billing cycles"],
    ["Organization", "DEPARTMENT · APP_USER · DEVICE", "Roles (IT Admin, Manager, Procurement, Compliance, Employee)"],
    ["Compliance", "ALLOCATION · COMPLIANCE_CHECK", "Triggers BR-01…BR-04 + dated audit trail per allocation"],
    ["Reporting", "6 SQL views", "Live-computed KPIs: utilization %, expiry bands, lifetime spend"],
], ["Module", "Tables", "Delivered Behaviour"], top=1.7, col_w=[1.1, 2.4, 3.4], fsize=12)
bullets(s, [
    "Every business rule enforced at the DATABASE level (triggers/constraints) — no application bypass possible",
    "Workflows run as transactions: allocate/reclaim/renew either fully commit or fully roll back (ACID)",
], top=5.0, size=13)
footer(s, "Modules map 1:1 to the Review 1 conceptual design — traceability from ER model to shipped artifacts")

s = base(prs, "Application Features — Web UI (Streamlit)", "APPLICATION FEATURES")
cards(s, [
    ("📊 Dashboard", "Live KPIs (licenses, seats, utilization %), color-banded expiry monitor, vendor spend chart, upcoming renewals.", BLUE),
    ("🔁 Workflows", "Allocate seats (only valid, non-full licenses offered), reclaim seats — rejected actions surface trigger errors in the browser.", CYAN),
    ("✅ Compliance", "One-click sweep writes dated audit rows; violations (expired / unassigned / inactive user) highlighted in red.", GREEN),
], top=1.7, height=2.6)
cards(s, [
    ("🛒 Purchases & Renewals", "Record purchases with unique invoices; renewal form extends validity and flips status back to ACTIVE in one transaction.", BLUE),
    ("⚙️ Manage Data", "Full CRUD on ALL 12 tables: add forms with FK dropdowns & date/enum pickers, spreadsheet-style edits, multi-row delete.", CYAN),
    ("🛡️ Integrity UX", "BR-01…BR-04, UNIQUE and FK rules enforced by the DB; every violation shows as a clear error toast — zero silent failures.", GREEN),
], top=4.5, height=2.2)

s = base(prs, "Application Implementation Notes", "APPLICATION FEATURES")
bullets(s, [
    "Dual-engine access: auto-detects MySQL 8 (LM_DB_* env vars), falls back to a bundled SQLite mirror with identical schema, views and triggers",
    "crud.py change-diffing: spreadsheet edits write only changed cells (verified 1 change → 1 UPDATE; no changes → 0)",
    "Expiry consistency: dashboard syncs stored status with validity dates on load; view exposes effective vs stored status",
    "Constrained forms: allocatable licenses = ACTIVE + unexpired + seats free; FK dropdowns list only real rows",
    "Unique widget keys across all 12 admin tabs (59 keys) — no duplicate-ID errors, stable state",
    "Verified headlessly: allocate→edit→reclaim round trip; BR-02/BR-03/UNIQUE/FK rejections surfaced; data restored after tests",
], size=14, gap=9)
footer(s, "Running prototype: streamlit run app.py → http://localhost:8602 (demo DB) or MySQL via LM_DB_* env vars")

# ---- screenshot slides -------------------------------------------------
import os
SHOTPOS = {
    "dashboard.png":   "Dashboard — KPIs, expiry monitor, vendor spend",
    "workflows.png":   "Allocations — allocate & reclaim seats",
    "compliance.png":  "Compliance — violations & audit trail",
    "procurement.png": "Purchases & Renewals — procurement forms",
    "manage_add.png":  "Manage Data — add-row form with FK dropdowns",
}
assert all(os.path.exists(f"screenshots/{k}") for k in SHOTPOS), "missing screenshot"
names = list(SHOTPOS)
for grp in (names[:3], names[3:]):
    s = base(prs, "Application Screenshots", "APPLICATION FEATURES")
    for i, fname in enumerate(grp):
        if len(grp) == 3:                # three across
            x, y, w = 0.6 + i * 4.05, 2.2, 3.8
        else:                            # two across, larger
            x, y, w = 0.6 + i * 6.05, 1.9, 5.8
        h = w * 1000 / 1600              # keep capture aspect 1600×1000
        s.shapes.add_picture(f"screenshots/{fname}", Inches(x), Inches(y),
                             width=Inches(w), height=Inches(h))
        cap = s.shapes.add_textbox(Inches(x), Inches(y + h + 0.02),
                                   Inches(w), Inches(0.3))
        cp = cap.text_frame.paragraphs[0]
        cr = cp.add_run(); cr.text = SHOTPOS[fname]
        cr.font.size = Pt(11); cr.font.bold = True; cr.font.color.rgb = NAVY
    footer(s, "Live capture from the running prototype — streamlit run app.py")

s = base(prs, "Business Rule Validation — Negative Test Evidence", "FINAL DEMONSTRATION")
table(s, [
    ["Over-allocate beyond purchased seats", "INSERT into ALLOCATION at seat limit", "Aborted — 'BR-03 violated: all purchased seats allocated'", "PASS"],
    ["Allocate on non-ACTIVE license", "INSERT against expired/revoked license", "Aborted by trigger BR-01", "PASS"],
    ["Return date before allocation date", "UPDATE ALLOCATION with earlier return", "Aborted by BR-04 CHECK + trigger", "PASS"],
    ["Duplicate license key / invoice", "INSERT duplicate key", "Rejected by UNIQUE constraint", "PASS"],
    ["Reclaim non-active allocation", "CALL sp_reclaim_license on RECLAIMED row", "Aborted — 'Allocation not found or not ACTIVE'", "PASS"],
], ["Scenario", "Attempted Operation", "Observed Behaviour", "Result"], top=1.7, col_w=[2.1, 2.3, 3.3, 0.6], fsize=11.5)
footer(s, "Integrity holds even when rules are deliberately violated — database-level enforcement proven")

s = base(prs, "Documentation — Final Deliverables", "DOCUMENTATION")
cards(s, [
    ("sql/01_schema.sql", "Complete 3NF DDL: 12 tables, PK/FK graph, CHECK & UNIQUE constraints, 4 triggers, business rules BR-01…BR-04.", BLUE),
    ("sql/02–05 scripts", "Seed dataset, 6 reporting views, 4 stored procedures and a 12-step demonstration script with README build instructions.", CYAN),
    ("Review decks 1–3", "Requirement analysis → design & implementation → final demonstration; full project narrative for evaluation.", GREEN),
], top=1.8, height=2.7)
bullets(s, [
    "README.md documents build order, requirements (MySQL 8), enforced business rules and verification results",
    "Verification evidence: schema + seed + views executed end-to-end; negative tests recorded with observed errors",
], top=4.9, size=14)

s = base(prs, "Testing Summary & Reliability", "DOCUMENTATION")
table(s, [
    ["Schema build", "12/12 tables created; all constraints attached", "PASS"],
    ["Seed data", "4 vendors, 6 products, 6 purchases, 6 licenses, 8 allocations loaded", "PASS"],
    ["Reporting views", "6/6 views return correct aggregates vs manual checks", "PASS"],
    ["Workflows", "Allocate / reclaim / renew transactions commit or roll back cleanly", "PASS"],
    ["Negative tests", "Seat limit, expiry, date-order, duplicate-key violations all blocked", "PASS"],
    ["Backups", "mysqldump scheduled backup procedure documented in README", "PLANNED"],
], ["Test Area", "Coverage", "Status"], top=1.8, col_w=[1.8, 4.2, 0.8], fsize=12.5)
footer(s, "Reports return in well under a second on the demo dataset — NFR performance target met")

s = base(prs, "Conclusion & Future Scope", "CONCLUSION")
bullets(s, [
    "Centralized single source of truth for every license, subscription, allocation and renewal across departments",
    "Business rules enforced inside the database — unique keys, seat limits, valid periods and ACID workflows",
    "Proactive monitoring: expiry bands, automated compliance sweeps and dated audit history",
    "Decision support: utilization percentages, department usage and lifetime vendor spend for renewal planning",
], size=15, gap=8)
bullets(s, [
    "Web dashboard for department managers and end users on top of the database layer",
    "Email/Slack alerts for CRITICAL expiry band; RBAC integration with campus SSO",
    "SaaS API ingestion for automatic usage and true-up reconciliation",
], top=4.6, size=14)
footer(s, "Thank you — Questions? · Jampana Naga Satya Sai Rishvarma · 25WU0102105 · Woxsen University")

prs.save(os.path.join(OUT_DIR, "ppt_review3.pptx"))
print(f"saved {OUT_DIR}/ppt_review2.pptx and {OUT_DIR}/ppt_review3.pptx")
