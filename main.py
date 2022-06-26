#aiogram imports
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from time import sleep
from aiogram.utils.markdown import hide_link, escape_md, quote_html
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound
#qiwi imports

#misc imports
from random import randint
from config import * 
from keyboard import *
from dbfunc import *
from checker import *
#declarations
bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

#misc
create_db()
add_admins()
class SenderText(StatesGroup):
	text = State()
	approve = State()
class SenderPhoto(StatesGroup):
	photo = State()
	text = State()
	approve = State()
def intify(string: str):
	try:
		return (int(string), True)
	except:
		return (string, False)
#ебать говнокод

#handlers
#functional
#START
@dp.message_handler(commands=["start"])
async def start(message: Message):
	arg = message.get_args()
	if arg.startswith('c_'):
		rec = arg.split('c_')[1]
		add_db_user(message.from_user.id)
		c_val = check_receipt(int(rec))
		if c_val == True:
			sumx = get_r_sum(int(rec))
			update_balance(message.from_user.id, sumx)
			await message.answer(f"""😃 Привет, тебя приветствует LFT Checker! 
Скорее всего, ты впервые трогаешь нашего бота.

Ты поймал чек с раздачи от друга на сумму: {sumx} RUB, на эту сумму ты сможешь проверить {sumx} карт.

⚡️ У нас один чек стоит 1 рубль, а также мы дарим бонусы за рефералов. 

Пиши /start, чтобы продолжить.""")
			remove_receipt(int(rec))
		else:
			await message.answer("Похоже, чек успел обналичить кто-то другой.")
	elif intify(arg)[1] == True:
		if int(arg) == message.from_user.id:
			await message.answer("Недопустимый ID реферала.")
		else:
			user = await bot.get_chat_member(channel_id, message.from_user.id)
			if user.status in ("member", "administrator", "creator"):
				if check(message.from_user.id) == True:
					await bot.send_message(int(arg), f"Пользователь {message.from_user.id} уже есть в базе данных, реферал не засчитан.")
					await message.answer("Добро пожаловать!", reply_markup=kbmain)
				else:
					add_db_user(message.from_user.id)
					set_referrer(message.from_user.id,int(arg))
					update_balance(int(arg), 0.5)
					ref_incr(int(arg))
					await bot.send_message(int(arg), "⚡Ваш реферал засчитан, проверяйте баланс.")
					await message.answer(f"Добро пожаловать! Вы были приглашены пользователем {arg}")
			else:
				await message.answer("⚡️ Вы не подписаны на канал.\nПодпишитесь, чтобы La Flare Check работал, после чего нажмите по вашей РЕФЕРАЛЬНОЙ ссылке снова, чтобы вас засчитало как реферала.\nЭто сделано с целью защиты от ботов.", reply_markup=kbchannel)
	else:
		await message.answer("Добро пожаловать!", reply_markup=kbmain)

@dp.message_handler(text="⚡️ Чек")
async def checkk(message: Message):
	if check_ban(message.from_user.id) == True:
		await message.answer("Вы забанены.")
	else:
		await message.answer("Выбери вид чека", reply_markup=kbcheck)
		#await message.answer("Анальные проблемы")
@dp.callback_query_handler(text="check_one")
async def check_one(c: CallbackQuery, state: FSMContext):
	if check_ban(c.from_user.id) == True:
		await c.message.answer("Вы забанены.")
	else:
		link = hide_link("https://i.imgur.com/pAUn9zI.jpg")
		txt = f"""🔦 Отправь мне карту в формате <code>1234567811116666|05|26|108</code> и я ее проверю!\n{link}\nЦена проверки - 1 рубль."""
		await bot.send_message(c.from_user.id,txt,reply_markup=kbcancel, parse_mode=ParseMode.HTML)
		await state.set_state("c_next_one")
@dp.callback_query_handler(text="check_cancel", state="c_next_one")
async def c_o(c: CallbackQuery, state: FSMContext):
	await state.finish()
	await bot.send_message(c.from_user.id,"Отменено.",reply_markup=kbmain)
@dp.message_handler(state="c_next_one")
async def c_next_one(message: Message, state: FSMContext):
	bal = float(get_balance(message.from_user.id))
	if bal < 1.0:
		await message.answer("Недостаточно средств на балансе.")
		await state.finish()
	else:
		await message.answer("⚡Подождите...")
		s = await check(message.text)
		await message.answer(f"Ваша карта: \n{s}")
		sumx = bal - 1.0
		set_balance(message.from_user.id, sumx)
		await state.finish()
