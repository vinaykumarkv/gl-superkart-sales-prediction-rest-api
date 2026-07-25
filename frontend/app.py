import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend API.
# Replace this with the URL of your deployed Flask application.
BACKEND_URL = "https://localhost:7860"  # Change this to your deployed backend URL

# Configure the Streamlit application
st.set_page_config(page_title="SuperKart Sales Forecasting", layout="centered")

# Application title and description
st.title("SuperKart Sales Forecasting")
st.write(
    "Predict the expected total sales revenue (**Product_Store_Sales_Total**) for a product "
    "at a given store using the trained machine learning model."
)

# Create two tabs:
# 1. Single Prediction
# 2. Batch Prediction using a CSV file
tab1, tab2 = st.tabs(["Single Prediction", "Batch Prediction (CSV)"])

# ---------------------------------------------------------------------------
# TAB 1: Single Prediction
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Enter Product and Store Details")

    # Split the input form into two columns for better layout
    col1, col2 = st.columns(2)

    # -------------------------
    # Product-related inputs
    # -------------------------
    with col1:
        product_weight = st.number_input(
            "Product Weight (kg)",
            min_value=0.1,
            value=10.0,
            step=0.1
        )

        product_sugar_content = st.selectbox(
            "Product Sugar Content",
            ["Low Sugar", "Regular", "No Sugar"]
        )

        product_allocated_area = st.number_input(
            "Product Allocated Area (ratio)",
            min_value=0.001,
            value=0.05,
            step=0.001,
            format="%.3f"
        )

        product_type = st.selectbox(
            "Product Type",
            [
                "Dairy",
                "Meat",
                "Beverages",
                "Snack Foods",
                "Frozen Foods",
                "Bakery",
                "Health and Hygiene",
                "Household",
                "Others",
            ],
        )

        product_mrp = st.number_input(
            "Product MRP ($)",
            min_value=0.1,
            value=100.0,
            step=1.0
        )

    # -------------------------
    # Store-related inputs
    # -------------------------
    with col2:
        store_size = st.selectbox(
            "Store Size",
            ["Small", "Medium", "High"]
        )

        store_location_city_type = st.selectbox(
            "Store Location City Type",
            ["Tier 1", "Tier 2", "Tier 3"]
        )

        store_type = st.selectbox(
            "Store Type",
            [
                "Food Mart",
                "Supermarket Type1",
                "Supermarket Type2",
                "Departmental Store",
            ],
        )

        store_age = st.number_input(
            "Store Age (years)",
            min_value=0,
            value=10,
            step=1
        )

        # Product ID prefix categories
        # FD = Food
        # DR = Drinks
        # NC = Non-Consumable
        # HC = Health Care
        # OT = Others
        product_id_category = st.selectbox(
            "Product Id Category",
            ["FD", "DR", "NC", "HC", "OT"]
        )

        # Broad product category
        product_category = st.selectbox(
            "Product Category",
            ["Food", "Non-Consumable", "Drinks"]
        )

    # Send the entered data to the backend API when the button is clicked
    if st.button("Predict Sales", type="primary"):

        # Create the JSON payload expected by the Flask API
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_Type": product_type,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Store_Age": store_age,
            "Product_Id_Category": product_id_category,
            "Product_Category": product_category,
        }

        try:
            # Send POST request to the backend prediction endpoint
            response = requests.post(f"{BACKEND_URL}/predict", json=payload)

            # Display prediction if request is successful
            if response.status_code == 200:
                result = response.json()
                st.success(f"💰 Predicted Sales: **${result['prediction']:,.2f}**")
            else:
                # Display backend error message
                st.error(f"Error: {response.text}")

        except Exception as e:
            # Handle connection or network errors
            st.error(f"Connection error: {str(e)}")

# ---------------------------------------------------------------------------
# TAB 2: Batch Prediction
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Upload CSV for Batch Prediction")

    # Inform users about the required CSV columns
    st.info(
        "CSV should contain the following columns: "
        "Product_Weight, Product_Sugar_Content, Product_Allocated_Area, "
        "Product_Type, Product_MRP, Store_Size, "
        "Store_Location_City_Type, Store_Type, Store_Age, "
        "Product_Id_Category, Product_Category"
    )

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:

        # Read uploaded CSV into a DataFrame
        df = pd.read_csv(uploaded_file)

        # Display uploaded data
        st.write("Uploaded Data:")
        st.dataframe(df)

        # Generate predictions for every row in the CSV
        if st.button("Predict Batch", type="primary"):

            predictions = []

            # Iterate through each record
            for _, row in df.iterrows():
                try:
                    # Send each row as JSON to the backend
                    response = requests.post(
                        f"{BACKEND_URL}/predict",
                        json=row.to_dict()
                    )

                    if response.status_code == 200:
                        predictions.append(response.json()['prediction'])
                    else:
                        predictions.append(None)

                except:
                    # Store None if prediction fails
                    predictions.append(None)

            # Add predictions as a new column
            df['Predicted_Sales'] = predictions

            # Display prediction results
            st.write("Predictions:")
            st.dataframe(df)

            # Create downloadable CSV containing predictions
            csv = df.to_csv(index=False).encode('utf-8')

            st.download_button(
                "Download Predictions",
                csv,
                "predictions.csv",
                "text/csv"
            )
