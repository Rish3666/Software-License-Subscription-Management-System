"""Streamlit UI for the Software License & Subscription Management System.

Run:  streamlit run app.py
Data: MySQL 8 (set LM_DB_* env vars) or the bundled SQLite demo (data/app.db).
"""
import pandas as pd
import streamlit as st

import db

st.set_page_config(page_title="License Management System",
                   page_icon="🗄️", layout="wide")

NAVY = "#0E1A2B"

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.4rem; }}
      h1 {{ color: {NAVY}; }}
      .metric-card {{ font-size: 0.9rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def header(title, subtitle=""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def err_box(e, action):
    msg = str(e)
    if "BR-0" in msg or "violated" in msg.lower() or "CHECK" in msg.upper():
        st.error(f"🚫 Rejected by the database — {msg}")
    else:
        st.error(f"{action} failed: {msg}")


# ---------------------------------------------------------------- pages
def page_dashboard():
    header("Dashboard", "Single source of truth for licenses, seats and spend")

    kind = db.engine_kind()
    st.caption(f"Connected to: **{kind.upper()}**"
               + (" — demo SQLite mirror (set LM_DB_* env vars for MySQL)"
                  if kind == "sqlite" else " — database `license_mgmt`"))

    util = db.q("SELECT * FROM v_license_utilization")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Licenses", len(util))
    c2.metric("Seats purchased", int(util.total_seats.sum()))
    c3.metric("Seats in use", int(util.seats_active.sum()))
    c4.metric("Avg utilization %", f"{util.utilization_pct.mean():.1f}")

    st.subheader("Expiry monitor")
    exp = db.q("SELECT * FROM v_expiry_monitor ORDER BY days_to_expiry")
    st.dataframe(
        exp.style.map(
            lambda v: ("background-color:#FFD9D9" if v == "EXPIRED"
                       else "background-color:#FFE8C2" if v.startswith("CRITICAL")
                       else "background-color:#FFF3C2" if v.startswith("WARNING")
                       else ""),
            subset=["expiry_band"]),
        use_container_width=True, hide_index=True)

    l, r = st.columns(2)
    with l:
        st.subheader("Upcoming renewals")
        ren = db.q("SELECT * FROM v_upcoming_renewals")
        st.dataframe(ren, use_container_width=True, hide_index=True)
    with r:
        st.subheader("Vendor lifetime spend (₹)")
        spend = db.q("SELECT * FROM v_vendor_spend ORDER BY lifetime_spend DESC")
        st.dataframe(spend, use_container_width=True, hide_index=True)
        st.bar_chart(spend.set_index("vendor_name")[["purchase_spend",
                                                     "renewal_spend"]])


def page_licenses():
    header("Licenses & Utilization",
           "Seats purchased vs allocated per license (view: v_license_utilization)")
    util = db.q("SELECT * FROM v_license_utilization")
    st.dataframe(util, use_container_width=True, hide_index=True)
    st.bar_chart(util.set_index("product_name")[["seats_active", "seats_free"]])

    st.subheader("Department allocations")
    st.dataframe(db.q("SELECT * FROM v_department_allocations "
                      "ORDER BY department_name"),
                 use_container_width=True, hide_index=True)


def page_allocations():
    header("Allocations & Workflows",
           "Allocate · Reclaim seats — rules BR-01…BR-04 enforced by triggers")

    st.subheader("Current allocations")
    alloc = db.q("""
        SELECT a.allocation_id, p.product_name, u.user_name,
               d.department_name, a.allocation_date, a.return_date, a.status
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
        # only offer licenses that are ACTIVE, not expired and have free seats
        licenses = db.q("""
            SELECT license_id, product_name, license_key, seats_free
              FROM v_license_utilization
             WHERE days_to_expiry >= 0 AND seats_free > 0
             ORDER BY product_name""")
        users = db.q("SELECT user_id, user_name FROM APP_USER ORDER BY user_name")
        devices = db.q("SELECT device_id, hostname FROM DEVICE ORDER BY hostname")
        with st.form("allocate_form"):
            lic = st.selectbox("License", licenses.to_dict("records"),
                format_func=lambda r: (f"#{r['license_id']} · {r['product_name']}"
                f" — {r['seats_free']} seat(s) free"))
            usr = st.selectbox("User", users.to_dict("records"),
                format_func=lambda r: f"#{r['user_id']} · {r['user_name']}")
            dev = st.selectbox("Device (optional)",
                               [None] + devices.to_dict("records"),
                               format_func=lambda r:
                                   "— none —" if r is None else
                                   f"{r['hostname']} (#{r['device_id']})")
            notes = st.text_input("Notes")
            if st.form_submit_button("Allocate", type="primary"):
                try:
                    db.execute(
                        "INSERT INTO ALLOCATION (license_id, user_id, device_id,"
                        " allocation_date, status, notes) VALUES (?,?,?,?,'ACTIVE',?)",
                        (lic["license_id"], usr["user_id"],
                         dev["device_id"] if dev else None,
                         db.today(), notes or None))
                    st.success("Seat allocated ✔")
                    st.rerun()
                except Exception as e:
                    err_box(e, "Allocation")

    with c2:
        st.subheader("↩️ Reclaim a seat")
        active = alloc[alloc.status == "ACTIVE"]
        if active.empty:
            st.info("No active allocations.")
        else:
            with st.form("reclaim_form"):
                row = st.selectbox("Active allocation", active.to_dict("records"),
                    format_func=lambda r: (f"#{r['allocation_id']} · "
                    f"{r['product_name']} — {r['user_name']}"))
                remark = st.text_input("Reason")
                if st.form_submit_button("Reclaim", type="primary"):
                    try:
                        db.execute(
                            "UPDATE ALLOCATION SET return_date = ?,"
                            " status = 'RECLAIMED', notes ="
                            " COALESCE(notes || ' | ', '') || ?"
                            " WHERE allocation_id = ? AND status = 'ACTIVE'",
                            (db.today(), f"Reclaimed: {remark or ''}",
                             row["allocation_id"]))
                        st.success("Seat reclaimed ✔")
                        st.rerun()
                    except Exception as e:
                        err_box(e, "Reclaim")


def page_compliance():
    header("Compliance",
           "Live violations view + dated audit trail (COMPLIANCE_CHECK)")

    st.subheader("Active allocation compliance")
    v = db.q("SELECT * FROM v_compliance_violations")
    bad = v[v.compliance_status != "PASS"]
    st.dataframe(
        bad.style.map(
            lambda c: "background-color:#FFD9D9" if c != "PASS" else "",
            subset=["compliance_status"]),
        use_container_width=True, hide_index=True)
    st.caption(f"{len(bad)} violation(s) across {len(v)} active allocation(s)")

    if st.button("🔍 Run compliance sweep", type="primary"):
        try:
            db.execute("""
                INSERT INTO COMPLIANCE_CHECK (allocation_id, check_date,
                                              check_status, remarks)
                SELECT allocation_id, ?, compliance_status,
                       'Sweep from UI'
                  FROM v_compliance_violations""", (db.today(),))
            st.success("Compliance sweep recorded ✔")
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
    header("Purchases & Renewals",
           "Procurement records and the renewal workflow (FR01, FR06)")

    st.subheader("Purchases")
    st.dataframe(db.q("""
        SELECT pu.purchase_id, v.vendor_name, p.product_name,
               pu.purchase_date, pu.quantity, pu.unit_cost, pu.total_cost,
               pu.invoice_no
          FROM PURCHASE pu
          JOIN VENDOR v ON v.vendor_id = pu.vendor_id
          JOIN SOFTWARE_PRODUCT p ON p.product_id = pu.product_id
         ORDER BY pu.purchase_id"""),
        use_container_width=True, hide_index=True)

    st.subheader("Renew a license")
    purch = db.q("""
        SELECT pu.purchase_id, p.product_name, l.license_id, l.valid_until
          FROM PURCHASE pu
          JOIN SOFTWARE_PRODUCT p ON p.product_id = pu.product_id
          JOIN LICENSE l ON l.purchase_id = pu.purchase_id
         ORDER BY pu.purchase_id""")
    rens = db.q("SELECT * FROM RENEWAL ORDER BY renewal_id DESC")
    c1, c2 = st.columns([2, 3])
    with c1:
        with st.form("renew_form"):
            row = st.selectbox("Purchase", purch.to_dict("records"),
                format_func=lambda r: (f"#{r['purchase_id']} · {r['product_name']}"
                f" — valid until {r['valid_until']}"))
            amount = st.number_input("Renewal amount (₹)", min_value=0.0,
                                     value=50000.0, step=1000.0)
            new_until = st.date_input("New valid until")
            remarks = st.text_input("Remarks")
            if st.form_submit_button("Renew", type="primary"):
                try:
                    db.execute(
                        "INSERT INTO RENEWAL (purchase_id, renewal_date,"
                        " renewal_amount, new_valid_until, remarks)"
                        " VALUES (?,?,?,?,?)",
                        (row["purchase_id"], db.today(), amount,
                         new_until.isoformat(), remarks or None))
                    db.execute(
                        "UPDATE LICENSE SET valid_until = ?, status = 'ACTIVE'"
                        " WHERE purchase_id = ?",
                        (new_until.isoformat(), row["purchase_id"]))
                    st.success("Renewal recorded, license validity extended ✔")
                    st.rerun()
                except Exception as e:
                    err_box(e, "Renewal")
    with c2:
        st.markdown("**Renewal history**")
        st.dataframe(rens, use_container_width=True, hide_index=True)


def page_data():
    header("Raw Tables", "Inspect any table from the schema")
    tables = ["VENDOR", "LICENSE_TYPE", "SOFTWARE_PRODUCT", "PURCHASE",
              "LICENSE", "SUBSCRIPTION", "DEPARTMENT", "APP_USER", "DEVICE",
              "ALLOCATION", "RENEWAL", "COMPLIANCE_CHECK"]
    t = st.selectbox("Table", tables)
    st.dataframe(db.q(f"SELECT * FROM {t}"), use_container_width=True,
                 hide_index=True)


# ---------------------------------------------------------------- router
pages = {
    "📊 Dashboard": page_dashboard,
    "🎫 Licenses & Utilization": page_licenses,
    "🔁 Allocations & Workflows": page_allocations,
    "✅ Compliance": page_compliance,
    "🛒 Purchases & Renewals": page_procurement,
    "🗃️ Raw Tables": page_data,
}

st.sidebar.title("🗄️ License Management")
st.sidebar.caption("Software License & Subscription Management System\n\n"
                   "DBMS Project · Woxsen University")
choice = st.sidebar.radio("Navigation", list(pages.keys()),
                          label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Business rules enforced at the DB level:\n"
                   "BR-01 active license · BR-02 within validity · "
                   "BR-03 seat limit · BR-04 valid period")

pages[choice]()
