from tikapi import TikAPI, ValidationException, ResponseException

api = TikAPI("Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av")

User = api.user(
    accountKey="a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"
)

try:
    response = User.info(   # 👈 USE THIS, NOT api.user()
        unique_id="stef_gamingg"
    )

    print(response.json())

except ValidationException as e:
    print("Validation Error:", e, e.field)

except ResponseException as e:
    print("Response Error:", e, e.response.status_code)
