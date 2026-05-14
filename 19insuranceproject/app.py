import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date
import time 

# EK
ENCRYPTION_KEY = 'secret_key_123' 

# --- PAGE CONFIG ---
st.set_page_config(page_title="Insurance Manager Pro", page_icon="🛡️", layout="wide")

# --- CUSTOM FONT & COLOR INJECTION ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    /* 1. Global Font - Safely excluded 'span' to protect Streamlit's native icons! */
    html, body, p, label, h1, h2, h3, li {
        font-family: 'Poppins', sans-serif;
    }

    /* 2. Headers (Forest Green) */
    h1, h2, h3 {
        color: #1B5E20 !important; 
        font-weight: 600 !important;
    }

    /* 3. Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #F1F8E9 !important;
    }
    
    /* 4. Sidebar Text Color Fix */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] label {
        color: #1B5E20 !important;
        font-weight: 500;
    }

    /* 5. Buttons - ONLY target our form submit buttons, ignore the uploader! */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }
    
    /* 6. Hide default Streamlit top menu */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- HELPER FUNCTION: EXECUTE AND REFRESH ---
def execute_and_refresh(connection, query, params, success_message):
    """Executes a database query, handles errors, and refreshes the page."""
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        st.success(f"{success_message} Refreshing data...")
        time.sleep(1.2)
        st.rerun()
    except mysql.connector.Error as err:
        # Catch Foreign Key Errors
        if err.errno == 1452:
            st.error("❌ Transaction Blocked: The referenced ID does not exist in the system.")
        # Catch Custom Triggers and General Errors
        else:
            st.error(f"❌ Transaction Blocked: {err.msg}")

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    return mysql.connector.connect(
        host='localhost',
        database='InsuranceDB',
        user='root',
        password='CB05f!2yin' 
    
    )

conn = init_connection()

# --- SERVICE ---
def fetch_customers():
    # Use the same key: 'secret_key_123'
    query = f"""
        SELECT 
            CustomerID, 
            CustomerName, 
            AES_DECRYPT(Address, '{ENCRYPTION_KEY}') AS Address, 
            AES_DECRYPT(PhoneNumber, '{ENCRYPTION_KEY}') AS PhoneNumber 
        FROM Customers
    """
    df = pd.read_sql(query, conn)
    
    # Convert from binary bytes back to UTF-8 strings
    df['Address'] = df['Address'].apply(lambda x: x.decode('utf-8') if x else "")
    df['PhoneNumber'] = df['PhoneNumber'].apply(lambda x: x.decode('utf-8') if x else "")
    return df

def fetch_contracts():
    # This query pulls the contracts and calculates expiration using your SQL UDF
    query = """
        SELECT 
            ic.ContractID, 
            c.CustomerName, 
            it.InsuranceName, 
            ic.SignDate, 
            GetContractExpiration(ic.ContractID) AS ExpirationDate
        FROM InsuranceContracts ic
        JOIN Customers c ON ic.CustomerID = c.CustomerID
        JOIN InsuranceTypes it ON ic.InsuranceTypeID = it.InsuranceTypeID
    """
    return pd.read_sql(query, conn)

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("🛡️ Navigation Menu")
menu = [
    "Menu", 
    "Dashboard", 
    "Manage Customers", 
    "Insurance Products", # <-- Add this new option
    "Manage Contracts", 
    "Claims & Assessments", 
    "Record Payouts"
]
choice = st.sidebar.radio("Go to:", menu)

# --- HELPER FUNCTION: FIX INDEX ---
def display_df(records, columns):
    df = pd.DataFrame(records, columns=columns)
    df.index = df.index + 1  
    st.dataframe(df, use_container_width=True)
    return df

# --- DYNAMIC CONTENT ---

if choice == "Menu":
    st.title("Welcome to Insurance Manager Pro")
    st.markdown("### 🏢 Centralized Agency Management System")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**For Agents:** Use the sidebar to enroll new customers, issue policies, and file damage assessments from the field.")
    with col2:
        st.success("**For Management:** Use the Business Dashboard to track real-time claim volumes, payout distributions, and company health.")
        
    st.write("---")
    st.write("👈 **Select an option from the navigation menu on the left to get started.**")

