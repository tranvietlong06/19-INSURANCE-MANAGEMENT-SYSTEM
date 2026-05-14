# 🛡️ Project 19: Insurance Management System

## 📌 Project Overview
The Insurance Management System is a centralized, data-driven application designed to handle the core operations of an insurance agency. It seamlessly connects a robust **MySQL** relational database with a modern **Streamlit (Python)** graphical interface. 

The system enforces strict business logic at the database level to ensure data integrity, prevent unauthorized financial payouts, and automate contract lifecycle tracking.

## ✨ Core Features & Technical Highlights
* **Automated Contract Management:** Utilizes a custom SQL User-Defined Function (`GetContractExpiration`) to calculate policy end-dates automatically.
* **Secure Claims Processing:** Implements a MySQL `BEFORE INSERT` Trigger that physically blocks financial payouts if the corresponding damage assessment has not been explicitly 'Approved'.
* **Referential Integrity:** Employs strict Primary Key/Foreign Key constraints with `ON DELETE CASCADE` to prevent orphan records when customer profiles are removed.
* **Business Intelligence:** Features a real-time reporting dashboard powered by a custom SQL View (`PayoutSummary`) to aggregate financial liabilities.
* **Role-Based Security:** Database access is segregated between Administrator and Agent roles to protect sensitive PII and financial data.

## 🛠️ Technology Stack
* **Database Engine:** MySQL 8.0+
* **Backend & Frontend:** Python 3.11, Streamlit
* **Data Processing:** Pandas
* **Connection Interface:** `mysql-connector-python`

---

## 🚀 Quick Start Guide

### 1. Database Setup
1. Open **MySQL Workbench**.
2. Create a new schema named `InsuranceDB`.
3. Open the `db/` folder in this repository and execute the provided `.sql` script. This will generate the normalized tables, advanced objects (Triggers, UDFs, Views), and insert the initial sample data.

### 2. Application Setup (One-Click)
To make evaluation as simple as possible, an automated setup script is included. 

1. Ensure Python and pip are installed on your machine.
2. Double-click the **`run.bat`** file located in the main directory.
3. The script will automatically install the necessary dependencies (`streamlit`, `pandas`, `mysql-connector-python`) and launch the application in your default web browser.

*(Alternatively, you can manually navigate to the `python/` directory and run `streamlit run app.py`)*

---

## 🎥 Project Demonstration
A full walkthrough of the system architecture, SQL logic validation, and graphical user interface can be viewed here:
* **(https://www.youtube.com/watch?v=VTvhU928gkA)**

## 📄 Documentation
The complete project documentation, including the Entity-Relationship Diagram (ERD), table structures, and future recommendations, is provided in the final LaTeX report submitted via the LMS.
