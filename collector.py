from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from time import sleep
from pprint import pprint

import re
import pandas as pd

class VerajohnTransactionLogCollector:
    def __init__(self):
        self.transaction_log_df = None

        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.go_verajohn_homepage()

    def set_login_data(self, email, password):
        self.email = email
        self.password = password

    def download(self, mode=None, term_from=None, term_to=None):
        self.login()
        self.open_transactions_and_netwinning()
        self.term_designation(mode, term_from, term_to)
        self.transaction_log_df = self.get_transactions()

    def export(self, filename):
        self.transaction_log_df.to_csv(filename)

    def go_verajohn_homepage(self):
        self.driver.get('https://www.verajohn.com/ja')
        while(True):
            sleep(1)
            if not (re.match('https://www.verajohn.com/ja', self.driver.current_url)):
                self.driver.get('https://verajohn.com/ja')
            else:
                break

    def login(self):
        input_email = self.driver.find_element_by_id("signin-mail")
        input_email.click()
        input_email.send_keys(self.email)

        input_password = self.driver.find_element_by_id("signin-pass")
        input_password.click()
        input_password.send_keys(self.password)

        login_button = self.driver.find_element_by_id("edit-submit-signin")
        login_button.click()

    def open_transactions_and_netwinning(self):
        self.driver.get("https://www.verajohn.com/ja/myaccount/transactions")
        show_all_history_button = self.driver.find_element_by_id("ゲーム履歴")
        show_all_history_button.click()

        netwinning_button = self.driver.find_element_by_class_name("netwinning")
        netwinning_button.click()

    def mmddyyyy_validation(self, term_from, term_to):
        validation_pattern = '[01][0-9]/[0123][0-9]/[0-9]{4}$'
        return (re.match(validation_pattern, term_from)
            and re.match(validation_pattern, term_to))

    def term_designation(self, mode=None, term_from=None, term_to=None):
        game_history_base = "//div[@id='ゲーム履歴']"

        sevenday_button_xpath = game_history_base + "//div[@class='week-statement date-selection']"
        term_select_button_xpath = game_history_base + "//div[@class='custom-statement date-selection']"
        term_from_input_xpath = game_history_base + "//div[@class='date-from']/input"
        term_to_input_xpath = game_history_base + "//div[@class='date-to']/input"

        if mode == "7days":
            sevenday_button = self.driver.find_element_by_xpath(sevenday_button_xpath)
            sevenday_button.click()
        elif mode == "custom":
            if not self.mmddyyyy_validation(term_from, term_to):
                raise YMDValidationException("term_fromおよびterm_toはmm/dd/yyyy形式で入力してください。")
            if not term_from or not term_to: 
                raise ParmeterRequiredException("term_fromまたはterm_toの入力が必要です。")

            term_select_button = self.driver.find_element_by_xpath(term_select_button_xpath)
            term_select_button.click()

            term_from_input = self.driver.find_element_by_xpath(term_from_input_xpath)
            term_from_input.clear()
            term_from_input.send_keys(term_from)

            term_to_input = self.driver.find_element_by_xpath(term_to_input_xpath)
            term_to_input.clear()
            term_to_input.send_keys(term_to)

            term_to_input.send_keys(Keys.ENTER)

    def get_transactions(self):
        table_headers = [
            "取引ID",
            "取引日時",
            "アカウント",
            "内容",
            "詳細",
            "取引金額",
            "キャッシュ",
            "ボーナス"
        ]
        transaction_list = []

        game_history_base = "//div[@id='ゲーム履歴']"
        netwinning_base = game_history_base + "//div[@class='building building--bottom js-toggle transaction-sub netwinning pagination-inited']"

        row_xpath = netwinning_base + "//tr[starts-with(@class, 'report-row')]"
        cell_data_xpath = "td[starts-with(@class, 'report-rowCell')]"
        previous_button_xpath = netwinning_base + "//span[@class='paging-link pull-right next-page paging-game']"

        previous_button = self.driver.find_element_by_xpath(previous_button_xpath)

        while(True):
            try:
                row = self.driver.find_elements_by_xpath(row_xpath)
                cell_data = [[cell.text for cell in row_cell.find_elements_by_xpath(cell_data_xpath)] for row_cell in row]
                transaction_list.extend(cell_data)

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                previous_button.click()
                sleep(0.5)
            except ElementClickInterceptedException as e:
                break
            except StaleElementReferenceException as e:
                previous_button = self.driver.find_element_by_xpath(previous_button_xpath)

        return pd.DataFrame(data=transaction_list, columns=table_headers)

class ParmeterRequiredException(Exception):
    pass

class YMDValidationException(Exception):
    pass
