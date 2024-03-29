import time
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

ALPHAVANTAGE_API_KEY = "QO1H0O59FMXBAA24"

cached_rate = None
last_cache_time = 0


def fetch_exchange_rate(source_currency: str, destination_currency: str):
    global cached_rate, last_cache_time

    if time.time() - last_cache_time < 10 and cached_rate:
        return cached_rate

    url = (
        "https://www.alphavantage.co/query?"
        f"function=CURRENCY_EXCHANGE_RATE"
        f"&from_currency={source_currency}"
        f"&to_currency={destination_currency}"
        f"&apikey={ALPHAVANTAGE_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

        rate = response.json()["Realtime Currency Exchange Rate"][
            "5. Exchange Rate"
        ]  # noqa

        cached_rate = rate
        last_cache_time = time.time()

        return rate
    except (requests.RequestException, KeyError) as e:
        raise Exception(f"Failed to fetch exchange rate: {str(e)}")


@csrf_exempt
def exchange_rate_view(request):
    if request.method == "POST":
        try:
            data = request.POST
            source_currency = data.get("source_currency")
            destination_currency = data.get("destination_currency")

            if not source_currency or not destination_currency:
                raise Exception(
                    "Source currency and destination currency are required."
                )

            rate = fetch_exchange_rate(source_currency, destination_currency)

            return JsonResponse({"rate": rate})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
