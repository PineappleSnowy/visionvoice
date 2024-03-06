import pyttsx3


def voice_announce(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()


if __name__ == "__main__":
    message_ = ""
    voice_announce(message_)
