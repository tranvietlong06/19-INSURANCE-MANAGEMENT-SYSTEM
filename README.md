# 🛡️ Insurance Management System

## Project Overview
This project is a full-stack Database Management System designed to handle insurance customers, policy contracts, claim assessments, and payouts. Built with a **MySQL** backend and a **Python (Streamlit)** frontend, the application supports contract tracking, claims processing, and automated financial reporting to ensure operational transparency.

## 🛠️ Tech Stack
* **Database:** MySQL (Relational Schema, Foreign Keys, Indexes)
* **Backend Logic:** SQL (Stored Procedures, Views, Triggers, UDFs)
* **Frontend/Interface:** Python (Streamlit, Pandas, `mysql-connector-python`)

## ✨ Key Features
* **Customer & Policy Management:** Enroll new customers and assign specialized insurance policies (Health, Auto, Home, etc.).
* **Automated Expiration Tracking:** Utilizes SQL User-Defined Functions (UDFs) to calculate and track active vs. expired contracts in real-time.
* **Claims Processing Guardrails:** A SQL `BEFORE INSERT` Trigger enforces business logic by blocking payouts for claims that have not been officially assessed and 'Approved'.
* **Dynamic Reporting Dashboard:** Uses SQL Views and Streamlit DataFrames to generate instant summaries of total payouts and active policies.

## 🚀 How to Run Locally

### 1. Database Setup
1. Open MySQL Workbench.
2. Open the `sql_finals.sql` script provided in this repository.
3. Execute the entire script to generate the `InsuranceDB` database, tables, mock data, and advanced SQL objects.

### 2. Application Setup
1. Ensure Python 3.x is installed on your machine.
2. Open your terminal and install the required dependencies:
   ```bash
   pip install mysql-connector-python streamlit pandas

3. Open app.py and update the database connection password on line 14 to match your local MySQL root password.

4. Run the application:
Bash

python -m streamlit run app.py  

Database Schema Highlights

    Customers: CustomerID (PK), Name, Address, Phone

    InsuranceTypes: InsuranceTypeID (PK), Name, Description

    InsuranceContracts: ContractID (PK), CustomerID (FK), InsuranceTypeID (FK), SignDate

    Assessments: AssessmentID (PK), ContractID (FK), Date, Result

    Payouts: PayoutID (PK), ContractID (FK), Amount, Date

    ### Final Step: The YouTube Video
When you record your screen for the YouTube presentation, keep it under 3-5 minutes. Here is a quick script/flow you can follow:
1. **Intro (30s):** "Hi, this is my Insurance Management System..." Show your ER diagram or SQL tables quickly.
2. **Demo Adding Data (60s):** Open the Streamlit web app. Show how easy it is to add a new customer using the form.
3. **Demo The Logic (60s):** Show the "Active Contracts" tab and explain how your custom SQL Function (`GetContractExpiration`) is doing the math behind the scenes. 
4. **Demo The Report (30s):** Show the "Payout Summary" tab. Mention that it is powered by a SQL View.

You now have the code, the report conclusion, and the GitHub documentation! Let me know if you need any adjustments to these texts before you submit.