elif choice == "Dashboard":
    st.title("📊 Dashboard")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PayoutSummary;")
    records = cursor.fetchall()
    
    if records:
        df = pd.DataFrame(records, columns=["ID", "Name", "Claims", "Total ($)"])
        
        # --- 1. Top Metrics (Added Average) ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", len(df))
        col2.metric("Claims Processed", df["Claims"].sum())
        col3.metric("Total Paid Out", f"${df['Total ($)'].sum():,.2f}")
        
        avg_payout = df['Total ($)'].sum() / len(df) if len(df) > 0 else 0
        col4.metric("Avg Paid per Cust.", f"${avg_payout:,.2f}")
        
        st.divider()
        st.subheader("Payout Summary")
        
        # --- 2. Global Search & Sort (Below metrics, side-by-side) ---
        col_search, col_sort = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search any field (Name, ID, Amount):")
        with col_sort:
            sort_option = st.selectbox("Sort by:", ["Default (ID)", "Name (A-Z)", "Name (Z-A)", "Highest Payout", "Lowest Payout"])

        # Apply Global Search (Checks all columns at once)
        if search_query:
            mask = df.apply(lambda x: x.astype(str).str.contains(search_query, case=False).any(), axis=1)
            df = df[mask]

        # Apply Sorting
        if sort_option == "Name (A-Z)":
            df = df.sort_values(by="Name", ascending=True)
        elif sort_option == "Name (Z-A)":
            df = df.sort_values(by="Name", ascending=False)
        elif sort_option == "Highest Payout":
            df = df.sort_values(by="Total ($)", ascending=False)
        elif sort_option == "Lowest Payout":
            df = df.sort_values(by="Total ($)", ascending=True)

        # Fix index to look nice after sorting/filtering
        df.index = range(1, len(df) + 1) 
        st.dataframe(df, use_container_width=True)
        
        # --- 3. More Analysis (Two Charts) ---
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Payout Distribution")
            st.bar_chart(data=df, x="Name", y="Total ($)")
        with col_chart2:
            st.subheader("Claims Volume by Customer")
            st.bar_chart(data=df, x="Name", y="Claims", color="#ffaa00")
    else:
        st.info("No data available yet.")

elif choice == "Manage Customers":
    st.title("👤 Customer Management")
    tab1, tab2, tab3 = st.tabs(["View All", "Add New", "Delete Customer"])

    # 1. Fetch the decrypted data ONCE for the whole section
    data = fetch_customers() 

    with tab1:
        st.subheader("All Enrolled Customers")
        # Use the decrypted data here instead of a raw cursor.execute
        if not data.empty:
            st.dataframe(data, use_container_width=True)
        else:
            st.info("No customer records found.")
        
    with tab2:
        with st.form("add_customer_form"):
          name = st.text_input("Full Name")
          addr = st.text_input("Address")
          phone = st.text_input("Phone Number")
        
          if st.form_submit_button("Save Customer"):
            # The query must call AES_ENCRYPT so the DB stores binary, not plain text
            query = f"""
                INSERT INTO Customers (CustomerName, Address, PhoneNumber) 
                VALUES (%s, AES_ENCRYPT(%s, '{ENCRYPTION_KEY}'), AES_ENCRYPT(%s, '{ENCRYPTION_KEY}'))
            """
            execute_and_refresh(conn, query, (name, addr, phone), f"Customer '{name}' secured and added!")
                
    with tab3:
        st.warning("⚠️ Warning: Deleting a customer will also automatically delete all their contracts, assessments, and payouts.")
        with st.form("delete_customer_form"):
            del_id = st.number_input("Enter Customer ID to Delete", min_value=1)
            del_submitted = st.form_submit_button("Delete Customer Data")
            
            if del_submitted:
                cursor = conn.cursor()
                # 1. Check if the customer actually exists first
                cursor.execute("SELECT CustomerName FROM Customers WHERE CustomerID = %s", (del_id,))
                result = cursor.fetchone()
                
                # 2. If they exist, delete them
                if result:
                    cursor.execute("DELETE FROM Customers WHERE CustomerID = %s", (del_id,))
                    conn.commit()
                    st.success(f"Success! Customer '{result[0]}' and all associated records have been permanently deleted.")
                else:
                    st.error("Error: Customer ID not found in the database.")

elif choice == "Insurance Products":
    st.title("🛡️ Insurance Product Catalog")
    tab1, tab2 = st.tabs(["Current Products", "Add New Product"])
    
    with tab1:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM insurancetypes;")
        display_df(cursor.fetchall(), ["ID", "Product Name", "Description"])

    with tab2:
        with st.form("new_product_form"):
            p_name = st.text_input("Product Name (e.g., Cyber Insurance)")
            p_desc = st.text_area("Coverage Description")
            if st.form_submit_button("Add to Catalog"):
                cursor = conn.cursor()
                cursor.execute("INSERT INTO insurancetypes (InsuranceName, Description) VALUES (%s, %s)", (p_name, p_desc))
                conn.commit()
                st.success(f"Product '{p_name}' is now live!")

