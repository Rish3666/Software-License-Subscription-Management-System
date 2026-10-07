-- SQLite verification copy (not shipped) — mirrors MySQL schema/seed/views
PRAGMA foreign_keys = ON;
DROP VIEW IF EXISTS v_upcoming_renewals;
DROP VIEW IF EXISTS v_vendor_spend;
DROP VIEW IF EXISTS v_compliance_violations;
DROP VIEW IF EXISTS v_expiry_monitor;
DROP VIEW IF EXISTS v_department_allocations;
DROP VIEW IF EXISTS v_license_utilization;
DROP TABLE IF EXISTS COMPLIANCE_CHECK;
DROP TABLE IF EXISTS RENEWAL;
DROP TABLE IF EXISTS ALLOCATION;
DROP TABLE IF EXISTS DEVICE;
DROP TABLE IF EXISTS APP_USER;
DROP TABLE IF EXISTS DEPARTMENT;
DROP TABLE IF EXISTS SUBSCRIPTION;
DROP TABLE IF EXISTS LICENSE;
DROP TABLE IF EXISTS PURCHASE;
DROP TABLE IF EXISTS SOFTWARE_PRODUCT;
DROP TABLE IF EXISTS LICENSE_TYPE;
DROP TABLE IF EXISTS VENDOR;

