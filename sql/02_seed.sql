-- ============================================================
--  SOFTWARE LICENSE & SUBSCRIPTION MANAGEMENT SYSTEM
--  02_seed.sql — representative sample data for prototype demo
--  MySQL 8.x
-- ============================================================
USE license_mgmt;

-- ---------- VENDORS (4) ----------
INSERT INTO VENDOR (vendor_name, contact_email, support_phone, address) VALUES
('Microsoft Corporation',  'sales@microsoft.com',  '+1-800-642-7676', 'Redmond, WA, USA'),
('Adobe Inc.',             'orders@adobe.com',     '+1-800-833-6687', 'San Jose, CA, USA'),
('JetBrains s.r.o.',       'sales@jetbrains.com',  '+420-2-9601-7500','Prague, Czech Republic'),
('AutoDesk Inc.',          'sales@autodesk.com',   '+1-866-801-8300', 'San Rafael, CA, USA');

-- ---------- LICENSE TYPES (4) ----------
INSERT INTO LICENSE_TYPE (type_name, description) VALUES
('Perpetual',    'One-time purchase, unlimited use of that version'),
('Subscription', 'Time-bound right to use, recurring billing'),
('Volume',       'Bulk seats purchased under a single agreement'),
('OEM',          'Bundled with hardware, tied to one device');

-- ---------- DEPARTMENTS (5) ----------
INSERT INTO DEPARTMENT (department_name, head_name, annual_it_budget) VALUES
('Computer Science',     'Dr. Ananya Rao',    250000.00),
('Electronics & Comm.',  'Dr. Ravi Menon',    180000.00),
('Mechanical Engineering','Dr. Suresh Babu',  120000.00),
('Administration',       'Ms. Kavya Reddy',    90000.00),
('Library & Info.',      'Mr. Prakash Nair',   40000.00);

-- ---------- SOFTWARE PRODUCTS (6) ----------
INSERT INTO SOFTWARE_PRODUCT (vendor_id, product_name, category, latest_version) VALUES
(1, 'Microsoft Office 365', 'Office',    '2409'),
(1, 'Windows 11 Pro',       'OS',        '23H2'),
(2, 'Adobe Creative Cloud', 'Design',    '2025'),
(3, 'IntelliJ IDEA Ultimate','IDE',      '2024.3'),
(3, 'PyCharm Professional', 'IDE',       '2024.3'),
(4, 'AutoCAD',              'CAD',       '2025');

-- ---------- APP_USERS (8) ----------
INSERT INTO APP_USER (department_id, user_name, email, user_role) VALUES
(1, 'Jampana N. S. S. Rishvarma', 'rishvarma@woxsen.edu.in',  'EMPLOYEE'),
(1, 'Dr. Ananya Rao',             'ananya.rao@woxsen.edu.in', 'DEPT_MANAGER'),
(1, 'Rohit Sharma',               'rohit.sharma@woxsen.edu.in','IT_ADMIN'),
(2, 'Meera Iyer',                 'meera.iyer@woxsen.edu.in', 'EMPLOYEE'),
(2, 'Dr. Ravi Menon',             'ravi.menon@woxsen.edu.in', 'DEPT_MANAGER'),
(4, 'Sandeep Kumar',              'sandeep.k@woxsen.edu.in',  'PROCUREMENT'),
(4, 'Latha Pillai',               'latha.pillai@woxsen.edu.in','COMPLIANCE_OFFICER'),
(5, 'Prakash Nair',               'prakash.nair@woxsen.edu.in','EMPLOYEE');

-- ---------- DEVICES (6) ----------
INSERT INTO DEVICE (user_id, device_type, hostname, os_name) VALUES
(1, 'LAPTOP',      'CS-LAB-001', 'Windows 11 Pro'),
(2, 'WORKSTATION', 'CS-HOD-WS',  'Ubuntu 24.04 LTS'),
(3, 'LAPTOP',      'CS-IT-002',  'macOS Sequoia'),
(4, 'DESKTOP',     'ECE-LAB-011','Windows 11 Pro'),
(6, 'LAPTOP',      'ADM-PRC-01', 'Windows 11 Pro'),
(8, 'LAPTOP',      'LIB-001',    'Windows 11 Pro');

