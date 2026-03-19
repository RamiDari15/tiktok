from tikapi import TikAPI, ValidationException, ResponseException

api = TikAPI("Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av")
User = api.user(
    accountKey="a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"
)

try:
    response = User.live.info(
        room_id="7112492061034646278"
    )

    print(response.json())

except ValidationException as e:
    print(e, e.field)

except ResponseException as e:
    print(e, e.response.status_code)
