#encoding:	utf-8

# 使用selenium+chromedriver来实现12306抢票
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#设置窗口居中
def window_info():
	ws = window.winfo_screenwidth()
	hs = window.winfo_screenheight()
	x = (ws / 2) - 200
	y = (hs / 2) - 200
	print("%d,%d" % (ws, hs))
	return x,y
	
#设置登陆窗口属性
window = tk.Tk()
window.title('Go票V1.0')
a,b=window_info()
window.geometry("450x300+%d+%d"%(a,b))
#登陆界面的信息
tk.Label(window,text="Go票助手",font=("宋体",32)).place(x=120,y=20) #x=80,y=50
tk.Label(window,text="出发地：").place(x=120,y=100)
tk.Label(window,text="目的地：").place(x=120,y=130)
tk.Label(window,text="出发时间：").place(x=120,y=160)
tk.Label(window,text="乘客姓名：").place(x=120,y=190)
tk.Label(window,text="车次：").place(x=120,y=220)

#显示输入框
var_from_place = tk.StringVar()
var_to_place = tk.StringVar()
var_time = tk.StringVar()
var_usr_name = tk.StringVar()
var_train_name = tk.StringVar()


str_var = tk.StringVar()
str_var.set('help')

#显示默认账号
var_from_place.set('深圳')
entry_from_place=tk.Entry(window,textvariable=var_from_place)
entry_from_place.place(x=190,y=100)

var_to_place.set('北京')
entry_to_place = tk.Entry(window,textvariable=var_to_place)
entry_to_place.place(x=190,y=130)

entry_time = tk.Entry(window,textvariable=var_time)
entry_time.place(x=190,y=160)

entry_usr_name = tk.Entry(window,textvariable=var_usr_name)
entry_usr_name.place(x=190,y=190)

entry_train_name = tk.Entry(window,textvariable=var_train_name)
entry_train_name.place(x=190,y=220)

class Qiangpiao(object):
	def __init__(self):
		self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"
		self.initmy_url = "https://kyfw.12306.cn/otn/view/index.html"
		self.search_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
		self.passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
		self.driver = webdriver.Firefox(
			executable_path='C:\Program Files\Mozilla Firefox\geckodriver.exe')


	def wait_input(self):
		self.from_station = var_from_place.get()
		self.to_station = var_to_place.get()
		# 时间格式必须是：yyyy-MM-dd 的方式
		self.depart_time = var_time.get()
		self.passengers = var_usr_name.get().split(",")	#input("乘客姓名（如有多个乘客，用英文逗号隔开）：").split(",")
		self.trains = var_train_name.get().split(",")	#input("车次（如有多个车次，用英文逗号隔开）：").split(",")


	def _login(self):
		self.driver.get(self.login_url)
		# 显示等待
		# 隐士等待
		WebDriverWait(self.driver,1000).until(
		EC.url_to_be(self.initmy_url))
		print('登陆成功!')


	def _order_ticket(self):
		# 1.跳转到查询余票的界面
		self.driver.get(self.search_url)

		# 2.等待出发地是否输入正确
		WebDriverWait(self.driver,1000).until(
			EC.text_to_be_present_in_element_value((By.ID,
				"fromStationText"),self.from_station))

		# 3.等待目的地是否输入正确
		WebDriverWait(self.driver,1000).until(
			EC.text_to_be_present_in_element_value((By.ID,
			"toStationText"),self.to_station))

		# 4.等待出发日期是否输入正确
		WebDriverWait(self.driver,1000).until(
			EC.text_to_be_present_in_element_value((By.ID,
			"train_date"),self.depart_time))

		# 5.等待查询按钮是否可用
		WebDriverWait(self.driver,1000).until(
			EC.element_to_be_clickable((By.ID,
			"query_ticket")))

		# 6.如果能够被点击了，那么就找到这个查询按钮，执行点击事件
		searchBtn = self.driver.find_element_by_id("query_ticket")
		searchBtn.click()

		# 7.在点击了查询按钮以后，等待车次信息是否显示出来了
		WebDriverWait(self.driver,1000).until(
			EC.presence_of_element_located((By.XPATH,
			".//tbody[@id='queryLeftTable']/tr")))

		# 8.找到所有没有datatrain属性的tr标签，这些标签是存储了车次信息的
		tr_list = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
		# 9.遍历所有满足条件的tr标签
		for tr in tr_list:
			train_number = tr.find_element_by_class_name("number").text
			if train_number in self.trains:
				left_ticket = tr.find_element_by_class_name("yes").text
				print(left_ticket)
				if left_ticket == 'yes' or left_ticket.isdigit:
					print(train_number+"有票")
					orderBtn = tr.find_element_by_class_name("btn72")       
					orderBtn.click()

					#等待是否来到了确认乘客的界面
					WebDriverWait(self.driver,1000).until(
						EC.url_to_be(self.passenger_url))

					#等待所有乘客信息是否被加载进来了
					WebDriverWait(self.driver,1000).until(
						EC.presence_of_element_located(
						(By.XPATH, ".//ul[@id='normal_passenger_id']/li")))

					#获取所有的乘客信息
					passenger_labels = self.driver.find_elements_by_xpath(".//ul[@id='normal_passenger_id']/li/label")

					for passenger_label in passenger_labels:
						name = passenger_label.text
						if name in self.passengers:
							passenger_label.click()
			
					#获取提交订单的按钮
					submitBtn = self.driver.find_element_by_id("submitOrder_id")
					submitBtn.click()

					#显示等待判断确认订单对话框是否已经出现了
					WebDriverWait(self.driver,2000).until(
						EC.presence_of_element_located((
						By.CLASS_NAME,"dhtmlx_wins_body_outer")))

					#再来做一个显示等待,如果确认订单按钮出现了,那么就执行点击操作
					WebDriverWait(self.driver,2000).until(
						EC.presence_of_element_located((By.ID,"qr_submit_id")))

					confirmBtn = self.driver.find_element_by_id("qr_submit_id")
					confirmBtn.click()

					while confirmBtn:
						confirmBtn.click()
						confirmBtn = self.driver.find_element_by_id("qr_submit_id")
					return


	def run(self):
		self.wait_input()
		self._login()
		self._order_ticket()

def help():
	messagebox.askokcancel('消息框', 'askokcancel')

def start():
	spider = Qiangpiao()
	spider.run()


#登陆和配置按钮
btn_login = tk.Button(window,text="登陆",command=start)
btn_login.place(x=130,y=260)
#	btn_sign_up = tk.Button(window,text="帮助",command=help)
#	btn_sign_up.place(x=300,y=260)
#	btn_sign_up = tk.Button(window,text="一键配置",command=usr_login)
#	btn_sign_up.place(x=200,y=260)
#	btn_sign_up = tk.Button(window,text="帮助",command=usr_login)
#	btn_sign_up.place(x=300,y=260)
#	window.mainloop()

if __name__ == "__main__":
	window.mainloop()


	