CREATE DATABASE IF NOT EXISTS InsuranceDB;
USE InsuranceDB;

-- Drop tables if they already exist (to prevent errors when rerunning)
DROP TABLE IF EXISTS Payouts;
DROP TABLE IF EXISTS Assessments;
DROP TABLE IF EXISTS InsuranceContracts;
DROP TABLE IF EXISTS InsuranceTypes;
DROP TABLE IF EXISTS Customers;

-- Retrieve and decrypt data
SELECT CustomerName, AES_DECRYPT(PhoneNumber, 'secret_key_123') AS DecryptedPhone 
FROM Customers;

-- 1. Create Customers Table (Parent)
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerName VARCHAR(100) NOT NULL,
    Address VARBINARY(255),
    PhoneNumber VARBINARY(255)
);

-- 2. Create InsuranceTypes Table (Parent)
CREATE TABLE InsuranceTypes (
    InsuranceTypeID INT AUTO_INCREMENT PRIMARY KEY,
    InsuranceName VARCHAR(100) NOT NULL,
    Description TEXT
);

-- 3. Create InsuranceContracts Table (Child of Customers & InsuranceTypes)
CREATE TABLE InsuranceContracts (
    ContractID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    InsuranceTypeID INT NOT NULL,
    SignDate DATE NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (InsuranceTypeID) REFERENCES InsuranceTypes(InsuranceTypeID) ON DELETE CASCADE
);

-- 4. Create Assessments Table (Child of InsuranceContracts)
CREATE TABLE Assessments (
    AssessmentID INT AUTO_INCREMENT PRIMARY KEY,
    ContractID INT NOT NULL,
    AssessmentDate DATE NOT NULL,
    Result VARCHAR(255) NOT NULL,
    FOREIGN KEY (ContractID) REFERENCES InsuranceContracts(ContractID) ON DELETE CASCADE
);

-- 5. Create Payouts Table (Child of InsuranceContracts)
CREATE TABLE Payouts (
    PayoutID INT AUTO_INCREMENT PRIMARY KEY,
    ContractID INT NOT NULL,
    Amount DECIMAL(15, 2) NOT NULL,
    PayoutDate DATE NOT NULL,
    FOREIGN KEY (ContractID) REFERENCES InsuranceContracts(ContractID) ON DELETE CASCADE
);

-- Insert 5 Customers (Fully Encrypted)
INSERT INTO Customers (CustomerName, Address, PhoneNumber) VALUES
('Alex Johnson', AES_ENCRYPT('123 Maple St, Springfield', 'my_secret_key_123'), AES_ENCRYPT('555-0101', 'my_secret_key_123')),
('Maria Garcia', AES_ENCRYPT('456 Oak Ave, Metropolis', 'my_secret_key_123'), AES_ENCRYPT('555-0102', 'my_secret_key_123')),
('David Chen', AES_ENCRYPT('789 Pine Rd, Gotham', 'my_secret_key_123'), AES_ENCRYPT('555-0103', 'my_secret_key_123')),
('Sarah Smith', AES_ENCRYPT('321 Elm St, Star City', 'my_secret_key_123'), AES_ENCRYPT('555-0104', 'my_secret_key_123')),
('James Wilson', AES_ENCRYPT('654 Cedar Ln, Central City', 'my_secret_key_123'), AES_ENCRYPT('555-0105', 'my_secret_key_123'));

-- Insert 5 Insurance Types
INSERT INTO InsuranceTypes (InsuranceName, Description) VALUES
('Health Premium', 'Comprehensive medical coverage including dental and vision.'),
('Auto Standard', 'Standard collision and liability coverage for vehicles.'),
('Home Protection', 'Covers property damage, fire, and theft.'),
('Life Plus', 'Term life insurance with a 20-year coverage period.'),
('Travel Safe', 'Short-term coverage for trip cancellations and medical emergencies abroad.');

-- Insert 5 Insurance Contracts
INSERT INTO InsuranceContracts (CustomerID, InsuranceTypeID, SignDate) VALUES
(1, 1, '2025-01-15'), -- Alex bought Health
(2, 2, '2025-02-20'), -- Maria bought Auto
(3, 3, '2025-03-10'), -- David bought Home
(4, 1, '2025-04-05'), -- Sarah bought Health
(5, 5, '2025-05-12'); -- James bought Travel

