import os
import re
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import time
from datetime import date, timedelta
x = "来源：深圳特区报    2020年05月13日"
c = re.findall(".*    ", x)[0]
print(c)
