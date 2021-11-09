import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# app pass will go here
sender = "ketangangal98@gmail.com"
my_password = 'test'
receiver = "pankajmalhan30@gmail.com"

msg = MIMEMultipart('alternative')
msg['Subject'] = "Alert"
msg['From'] = sender
msg['To'] = receiver

html = '<html><body><p>Hi, I have the following alerts for you!</p></body></html>'
part2 = MIMEText(html, 'html')

msg.attach(part2)
s = smtplib.SMTP_SSL('smtp.gmail.com')
s.login(sender, my_password)

s.sendmail(sender, receiver, msg.as_string())
s.quit()