-- Insert 5 Assessments
INSERT INTO Assessments (ContractID, AssessmentDate, Result) VALUES
(2, '2025-08-10', 'Approved: Minor bumper damage assessed.'),
(1, '2025-09-15', 'Approved: Routine surgery costs verified.'),
(3, '2025-10-05', 'Denied: Water damage not covered under standard policy.'),
(2, '2025-11-20', 'Approved: Windshield replacement.'),
(5, '2025-12-01', 'Approved: Flight cancellation due to weather.');

-- Insert 5 Payouts (Only for the approved assessments)
INSERT INTO Payouts (ContractID, Amount, PayoutDate) VALUES
(2, 1500.00, '2025-08-15'),
(1, 8500.00, '2025-09-20'),
(2, 300.00, '2025-11-25'),
(5, 1200.00, '2025-12-05'),
(1, 450.00, '2026-01-10');

SELECT * FROM InsuranceContracts;

-- Indexes
-- Optimize looking up contracts by a specific customer
CREATE INDEX idx_customer_contract ON InsuranceContracts(CustomerID);

-- Optimize looking up assessments by date
CREATE INDEX idx_assessment_date ON Assessments(AssessmentDate);

-- Views
CREATE VIEW PayoutSummary AS
SELECT 
    c.CustomerName, 
    it.InsuranceName, 
    p.Amount, 
    p.PayoutDate
FROM Payouts p
JOIN InsuranceContracts ic ON p.ContractID = ic.ContractID
JOIN Customers c ON ic.CustomerID = c.CustomerID
JOIN InsuranceTypes it ON ic.InsuranceTypeID = it.InsuranceTypeID;

-- 
SELECT * FROM PayoutSummary;

-- User Defined Function (UDF)
DELIMITER //

CREATE FUNCTION GetContractExpiration(c_id INT) 
RETURNS DATE
DETERMINISTIC
BEGIN
    DECLARE exp_date DATE;
    
    -- Calculate expiration as 1 year after the SignDate
    SELECT DATE_ADD(SignDate, INTERVAL 1 YEAR) INTO exp_date
    FROM InsuranceContracts
    WHERE ContractID = c_id;
    
    RETURN exp_date;
END //

DELIMITER ;

SELECT ContractID, SignDate, GetContractExpiration(ContractID) AS ExpirationDate FROM InsuranceContracts;

-- Stored proc
DELIMITER //

CREATE PROCEDURE GetCustomerTotalPayout(
    IN p_CustomerID INT, 
    OUT p_TotalPayout DECIMAL(15,2)
)
BEGIN
    SELECT SUM(p.Amount) INTO p_TotalPayout
    FROM Payouts p
    JOIN InsuranceContracts ic ON p.ContractID = ic.ContractID
    WHERE ic.CustomerID = p_CustomerID;
END //

DELIMITER ;


CALL GetCustomerTotalPayout(1, @total);
SELECT @total AS TotalPaidToAlex;

-- Trigger
DELIMITER //

CREATE TRIGGER BeforePayoutInsert
BEFORE INSERT ON Payouts
FOR EACH ROW
BEGIN
    DECLARE assessment_result VARCHAR(255);

    -- Find the result of the latest assessment for this contract
    SELECT Result INTO assessment_result
    FROM Assessments
    WHERE ContractID = NEW.ContractID
    ORDER BY AssessmentDate DESC LIMIT 1;

    -- Block the insertion if there is no assessment, or if it was Denied
    IF assessment_result IS NULL OR assessment_result NOT LIKE 'Approved%' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Payout Blocked: The assessment for this contract was not approved.';
    END IF;
END //

DELIMITER ;

INSERT INTO Payouts (ContractID, Amount, PayoutDate) VALUES (3, 500.00, '2025-11-01');

CREATE OR REPLACE VIEW PayoutSummary AS
SELECT 
    cust.CustomerID, 
    cust.CustomerName, 
    COUNT(p.PayoutID) AS NumberOfPayouts, 
    SUM(p.Amount) AS TotalAmountPaid
FROM Customers cust
JOIN InsuranceContracts c ON cust.CustomerID = c.CustomerID
JOIN Payouts p ON c.ContractID = p.ContractID
GROUP BY cust.CustomerID, cust.CustomerName;

SHOW TABLES;