-- ---------- PURCHASES (6) ----------
INSERT INTO PURCHASE (vendor_id, product_id, purchase_date, quantity, unit_cost, total_cost, invoice_no) VALUES
(1, 1, '2025-01-10', 50,  1200.00, 60000.00, 'INV-MS-2025-001'),  -- Office 365
(1, 2, '2025-01-10', 30,   350.00, 10500.00, 'INV-MS-2025-002'),  -- Win 11 Pro
(2, 3, '2025-02-15', 10,  4800.00, 48000.00, 'INV-AD-2025-014'),  -- Adobe CC
(3, 4, '2025-03-01', 25,  2600.00, 65000.00, 'INV-JB-2025-101'),  -- IntelliJ
(3, 5, '2025-03-01', 20,  1900.00, 38000.00, 'INV-JB-2025-102'),  -- PyCharm
(4, 6, '2025-02-20',  8, 12000.00, 96000.00, 'INV-ADSK-2025-07'); -- AutoCAD

-- ---------- LICENSES (6, one per purchase line) ----------
INSERT INTO LICENSE (product_id, license_type_id, license_key, total_seats, valid_from, valid_until, status, purchase_id) VALUES
(1, 2, 'M365-CAMPUS-2025-A1-SEATS50',     50, '2025-01-10', '2026-01-09', 'ACTIVE', 1),
(2, 3, 'WIN11-VOL-WOX-2025-SEATS30',      30, '2025-01-10', '2027-01-09', 'ACTIVE', 2),
(3, 2, 'ADBE-CC-TDY-2025-SEATS10',        10, '2025-02-15', '2026-02-14', 'ACTIVE', 3),
(4, 3, 'IDEA-U-EDU-2025-SEATS25',         25, '2025-03-01', '2026-03-31', 'ACTIVE', 4),
(5, 2, 'PCP-EDU-2025-SEATS20',            20, '2025-03-01', '2026-03-31', 'ACTIVE', 5),
(6, 1, 'ACAD-PERP-2025-LAB8',              8, '2025-02-20', '2030-02-19', 'ACTIVE', 6);

-- ---------- SUBSCRIPTIONS (5) ----------
INSERT INTO SUBSCRIPTION (license_id, billing_cycle, start_date, end_date, amount, auto_renew) VALUES
(1, 'ANNUAL',    '2025-01-10', '2026-01-09', 60000.00, TRUE),
(3, 'ANNUAL',    '2025-02-15', '2026-02-14', 48000.00, TRUE),
(4, 'ANNUAL',    '2025-03-01', '2026-03-31', 65000.00, FALSE),
(5, 'ANNUAL',    '2025-03-01', '2026-03-31', 38000.00, FALSE),
(6, 'QUARTERLY', '2025-02-20', '2025-05-20', 12000.00, FALSE);

-- ---------- ALLOCATIONS (8 — includes edge cases for demo) ----------
INSERT INTO ALLOCATION (license_id, user_id, device_id, allocation_date, return_date, status, notes) VALUES
(1, 1, 1, '2025-01-12', NULL, 'ACTIVE', 'Student laptop — CS dept'),
(1, 2, 2, '2025-01-12', NULL, 'ACTIVE', 'HOD workstation'),
(1, 3, 3, '2025-01-15', NULL, 'ACTIVE', 'IT admin laptop'),
(1, 8, 6, '2025-01-20', NULL, 'ACTIVE', 'Library staff'),
(3, 4, 4, '2025-02-18', NULL, 'ACTIVE', 'Design lab PC'),
(4, 1, 1, '2025-03-03', NULL, 'ACTIVE', 'Coursework IDE'),
(4, 2, 2, '2025-03-03', '2025-06-30', 'RECLAIMED', 'Returned after semester'),
(5, 4, 4, '2025-03-05', NULL, 'ACTIVE', 'Python lab work');

-- ---------- RENEWALS (2) ----------
INSERT INTO RENEWAL (purchase_id, renewal_date, renewal_amount, new_valid_until, remarks) VALUES
(1, '2025-12-20', 63000.00, '2027-01-09', '3% price uplift on renewal'),
(4, '2025-09-15', 67500.00, '2027-03-31', 'Two-year education renewal');

-- ---------- COMPLIANCE CHECKS (3) ----------
INSERT INTO COMPLIANCE_CHECK (allocation_id, check_date, check_status, remarks) VALUES
(1, '2025-09-01', 'PASS',               'Key in use on registered device'),
(4, '2025-09-01', 'USER_INACTIVE',      'Library staff transfer pending'),
(7, '2025-09-01', 'EXPIRED_LICENSE',    'Allocation outlived license validity');
