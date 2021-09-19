import time
from datetime import datetime
from functools import reduce

import cbpro
import pytz

import conf as cf
import db_ops
import email_messaging as em
from data_models import TradeRecord


def get_cash_balance(client: cbpro.AuthenticatedClient, currency='USD') -> (float, str):
    for acc in client.get_accounts():
        if acc['currency'] == currency:
            return float(acc['balance']), 'ok'
    return 0, "Could not find balance in " + currency


def pretrade_checks() -> cbpro.AuthenticatedClient:
    auth_client = cbpro.AuthenticatedClient(key=cf.CB_API_KEY,
                                            b64secret=cf.CB_API_SECRET,
                                            passphrase=cf.CB_PASSPHRASE,
                                            api_url='https://api-public.sandbox.pro.coinbase.com')
    cash_needed = reduce(lambda x, y: x + y, map(lambda trade: trade.amount, cf.TRADES_TO_MAKE))
    cash_available, msg = get_cash_balance(auth_client)

    if cash_needed > cash_available:
        email_msg = em.build_email_html(em.insufficient_balance(cash_available, cash_needed, msg))
        em.send_email(email_msg, "TradeBot ERROR: Insufficient Balance")
        exit(1)
    elif cash_needed * 2 > cash_available:
        email_msg = em.build_email_html(em.low_balance(cash_available, cash_needed))
        em.send_email(email_msg, "TradeBot INFO: Low Balance Reminder")
    return auth_client


def execute_trades(client: cbpro.AuthenticatedClient):
    JST = pytz.timezone('Asia/Tokyo')
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
        email_msg = em.build_email_html('Trade succeeded but could not persist record to MongoDB.')
        em.send_email(email_msg, "TradeBot ERROR: Persisting Trades Failed")
        exit(1)
    return


def run():
    try:
        client = pretrade_checks()
        executed_trades = execute_trades(client)
        persist_trades(executed_trades)
    except Exception as e:
        email_msg = em.build_email_html(e)
        em.send_email(email_msg, "TradeBot ERROR: Investigate")
        raise Exception
    return 0


run()