CREATE TABLE VENDOR (
    vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_name TEXT NOT NULL UNIQUE,
    contact_email TEXT NOT NULL UNIQUE
);
CREATE TABLE LICENSE_TYPE (
    license_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE
);
CREATE TABLE SOFTWARE_PRODUCT (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL REFERENCES VENDOR(vendor_id),
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    UNIQUE (vendor_id, product_name)
);
CREATE TABLE PURCHASE (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL REFERENCES VENDOR(vendor_id),
    product_id INTEGER NOT NULL REFERENCES SOFTWARE_PRODUCT(product_id),
    purchase_date TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_cost REAL NOT NULL,
    total_cost REAL NOT NULL,
    invoice_no TEXT UNIQUE
);
CREATE TABLE LICENSE (
    license_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES SOFTWARE_PRODUCT(product_id),
    license_type_id INTEGER NOT NULL REFERENCES LICENSE_TYPE(license_type_id),
    license_key TEXT NOT NULL UNIQUE,
    total_seats INTEGER NOT NULL CHECK (total_seats >= 1),
    valid_from TEXT NOT NULL,
    valid_until TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','EXPIRED','REVOKED')),
    purchase_id INTEGER NOT NULL REFERENCES PURCHASE(purchase_id),
    CHECK (valid_until >= valid_from)
);
CREATE TABLE SUBSCRIPTION (
    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_id INTEGER NOT NULL REFERENCES LICENSE(license_id),
    billing_cycle TEXT NOT NULL CHECK (billing_cycle IN ('MONTHLY','QUARTERLY','ANNUAL')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    auto_renew INTEGER NOT NULL DEFAULT 0,
    CHECK (end_date > start_date)
);
CREATE TABLE DEPARTMENT (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE,
    head_name TEXT,
    annual_it_budget REAL DEFAULT 0
);
CREATE TABLE APP_USER (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL REFERENCES DEPARTMENT(department_id),
    user_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    user_role TEXT NOT NULL DEFAULT 'EMPLOYEE' CHECK (user_role IN ('IT_ADMIN','DEPT_MANAGER','PROCUREMENT','EMPLOYEE','COMPLIANCE_OFFICER')),
    is_active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE DEVICE (
    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES APP_USER(user_id),
    device_type TEXT NOT NULL CHECK (device_type IN ('LAPTOP','DESKTOP','WORKSTATION','MOBILE','SERVER')),
    hostname TEXT NOT NULL UNIQUE
);
CREATE TABLE ALLOCATION (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_id INTEGER NOT NULL REFERENCES LICENSE(license_id),
    user_id INTEGER NOT NULL REFERENCES APP_USER(user_id),
    device_id INTEGER REFERENCES DEVICE(device_id),
    allocation_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','RECLAIMED','EXPIRED')),
    notes TEXT,
    CHECK (return_date IS NULL OR return_date >= allocation_date)
);
CREATE TABLE RENEWAL (
    renewal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER NOT NULL REFERENCES PURCHASE(purchase_id),
    renewal_date TEXT NOT NULL,
    renewal_amount REAL NOT NULL CHECK (renewal_amount >= 0),
    new_valid_until TEXT NOT NULL,
    remarks TEXT
);
CREATE TABLE COMPLIANCE_CHECK (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    allocation_id INTEGER NOT NULL REFERENCES ALLOCATION(allocation_id),
    check_date TEXT NOT NULL,
    check_status TEXT NOT NULL CHECK (check_status IN ('PASS','OVERALLOCATED','EXPIRED_LICENSE','UNASSIGNED_DEVICE','USER_INACTIVE')),
    remarks TEXT,
    UNIQUE (allocation_id, check_date, check_status)
);

-- seed data (mirrors 02_seed.sql)
INSERT INTO VENDOR (vendor_name, contact_email) VALUES
('Microsoft Corporation','sales@microsoft.com'),
('Adobe Inc.','orders@adobe.com'),
('JetBrains s.r.o.','sales@jetbrains.com'),
('AutoDesk Inc.','sales@autodesk.com');
INSERT INTO LICENSE_TYPE (type_name) VALUES ('Perpetual'),('Subscription'),('Volume'),('OEM');
INSERT INTO DEPARTMENT (department_name, head_name, annual_it_budget) VALUES
('Computer Science','Dr. Ananya Rao',250000),
('Electronics & Comm.','Dr. Ravi Menon',180000),
('Mechanical Engineering','Dr. Suresh Babu',120000),
('Administration','Ms. Kavya Reddy',90000),
('Library & Info.','Mr. Prakash Nair',40000);
INSERT INTO SOFTWARE_PRODUCT (vendor_id, product_name, category) VALUES
(1,'Microsoft Office 365','Office'),
(1,'Windows 11 Pro','OS'),
(2,'Adobe Creative Cloud','Design'),
(3,'IntelliJ IDEA Ultimate','IDE'),
(3,'PyCharm Professional','IDE'),
(4,'AutoCAD','CAD');
INSERT INTO APP_USER (department_id, user_name, email, user_role) VALUES
(1,'Rishvarma','r@w.edu','EMPLOYEE'),
(1,'Dr. Ananya Rao','a@w.edu','DEPT_MANAGER'),
(1,'Rohit Sharma','r2@w.edu','IT_ADMIN'),
(2,'Meera Iyer','m@w.edu','EMPLOYEE'),
(2,'Dr. Ravi Menon','rm@w.edu','DEPT_MANAGER'),
(4,'Sandeep Kumar','s@w.edu','PROCUREMENT'),
(4,'Latha Pillai','l@w.edu','COMPLIANCE_OFFICER'),
(5,'Prakash Nair','p@w.edu','EMPLOYEE');
INSERT INTO DEVICE (user_id, device_type, hostname) VALUES
(1,'LAPTOP','CS-LAB-001'),(2,'WORKSTATION','CS-HOD-WS'),(3,'LAPTOP','CS-IT-002'),
(4,'DESKTOP','ECE-LAB-011'),(6,'LAPTOP','ADM-PRC-01'),(8,'LAPTOP','LIB-001');
INSERT INTO PURCHASE (vendor_id, product_id, purchase_date, quantity, unit_cost, total_cost, invoice_no) VALUES
(1,1,'2025-01-10',50,1200,60000,'INV1'),
(1,2,'2025-01-10',30,350,10500,'INV2'),
(2,3,'2025-02-15',10,4800,48000,'INV3'),
(3,4,'2025-03-01',25,2600,65000,'INV4'),
(3,5,'2025-03-01',20,1900,38000,'INV5'),
(4,6,'2025-02-20',8,12000,96000,'INV6');
INSERT INTO LICENSE (product_id, license_type_id, license_key, total_seats, valid_from, valid_until, status, purchase_id) VALUES
(1,2,'K1',50,'2025-01-10','2026-01-09','ACTIVE',1),
(2,3,'K2',30,'2025-01-10','2027-01-09','ACTIVE',2),
(3,2,'K3',10,'2025-02-15','2026-02-14','ACTIVE',3),
(4,3,'K4',25,'2025-03-01','2026-03-31','ACTIVE',4),
(5,2,'K5',20,'2025-03-01','2026-03-31','ACTIVE',5),
(6,1,'K6',8,'2025-02-20','2030-02-19','ACTIVE',6);
INSERT INTO SUBSCRIPTION (license_id, billing_cycle, start_date, end_date, amount, auto_renew) VALUES
(1,'ANNUAL','2025-01-10','2026-01-09',60000,1),
(3,'ANNUAL','2025-02-15','2026-02-14',48000,1),
(4,'ANNUAL','2025-03-01','2026-03-31',65000,0),
(5,'ANNUAL','2025-03-01','2026-03-31',38000,0),
(6,'QUARTERLY','2025-02-20','2025-05-20',12000,0);
INSERT INTO ALLOCATION (license_id, user_id, device_id, allocation_date, return_date, status, notes) VALUES
(1,1,1,'2025-01-12',NULL,'ACTIVE','x'),
(1,2,2,'2025-01-12',NULL,'ACTIVE','x'),
(1,3,3,'2025-01-15',NULL,'ACTIVE','x'),
(1,8,6,'2025-01-20',NULL,'ACTIVE','x'),
(3,4,4,'2025-02-18',NULL,'ACTIVE','x'),
(4,1,1,'2025-03-03',NULL,'ACTIVE','x'),
(4,2,2,'2025-03-03','2025-06-30','RECLAIMED','x'),
(5,4,4,'2025-03-05',NULL,'ACTIVE','x');
INSERT INTO RENEWAL (purchase_id, renewal_date, renewal_amount, new_valid_until, remarks) VALUES
(1,'2025-12-20',63000,'2027-01-09','r'),
(4,'2025-09-15',67500,'2027-03-31','r');
INSERT INTO COMPLIANCE_CHECK (allocation_id, check_date, check_status, remarks) VALUES
(1,'2025-09-01','PASS','ok'),
(4,'2025-09-01','USER_INACTIVE','x'),
(7,'2025-09-01','EXPIRED_LICENSE','x');

-- views (mirrors 03_views_reports.sql)
CREATE VIEW v_license_utilization AS
SELECT l.license_id, p.product_name, lt.type_name, l.license_key, l.total_seats,
       COUNT(a.allocation_id) AS seats_active,
       (l.total_seats - COUNT(a.allocation_id)) AS seats_free,
       ROUND(COUNT(a.allocation_id) * 100.0 / l.total_seats, 1) AS utilization_pct,
       l.valid_until,
       CAST(julianday(l.valid_until) - julianday('now') AS INTEGER) AS days_to_expiry
FROM LICENSE l
JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
JOIN LICENSE_TYPE lt ON lt.license_type_id = l.license_type_id
LEFT JOIN ALLOCATION a ON a.license_id = l.license_id AND a.status = 'ACTIVE'
GROUP BY l.license_id, p.product_name, lt.type_name, l.license_key, l.total_seats, l.valid_until;

CREATE VIEW v_department_allocations AS
SELECT d.department_id, d.department_name, p.product_name,
       COUNT(a.allocation_id) AS active_allocations
FROM DEPARTMENT d
LEFT JOIN APP_USER u ON u.department_id = d.department_id
LEFT JOIN ALLOCATION a ON a.user_id = u.user_id AND a.status = 'ACTIVE'
LEFT JOIN LICENSE l ON l.license_id = a.license_id
LEFT JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
GROUP BY d.department_id, d.department_name, p.product_name;

CREATE VIEW v_expiry_monitor AS
SELECT l.license_id, p.product_name, l.license_key, l.valid_until,
       CAST(julianday(l.valid_until) - julianday('now') AS INTEGER) AS days_to_expiry,
       CASE
           WHEN l.valid_until < date('now') THEN 'EXPIRED'
           WHEN julianday(l.valid_until) - julianday('now') <= 30 THEN 'CRITICAL (<30d)'
           WHEN julianday(l.valid_until) - julianday('now') <= 90 THEN 'WARNING (<90d)'
           ELSE 'OK'
       END AS expiry_band, l.status
FROM LICENSE l JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id;

CREATE VIEW v_compliance_violations AS
SELECT a.allocation_id, u.user_name, d.department_name, p.product_name, l.license_key,
       CASE
           WHEN l.valid_until < date('now') OR l.status <> 'ACTIVE' THEN 'EXPIRED_LICENSE'
           WHEN a.device_id IS NULL THEN 'UNASSIGNED_DEVICE'
           WHEN u.is_active = 0 THEN 'USER_INACTIVE'
           ELSE 'PASS'
       END AS compliance_status
FROM ALLOCATION a
JOIN LICENSE l ON l.license_id = a.license_id
JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
JOIN APP_USER u ON u.user_id = a.user_id
JOIN DEPARTMENT d ON d.department_id = u.department_id
WHERE a.status = 'ACTIVE';

CREATE VIEW v_vendor_spend AS
SELECT v.vendor_id, v.vendor_name,
       COUNT(DISTINCT pu.purchase_id) AS purchases,
       COALESCE(SUM(pu.total_cost),0) AS purchase_spend,
       (SELECT COALESCE(SUM(r.renewal_amount),0) FROM RENEWAL r JOIN PURCHASE pu2 ON pu2.purchase_id = r.purchase_id WHERE pu2.vendor_id = v.vendor_id) AS renewal_spend,
       COALESCE(SUM(pu.total_cost),0) + (SELECT COALESCE(SUM(r.renewal_amount),0) FROM RENEWAL r JOIN PURCHASE pu2 ON pu2.purchase_id = r.purchase_id WHERE pu2.vendor_id = v.vendor_id) AS lifetime_spend
FROM VENDOR v LEFT JOIN PURCHASE pu ON pu.vendor_id = v.vendor_id
GROUP BY v.vendor_id, v.vendor_name;

CREATE VIEW v_upcoming_renewals AS
SELECT s.subscription_id, p.product_name, s.billing_cycle, s.end_date,
       CAST(julianday(s.end_date) - julianday('now') AS INTEGER) AS days_to_renewal,
       s.amount, s.auto_renew
FROM SUBSCRIPTION s
JOIN LICENSE l ON l.license_id = s.license_id
JOIN SOFTWARE_PRODUCT p ON p.product_id = l.product_id
WHERE s.end_date >= date('now')
ORDER BY s.end_date ASC;

-- triggers mirroring the MySQL business rules BR-01..BR-03
CREATE TRIGGER trg_alloc_before_insert
BEFORE INSERT ON ALLOCATION
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'BR-01 violated: license is not ACTIVE')
    WHERE (SELECT status FROM LICENSE WHERE license_id = NEW.license_id) <> 'ACTIVE';
    SELECT RAISE(ABORT, 'BR-02 violated: allocation date is past license expiry')
    WHERE NEW.allocation_date > (SELECT valid_until FROM LICENSE WHERE license_id = NEW.license_id);
    SELECT RAISE(ABORT, 'BR-03 violated: all purchased seats for this license are allocated')
    WHERE (SELECT COUNT(*) FROM ALLOCATION WHERE license_id = NEW.license_id AND status = 'ACTIVE')
          >= (SELECT total_seats FROM LICENSE WHERE license_id = NEW.license_id);
END;
SELECT product_name, billing_cycle, end_date, days_to_renewal FROM v_upcoming_renewals;

