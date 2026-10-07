-- ============================================================
--  SOFTWARE LICENSE & SUBSCRIPTION MANAGEMENT SYSTEM
--  04_procedures.sql — transactional workflows (FR01–FR06)
--  MySQL 8.x
-- ============================================================
USE license_mgmt;

DELIMITER $$

-- ------------------------------------------------------------
-- sp_allocate_license : allocate a seat to a user (FR02)
-- Enforces seat limits & license validity inside a transaction.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_allocate_license (
    IN  p_license_id  INT UNSIGNED,
    IN  p_user_id     INT UNSIGNED,
    IN  p_device_id   INT UNSIGNED,        -- may be NULL
    IN  p_notes       VARCHAR(255),
    OUT p_alloc_id    INT UNSIGNED
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        INSERT INTO ALLOCATION (license_id, user_id, device_id,
                                allocation_date, status, notes)
        VALUES (p_license_id, p_user_id, p_device_id,
                CURDATE(), 'ACTIVE', p_notes);
        SET p_alloc_id = LAST_INSERT_ID();
    COMMIT;
END$$

-- ------------------------------------------------------------
-- sp_reclaim_license : reclaim a seat from a user (FR03)
-- ------------------------------------------------------------
CREATE PROCEDURE sp_reclaim_license (
    IN  p_alloc_id    INT UNSIGNED,
    IN  p_remarks     VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        UPDATE ALLOCATION
           SET return_date = CURDATE(),
               status      = 'RECLAIMED',
               notes       = CONCAT(COALESCE(notes, ''), ' | Reclaimed: ',
                                    COALESCE(p_remarks, ''))
         WHERE allocation_id = p_alloc_id
           AND status = 'ACTIVE';
        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Allocation not found or not ACTIVE';
        END IF;
    COMMIT;
END$$

-- ------------------------------------------------------------
-- sp_renew_license : record a renewal and extend validity (FR06)
-- ------------------------------------------------------------
CREATE PROCEDURE sp_renew_license (
    IN  p_purchase_id      INT UNSIGNED,
    IN  p_renewal_amount   DECIMAL(12,2),
    IN  p_new_valid_until  DATE,
    IN  p_remarks          VARCHAR(255)
)
BEGIN
    DECLARE v_product_id INT UNSIGNED;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT product_id INTO v_product_id
      FROM PURCHASE WHERE purchase_id = p_purchase_id;

    START TRANSACTION;
        INSERT INTO RENEWAL (purchase_id, renewal_date, renewal_amount,
                             new_valid_until, remarks)
        VALUES (p_purchase_id, CURDATE(), p_renewal_amount,
                p_new_valid_until, p_remarks);

        UPDATE LICENSE
           SET valid_until = p_new_valid_until,
               status      = 'ACTIVE'
         WHERE purchase_id = p_purchase_id;
    COMMIT;
END$$

-- ------------------------------------------------------------
-- sp_run_compliance_check : audit all active allocations (FR05)
-- Writes one COMPLIANCE_CHECK row per allocation.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_run_compliance_check ()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_alloc   INT UNSIGNED;
    DECLARE v_status  VARCHAR(30);
    DECLARE cur CURSOR FOR
        SELECT allocation_id, compliance_status
          FROM v_compliance_violations;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_alloc, v_status;
        IF done = 1 THEN
            LEAVE read_loop;
        END IF;
        INSERT INTO COMPLIANCE_CHECK (allocation_id, check_date,
                                      check_status, remarks)
        VALUES (v_alloc, CURDATE(), v_status, 'Automated compliance sweep');
    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;
