import telepot
import stripe
import json
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import time

stripe.ca_bundle_path = 'ca-certificates.crt'

class TGbot(object):
    def __init__(self, bot_name, bottoken, stripekey, proxy, cdata={}):
        self.bot_name = bot_name
        self.bottoken = bottoken
        self.stripekey = stripekey
        self.cdata = cdata
        self.proxy = proxy
        self.localstripe = stripe
        self.bot()

    def payment(self, chtype, amount, name, cardnum, cardmonth, cardyear, cardcvc, email, phone, description, country,
                city, address_line1, address_line2, zip):
        if '+' in str(chtype):
            try:
                if cardnum not in self.cdata:
                    self.token = self.localstripe.Token.create(
                        card={
                            "number": cardnum,
                            "exp_month": cardmonth,
                            "exp_year": cardyear,
                            "cvc": cardcvc,
                            "name": name,
                            "address_city": city,
                            "address_country": country,
                            "address_line1": address_line1,
                            "address_line2": address_line2,
                            "address_zip": zip
                        },
                    )

                    time.sleep(2)
                    self.customer = self.localstripe.Customer.create(
                        card=self.token,
                        email=email,
                        phone=phone,
                        description=description,
                        name=name,
                        address={'city': city, 'line1': address_line1, 'country': country}
                    )

                    self.cdata[cardnum] = self.customer.id
                    self.customer_id = self.customer.id
                else:
                    self.customer_id = self.cdata[cardnum]
            except stripe.error.CardError as e:
                print(e)
                return e
            except stripe.error.RateLimitError as e:
                print(e)
                return e
            except stripe.error.InvalidRequestError as e:
                print(e)
                return e
            except stripe.error.AuthenticationError as e:
                print(e)
                return e
            except stripe.error.APIConnectionError as e:
                print(e)
                return e
            except stripe.error.StripeError as e:
                print(e)
                return e
            except Exception as e:
                print(e)
                return e

            self.charge = self.localstripe.Charge.create(

                customer=self.customer_id,
                amount=int(float(amount) * 100),
                currency="usd",
                description=description,
                receipt_email=email
            )
            return self.charge.status
        elif '-' in str(chtype):
            stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": cardnum,
                    "exp_month": cardmonth,
                    "exp_year": cardyear,
                    "cvc": cardcvc,
                    "name": name,
                    "address_city": city,
                    "address_country": country,
                    "address_line1": address_line1,
                    "address_line2": address_line2,
                    "address_zip": zip
                }
            )

    def handler(self, data):
        uid = data['from']['id']
        # print(data)
        if data['text'] == '/start':
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Pay')],
            ], resize_keyboard=True, one_time_keyboard=True)
            self.telegrambot.sendMessage(uid, 'If you want to pay click pay', reply_markup=keyboard)
        elif data['text'].lower() == 'pay':
            self.telegrambot.sendMessage(uid,
                            'Введите данные карты через |:\nCreate customer?+/-\nAmount\nName\nCard number\nMonth\nYear\nCVC\nEmail\nPhone\nDescription\nCountry\nCity\nAddress line 1\nAddress line 2\nZip')
        else:
            paydata = data['text'].split('|')
            # print(paydata)
            for i in range(len(paydata)):
                if '-' in paydata[i]:
                    paydata[i] = None

            try:
                self.telegrambot.sendMessage(uid, self.payment(paydata[0],
                                             paydata[1],
                                             paydata[2],
                                             paydata[3],
                                             paydata[4],
                                             paydata[5],
                                             paydata[6],
                                             paydata[7],
                                             paydata[8],
                                             paydata[9],
                                             paydata[10],
                                             paydata[11],
                                             paydata[12],
                                             paydata[13],
                                             paydata[14]
                                             ))
            except Exception as e:
                print(e)
                self.telegrambot.sendMessage(uid, e)

    def bot(self):
        try:
            self.localstripe.api_key = self.stripekey
            if str(self.proxy) != '':
                self.localstripe.proxy = self.proxy
            self.telegrambot = telepot.Bot(self.bottoken)
            print('RUNNING', self.bot_name, self.telegrambot.getMe()['first_name'])
            self.telegrambot.deleteWebhook()
            MessageLoop(self.telegrambot, self.handler).run_as_thread()
            while 1:
                time.sleep(1)
        except Exception as e:
            print('Bot with name {} and token {} dropped an error: '.format(self.bot_name, self.bottoken), e)

with open('config.txt', 'r') as f:
    conf = json.load(f)
    TGbot(bot_name='bot1', bottoken=conf['bottoken'], stripekey=conf['stripekey'], proxy='')