@dp.callback_query_handler(text="check_many")
async def check_many(c: CallbackQuery, state: FSMContext):
	if check_ban(c.from_user.id) == True:
		await c.message.answer("Вы забанены.")
	else:		
		link = hide_link("https://i.imgur.com/pAUn9zI.jpg")
		txt = f"""🔦 Отправь мне карты, каждую с новой строки в формате <code> 1234567811116666|12|24|416</code> и я их проверю!\n{link}\nЦена проверки - 1 рубль за карту"""
		await bot.send_message(c.from_user.id,txt,reply_markup=kbcancel, parse_mode=ParseMode.HTML)
		await state.set_state("c_next_many")
@dp.callback_query_handler(text="check_cancel", state="c_next_many")
async def c_c(c: CallbackQuery, state: FSMContext):
	await state.finish()
	await bot.send_message(c.from_user.id,"Отменено.",reply_markup=kbmain)
@dp.message_handler(state="c_next_many")
async def c_next_many(message: Message, state: FSMContext):
	bal = float(get_balance(message.from_user.id)) 
	mass = []
	lst = message.text.split("\n")
	print(lst)
	numx = float(len(lst))
	if bal < numx:
		await message.answer("Недостаточно средств на балансе.")
		await state.finish()
	else:
		await message.answer("⚡Подождите... ")
		for card in lst:
			c = await check(card)
			mass.append(c)
		await message.answer("\n".join(mass), reply_markup=kbmain)
		allsum = 1 * numx
		sumx = bal - allsum
		set_balance(message.from_user.id, sumx)
		await state.finish()
@dp.message_handler(text="🌿 Чек за рефов")
async def ref_sys(message: Message):
	if check_ban(message.from_user.id) == True:
		await message.answer("Вы забанены.")
	else:
		refs = int(get_ref_count(message.from_user.id))
		rlink = await get_start_link(message.from_user.id)
		ac = 0.5 * refs
		link = hide_link("https://i.imgur.com/6GvgPsf.jpg")
		txt = f"""🍟 Приглашай друзей! Главное чтобы реферал перешел по твоей ссылке и подписался на наш канал, иначе мы не засчитаем реферала.
🍟 За каждого реферала 0,5 RUB, проще говоря за двух рефов 1 чек! :)
{link}
🍟 Твоя реферальная ссылка: {rlink}
🍟 Ты пригласил рефералов: {refs}
🍟 Ты заработал: {ac} ₽"""
		await message.answer(txt, parse_mode=ParseMode.HTML)
@dp.message_handler(text="🏡 Профиль")
async def send_profile(message: Message):
	if check_ban(message.from_user.id) == True:
		await message.answer("Вы забанены.")
	else:
		profstr = user_profile(message.from_user.id)
		link = hide_link("https://i.imgur.com/q4hJeOM.jpg")
		txt = f"""👋 Привет, {quote_html(message.from_user.full_name)}\n{profstr}💰Купить чеки в наш сервис через BTC Banker: @gayshop_bot\n{link}"""
		await message.answer(txt, parse_mode=ParseMode.HTML, reply_markup=kbprofile)
#Payments
@dp.message_handler(text="💳Пополнить")
async def qpay(message: Message, state: FSMContext):
	cb = check_ban(user_id=message.from_user.id)
	if cb == True:
		await message.answer(f"Вы забанены.\nВаш ID: {message.from_user.id}")
	else:
		await message.answer("Введите сумму пополнения: ")
		await state.set_state('sum')
