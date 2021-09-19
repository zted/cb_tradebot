from pprint import pprint

import db_ops
from data_models import TradeRecord

col = db_ops.start_mongo()
trade = TradeRecord("CrunchCoin", 200)

most_recent = db_ops.get_most_recent(col)
pprint(most_recent)
insert_id = db_ops.insert(col, trade)
more_recent = db_ops.get_most_recent(col)
pprint(more_recent)
