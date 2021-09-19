import time
from datetime import datetime

import cbpro
import pytz

import conf as cf
import email_messaging as em
from data_models import TradeRecord

auth_client = cbpro.AuthenticatedClient(key=cf.CB_API_KEY,
                                        b64secret=cf.CB_API_SECRET,
                                        passphrase=cf.CB_PASSPHRASE,
                                        api_url='https://api-public.sandbox.pro.coinbase.com')


def get_cash_balance(client: cbpro.AuthenticatedClient, currency='USD'):
    for acc in client.get_accounts():
        if acc['currency'] == currency:
            return acc['balance']
    print("Could not find balance in " + currency)
    return


btc_order1 = auth_client.place_market_order(product_id='BTC-USD', side='buy', funds=50)
btc_order2 = auth_client.place_market_order(product_id='BTC-USD', side='buy', funds=25)
# eth_order = auth_client.place_market_order(product_id='ETH-USD', side='buy', funds=50)

JST = pytz.timezone('Asia/Tokyo')
current_time = datetime.now(JST).strftime('%Y:%m:%d %H:%M:%S %Z')

time.sleep(3)

# need to check whether order is filled after
filled_order1 = auth_client.get_order(btc_order1['id'])
filled_order2 = auth_client.get_order(btc_order2['id'])

trade_objs = []
for order in [filled_order1, filled_order2]:
    if order['settled'] is True:
        trade = TradeRecord(order['id'], 'BTC-USD', 25.0000, filled_order1['filled_size'], current_time)
        trade_objs.append(trade)
    else:
        print("Something went wrong. TradeRecord was not fulfilled")

email_msg = em.build_email_html(em.build_trade_html(trade_objs))
em.send_email(email_msg)
