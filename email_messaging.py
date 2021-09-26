import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from conf import SENDER_EMAIL, SENDER_PW, RECEIVER_EMAIL, SMTP_SERVER, EMAIL_PORT
from data_models import TradeRecord


def build_success_trade(trades: [TradeRecord]) -> str:
    accum_str = 'Executed the following:<br>'
    for t in trades:
        accum_str += 'Side: {} - Product: {} - Cost: {} - Units: {} - Time: {}<br>' \
            .format(t.direction, t.product, t.cost, t.units, t.time)
    accum_str = accum_str[:-4]
    return accum_str


def build_pending_trade(trades: [TradeRecord]) -> str:
    accum_str = ''
    for t in trades:
        accum_str += 'STILL PENDING - Side: {} - Product: {} - Cost: {} - Time: {}<br>' \
            .format(t.direction, t.product, t.cost, t.time)
    accum_str = accum_str[:-4]
    return accum_str


def low_balance(remaining_balance, amount_needed):
    return 'You have {} remaining in the account. Trading requires {}.'.format(remaining_balance, amount_needed)


def insufficient_balance(remaining_balance, amount_needed, additional_message):
    return '{}Additional information:<br>{}'.format(low_balance(remaining_balance, amount_needed), additional_message)


def build_email_html(message: str) -> str:
    return """\
    <html>
      <body>
        <p>{}</p>
      </body>
    </html>
    """.format(message)


def send_email(email_html: str, subject: str):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    part = MIMEText(email_html, 'html')
    message.attach(part)

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, EMAIL_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PW)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
