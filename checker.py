from tikapi import TikAPI, ValidationException, ResponseException

api = TikAPI("Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av")

try:
    response = api.public.check(
        username="jiinaa777"
    )

    print(response.json())

except ValidationException as e:
    print(e, e.field)

except ResponseException as e:
    print(e, e.response.status_code)
