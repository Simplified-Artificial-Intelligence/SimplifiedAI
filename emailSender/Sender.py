import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from from_root import from_root
import os
import zipfile


# def zip_dir(paths):
#     with zipfile.ZipFile('Files'+'.zip', "w", zipfile.ZIP_DEFLATED) as zip_file:
#         for path in paths:
#             zip_file.write(path)
#
#
# def file_path(pid=None):
#     paths = []
#     path = os.path.join(from_root(), 'artifacts', pid)
#     for file in os.listdir(path):
#         paths.append(os.path.join(path, file))
#     zip_dir(paths)
#
# file_path()


def email_sender(receiver_email):
    try:
        sender = "ketangangal98@gmail.com"
        my_password = 'dfdw yazr ckiy pjqu'
        receiver = receiver_email

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "SIMPLIFIED AI : Process Completed"
        msg['From'] = sender
        msg['To'] = receiver

        html = '<html><body><p>Hello, Your process has been completed please download the resouces!</p></body></html>'
        part2 = MIMEText(html, 'html')

        msg.attach(part2)
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        s.login(sender, my_password)

        s.sendmail(sender, receiver, msg.as_string())
        s.quit()
        return True
    except Exception as e:
        return False

email_sender('pankajmalhan30@gmail.com')