elif choice == "Manage Contracts":
    st.title("📝 Contract Management")

    df = fetch_contracts() 

    if not df.empty:
        # 2. Now 'df' is defined, so line 318 will work!
        styled_df = df.style.apply(highlight_expiring, axis=1).hide(axis="index")
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No active contracts found.")
    
    tab1, tab2 = st.tabs(["Active Contracts", "Create New Contract"])
    
    with tab1:
        cursor = conn.cursor()
        cursor.execute("SELECT ContractID, CustomerID, SignDate, GetContractExpiration(ContractID) FROM insurancecontracts;")
        records = cursor.fetchall()
        
        if records:
            df = pd.DataFrame(records, columns=["Contract ID", "Customer ID", "Sign Date", "Expiration Date"])
            df['Expiration Date'] = pd.to_datetime(df['Expiration Date']).dt.date
            
            def highlight_expiring(row):
                days_left = (row['Expiration Date'] - date.today()).days
                if days_left < 0:
                    return ['background-color: #FFCDD2'] * len(row)
                elif days_left <= 30:
                    return ['background-color: #FFF9C4'] * len(row)
                return [''] * len(row)

            st.write("💡 *Yellow rows expire within 30 days. Red rows have already expired.*")
            styled_df = df.style.apply(highlight_expiring, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No contracts found.")

    with tab2:
        with st.form("new_contract_form"):
            cust_id = st.number_input("Customer ID", min_value=1)
            
            # Fetch Insurance Types
            cursor.execute("SELECT InsuranceTypeID, InsuranceName FROM insurancetypes;")
            db_types = cursor.fetchall()
            type_options = {f"{t[0]} - {t[1]}": t[0] for t in db_types}
            selected_type_str = st.selectbox("Insurance Type", list(type_options.keys()))
            type_id = type_options[selected_type_str] 
            
            sign_date = st.date_input("Sign Date", value=date.today())
            
            if st.form_submit_button("Issue Policy"):
                query = "INSERT INTO insurancecontracts (CustomerID, InsuranceTypeID, SignDate) VALUES (%s, %s, %s)"
                execute_and_refresh(conn, query, (cust_id, type_id, sign_date), "Policy issued successfully!")
           
            st.write("💡 *Yellow rows expire within 30 days. Red rows have already expired.*")
            
            # --- THE FIX: Add .hide(axis="index") to the end ---
            styled_df = df.style.apply(highlight_expiring, axis=1).hide(axis="index")
            
            st.dataframe(styled_df, use_container_width=True)

            
           
elif choice == "Claims & Assessments":
    st.title("🔍 Damage Assessments")
    st.info("File a new damage assessment here to authorize a future payout.")
    
    with st.form("new_assessment_form"):
        contract_id = st.number_input("Contract ID", min_value=1)
        assess_date = st.date_input("Assessment Date", value=date.today())
        result = st.selectbox("Status", ["Approved: Minor", "Approved: Major", "Denied: Out of Policy", "Pending Investigation"])
        
        st.write("📷 **Upload Evidence**")
        uploaded_file = st.file_uploader("Upload photos of damage (JPEG/PNG)", type=['png', 'jpg', 'jpeg'])
        
        # --- DRY PRINCIPLE APPLIED HERE ---
        if st.form_submit_button("Log Assessment"):
            if uploaded_file is not None:
                st.toast("Photo evidence linked to claim!")
            
            query = "INSERT INTO Assessments (ContractID, AssessmentDate, Result) VALUES (%s, %s, %s)"
            execute_and_refresh(conn, query, (contract_id, assess_date, result), "Assessment recorded successfully!")

elif choice == "Record Payouts":
    st.title("💸 Financial Payouts")
    tab1, tab2 = st.tabs(["Pending Claims (Unpaid)", "Process New Payment"])

    with tab1:
        st.subheader("📋 Claims Awaiting Payment")
        cursor = conn.cursor()
        # SQL logic: Join Contracts + Assessments, filter for Approved, exclude those already in Payouts
        query = """
        SELECT c.ContractID, cust.CustomerName, a.AssessmentDate, a.Result
        FROM insurancecontracts c
        JOIN customers cust ON c.CustomerID = cust.CustomerID
        JOIN assessments a ON c.ContractID = a.ContractID
        LEFT JOIN payouts p ON c.ContractID = p.ContractID
        WHERE (a.Result LIKE '%Approved%' OR a.Result LIKE '%Major%' OR a.Result LIKE '%Minor%')
        AND p.PayoutID IS NULL;
        """
        cursor.execute(query)
        pending = cursor.fetchall()
        
        if pending:
            st.warning(f"There are {len(pending)} approved claims that have not been paid.")
            display_df(pending, ["Contract ID", "Customer Name", "Approved Date", "Result"])
        else:
            st.success("All approved claims have been settled! No pending payouts.")

    with tab2:
        with st.form("payout_form"):
            contract_id = st.number_input("Contract ID to Pay", min_value=1)
            amount = st.number_input("Payout Amount ($)", min_value=0.0, format="%.2f")
            payout_date = st.date_input("Date of Payout", value=date.today())
            
            # --- DRY PRINCIPLE APPLIED HERE ---
            if st.form_submit_button("Process Payment"):
                query = "INSERT INTO Payouts (ContractID, Amount, PayoutDate) VALUES (%s, %s, %s)"
                execute_and_refresh(conn, query, (contract_id, amount, payout_date), "Payment processed successfully!")