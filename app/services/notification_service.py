def send_notification(destination: str, message: str, method: str = "email"):
    if method == "email":
        print(f"📧 EMAIL envoyé à {destination} : {message}")
    else:
        print(f"📱 SMS envoyé à {destination} : {message}")