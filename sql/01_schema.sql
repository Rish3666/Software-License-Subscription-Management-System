-- ============================================================
--  SOFTWARE LICENSE & SUBSCRIPTION MANAGEMENT SYSTEM
--  Review 2/3 Deliverable — Complete Relational Schema (3NF)
--  Target DBMS : MySQL 8.x
--  Student     : Jampana Naga Satya Sai Rishvarma (25WU0102105)
-- ============================================================
-- Run order : 01_schema.sql -> 02_seed.sql -> 03_views_reports.sql
--             -> 04_procedures.sql -> 05_demo_queries.sql
-- ============================================================

DROP DATABASE IF EXISTS license_mgmt;
CREATE DATABASE license_mgmt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE license_mgmt;

-- ------------------------------------------------------------
-- 1. VENDOR  — supplier of software products
-- ------------------------------------------------------------
CREATE TABLE VENDOR (
    vendor_id        INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    vendor_name      VARCHAR(100)     NOT NULL,
    contact_email    VARCHAR(120)     NOT NULL,
    support_phone    VARCHAR(20),
    address          VARCHAR(255),
    CONSTRAINT pk_vendor PRIMARY KEY (vendor_id),
    CONSTRAINT uq_vendor_name  UNIQUE (vendor_name),
    CONSTRAINT uq_vendor_email UNIQUE (contact_email),
    CONSTRAINT chk_vendor_email CHECK (contact_email LIKE '%_@_%._%')
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. LICENSE_TYPE  — classification of licensing models
-- ------------------------------------------------------------
CREATE TABLE LICENSE_TYPE (
    license_type_id  INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    type_name        VARCHAR(50)      NOT NULL,   -- Perpetual / Subscription / OEM / Volume / Floating
    description      VARCHAR(255),
    CONSTRAINT pk_license_type PRIMARY KEY (license_type_id),
    CONSTRAINT uq_type_name UNIQUE (type_name)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. SOFTWARE_PRODUCT  — a product sold by a vendor
-- ------------------------------------------------------------
CREATE TABLE SOFTWARE_PRODUCT (
    product_id       INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    vendor_id        INT UNSIGNED     NOT NULL,
    product_name     VARCHAR(100)     NOT NULL,
    category         VARCHAR(50)      NOT NULL,   -- Office / IDE / Security / Design ...
    latest_version   VARCHAR(20),
    CONSTRAINT pk_product PRIMARY KEY (product_id),
    CONSTRAINT uq_product_name UNIQUE (vendor_id, product_name),
    CONSTRAINT fk_product_vendor FOREIGN KEY (vendor_id)
        REFERENCES VENDOR (vendor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. PURCHASE  — a procurement event against a vendor/product
-- ------------------------------------------------------------
CREATE TABLE PURCHASE (
    purchase_id      INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    vendor_id        INT UNSIGNED     NOT NULL,
    product_id       INT UNSIGNED     NOT NULL,
    purchase_date    DATE             NOT NULL,
    quantity         INT UNSIGNED     NOT NULL,
    unit_cost        DECIMAL(10,2)    NOT NULL,
    total_cost       DECIMAL(12,2)    NOT NULL,
    invoice_no       VARCHAR(40),
    CONSTRAINT pk_purchase PRIMARY KEY (purchase_id),
    CONSTRAINT fk_purchase_vendor  FOREIGN KEY (vendor_id)
        REFERENCES VENDOR (vendor_id)          ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_purchase_product FOREIGN KEY (product_id)
        REFERENCES SOFTWARE_PRODUCT (product_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_purchase_qty   CHECK (quantity > 0),
    CONSTRAINT chk_purchase_cost  CHECK (unit_cost >= 0 AND total_cost >= 0),
    CONSTRAINT uq_purchase_invoice UNIQUE (invoice_no)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. LICENSE  — an individual licensable item of a product
-- ------------------------------------------------------------
CREATE TABLE LICENSE (
    license_id        INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    product_id        INT UNSIGNED     NOT NULL,
    license_type_id   INT UNSIGNED     NOT NULL,
    license_key       VARCHAR(120)     NOT NULL,
    total_seats       INT UNSIGNED     NOT NULL DEFAULT 1,
    valid_from        DATE             NOT NULL,
    valid_until       DATE             NOT NULL,
    status            ENUM('ACTIVE','EXPIRED','REVOKED') NOT NULL DEFAULT 'ACTIVE',
    purchase_id       INT UNSIGNED     NOT NULL,
    CONSTRAINT pk_license PRIMARY KEY (license_id),
    CONSTRAINT uq_license_key UNIQUE (license_key),
    CONSTRAINT fk_license_product FOREIGN KEY (product_id)
        REFERENCES SOFTWARE_PRODUCT (product_id)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_license_type   FOREIGN KEY (license_type_id)
        REFERENCES LICENSE_TYPE (license_type_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_license_purchase FOREIGN KEY (purchase_id)
        REFERENCES PURCHASE (purchase_id)         ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_license_dates CHECK (valid_until >= valid_from),
    CONSTRAINT chk_license_seats CHECK (total_seats >= 1)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 6. SUBSCRIPTION  — recurring billing extension of a license
-- ------------------------------------------------------------
CREATE TABLE SUBSCRIPTION (
    subscription_id   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    license_id        INT UNSIGNED     NOT NULL,
    billing_cycle     ENUM('MONTHLY','QUARTERLY','ANNUAL') NOT NULL,
    start_date        DATE             NOT NULL,
    end_date          DATE             NOT NULL,
    amount            DECIMAL(10,2)    NOT NULL,
    auto_renew        BOOLEAN          NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_subscription PRIMARY KEY (subscription_id),
    CONSTRAINT fk_subscription_license FOREIGN KEY (license_id)
        REFERENCES LICENSE (license_id)  ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_subscription_dates CHECK (end_date > start_date),
    CONSTRAINT chk_subscription_amt   CHECK (amount >= 0)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. DEPARTMENT  — organizational unit
-- ------------------------------------------------------------
CREATE TABLE DEPARTMENT (
    department_id    INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    department_name  VARCHAR(80)      NOT NULL,
    head_name        VARCHAR(80),
    annual_it_budget DECIMAL(12,2)    DEFAULT 0.00,
    CONSTRAINT pk_department PRIMARY KEY (department_id),
    CONSTRAINT uq_department_name UNIQUE (department_name)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 8. APP_USER  — employee / end user (USER is reserved in MySQL)
-- ------------------------------------------------------------
CREATE TABLE APP_USER (
    user_id          INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    department_id    INT UNSIGNED     NOT NULL,
    user_name        VARCHAR(80)      NOT NULL,
    email            VARCHAR(120)     NOT NULL,
    user_role        ENUM('IT_ADMIN','DEPT_MANAGER','PROCUREMENT','EMPLOYEE','COMPLIANCE_OFFICER')
                                      NOT NULL DEFAULT 'EMPLOYEE',
    is_active        BOOLEAN          NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_app_user PRIMARY KEY (user_id),
    CONSTRAINT uq_user_email UNIQUE (email),
    CONSTRAINT fk_user_department FOREIGN KEY (department_id)
        REFERENCES DEPARTMENT (department_id)  ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 9. DEVICE  — machine registered to a user
-- ------------------------------------------------------------
CREATE TABLE DEVICE (
    device_id        INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    user_id          INT UNSIGNED     NOT NULL,
    device_type      ENUM('LAPTOP','DESKTOP','WORKSTATION','MOBILE','SERVER') NOT NULL,
    hostname         VARCHAR(60)      NOT NULL,
    os_name          VARCHAR(50),
    CONSTRAINT pk_device PRIMARY KEY (device_id),
    CONSTRAINT uq_device_hostname UNIQUE (hostname),
    CONSTRAINT fk_device_user FOREIGN KEY (user_id)
        REFERENCES APP_USER (user_id)  ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 10. ALLOCATION  — license assigned to a user (optionally device)
-- ------------------------------------------------------------
CREATE TABLE ALLOCATION (
    allocation_id    INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    license_id       INT UNSIGNED     NOT NULL,
    user_id          INT UNSIGNED     NOT NULL,
    device_id        INT UNSIGNED,                -- NULL until installed
    allocation_date  DATE             NOT NULL,
    return_date      DATE,                        -- NULL = still active
    status           ENUM('ACTIVE','RECLAIMED','EXPIRED') NOT NULL DEFAULT 'ACTIVE',
    notes            VARCHAR(255),
    CONSTRAINT pk_allocation PRIMARY KEY (allocation_id),
    CONSTRAINT fk_alloc_license FOREIGN KEY (license_id)
        REFERENCES LICENSE (license_id)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_alloc_user    FOREIGN KEY (user_id)
        REFERENCES APP_USER (user_id)    ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_alloc_device  FOREIGN KEY (device_id)
        REFERENCES DEVICE (device_id)    ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_alloc_dates CHECK (return_date IS NULL OR return_date >= allocation_date)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 11. RENEWAL  — extension recorded against a purchase
-- ------------------------------------------------------------
CREATE TABLE RENEWAL (
    renewal_id       INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    purchase_id      INT UNSIGNED     NOT NULL,
    renewal_date     DATE             NOT NULL,
    renewal_amount   DECIMAL(12,2)    NOT NULL,
    new_valid_until  DATE             NOT NULL,
    remarks          VARCHAR(255),
    CONSTRAINT pk_renewal PRIMARY KEY (renewal_id),
    CONSTRAINT fk_renewal_purchase FOREIGN KEY (purchase_id)
        REFERENCES PURCHASE (purchase_id)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_renewal_amount CHECK (renewal_amount >= 0)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 12. COMPLIANCE_CHECK  — audit result per active allocation
-- ------------------------------------------------------------
CREATE TABLE COMPLIANCE_CHECK (
    check_id         INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    allocation_id    INT UNSIGNED     NOT NULL,
    check_date       DATE             NOT NULL,
    check_status     ENUM('PASS','OVERALLOCATED','EXPIRED_LICENSE','UNASSIGNED_DEVICE','USER_INACTIVE')
                                      NOT NULL,
    remarks          VARCHAR(255),
    CONSTRAINT pk_compliance PRIMARY KEY (check_id),
    CONSTRAINT fk_check_allocation FOREIGN KEY (allocation_id)
        REFERENCES ALLOCATION (allocation_id)  ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_check_per_day UNIQUE (allocation_id, check_date, check_status)
) ENGINE=InnoDB;

-- ============================================================
--  TRIGGERS — business rules enforced at the database level
-- ============================================================

-- BR-01 : license_key must never be allocated beyond purchased seats
DELIMITER $$

CREATE TRIGGER trg_alloc_before_insert
BEFORE INSERT ON ALLOCATION
FOR EACH ROW
BEGIN
    DECLARE v_seats      INT UNSIGNED;
    DECLARE v_active     INT;
    DECLARE v_status     VARCHAR(10);
    DECLARE v_until      DATE;

    SELECT total_seats, status, valid_until
      INTO v_seats, v_status, v_until
      FROM LICENSE
     WHERE license_id = NEW.license_id;

    IF v_status <> 'ACTIVE' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'BR-01 violated: license is not ACTIVE';
    END IF;

    IF NEW.allocation_date > v_until THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'BR-02 violated: allocation date is past license expiry';
    END IF;

    SELECT COUNT(*) INTO v_active
      FROM ALLOCATION
     WHERE license_id = NEW.license_id
       AND status = 'ACTIVE';

    IF v_active >= v_seats THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'BR-03 violated: all purchased seats for this license are allocated';
    END IF;
END$$

CREATE TRIGGER trg_alloc_before_update
BEFORE UPDATE ON ALLOCATION
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        SET NEW.status = 'RECLAIMED';          -- reclaim workflow
    END IF;
    IF NEW.return_date IS NOT NULL AND NEW.return_date < NEW.allocation_date THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'BR-04 violated: return date precedes allocation date';
    END IF;
END$$

DELIMITER ;
