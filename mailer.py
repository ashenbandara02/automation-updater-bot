import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = ""
sender_password = ""

current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def sendmail(ustart, ustop, filestobe, filesdone, filesremaining, urls, errorlist):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)

        recipient_email = "chamaralakshan7799@gmail.com"
        subject = f"Uploader Bot Log : {str(current_time)}"
        body = f"""
        <b>Update Started :</b> {str(ustart)}<br>
        <b>Update Stopped :</b> {str(ustop)}<br><br>

        <b>Files was to be Updated :</b> {str(filestobe)}<br>
        <b>Files Updated :</b> {str(filesdone)}<br>
        <b>Failed to Update :</b> {str(filesremaining)}<br><br>

        <b>File List:</b> <br>
        {urls}<br><br>

        <b>Error List :</b> <br>
        {errorlist}
        """

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        html_part = MIMEText(body, 'html')
        message.attach(html_part)

        server.sendmail(sender_email, recipient_email, message.as_string())

