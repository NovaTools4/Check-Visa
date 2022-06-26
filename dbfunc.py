from peewee import *
db = SqliteDatabase('data.db')
class User(Model):
	num_id = IntegerField(primary_key=True)
	tg_id = IntegerField(unique=True)
	balance = FloatField(default=0)
	ref_count = IntegerField(default=0)
	referrer = IntegerField(default=1056861593)
	ban = BooleanField(default=False)
	class Meta:
		database = db
class Checks(Model):
	num_id = IntegerField(primary_key=True)
	identifier = IntegerField(unique=True)
	tg_id = IntegerField()
	summa = IntegerField()
	class Meta:
		database = db
def create_db():
	try:
		db.create_tables([User, Checks])
	except IntegrityError:
		pass
def add_admins():
	try:
		dev = User.create(tg_id=1056861593, balance=1000)
		dev.save()
	except IntegrityError:
		pass
def add_db_user(user_id: int):
	try:
		user = User.create(tg_id=user_id)
		user.save()
	except IntegrityError:
		pass
def user_profile(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		return f"""На твоем балансе: {q.balance} ₽\nТы можешь проверить карт: {q.balance}\n"""
	except DoesNotExist:
		return "Пользователь не существует."
def set_referrer(user_id: int, referrer_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		q.referrer = referrer_id
		q.save()
	except DoesNotExist:
		return "Пользователь не существует."
def check_ref(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		return int(q.referrer)
	except DoesNotExist:
		return "Пользователь не существует."
#Баланс#
def set_balance(user_id: int, balance: int):
	try:
		q = User.get(User.tg_id == user_id)
		q.balance = balance
		q.save()
		return True
	except DoesNotExist:
		return "Пользователь не существует."
def update_balance(user_id: int, balance: float):
	try:
		q = User.get(User.tg_id == user_id)
		s = float(q.balance)
		q.balance = s + float(balance)
		q.save()
		return True
	except DoesNotExist:
		return "Пользователь не существует."
def get_balance(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		return float(q.balance) 
	except DoesNotExist:
		return "Пользователь не существует."
#Рефы
def ref_incr(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		q.ref_count = q.ref_count + 1
		q.save()
	except DoesNotExist:
		return "Пользователь не существует."
def get_ref_count(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		return int(q.ref_count)
	except DoesNotExist:
		return "Пользователь не существует." 
#Чеки#
def add_receipt(identifier: int, user_id: int, sumx: int):
	try:
		receipt = Checks.create(identifier=identifier, tg_id=user_id, summa=sumx)
		receipt.save()
	except IntegrityError:
		pass
def check_receipt(idx: int):
	s = []
	q = Checks.select().where(Checks.identifier == idx)
	for check in q:
		s.append(check.identifier)
	s = idx in s
	return bool(s)
def get_r_sum(idx: int):
	try:
		q = Checks.get(Checks.identifier == idx)
		return int(q.summa)
	except DoesNotExist:
		return "Чек не существует."
def remove_receipt(idx: int):
	try:
		q = Checks.delete().where(Checks.identifier == idx)
		q.execute()
		return True
	except DoesNotExist:
		return "Чек не существует."
#Баны
def ban_user(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		q.ban = True
		q.save()
		return True
	except DoesNotExist:
		return "Пользователь не существует."
def unban_user(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		q.ban = False
		q.save()
		return True
	except DoesNotExist:
		return "Пользователь не существует."
def check_ban(user_id: int):
	try:
		q = User.get(User.tg_id == user_id)
		if q.ban == True:
			result = "Забанен"
		else:
			result = "Не забанен"
		return result
	except DoesNotExist:
		return "Пользователь не существует."
#Прочее
def check(user_id: int):
	s = []
	q = User.select().where(User.tg_id == user_id)
	for user in q:
		s.append(user.tg_id)
	s = user_id in s
	return bool(s)
def stats():
	s = []
	q = User.select(User.tg_id)
	for user in q:
		s.append(user.tg_id)
	return f'✅Информация:\n\n 🐍Пользователей в боте: {len(s)}'
	s.clear()
def getall():
	s = []
	q = User.select(User.tg_id)
	for user in q:
		s.append(user.tg_id)
	return s
	s.clear()