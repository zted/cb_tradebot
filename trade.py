import time
from datetime import datetime
from functools import reduce
from importlib import reload

import cbpro
import pytz
from dateutil import parser
from dateutil.tz import gettz

import conf as cf
import db_ops
import email_messaging as em
from data_models import TradeRecord

JST = pytz.timezone('Asia/Tokyo')


class TradeExceptionError(Exception):
    def __init__(self, exception_details, email_title, error: Exception = None):
        self.message = exception_details
        if error:
            self.message += '<br>{}'.format(repr(error))
        self.email_title = email_title
        super().__init__(self.message)


def get_cash_balance(client: cbpro.AuthenticatedClient, currency='USD') -> (float, str):
    for acc in client.get_accounts():
        if acc['currency'] == currency:
            return float(acc['balance']), 'ok'
    return 0, "Could not find balance in " + currency


def pretrade_checks() -> cbpro.AuthenticatedClient:
    auth_client = cbpro.AuthenticatedClient(key=cf.CB_API_KEY,
                                            b64secret=cf.CB_API_SECRET,
                                            passphrase=cf.CB_PASSPHRASE)
    # api_url='https://api-public.sandbox.pro.coinbase.com') # for sandbox
    cash_needed = reduce(lambda x, y: x + y, map(lambda trade: trade.amount, cf.TRADES_TO_MAKE))
    cash_available, msg = get_cash_balance(auth_client)

    if cash_needed > cash_available:
        raise TradeExceptionError(exception_details=em.insufficient_balance(cash_available, cash_needed, msg),
                                  email_title='TradeBot ERROR: Insufficient Balance')
    elif int(cash_needed * 3) >= int(cash_available):
        email_msg = em.build_email_html(em.low_balance(cash_available, cash_needed))
        em.send_email(email_msg, "TradeBot INFO: Low Balance Reminder")
    return auth_client


def execute_trades(client: cbpro.AuthenticatedClient):
    settled_trades: [TradeRecord] = []
    unsettled_trades: [TradeRecord] = []
    for trade_instr in cf.TRADES_TO_MAKE:
        trade_time = datetime.now(JST).strftime(cf.TIME_FORMAT)
        order = client.place_market_order(product_id=trade_instr.product, side=trade_instr.direction,
                                          funds=trade_instr.amount)
        time.sleep(3)

        # need to check whether order is filled
        order_status = client.get_order(order['id'])
        trade_record = TradeRecord(trade_instr, order_status['id'], order_status['filled_size'], trade_time)
        if order_status['settled'] is True:
            settled_trades.append(trade_record)
        else:
            unsettled_trades.append(trade_record)
    print("Successfully finished trading.")

    if settled_trades:
        email_msg = em.build_email_html(em.build_success_trade(settled_trades))
        em.send_email(email_msg, "TradeBot SUCCESS: Trades Settled")
    if unsettled_trades:
        email_msg = em.build_email_html(em.build_pending_trade(unsettled_trades))
        em.send_email(email_msg, "TradeBot INFO: Trades Pending")
    return settled_trades + unsettled_trades


def persist_trades(all_trades: [TradeRecord]):
    ### persist to mongo
    collection = db_ops.start_mongo()
    for trade in all_trades:
        db_ops.insert(collection, trade)

    ### test that persisting to mongo succeeded. if persisting failed then exit process
    if not (collection.find_one({'trade_id': all_trades[-1].trade_id})):
        # couldn't find what we just persisted'
        raise TradeExceptionError(exception_details='Trade succeeded but could not persist record to MongoDB.',
                                  email_title='TradeBot ERROR: Persisting Trades to MongoDB Failed')
    return


def time_to_trade():
    now = datetime.now(JST)
    today = now.strftime('%A')
    same_trade_day = today.lower() == cf.TRADE_DAY.lower()
    print("Current time is {} {}".format(today, now.strftime(cf.TIME_FORMAT)))
    if not same_trade_day:
        print("Trade day is {}, going back to sleep.".format(cf.TRADE_DAY))
        return False

    # check if trade already made today
    try:
        collection = db_ops.start_mongo()
        most_recent_time = parser.parse(db_ops.get_most_recent(collection)['time'],
                                        tzinfos={'JST': gettz('Asia/Tokyo')})
        already_traded = most_recent_time.date() == now.date()
    except Exception as e:
        # couldn't find the record we want in MongoDB'
        raise TradeExceptionError(exception_details='Could not find existing records in MongoDB.',
                                  email_title='TradeBot ERROR: Retrieving Info From MongoDB Failed',
                                  error=e) from e
    if already_traded:
        print("Already made a trade today.")
        return False
    print("It is time to trade.")
    return True


def run():
    reload(cf)

    try:
        if time_to_trade() is False:
            return 0
        client = pretrade_checks()
        executed_trades = execute_trades(client)
        persist_trades(executed_trades)
    except TradeExceptionError as e:
        email_msg = em.build_email_html(e.message)
        em.send_email(email_msg, e.email_title)
        return 1
    except Exception as e:
        email_msg = em.build_email_html(str(e))
        em.send_email(email_msg, "TradeBot ERROR: Investigate")
        return 1
    return 0
