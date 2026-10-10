"""Streamlit UI for the Software License & Subscription Management System.

Full CRUD build: every table can be created, edited and deleted from the UI,
in addition to the workflow pages (allocate / reclaim / renew / compliance).

Run:  streamlit run app.py
Data: MySQL 8 (set LM_DB_* env vars) or the bundled SQLite demo (data/app.db).
"""
import datetime
import pandas as pd
import streamlit as st

import crud
import db

st.set_page_config(page_title="License Management System",
                   page_icon="🗄️", layout="wide")

NAVY = "#0E1A2B"
st.markdown(f"""<style>
.block-container {{ padding-top: 1.4rem; }}
h1 {{ color: {NAVY}; }}
</style>""", unsafe_allow_html=True)


def header(title, subtitle=""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def err_box(e, action):
    msg = str(e)
    if ("BR-0" in msg or "violated" in msg.lower() or "UNIQUE" in msg.upper()
            or "CHECK" in msg.upper() or "FOREIGN KEY" in msg.upper()
            or "Restric" in msg or "constraint" in msg.lower()):
        st.error(f"🚫 Rejected by the database — {msg}")
    else:
        st.error(f"{action} failed: {msg}")


def grd(name, minimum=0.0, value=0.0, step=100.0, key=""):
    return st.number_input(name, min_value=minimum, value=value, step=step,
                           key=key)


def not_null(msg="Required"):
    st.error(msg)


# ================================================================ DASHBOARD
def page_dashboard():
    header("Dashboard", "Single source of truth for licenses, seats and spend")
    util = db.q("SELECT * FROM v_license_utilization")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Licenses", len(util))
    c2.metric("Seats purchased", int(util.total_seats.sum()))
    c3.metric("Seats in use", int(util.seats_active.sum()))
    c4.metric("Avg utilization %", f"{util.utilization_pct.mean():.1f}")

    st.subheader("Expiry monitor")
    # sync stored status with reality: ACTIVE licenses past validity -> EXPIRED
    try:
        db.execute("UPDATE LICENSE SET status='EXPIRED' "
                   "WHERE status='ACTIVE' AND valid_until < ?", (db.today(),))
    except Exception:
        pass  # read-only or transient connection issue; view still computed
    exp = db.q("SELECT * FROM v_expiry_monitor ORDER BY days_to_expiry")
    st.dataframe(exp.style.map(
        lambda v: ("background-color:#FFD9D9" if v == "EXPIRED"
                   else "background-color:#FFE8C2" if v.startswith("CRITICAL")
                   else "background-color:#FFF3C2" if v.startswith("WARNING")
                   else ""), subset=["expiry_band"]),
        use_container_width=True, hide_index=True)

    l, r = st.columns(2)
    with l:
        st.subheader("Upcoming renewals")
        st.dataframe(db.q("SELECT * FROM v_upcoming_renewals"),
                     use_container_width=True, hide_index=True)
    with r:
        st.subheader("Vendor lifetime spend (₹)")
        spend = db.q("SELECT * FROM v_vendor_spend ORDER BY lifetime_spend DESC")
        st.dataframe(spend, use_container_width=True, hide_index=True)
        st.bar_chart(spend.set_index("vendor_name")[["purchase_spend",
                                                     "renewal_spend"]])


# ================================================================ WORKFLOWS
def page_allocations():
    header("Allocations & Workflows",
           "Allocate · Reclaim seats — BR-01…BR-04 enforced by DB triggers")
    alloc = db.q("""
        SELECT a.allocation_id, p.product_name, u.user_name,
               d.department_name, a.allocation_date, a.return_date, a.status,
               a.notes
          FROM ALLOCATION a
          JOIN LICENSE l ON l.license_id = a.license_id
          JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
          JOIN APP_USER u ON u.user_id = a.user_id
          JOIN DEPARTMENT d ON d.department_id = u.department_id
         ORDER BY a.allocation_id DESC""")
    st.dataframe(alloc, use_container_width=True, hide_index=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("➕ Allocate a seat")
        licenses = db.q("""SELECT license_id, product_name, license_key, seats_free
            FROM v_license_utilization
            WHERE days_to_expiry >= 0 AND seats_free > 0 ORDER BY product_name""")
        users = db.q("SELECT user_id, user_name FROM APP_USER ORDER BY user_name")
        devices = db.q("SELECT device_id, hostname FROM DEVICE ORDER BY hostname")
        if licenses.empty:
            st.info("No allocatable license (all expired or full). "
                    "Add one under Manage Data → LICENSE.")
        with st.form("allocate_form"):
            lic = st.selectbox("License", licenses.to_dict("records"),
                format_func=lambda r: f"#{r['license_id']} · {r['product_name']}"
                                      f" — {r['seats_free']} free")
            usr = st.selectbox("User", users.to_dict("records"),
                format_func=lambda r: f"#{r['user_id']} · {r['user_name']}")
            dev = st.selectbox("Device (optional)",
                               [None] + devices.to_dict("records"),
                format_func=lambda r: "— none —" if r is None
                                      else f"{r['hostname']} (#{r['device_id']})")
            notes = st.text_input("Notes")
            if st.form_submit_button("Allocate", type="primary"):
                try:
                    db.execute(
                        "INSERT INTO ALLOCATION (license_id,user_id,device_id,"
                        "allocation_date,status,notes) VALUES (?,?,?,?,'ACTIVE',?)",
                        (lic["license_id"], usr["user_id"],
                         dev["device_id"] if dev else None,
                         db.today(), notes or None))
                    st.success("Seat allocated ✔"); st.rerun()
                except Exception as e:
                    err_box(e, "Allocation")

    with c2:
        st.subheader("↩️ Reclaim a seat")
        active = alloc[alloc.status == "ACTIVE"]
        if active.empty:
            st.info("No active allocations.")
        else:
            with st.form("reclaim_form"):
                row = st.selectbox("Active allocation",
                    active.to_dict("records"),
                    format_func=lambda r: (f"#{r['allocation_id']} · "
                    f"{r['product_name']} — {r['user_name']}"))
                remark = st.text_input("Reason")
                if st.form_submit_button("Reclaim", type="primary"):
                    try:
                        db.execute(
                            "UPDATE ALLOCATION SET return_date=?,"
                            " status='RECLAIMED', notes=COALESCE(notes||' | ','')||?"
                            " WHERE allocation_id=? AND status='ACTIVE'",
                            (db.today(), f"Reclaimed: {remark or ''}",
                             row["allocation_id"]))
                        st.success("Seat reclaimed ✔"); st.rerun()
                    except Exception as e:
                        err_box(e, "Reclaim")


def page_compliance():
    header("Compliance",
           "Live violations + dated audit trail (COMPLIANCE_CHECK)")
    v = db.q("SELECT * FROM v_compliance_violations")
    bad = v[v.compliance_status != "PASS"]
    st.dataframe(bad.style.map(
        lambda c: "background-color:#FFD9D9" if c != "PASS" else "",
        subset=["compliance_status"]),
        use_container_width=True, hide_index=True)
    st.caption(f"{len(bad)} violation(s) across {len(v)} active allocation(s)")

    if st.button("🔍 Run compliance sweep", type="primary"):
        try:
            db.execute("""INSERT INTO COMPLIANCE_CHECK
                (allocation_id, check_date, check_status, remarks)
                SELECT allocation_id, ?, compliance_status, 'Sweep from UI'
                  FROM v_compliance_violations""", (db.today(),))
            st.success("Compliance sweep recorded ✔"); st.rerun()
        except Exception as e:
            err_box(e, "Compliance sweep")

    st.subheader("Audit history")
    st.dataframe(db.q("""
        SELECT c.check_id, a.allocation_id, p.product_name, u.user_name,
               c.check_date, c.check_status, c.remarks
          FROM COMPLIANCE_CHECK c
          JOIN ALLOCATION a ON a.allocation_id = c.allocation_id
          JOIN LICENSE l ON l.license_id = a.license_id
          JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
          JOIN APP_USER u ON u.user_id = a.user_id
         ORDER BY c.check_id DESC"""),
        use_container_width=True, hide_index=True)


def page_procurement():
    header("Purchases & Renewals", "Record purchases · renew licenses (FR01, FR06)")

    st.subheader("Record a new purchase")
    vendors = db.q("SELECT vendor_id, vendor_name FROM VENDOR ORDER BY vendor_name")
    products = db.q("SELECT product_id, product_name FROM SOFTWARE_PRODUCT ORDER BY product_name")
    with st.form("purchase_form"):
        a, b, c = st.columns(3)
        ven = a.selectbox("Vendor", vendors.to_dict("records"),
                          format_func=lambda r: r["vendor_name"])
        pro = b.selectbox("Product", products.to_dict("records"),
                          format_func=lambda r: r["product_name"])
        pdate = c.date_input("Purchase date", value=datetime.date.today())
        a, b, c = st.columns(3)
        qty = a.number_input("Quantity", min_value=1, value=1)
        unit = b.number_input("Unit cost (₹)", min_value=0.0, value=1000.0, step=100.0)
        total = c.number_input("Total cost (₹)", min_value=0.0,
                               value=float(qty * unit), step=100.0)
        inv = st.text_input("Invoice number (unique)")
        if st.form_submit_button("Save purchase", type="primary"):
            try:
                crud.insert("PURCHASE", dict(
                    vendor_id=ven["vendor_id"], product_id=pro["product_id"],
                    purchase_date=pdate.isoformat(), quantity=int(qty),
                    unit_cost=float(unit), total_cost=float(total),
                    invoice_no=inv or None))
                st.success("Purchase recorded ✔"); st.rerun()
            except Exception as e:
                err_box(e, "Purchase")

    st.subheader("Renew a license")
    purch = db.q("""SELECT pu.purchase_id, p.product_name, l.license_id, l.valid_until
        FROM PURCHASE pu JOIN SOFTWARE_PRODUCT p ON p.product_id = pu.product_id
        JOIN LICENSE l ON l.purchase_id = pu.purchase_id ORDER BY pu.purchase_id""")
    with st.form("renew_form"):
        row = st.selectbox("Purchase", purch.to_dict("records"),
            format_func=lambda r: f"#{r['purchase_id']} · {r['product_name']}"
                                  f" — valid until {r['valid_until']}")
        amount = st.number_input("Renewal amount (₹)", min_value=0.0,
                                 value=50000.0, step=1000.0)
        new_until = st.date_input("New valid until")
        remarks = st.text_input("Remarks")
        if st.form_submit_button("Renew", type="primary"):
            try:
                db.execute("INSERT INTO RENEWAL (purchase_id, renewal_date,"
                           " renewal_amount, new_valid_until, remarks)"
                           " VALUES (?,?,?,?,?)",
                           (row["purchase_id"], db.today(), float(amount),
                            new_until.isoformat(), remarks or None))
                db.execute("UPDATE LICENSE SET valid_until=?, status='ACTIVE'"
                           " WHERE purchase_id=?",
                           (new_until.isoformat(), row["purchase_id"]))
                st.success("Renewal recorded ✔"); st.rerun()
            except Exception as e:
                err_box(e, "Renewal")

    st.subheader("All purchases")
    st.dataframe(db.q("""SELECT pu.purchase_id, v.vendor_name, p.product_name,
            pu.purchase_date, pu.quantity, pu.unit_cost, pu.total_cost,
            pu.invoice_no FROM PURCHASE pu
            JOIN VENDOR v ON v.vendor_id = pu.vendor_id
            JOIN SOFTWARE_PRODUCT p ON p.product_id = pu.product_id
            ORDER BY pu.purchase_id"""),
        use_container_width=True, hide_index=True)
    st.subheader("Renewal history")
    st.dataframe(db.q("SELECT * FROM RENEWAL ORDER BY renewal_id DESC"),
                 use_container_width=True, hide_index=True)


# ================================================================ ADMIN CRUD
TABLES = {
    "VENDOR": dict(pk="vendor_id",
        cols=["vendor_name", "contact_email", "support_phone", "address"],
        edit=["vendor_name", "contact_email"]),
    "LICENSE_TYPE": dict(pk="license_type_id", cols=["type_name", "description"]),
    "SOFTWARE_PRODUCT": dict(pk="product_id",
        cols=["vendor_id", "product_name", "category", "latest_version"]),
    "PURCHASE": dict(pk="purchase_id",
        cols=["vendor_id", "product_id", "purchase_date", "quantity",
              "unit_cost", "total_cost", "invoice_no"]),
    "LICENSE": dict(pk="license_id",
        cols=["product_id", "license_type_id", "license_key", "total_seats",
              "valid_from", "valid_until", "status", "purchase_id"],
        edit=["total_seats", "status"]),
    "SUBSCRIPTION": dict(pk="subscription_id",
        cols=["license_id", "billing_cycle", "start_date", "end_date",
              "amount", "auto_renew"]),
    "DEPARTMENT": dict(pk="department_id",
        cols=["department_name", "head_name", "annual_it_budget"]),
    "APP_USER": dict(pk="user_id",
        cols=["department_id", "user_name", "email", "user_role", "is_active"],
        edit=["user_role", "is_active"]),
    "DEVICE": dict(pk="device_id",
        cols=["user_id", "device_type", "hostname", "os_name"]),
    "ALLOCATION": dict(pk="allocation_id",
        cols=["license_id", "user_id", "device_id", "allocation_date",
              "return_date", "status", "notes"]),
    "RENEWAL": dict(pk="renewal_id",
        cols=["purchase_id", "renewal_date", "renewal_amount",
              "new_valid_until", "remarks"]),
    "COMPLIANCE_CHECK": dict(pk="check_id",
        cols=["allocation_id", "check_date", "check_status", "remarks"]),
}


def page_admin():
    header("Manage Data", "Create, edit and delete rows in every table — "
                          "database constraints still guard each change")
    tabs = st.tabs(list(TABLES))
    for tab, (table, spec) in zip(tabs, TABLES.items()):
        with tab:
            _table_tab(table, spec)


def _table_tab(table, spec):
    pk = spec["pk"]
    df = crud.get_table(table)

    with st.expander(f"➕ Add a row to {table}", expanded=df.empty):
        vals = {}
        cols = st.columns(3)
        for i, col in enumerate(spec["cols"]):
            vals[col] = _input_widget(table, col, cols[i % 3],
                                      key=f"inp_{table}_{col}")
        if st.button("Save", key=f"save_{table}", type="primary"):
            clean = {k: v for k, v in vals.items() if v not in (None, "")}
            if (table in ("VENDOR", "LICENSE_TYPE", "DEPARTMENT")
                    and len(clean) < len(spec["cols"]) - 1):
                not_null()
            else:
                try:
                    crud.insert(table, clean)
                    st.success("Row added ✔"); st.rerun()
                except Exception as e:
                    err_box(e, "Insert")

    with st.expander(f"✏️ Edit rows in {table}"):
        if df.empty:
            st.info("Table is empty.")
        else:
            editable_cols = spec.get("edit", [c for c in df.columns if c != pk])
            with st.form(f"edit_{table}"):
                edited = st.data_editor(df, key=f"ed_{table}",
                    disabled=[c for c in df.columns if c not in editable_cols],
                    use_container_width=True, hide_index=True,
                    num_rows="fixed")
                if st.form_submit_button("Apply changes", type="primary"):
                    try:
                        n = crud.apply_edits(table, pk, df, edited)
                        st.success(f"{n} row(s) updated ✔"); st.rerun()
                    except Exception as e:
                        err_box(e, "Update")

    with st.expander(f"🗑️ Delete rows from {table}"):
        if df.empty:
            st.info("Table is empty.")
        else:
            sel = st.multiselect("Select rows to delete", df[pk],
                                 format_func=lambda v: f"#{v}",
                                 key=f"del_{table}")
            if st.button("Delete selected", key=f"delbtn_{table}",
                         type="primary"):
                try:
                    crud.delete_rows(table, pk, sel)
                    st.success("Deleted ✔"); st.rerun()
                except Exception as e:
                    err_box(e, "Delete")


def _input_widget(table, col, slot, key=""):
    if col in ("auto_renew", "is_active"):
        return slot.checkbox(col, value=True, key=key)
    if col in ("quantity", "total_seats"):
        return slot.number_input(col, min_value=1, value=1, key=key)
    if col in ("unit_cost", "total_cost", "renewal_amount", "amount",
               "annual_it_budget"):
        return slot.number_input(col, min_value=0.0, value=1000.0, step=100.0,
                                 key=key)
    if col.endswith("_date"):
        d = slot.date_input(col, value=datetime.date.today(), key=key)
        return d.isoformat()
    if col in ("vendor_id", "product_id", "license_type_id", "department_id",
               "user_id", "device_id", "purchase_id", "license_id",
               "allocation_id"):
        fks = {
            "vendor_id": ("VENDOR", "vendor_id", "vendor_name"),
            "product_id": ("SOFTWARE_PRODUCT", "product_id", "product_name"),
            "license_type_id": ("LICENSE_TYPE", "license_type_id", "type_name"),
            "department_id": ("DEPARTMENT", "department_id", "department_name"),
            "user_id": ("APP_USER", "user_id", "user_name"),
            "device_id": ("DEVICE", "device_id", "hostname"),
            "purchase_id": ("PURCHASE", "purchase_id", "purchase_id"),
            "license_id": ("LICENSE", "license_id", "license_key"),
            "allocation_id": ("ALLOCATION", "allocation_id", "allocation_id"),
        }
        reftab, refpk, refcol = fks[col]
        options = [None] + db.q(
            f"SELECT {refpk} FROM {reftab}").iloc[:, 0].tolist()
        idx = slot.selectbox(f"{col} (FK → {reftab})", options, key=key,
                             format_func=lambda v: "— NULL —" if v is None
                                                   else f"#{v}")
        return idx
    if col in ("status",):
        return slot.selectbox(col, ["ACTIVE", "EXPIRED", "REVOKED"], key=key)
    if col in ("check_status",):
        return slot.selectbox(col, ["PASS", "OVERALLOCATED", "EXPIRED_LICENSE",
                                    "UNASSIGNED_DEVICE", "USER_INACTIVE"],
                              key=key)
    if col in ("billing_cycle",):
        return slot.selectbox(col, ["MONTHLY", "QUARTERLY", "ANNUAL"], key=key)
    if col in ("device_type",):
        return slot.selectbox(col, ["LAPTOP", "DESKTOP", "WORKSTATION",
                                    "MOBILE", "SERVER"], key=key)
    if col in ("user_role",):
        return slot.selectbox(col, ["EMPLOYEE", "IT_ADMIN", "DEPT_MANAGER",
                                    "PROCUREMENT", "COMPLIANCE_OFFICER"],
                              key=key)
    return slot.text_input(col, key=key)


# ================================================================ ROUTER
pages = {
    "📊 Dashboard": page_dashboard,
    "🔁 Allocations & Workflows": page_allocations,
    "✅ Compliance": page_compliance,
    "🛒 Purchases & Renewals": page_procurement,
    "⚙️ Manage Data": page_admin,
}

st.sidebar.title("🗄️ License Management")
st.sidebar.caption("Software License & Subscription Management System\n\n"
                   "DBMS Project · Woxsen University · Full CRUD build")
choice = st.sidebar.radio("Navigation", list(pages.keys()),
                          label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Business rules enforced at the DB level:\n"
                   "BR-01 active license · BR-02 within validity · "
                   "BR-03 seat limit · BR-04 valid period")

pages[choice]()
