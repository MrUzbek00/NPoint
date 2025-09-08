import smtplib

my_email="mrparkerbot@gmail.com" # your email address
my_password = "abxs ffgd cugo ezml" #your password

def send_mail(receiver_email: str, reset_code: str):
    # for sending email using bravomailing server
    # "Subject:This is a subject for the message\n\n This is a body: Hello"
    message = f"Subject:This is No-Reply Email, Password Reset Code\n\n Your password reset code is: {reset_code}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls() # is used to sacure the connection
        connection.login(user=my_email, password=my_password)
        connection.sendmail(from_addr=my_email, to_addrs=receiver_email, msg=message)

