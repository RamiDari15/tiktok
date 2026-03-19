from tikapi import TikAPI, ValidationException, ResponseException




TEXT_MESSAGE = "Hey! How are you?"

CONVERSATION_ID = "0:1:7069796194781529134:7143877991353009194"
CONVERSATION_SHORT_ID = "7416591677414998318"

TICKET = "deprecated"

# --------------------------------
# INIT API
# --------------------------------
api = TikAPI("LxcVXRgh5Asr59aQvc2GNHRbz4gTUh1IFLHZHuBjIqRMO8RK")
User = api.user(
    accountKey="a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"
)

CONVERSATION_ID = "0:1:7069796194781529134:7143877991353009194"
CONVERSATION_SHORT_ID = "7416591677414998318"


try:

    response = User.sendMessage(
        text=TEXT_MESSAGE,
        conversation_id=CONVERSATION_ID,
        conversation_short_id=CONVERSATION_SHORT_ID,
        ticket="3M8IlBpABq00h2aNB1B5JJ2ne0DTnGLLAFjGQQGMf4BKWJxEYxf7RAE0KaD2EjkQkWiJalT4xj36JGWa1ZmQg7SgQfHLoXffNFYLkIJhe1HVyiPXitoxWFyuzlX1xvBCYhZxkQALHE4gx9AaXBPEZjks7jC"
    )

    print("Message sent successfully")
    print(response.json())

except ValidationException as e:
    print("Validation error:", e, e.field)

except ResponseException as e:
    print("API error:", e.response.status_code, e)