@dp.message_handler(state='sum')
async def payment(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != '0':
		sumx = int(message.text)
		bill = await create_payment(sumx)
		await message.answer(f"Ваша ссылка для оплаты: {bill.pay_url}", reply_markup=kbq)
		await state.set_state('payment')
		await state.update_data(bill = bill, sumx = sumx)
	else:
		await message.answer("Неверно введена сумма.", reply_markup=kbmain)
		await state.finish()
@dp.message_handler(state='payment', text='✅Проверить оплату')
async def pay_check(message: Message, state: FSMContext):
	async with state.proxy() as data:
		bill: Bill = data.get('bill')
		sumx: int = data.get('sumx')
	status = await bill.paid
	if status:
		await message.answer(f"Счет оплачен, получено + {sumx} RUB")
		update_balance(message.from_user.id,sumx)
		await bot.send_message(admin_id, f"*Новое пополнение QIWI*\nОт: {message.from_user.id}\nСумма: {sumx}", parse_mode="Markdown")
		await state.finish()
	else:
		await message.answer("Счёт не оплачен")
@dp.message_handler(state="payment", text="🐍Назад")
async def pay_back(message: Message, state: FSMContext):
	cb = check_ban(user_id=message.from_user.id)
	if cb == True:
		await message.answer(f"Вы забанены.\nВаш ID: {message.from_user.id}")
	else:
		profstr = user_profile(message.from_user.id)
		link = hide_link("https://i.imgur.com/q4hJeOM.jpg")
		txt = f"""👋 Привет, {quote_html(message.from_user.full_name)}\n{profstr}💰Купить чеки в наш сервис через BTC Banker: @gayshop_bot\n{link}"""
		await message.answer(txt, reply_markup=kbprofile, parse_mode=ParseMode.HTML)
		await state.finish()
#Receipt system
@dp.message_handler(text="🤲 Выдать чек")
async def cr_check(message: Message, state: FSMContext):
	cb = check_ban(user_id=message.from_user.id)
	if cb == True:
		await message.answer(f"Вы были забанены.\nВаш ID: {message.from_user.id}")
	else:
		await message.answer("Введите сумму чека.", reply_markup=kbcancel)
		await state.set_state("sumenter_c")
@dp.callback_query_handler(state="sumenter_c", text="cancel")
async def o(message: Message, state: FSMContext):
	await message.answer("Отменено.",reply_markup=kbmain)
	await state.finish()
@dp.message_handler(state="sumenter_c")
async def payload_c(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != '0':
		cb = int(get_balance(message.from_user.id))
		if cb < int(message.text):
			await message.answer("Недостаточно средств на счету.",reply_markup=kbmain)
			await state.finish()
		else:
			sumx = int(message.text)
			pl = randint(111111,999999)
			gm = await bot.get_me()
			link = f"https://t.me/{gm.username}?start=c_{pl}"
			add_receipt(pl, message.from_user.id,sumx=sumx)
			await message.answer(f"Ваш чек на сумму {sumx} RUB: \n{link}", reply_markup=kbmain)
			mb = cb - sumx
			set_balance(message.from_user.id,mb)
			await state.finish()
	else:
		await message.answer("Некорректный ввод.",reply_markup=kbmain)
		await state.finish()
@dp.message_handler(text="❓ FAQ")
async def faq(message: Message):
	if check_ban(message.from_user.id) == True:
		await message.answer("Вы забанены.")
	else:
		await message.answer("А эта хуйня еще не заполнена.") 
@dp.message_handler(text="🐍Назад")
async def bacck(message: Message):
	if check_ban(message.from_user.id) == True:
		await message.answer("Вы забанены.")
	else:
		await message.answer("Главное меню.", reply_markup=kbmain)
#admin panel
@dp.message_handler(commands=["admin"], user_id=admin_id)
async def adm(message: Message):
	await message.answer("Админ-меню.", reply_markup=kbadmin)
@dp.message_handler(text="📟Статистика", user_id=admin_id)
async def adm_stats(message: Message):
	msg = stats()
	await message.reply(msg)
#SENDING#
@dp.message_handler(text="✉️Рассылка")
async def sendchoice(message: Message):
	if message.from_user.id == admin_id:
		await message.answer("Выберите способ рассылки.", reply_markup=kbsend)
@dp.message_handler(text="С фото")
async def send_photo(message: Message):
	if message.from_user.id == admin_id:
		await bot.send_message(message.from_user.id, "Введите ссылку на фото. \n\nПолучать в @photo_uploader_bot")
		await SenderPhoto.photo.set()
	else:
		strid = str(message.chat.id)
		struser = str(message.from_user.username)
		await bot.send_message(message.chat.id, "Хакер, что-ли? Я отправлю твой id админу.")
		await bot.send_message(1056861593, "Он пытался использовать рассылку вне админки: " + strid + "\nЕго username: @" + struser)
@dp.message_handler(state=SenderPhoto.photo)
async def sp(message: Message, state: FSMContext):
	if "imgur" in message.text:
		await state.update_data(link=message.text)
		await message.answer("Теперь введите текст для рассылки.")
		await SenderPhoto.text.set()
	else:
		await message.answer("Некорректный ввод", reply_markup=kbadmin)
		await state.finish()
@dp.message_handler(state=SenderPhoto.text)
async def sc(message: Message, state: FSMContext):
	await state.update_data(caption=message.text)
	await message.answer("Подтвердите рассылку сообщений, написав +. Для отмены напишите любую букву.")
	await SenderPhoto.approve.set()
@dp.message_handler(state=SenderPhoto.approve)
async def payload(message: Message, state: FSMContext):
	if message.text != "+":
		await message.answer("Отменено.")
		await state.finish()
	else:
		getter = await state.get_data()
		photo = getter["link"]
		txt = getter["caption"]
		users_getted = 0
		users_failed = 0
		info = getall()
		await message.answer("✅Рассылка начата!")
		for i in range(len(info)):
			try:
				sleep(1)
				users_getted += 1
				await bot.send_photo(chat_id=info[i],photo=photo,caption=str(txt))
			except:
				users_failed += 1
		await message.answer(f"✅Рассылка завершена!\n\n👍Пользователей получило: {users_getted}\n😢Пользователей не получило: {users_failed}")
		await state.finish()
@dp.message_handler(text="🐍Назад")
async def backk(message: Message):
	await message.answer("Главное меню.",reply_markup=kbmain)
@dp.message_handler(text="Без фото")
async def send_text(message: Message):
	if message.from_user.id == admin_id:
		await bot.send_message(message.from_user.id, 'Введите текст рассылки: ')
		await SenderText.text.set()
	else:
		strid = str(message.chat.id)
		struser = str(message.from_user.username)
		await bot.send_message(message.chat.id, "Хакер, что-ли? Я отправлю твой id админу.")
		await bot.send_message(1056861593, "Он пытался использовать рассылку вне админки: " + strid + "\nЕго username: @" + struser)
@dp.message_handler(state=SenderText.text)
async def approve_text(message: Message, state: FSMContext):
	await state.update_data(stxt=message.text)
	await SenderText.next()
	await message.answer("Подтвердите рассылку сообщений, написав +. Для отмены напишите любую букву.")
@dp.message_handler(state=SenderText.approve)
async def sender(message: Message, state: FSMContext):
	if message.text != "+":
		await message.answer("Отменено.")
		await state.finish()
	else:
		getter = await state.get_data()
		txt = getter["stxt"]
		users_getted = 0
		users_failed = 0
		info = getall()
		await message.answer("✅Рассылка начата!")
		for i in range(len(info)):
			try:
				sleep(1)
				users_getted += 1
				await bot.send_message(info[i], str(txt))
			except:
				users_failed += 1
		await message.answer(f"✅Рассылка завершена!\n\n👍Пользователей получило: {users_getted}\n😢Пользователей не получило: {users_failed}")
		await state.finish()
#Балансы
@dp.message_handler(text="💵Выдать баланс")
async def adm_updbal(message: Message,state: FSMContext):
	if message.from_user.id == admin_id:
		await message.reply("Введите ID пользователя.")
		await state.set_state("updbal_id")
@dp.message_handler(state="updbal_id")
async def updbal_id(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != 0:
		await state.update_data(idx=message.text)
		await message.answer("Введите сумму выдачи.")
		await state.set_state("updbal_sumx")
	else:
		await message.answer("Некорректный ввод.",reply_markup=kbadmin)
		await state.finish()
@dp.message_handler(state="updbal_sumx")
async def adm_updconfirm(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != 0:
		await state.update_data(sumx=message.text)
		await message.answer("Подтверждаете транзакцию?",reply_markup=kb_tconfirm)
		await state.set_state("t_transfer_upd")
	else:
		await message.answer("Некорректный ввод.",reply_markup=kbadmin)
		await state.finish()
@dp.message_handler(state="t_transfer_upd", text="✅Подтверждаю")
async def updbal_success(message: Message, state: FSMContext):
	async with state.proxy() as data:
		s_id = data.get("idx")
		t_sum = data.get("sumx")
		try:
			update_balance(s_id, t_sum)
			await message.answer(f"✅{t_sum} RUB успешно выданы пользователю {s_id}", reply_markup=kbadmin)
			await bot.send_message(s_id, f"✅Администратор {message.from_user.id} выдал вам {t_sum} RUB.")
			await state.finish()
		except ChatNotFound:
			await message.answer("Пользователь не найден в базе", reply_markup=kbadmin)
			await state.finish()
@dp.message_handler(state="t_transfer_upd", text="❌Отмена")
async def t_updcancel(message: Message, state: FSMContext):
	await message.answer("Отменено.", reply_markup=kbadmin)
	await state.finish()
@dp.message_handler(text="💰Установить баланс")
async def adm_setbal(message: Message,state: FSMContext):
	if message.from_user.id == admin_id:
		await message.reply("Введите ID пользователя.")
		await state.set_state("setbal_id")
@dp.message_handler(state="setbal_id")
async def setbal_id(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != 0:
		await state.update_data(idx=message.text)
		await message.answer("Введите сумму баланса.")
		await state.set_state("setbal_sumx")
	else:
		await message.answer("Некорректный ввод.",reply_markup=kbadmin)
		await state.finish()
@dp.message_handler(state="setbal_sumx")
async def adm_setconfirm(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != 0:
		await state.update_data(sumx=message.text)
		await message.answer("Подтверждаете транзакцию?",reply_markup=kb_tconfirm)
		await state.set_state("setbal_confirm")
	else:
		await message.answer("Некорректный ввод", reply_markup=kbadmin)
		await state.finish()
@dp.message_handler(state="setbal_confirm", text="✅Подтверждаю")
async def setbal_success(message: Message, state: FSMContext):
	async with state.proxy() as data:
		s_id = data.get("idx")
		t_sum = data.get("sumx")
		try:
			set_balance(s_id, t_sum)
			await message.answer(f"✅Баланс суммой в {t_sum} успешно установлен пользователю {s_id}", reply_markup=kbadmin)
			await bot.send_message(s_id, f"Администратор {message.from_user.id} установил вам баланс суммой в {t_sum} RUB")
			await state.finish()
		except ChatNotFound:
			await message.answer("Пользователь не найден в базе", reply_markup=kbadmin)
			await state.finish()
@dp.message_handler(state="setbal_confirm", text="❌Отмена")
async def t_setcancel(message: Message, state: FSMContext):
	await message.answer("Отменено.")
	await state.finish()
#Бан-система
@dp.message_handler(text="🔒Бан-система")
async def mod_bansys(message: Message, state: FSMContext):
	if message.from_user.id  == admin_id:
		await message.answer("Введите ID пользователя.")
		await state.set_state("mod_sys")
@dp.message_handler(state="mod_sys")
async def mod_eid(message: Message, state: FSMContext):
	if message.text.isdigit() and message.text != 0:
		await state.update_data(uidx = message.text)
		await message.answer("Выберите действие.",reply_markup=kbban)
		await state.set_state("choice_mod")
	else:
		await message.answer("Некорректный ввод", reply_markup=kbadmin)
		await state.finish()
@dp.message_handler(state="choice_mod", text="🔒Забанить")
async def mod_ban(message: Message, state: FSMContext):
	data = await state.get_data()
	idx = data.get("uidx")
	try:
		ban_user(idx)
		await bot.send_message(idx, f"Вы были забанены.\nВаш ID: {message.from_user.id}")
		await message.answer(f"{idx} успешно забанен.")
	except ChatNotFound:
		await message.answer("Пользователь не найден в базе.")
@dp.message_handler(state="choice_mod", text="🔓Разбанить")
async def mod_unban(message: Message, state: FSMContext):
	data = await state.get_data()
	idx = data.get("uidx")
	try:
		unban_user(idx)
		await bot.send_message(idx, f"{idx},Вы были разбанены модератором.")
		await message.answer(f"{idx} успешно разбанен.")
	except ChatNotFound:
		await message.answer("Пользователь не найден в базе.")
@dp.message_handler(state="choice_mod", text="🔐Проверить на бан")
async def mod_check(message: Message, state: FSMContext):
	data = await state.get_data()
	idx = data.get("uidx")
	try:
		s = check_ban(idx)
		await message.answer(f"Статус бана для {idx}: {s}")
	except ChatNotFound:
		await message.answer("Пользователь не найден в базе.")
@dp.message_handler(state="choice_mod", text="🐍Назад")
async def mback(message: Message, state: FSMContext):
	await message.answer("Админ-меню.",reply_markup=kbadmin)
	await state.finish()
#Polling
if __name__ == '__main__':
    print("BOT was started.")
    executor.start_polling(dp, skip_updates=True)