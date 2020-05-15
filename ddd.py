import os
import re
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import time
from datetime import date, timedelta

print(datetime.date.today())
if str(datetime.date.today())+" 00:00:00" < "2020-05-15 16:06:22" < str(datetime.date.today())+" 23:59:59":
    print("ooooo")
else:
    print("0000000000")