from data_models import TradeInstruction

### Mongo Confs
MONGODB_URL = "mongodb://127.0.0.1:27017"
MONGO_DB = 'mydatabase'
MONGO_COLLECTION = 'trades'

### Coinbase Conf - Example credentials.
CB_API_SECRET = '+Gf6vG0fIhIwQ1lYyGDecRBftfKXUSsS5Bprz+QqIkkrzNqyrz9Yc72CV6mFmmQeuMUkfKs01ZxZjEdo3Liqwg=='
CB_PASSPHRASE = 'kjj5oomcr53'
CB_API_KEY = 'a269b3be9c1ac8fdd35le69k50261c7'

### Email Conf
SMTP_SERVER = "smtp.gmail.com"
SENDER_EMAIL = ""  # the email address to send from
EMAIL_PORT = 465  # For SSL
SENDER_PW = ""  # real password to login into email
RECEIVER_EMAIL = ""  # the email address to receive emails

### Timing Conf
TIME_FORMAT = '%Y:%m:%d %H:%M:%S %Z'
TRADE_DAY = 'Monday'

### Trade Parameters
TRADES_TO_MAKE = [
    TradeInstruction('BTC-USD', 25, 'buy'),
    TradeInstruction('ETH-USD', 25, 'buy')
]