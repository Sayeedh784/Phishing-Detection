import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import your ML scripts
from ml.predict import predict_url, predict_email

@csrf_exempt
def predict_view(request):
    # 1. 🛡️ FIX THE EXTENSION SECURITY BLOCK (Handle OPTIONS preflight)
    if request.method == "OPTIONS":
        response = JsonResponse({"message": "CORS OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response

    # 2. 🧠 HANDLE THE ACTUAL SCAN
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            t = data.get("type")
            text = data.get("text", "")

            # Run the Machine Learning model
            if t == "url":
                result = predict_url(text)
            elif t == "email":
                result = predict_email(text)
            else:
                return JsonResponse({"error": "Invalid scan type"}, status=400)

            # Return the ML result to the extension safely
            response = JsonResponse(result)
            response["Access-Control-Allow-Origin"] = "*"
            return response

        except Exception as e:
            # If the ML model crashes, catch it so it doesn't break the extension!
            error_details = str(e)
            print(f"🚨 ML CRASH: {error_details}") # Print to your terminal
            
            response = JsonResponse({"error": "ML Prediction failed", "detail": error_details}, status=500)
            response["Access-Control-Allow-Origin"] = "*"
            return response

    return JsonResponse({"error": "Only POST allowed"}, status=405)


def health_view(request):
    response = JsonResponse({"status": "ok", "message": "PhishDetect API is running"})
    response["Access-Control-Allow-Origin"] = "*"
    return response