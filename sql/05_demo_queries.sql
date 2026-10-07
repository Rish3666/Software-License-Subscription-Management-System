-- ============================================================
--  SOFTWARE LICENSE & SUBSCRIPTION MANAGEMENT SYSTEM
--  05_demo_queries.sql — prototype demonstration script
--  MySQL 8.x
-- ============================================================
USE license_mgmt;

-- Demo 1 : License utilization snapshot (V1)
SELECT license_id, product_name, total_seats, seats_active,
       seats_free, utilization_pct, days_to_expiry
  FROM v_license_utilization;

-- Demo 2 : Department allocation report (V2)
SELECT department_name, product_name, seats_in_use
  FROM v_department_allocations
 ORDER BY department_name, product_name;

-- Demo 3 : Expiry monitor (V3) — which licenses need attention?
SELECT product_name, license_key, valid_until, expiry_band
  FROM v_expiry_monitor
 WHERE expiry_band <> 'OK'
 ORDER BY days_to_expiry;

-- Demo 4 : Compliance violations (V4)
SELECT allocation_id, user_name, department_name, product_name,
       compliance_status
  FROM v_compliance_violations
 WHERE compliance_status <> 'PASS';

-- Demo 5 : Vendor lifetime spend (V5)
SELECT vendor_name, purchase_spend, renewal_spend, lifetime_spend
  FROM v_vendor_spend
 ORDER BY lifetime_spend DESC;

-- Demo 6 : Upcoming renewals (V6)
SELECT product_name, billing_cycle, end_date, days_to_renewal, auto_renew
  FROM v_upcoming_renewals;

-- Demo 7 : Workflow — allocate a new Adobe CC seat (FR02)
CALL sp_allocate_license(3, 4, 4, 'Demo allocation from Review 3', @id);
SELECT allocation_id, license_id, user_id, allocation_date, status
  FROM ALLOCATION WHERE allocation_id = @id;

-- Demo 8 : Workflow — attempt to over-allocate Office 365 beyond
--          active seats only fails when seats run out (BR-03)
SELECT COUNT(*) AS active_before
  FROM ALLOCATION WHERE license_id = 1 AND status = 'ACTIVE';

-- Demo 9 : Workflow — reclaim a seat (FR03)
-- (only safe to run once; allocation 8 is ACTIVE in seed data)
CALL sp_reclaim_license(8, 'End of demo — seat returned');

-- Demo 10 : Workflow — renew a license (FR06)
CALL sp_renew_license(3, 50000.00, '2027-02-14', 'Demo Adobe CC renewal');

-- Demo 11 : Run a compliance sweep and show findings (FR05)
CALL sp_run_compliance_check();
SELECT c.check_id, a.allocation_id, c.check_date, c.check_status
  FROM COMPLIANCE_CHECK c
  JOIN ALLOCATION a ON a.allocation_id = c.allocation_id
 ORDER BY c.check_id DESC
 LIMIT 10;

-- Demo 12 : Audit history — full allocation lifecycle for user 1 (FR08)
SELECT a.allocation_id, p.product_name, a.allocation_date,
       a.return_date, a.status
  FROM ALLOCATION a
  JOIN LICENSE l  ON l.license_id  = a.license_id
  JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
 WHERE a.user_id = 1
 ORDER BY a.allocation_date;
