
import joblib
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the serialized model pipeline (preprocessing + regressor bundled together)
model = joblib.load("superkart_sales_model.joblib")

# The exact set of input columns the model pipeline expects
EXPECTED_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_Type",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Store_Age",
    "Product_Id_Category",
    "Product_Category",
]


@app.route("/", methods=["GET"])
def health_check():
    """Simple health-check endpoint to confirm the API is running."""
    return jsonify({"status": "SuperKart Sales Forecasting API is up and running."})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predicts Product_Store_Sales_Total for a single record.
    Expects a JSON body with keys matching EXPECTED_COLUMNS.
    """
    try:
        data = request.get_json()

        # Validate input
        missing_cols = set(EXPECTED_COLUMNS) - set(data.keys())
        if missing_cols:
            return jsonify({"error": f"Missing columns: {missing_cols}"}), 400

        # Create DataFrame in the correct column order
        input_df = pd.DataFrame([data])[EXPECTED_COLUMNS]

        # Make prediction
        prediction = model.predict(input_df)[0]

        return jsonify({
            "prediction": float(prediction),
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict_batch", methods=["POST"])
def predict_batch():
    """
    Predicts Product_Store_Sales_Total for multiple records.
    Expects a JSON body with a list of records, each with keys matching EXPECTED_COLUMNS.
    """
    try:
        data = request.get_json()

        # Handle both list and {"data": [...]} formats
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict) and "data" in data:
            records = data["data"]
        else:
            return jsonify({"error": "Expected a list of records or {'data': [...]}"}), 400

        predictions = []
        for record in records:
            # Validate input
            missing_cols = set(EXPECTED_COLUMNS) - set(record.keys())
            if missing_cols:
                return jsonify({"error": f"Missing columns: {missing_cols}"}), 400

            # Create DataFrame in the correct column order
            input_df = pd.DataFrame([record])[EXPECTED_COLUMNS]

            # Make prediction
            prediction = model.predict(input_df)[0]
            predictions.append(float(prediction))

        return jsonify({
            "predictions": predictions,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
