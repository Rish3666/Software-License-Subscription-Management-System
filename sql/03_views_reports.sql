-- ============================================================
--  SOFTWARE LICENSE & SUBSCRIPTION MANAGEMENT SYSTEM
--  03_views_reports.sql — reporting & monitoring layer
--  MySQL 8.x
-- ============================================================
USE license_mgmt;

-- ------------------------------------------------------------
-- V1 : License utilization — seats used vs purchased (FR07)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_license_utilization AS
SELECT
    l.license_id,
    p.product_name,
    lt.type_name,
    l.license_key,
    l.total_seats,
    COUNT(a.allocation_id)                              AS seats_active,
    (l.total_seats - COUNT(a.allocation_id))            AS seats_free,
    ROUND(COUNT(a.allocation_id) / l.total_seats * 100, 1) AS utilization_pct,
    l.valid_until,
    DATEDIFF(l.valid_until, CURDATE())                  AS days_to_expiry
FROM LICENSE l
JOIN SOFTWARE_PRODUCT p  ON p.product_id  = l.product_id
JOIN LICENSE_TYPE    lt  ON lt.license_type_id = l.license_type_id
LEFT JOIN ALLOCATION a   ON a.license_id = l.license_id
                        AND a.status = 'ACTIVE'
GROUP BY l.license_id, p.product_name, lt.type_name, l.license_key,
         l.total_seats, l.valid_until;

-- ------------------------------------------------------------
-- V2 : Department allocation report (FR07)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_department_allocations AS
SELECT
    d.department_id,
    d.department_name,
    p.product_name,
    COUNT(a.allocation_id)                                   AS active_allocations,
    COALESCE(SUM(CASE WHEN a.status = 'ACTIVE' THEN 1 ELSE 0 END), 0) AS seats_in_use
FROM DEPARTMENT d
LEFT JOIN APP_USER  u ON u.department_id = d.department_id
LEFT JOIN ALLOCATION a ON a.user_id = u.user_id AND a.status = 'ACTIVE'
LEFT JOIN LICENSE   l ON l.license_id = a.license_id
LEFT JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
GROUP BY d.department_id, d.department_name, p.product_name;

-- ------------------------------------------------------------
-- V3 : Expiry monitor — expiring / expired licenses (FR04)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_expiry_monitor AS
SELECT
    l.license_id,
    p.product_name,
    l.license_key,
    l.valid_until,
    DATEDIFF(l.valid_until, CURDATE()) AS days_to_expiry,
    CASE
        WHEN l.valid_until < CURDATE()                          THEN 'EXPIRED'
        WHEN DATEDIFF(l.valid_until, CURDATE()) <= 30           THEN 'CRITICAL (<30d)'
        WHEN DATEDIFF(l.valid_until, CURDATE()) <= 90           THEN 'WARNING (<90d)'
        ELSE 'OK'
    END AS expiry_band,
    l.status
FROM LICENSE l
JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id;

-- ------------------------------------------------------------
-- V4 : Compliance violations across active allocations (FR05)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_compliance_violations AS
SELECT
    a.allocation_id,
    u.user_name,
    d.department_name,
    p.product_name,
    l.license_key,
    a.allocation_date,
    a.device_id,
    CASE
        WHEN l.valid_until < CURDATE() OR l.status <> 'ACTIVE'
             THEN 'EXPIRED_LICENSE'
        WHEN a.device_id IS NULL
             THEN 'UNASSIGNED_DEVICE'
        WHEN u.is_active = FALSE
             THEN 'USER_INACTIVE'
        ELSE 'PASS'
    END AS compliance_status
FROM ALLOCATION a
JOIN LICENSE           l ON l.license_id = a.license_id
JOIN SOFTWARE_PRODUCT  p ON p.product_id = l.product_id
JOIN APP_USER          u ON u.user_id    = a.user_id
JOIN DEPARTMENT        d ON d.department_id = u.department_id
WHERE a.status = 'ACTIVE';

-- ------------------------------------------------------------
-- V5 : Vendor cost analysis (FR06 / FR07)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_vendor_spend AS
SELECT
    v.vendor_id,
    v.vendor_name,
    COUNT(DISTINCT pu.purchase_id)                AS purchases,
    COALESCE(SUM(pu.total_cost), 0)               AS purchase_spend,
    (SELECT COALESCE(SUM(r.renewal_amount), 0)
       FROM RENEWAL r
       JOIN PURCHASE pu2 ON pu2.purchase_id = r.purchase_id
      WHERE pu2.vendor_id = v.vendor_id)          AS renewal_spend,
    COALESCE(SUM(pu.total_cost), 0)
      + (SELECT COALESCE(SUM(r.renewal_amount), 0)
           FROM RENEWAL r
           JOIN PURCHASE pu2 ON pu2.purchase_id = r.purchase_id
          WHERE pu2.vendor_id = v.vendor_id)      AS lifetime_spend
FROM VENDOR v
LEFT JOIN PURCHASE pu ON pu.vendor_id = v.vendor_id
GROUP BY v.vendor_id, v.vendor_name;

-- ------------------------------------------------------------
-- V6 : Upcoming renewals decision support (FR06)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_upcoming_renewals AS
SELECT
    s.subscription_id,
    p.product_name,
    s.billing_cycle,
    s.end_date,
    DATEDIFF(s.end_date, CURDATE()) AS days_to_renewal,
    s.amount,
    s.auto_renew
FROM SUBSCRIPTION s
JOIN LICENSE l ON l.license_id = s.license_id
JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
WHERE s.end_date >= CURDATE()
ORDER BY s.end_date ASC;
