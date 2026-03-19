from tikapi import TikAPI, ValidationException, ResponseException
import json

api = TikAPI("Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av")

User = api.user(
    accountKey="a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"
)

try:
    response = User.live.search(
        query="lilyachty"
    )

    data = response.json()

    # Write JSON to file
    with open("live_search_result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ JSON saved to live_search_result.json")

except ValidationException as e:
    print("Validation Error:", e, e.field)

except ResponseException as e:
    print("Response Error:", e, e.response.status_code)
