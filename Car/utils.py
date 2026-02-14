import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def predict_vehicle_price(vehicle_data):
    
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are a vehicle price prediction expert in India.

    Predict the resale price in INR.

    Vehicle Type: {vehicle_data.get('vehicle_type')}
    Brand: {vehicle_data.get('brand')}
    Model: {vehicle_data.get('model')}
    Year: {vehicle_data.get('year')}
    KM Driven: {vehicle_data.get('km_driven')}
    Fuel: {vehicle_data.get('fuel')}
    Condition: {vehicle_data.get('condition')}

    Only return estimated price in number format.
    """

    response = model.generate_content(prompt)
    
    return response.text
