from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QComboBox
from UI.ClickedComboBox import ClickedComboBox
import src
from UI.ItemsContainer import ItemsContainer
from UI.UiConstants import *
from Bank.BuilderClient import BuilderClient
from Bank.Transaction import *
from Bank.Bank import Bank
from Structures.Passport import Passport
from Database.DbReader import DbReader
from Database.DbWriter import DbWriter
from Bank.BankAccount import BankAccount, DebitAccount, CreditAccount, \
    DepositAccount
from Structures.Types import TypeBankAccount


class UiMainWindow(object):
    """Класс основного и единственного окна интерфейса
    Рисую всё на одном чтобы не было лагов при переключении между окнами, да и
    смысла в нескольких окнах тут, кажется, нет"""

    def __init__(self):
        """Инициализация самых необходимых и общих для многих сценариев
        объектов"""
        self.all_obj = {}
        self.all_items = ItemsContainer()
        self.db_reader = DbReader()
        self.db_writer = DbWriter()
        self.tmp_list_bank_accounts = []
        self.tmp_list_transactions = []
        self.tmp_list_banks = []
        self.current_id_acc = EMPTY
        self.last_connect_top_up = None
        self.cnt_of_combo_box = 0
        self.map_name_account = {}

        self.spacer_up = \
            QtWidgets.QSpacerItem(20, 20,
                                  QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        self.spacer_down = \
            QtWidgets.QSpacerItem(20, 20,
                                  QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        self.spacer_left = \
            QtWidgets.QSpacerItem(20, 20,
                                  QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Minimum)
        self.spacer_right = \
            QtWidgets.QSpacerItem(20, 20,
                                  QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Minimum)

    def setupUi(self, window):
        """Установка окна и показ домашней страницы"""
        self.window = window
        window.resize(SIZE_WIDTH_WINDOW, SIZE_HEIGHT_WINDOW)
        window.setInputMethodHints(QtCore.Qt.ImhNone)
        desktop = QtWidgets.QApplication.desktop()
        x = (desktop.width() - window.width()) // 2
        y = (desktop.height() - window.height()) // 2
        window.move(x, y)
        self.initAll()
        self.showHome()

    def initAll(self):
        """Инициализация объектов в основном UI для всех сценариев"""
        self.initStartWindow()
        self.initCreateClient()
        self.initCreateBank()
        self.initHome()
        self.initClientAccount()
        self.initClientTransaction()
        self.initBankManagerAccount()
        self.initNewBankAccount()
        self.initTopUp()
        self.initTransfer()

        self.hideAll()

    def initHome(self):
        """Инициализация кнопки домой"""
        self.push_btn_home = QtWidgets.QPushButton(self.window)
        self.push_btn_home.setGeometry(
            QtCore.QRect(INDENT_HOME_BUTTON, INDENT_HOME_BUTTON,
                         SIZE_WIDTH_HOME_BUTTON, SIZE_HEIGHT_HOME_BUTTON))
        self.push_btn_home.setText(HOME)
        self.push_btn_home.clicked.connect(self.showHome)
        self.push_btn_home.show()

        QtCore.QMetaObject.connectSlotsByName(self.window)

    def initStartWindow(self):
        """Инициализация стартовой страницы"""
        self.main_grid_layout_widget = QtWidgets.QWidget(self.window)
        self.main_grid_layout = QtWidgets.QGridLayout(
            self.main_grid_layout_widget)
        self.main_grid_layout.setSizeConstraint(
            QtWidgets.QLayout.SetMaximumSize)
        self.main_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_grid_layout.setVerticalSpacing(7)

        self.start_main_layout = QtWidgets.QVBoxLayout()

        self.start_push_btn_layout = QtWidgets.QVBoxLayout()

        self.start_radio_btn_layout = QtWidgets.QHBoxLayout()

        self.radio_btn_Client = QtWidgets.QRadioButton(self.window)
        self.radio_btn_Client.setChecked(True)
        self.start_radio_btn_layout.addWidget(self.radio_btn_Client)

        self.radio_btn_Bank = QtWidgets.QRadioButton(self.window)
        self.start_radio_btn_layout.addWidget(self.radio_btn_Bank)

        self.start_push_btn_layout.addLayout(self.start_radio_btn_layout)
        spacer_item = QtWidgets.QSpacerItem(20, 40,
                                            QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Expanding)
        self.start_push_btn_layout.addItem(spacer_item)
        self.push_btn_sign_in = QtWidgets.QPushButton(self.window)
        self.push_btn_sign_in.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_BUTTON, SIZE_HEIGHT_BUTTON))
        self.start_push_btn_layout.addWidget(self.push_btn_sign_in)

        self.push_btn_sign_up = QtWidgets.QPushButton(self.window)
        self.push_btn_sign_up.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_BUTTON, SIZE_HEIGHT_BUTTON))
        self.start_push_btn_layout.addWidget(self.push_btn_sign_up)

        self.setStartSpacer()
        self.main_grid_layout.addItem(self.start_main_layout, 1, 1, 1, 1)

        self.start_main_layout.addLayout(self.start_push_btn_layout)
        self.radio_btn_Client.setText(BANK_CLIENT)
        self.radio_btn_Bank.setText(BANK[:-1])
        self.push_btn_sign_in.setText(SIGN_IN)
        self.push_btn_sign_up.setText(CREATE)
        QtCore.QMetaObject.connectSlotsByName(self.window)
        self.window.setCentralWidget(self.main_grid_layout_widget)

        self.all_items.start_window = [self.radio_btn_Client,
                                       self.radio_btn_Bank,
                                       self.push_btn_sign_in,
                                       self.push_btn_sign_up]

        self.push_btn_sign_up.clicked.connect(self.onClickSignUp)
        self.push_btn_sign_in.clicked.connect(self.onClickSignIn)

    def initCreateBank(self):
        """Инициализация страницы создание банка"""
        self.create_bank_vertical_layout_widget = QtWidgets.QWidget(
            self.window)
        self.create_bank_vertical_layout = QtWidgets.QVBoxLayout(
            self.create_bank_vertical_layout_widget)
        self.create_bank_horizontal_layout = QtWidgets.QHBoxLayout()
        self.label_name_bank = QtWidgets.QLabel(
            self.create_bank_vertical_layout_widget)
        self.create_bank_horizontal_layout.addWidget(self.label_name_bank)
        self.line_edit_name_bank = QtWidgets.QLineEdit(
            self.create_bank_vertical_layout_widget)
        self.create_bank_horizontal_layout.addWidget(self.line_edit_name_bank)
        self.create_bank_vertical_layout.addLayout(
            self.create_bank_horizontal_layout)
        self.push_btn_create_bank = QtWidgets.QPushButton(
            self.create_bank_vertical_layout_widget)
        self.push_btn_create_bank.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_BUTTON, SIZE_HEIGHT_BUTTON))
        self.create_bank_vertical_layout.addWidget(self.push_btn_create_bank)

        self.push_btn_create_bank.setText(CREATE_BANK)
        self.push_btn_create_bank.clicked.connect(self.onClickCreateBank)
        self.label_name_bank.setText(NAME_BANK)

        self.all_items.create_bank_window = \
            [self.push_btn_create_bank,
             self.label_name_bank,
             self.line_edit_name_bank,
             self.create_bank_vertical_layout_widget]

        QtCore.QMetaObject.connectSlotsByName(self.window)
        self.main_grid_layout.addWidget(
            self.create_bank_vertical_layout_widget,
            1, 1, 1, 1)

    def initClientAccount(self):
        """Инициализация страницы-кабинета клиента"""
        self.widget_client_account = QtWidgets.QWidget(self.window)
        self.vbox_bank_accounts = QtWidgets.QVBoxLayout(self.widget_client_account)
        self.vbox_client_account_main = QtWidgets.QVBoxLayout()
        self.hbox_client_account_top_bar = QtWidgets.QHBoxLayout()

        self.label_client_name = QtWidgets.QLabel()
        self.label_client_name.setBackgroundRole(QtGui.QPalette.Midlight)
        self.label_client_name.setAutoFillBackground(True)

        self.push_btn_create_bank_account = QtWidgets.QPushButton()
        self.push_btn_create_bank_account.setText(CREATE_BANK_ACCOUNT)
        self.push_btn_create_bank_account.setMinimumSize(
            SIZE_WIDTH_TOP_BUTTON,
            SIZE_HEIGHT_TOP_BUTTON)
        self.push_btn_create_bank_account.clicked.connect(
            self.onClickOpenBankAccount)
        self.push_btn_show_all_transaction = QtWidgets.QPushButton(
            MY_TRANSACTIONS)
        self.push_btn_show_all_transaction.setMinimumSize(
            SIZE_WIDTH_TOP_BUTTON,
            SIZE_HEIGHT_TOP_BUTTON)
        self.push_btn_show_all_transaction.clicked.connect(
            self.onClickShowAllTransaction)

        self.push_btn_change_data = QtWidgets.QPushButton(CHANGE_DATA)
        self.push_btn_change_data.setMinimumSize(SIZE_WIDTH_TOP_BUTTON,
                                                 SIZE_HEIGHT_TOP_BUTTON)
        self.push_btn_change_data.clicked.connect(self.showChangeClientData)

        spacer_left = QtWidgets.QSpacerItem(20, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        spacer_right = QtWidgets.QSpacerItem(20, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)

        self.hbox_client_account_top_bar.addItem(spacer_left)
        self.hbox_client_account_top_bar.addWidget(self.label_client_name)
        self.hbox_client_account_top_bar.addWidget(self.push_btn_change_data)
        self.hbox_client_account_top_bar.addWidget(
            self.push_btn_create_bank_account)
        self.hbox_client_account_top_bar.addWidget(
            self.push_btn_show_all_transaction)
        self.hbox_client_account_top_bar.addItem(spacer_right)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget_client_account)

        self.vbox_client_account_main.addLayout(
            self.hbox_client_account_top_bar)
        self.vbox_client_account_main.addWidget(self.scroll)
        self.main_grid_layout.addLayout(
            self.vbox_client_account_main, 1, 1, 1, 1)

        self.all_items.client_account = [self.widget_client_account,
                                         self.scroll,
                                         self.label_client_name,
                                         self.push_btn_create_bank_account,
                                         self.push_btn_show_all_transaction,
                                         self.push_btn_change_data]

    def initClientTransaction(self):
        """Инициализация страницы показа транзакций"""
        self.widget_client_transaction = QtWidgets.QWidget(self.window)
        self.vbox_bank_transaction = QtWidgets.QVBoxLayout(self.widget_client_transaction)
        self.vbox_client_transaction_main = QtWidgets.QVBoxLayout()
        self.hbox_client_transaction_top_bar = QtWidgets.QHBoxLayout()

        self.push_btn_escape = QtWidgets.QPushButton()
        self.push_btn_escape.setText(ESCAPE)
        self.push_btn_escape.setMinimumSize(SIZE_WIDTH_TOP_BUTTON,
                                            SIZE_HEIGHT_TOP_BUTTON)
        self.push_btn_escape.clicked.connect(self.showClientAccount)

        spacer_left = QtWidgets.QSpacerItem(20, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        spacer_right = QtWidgets.QSpacerItem(20, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)

        self.hbox_client_transaction_top_bar.addItem(spacer_left)
        self.hbox_client_transaction_top_bar.addWidget(self.push_btn_escape)
        self.hbox_client_transaction_top_bar.addItem(spacer_right)

        self.scroll_transaction = QtWidgets.QScrollArea()
        self.scroll_transaction.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_transaction.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_transaction.setWidgetResizable(True)
        self.scroll_transaction.setWidget(self.widget_client_transaction)

        self.vbox_client_transaction_main.addLayout(
            self.hbox_client_transaction_top_bar)
        self.vbox_client_transaction_main.addWidget(self.scroll_transaction)
        self.main_grid_layout.addLayout(
            self.vbox_client_transaction_main, 1, 1, 1, 1)

        self.all_items.client_transaction = [self.widget_client_transaction,
                                             self.scroll_transaction,
                                             self.push_btn_escape]

    def initCreateClient(self):
        """Инициализация страницы создания клиента"""
        self.create_client_layout_widget = QtWidgets.QWidget(self.window)

        self.create_client_main_vertical_layout = QtWidgets.QVBoxLayout(
            self.create_client_layout_widget)

        self.create_client_main_horizontal_layout = QtWidgets.QHBoxLayout()

        self.create_client_labels_vertical_layout = QtWidgets.QVBoxLayout()

        self.label_first_name = QtWidgets.QLabel(
            self.create_client_layout_widget)
        self.create_client_labels_vertical_layout.addWidget(
            self.label_first_name)

        self.label_second_name = QtWidgets.QLabel(
            self.create_client_layout_widget)
        self.create_client_labels_vertical_layout.addWidget(
            self.label_second_name)

        self.label_seria = QtWidgets.QLabel(self.create_client_layout_widget)
        self.create_client_labels_vertical_layout.addWidget(self.label_seria)

        self.label_number = QtWidgets.QLabel(self.create_client_layout_widget)
        self.create_client_labels_vertical_layout.addWidget(self.label_number)

        self.label_address = QtWidgets.QLabel(self.create_client_layout_widget)
        self.create_client_labels_vertical_layout.addWidget(self.label_address)

        self.create_client_main_horizontal_layout.addLayout(
            self.create_client_labels_vertical_layout)

        self.create_client_edits_vertical_layout = QtWidgets.QVBoxLayout()

        self.line_edit_first_name = QtWidgets.QLineEdit(
            self.create_client_layout_widget)
        self.create_client_edits_vertical_layout.addWidget(
            self.line_edit_first_name)

        self.line_edit_second_name = QtWidgets.QLineEdit(
            self.create_client_layout_widget)
        self.create_client_edits_vertical_layout.addWidget(
            self.line_edit_second_name)

        self.line_edit_seria = QtWidgets.QLineEdit(
            self.create_client_layout_widget)
        self.create_client_edits_vertical_layout.addWidget(
            self.line_edit_seria)

        self.line_edit_number = QtWidgets.QLineEdit(
            self.create_client_layout_widget)
        self.create_client_edits_vertical_layout.addWidget(
            self.line_edit_number)

        self.line_edit_address = QtWidgets.QLineEdit(
            self.create_client_layout_widget)
        self.create_client_edits_vertical_layout.addWidget(
            self.line_edit_address)

        self.create_client_main_horizontal_layout.addLayout(
            self.create_client_edits_vertical_layout)
        self.create_client_main_vertical_layout.addLayout(
            self.create_client_main_horizontal_layout)

        self.push_btn_create_client = QtWidgets.QPushButton(
            self.create_client_layout_widget)
        self.push_btn_create_client.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_BUTTON, SIZE_HEIGHT_BUTTON))
        self.push_btn_create_client.clicked.connect(self.onClickCreateClient)
        self.create_client_main_vertical_layout.addWidget(
            self.push_btn_create_client)

        self.change_data_push_btn_back = QtWidgets.QPushButton(ESCAPE)
        self.change_data_push_btn_back.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_BUTTON, 0))
        self.change_data_push_btn_back.clicked.connect(self.showClientAccount)
        self.change_data_push_btn_back.hide()
        self.create_client_main_vertical_layout.addWidget(
            self.change_data_push_btn_back)

        self.main_grid_layout.addWidget(
            self.create_client_layout_widget, 1, 1, 1, 1)

        self.label_first_name.setText(FIRST_NAME)
        self.label_second_name.setText(SECOND_NAME)
        self.label_seria.setText(SERIA_PASSPORT)
        self.label_number.setText(NUMBER_PASSPORT)
        self.label_address.setText(ADDRESS)
        self.push_btn_create_client.setText(SIGN_UP)
        self.all_items.create_client_window = [
            self.label_first_name,
            self.label_second_name,
            self.label_seria,
            self.label_number,
            self.push_btn_create_client,
            self.line_edit_number,
            self.line_edit_first_name,
            self.line_edit_seria,
            self.line_edit_second_name,
            self.create_client_layout_widget,
            self.line_edit_address,
            self.label_address]

    def initBankManagerAccount(self):
        """Инициализация страницы для управления банком"""
        self.bank_manager_account_widget = QtWidgets.QWidget(self.window)
        self.bank_manager_account_main_grid = QtWidgets.QGridLayout(
            self.bank_manager_account_widget)

        label_change_name = QtWidgets.QLabel(NAME_BANK)
        label_set_limit = QtWidgets.QLabel(LIMIT)
        self.line_edit_change_name_bank = QtWidgets.QLineEdit()
        self.line_edit_change_name_bank.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_LINE_EDIT, 0))
        self.line_edit_set_limit_bank = QtWidgets.QLineEdit()
        self.line_edit_set_limit_bank.setMinimumSize(
            QtCore.QSize(SIZE_WIDTH_LINE_EDIT, 0))
        push_btn_change_name = QtWidgets.QPushButton(CHANGE_NAME_BANK)
        push_btn_change_name.clicked.connect(self.changeNameBank)
        push_btn_set_limit = QtWidgets.QPushButton(SET_LIMIT)
        push_btn_set_limit.clicked.connect(self.changeLimitBank)

        self.bank_manager_account_main_grid.addWidget(label_change_name, 0, 0)
        self.bank_manager_account_main_grid.addWidget(label_set_limit, 1, 0)
        self.bank_manager_account_main_grid.addWidget(
            self.line_edit_change_name_bank, 0, 1)
        self.bank_manager_account_main_grid.addWidget(
            self.line_edit_set_limit_bank, 1, 1)
        self.bank_manager_account_main_grid.addWidget(
            push_btn_change_name, 0, 2)
        self.bank_manager_account_main_grid.addWidget(push_btn_set_limit, 1, 2)

        self.main_grid_layout.addWidget(
            self.bank_manager_account_widget, 1, 1, 1, 1)

        self.all_items.bank_manager_account = [
            self.bank_manager_account_widget]

    def initTopUp(self):
        """Инициализация страницы пополнения баланса счёта"""
        self.top_up_widget = QtWidgets.QWidget(self.window)
        self.top_up_layout = QtWidgets.QHBoxLayout(self.top_up_widget)

        btn_cancel = QtWidgets.QPushButton()
        btn_cancel.setText(CANCEL)
        btn_cancel.clicked.connect(self.showClientAccount)
        btn_cancel.setMinimumSize(SIZE_WIDTH_TYPICAL_BUTTON,
                                  SIZE_HEIGHT_BUTTON)

        self.btn_top_up = QtWidgets.QPushButton()
        self.btn_top_up.setText(TOP_UP)
        self.btn_top_up.clicked.connect(self.topUp)
        self.last_connect_top_up = self.topUp
        self.btn_top_up.setMinimumSize(SIZE_WIDTH_TYPICAL_BUTTON,
                                       SIZE_HEIGHT_BUTTON)

        self.top_up_amount = QtWidgets.QLineEdit()
        self.top_up_amount.setMinimumSize(SIZE_WIDTH_TYPICAL_BUTTON,
                                          SIZE_HEIGHT_BUTTON)
        self.top_up_amount.setFont(
            QtGui.QFont(TIMES, SIZE_TEXT, QtGui.QFont.Bold))
        self.top_up_amount.setAlignment(QtCore.Qt.AlignCenter)

        self.top_up_layout.addWidget(btn_cancel)
        self.top_up_layout.addWidget(self.top_up_amount)
        self.top_up_layout.addWidget(self.btn_top_up)

        self.main_grid_layout.addWidget(self.top_up_widget, 1, 1, 1, 1)

        self.all_items.top_up = [self.top_up_widget]

    def initTransfer(self):
        """Инициализация страницы перевода денег"""
        self.transfer_widget = QtWidgets.QWidget(self.window)
        vbox = QtWidgets.QVBoxLayout(self.transfer_widget)
        hbox_first_name = QtWidgets.QHBoxLayout()
        hbox_second_name = QtWidgets.QHBoxLayout()
        hbox_combo_box = QtWidgets.QHBoxLayout()
        hbox_buttons = QtWidgets.QHBoxLayout()

        label_first_name = QtWidgets.QLabel(TRANSFER_FIRST_NAME)
        label_second_name = QtWidgets.QLabel(TRANSFER_SECOND_NAME)
        self.transfer_le_first_name = QtWidgets.QLineEdit()
        self.transfer_le_second_name = QtWidgets.QLineEdit()
        self.transfer_le_amount = QtWidgets.QLineEdit()
        self.transfer_le_amount.setFont(
            QtGui.QFont(TIMES, SIZE_TEXT, QtGui.QFont.Bold))
        self.transfer_le_amount.setAlignment(QtCore.Qt.AlignCenter)
        self.transfer_combo_box = ClickedComboBox()
        self.transfer_combo_box.popupAboutToBeShown.connect(
            self.writeBankAccountOnComboBox)
        btn_cancel = QtWidgets.QPushButton()
        btn_cancel.setText(CANCEL)
        btn_cancel.clicked.connect(self.showClientAccount)
        btn_cancel.setMinimumSize(SIZE_WIDTH_TYPICAL_BUTTON,
                                  SIZE_HEIGHT_BUTTON)
        self.btn_transfer = QtWidgets.QPushButton()
        self.btn_transfer.setText(TRANSFER)
        self.btn_transfer.clicked.connect(self.transfer)
        self.btn_transfer.setMinimumSize(SIZE_WIDTH_TYPICAL_BUTTON,
                                         SIZE_HEIGHT_BUTTON)

        hbox_first_name.addWidget(label_first_name)
        hbox_first_name.addWidget(self.transfer_le_first_name)

        hbox_second_name.addWidget(label_second_name)
        hbox_second_name.addWidget(self.transfer_le_second_name)

        hbox_combo_box.addWidget(self.transfer_combo_box)

        hbox_buttons.addWidget(btn_cancel)
        hbox_buttons.addWidget(self.btn_transfer)

        vbox.addLayout(hbox_first_name)
        vbox.addLayout(hbox_second_name)
        vbox.addLayout(hbox_combo_box)
        vbox.addWidget(self.transfer_le_amount)
        vbox.addLayout(hbox_buttons)

        self.main_grid_layout.addWidget(self.transfer_widget, 1, 1, 1, 1)
        self.all_items.transfer = [self.transfer_widget]

    def initNewBankAccount(self):
        """Инициализация страницы создание нового счёта"""
        self.new_bank_account_widget = QtWidgets.QWidget(self.window)
        self.new_bank_account_bank_list = QComboBox()
        vbox = QtWidgets.QVBoxLayout(self.new_bank_account_widget)
        hbox_top = QtWidgets.QHBoxLayout()
        hbox_mid = QtWidgets.QHBoxLayout()
        hbox_down = QtWidgets.QHBoxLayout()

        self.new_bank_account_kinds_account = QComboBox()
        self.new_bank_account_kinds_account.addItem(DEBIT)
        self.new_bank_account_kinds_account.addItem(CREDIT)
        self.new_bank_account_kinds_account.addItem(DEPOSIT)

        self.new_bank_account_bth_cancel = QtWidgets.QPushButton()
        self.new_bank_account_bth_cancel.setText(CANCEL)

        self.new_bank_account_bth_create = QtWidgets.QPushButton()
        self.new_bank_account_bth_create.setText(CREATE)

        self.label_name_account = QtWidgets.QLabel(NAME_ACCOUNT)

        self.edit_text_name_bank_account = QtWidgets.QLineEdit()
        self.edit_text_name_bank_account.setFont(QtGui.QFont(TIMES, SIZE_TEXT))

        hbox_down.addWidget(self.new_bank_account_bth_cancel)
        hbox_down.addWidget(self.new_bank_account_bth_create)
        hbox_mid.addWidget(self.label_name_account)
        hbox_mid.addWidget(self.edit_text_name_bank_account)
        hbox_top.addWidget(self.new_bank_account_bank_list)
        hbox_top.addWidget(self.new_bank_account_kinds_account)

        vbox.addLayout(hbox_top)
        vbox.addLayout(hbox_mid)
        vbox.addLayout(hbox_down)

        self.new_bank_account_bth_cancel.setMinimumSize(
            SIZE_WIDTH_TYPICAL_BUTTON, SIZE_HEIGHT_BUTTON)
        self.new_bank_account_bth_create.setMinimumSize(
            SIZE_WIDTH_TYPICAL_BUTTON, SIZE_HEIGHT_BUTTON)
        self.new_bank_account_kinds_account.setMinimumSize(
            SIZE_WIDTH_TYPICAL_BUTTON, SIZE_HEIGHT_BUTTON)
        self.new_bank_account_bank_list.setMinimumSize(
            SIZE_WIDTH_TYPICAL_BUTTON, SIZE_HEIGHT_BUTTON)
        self.edit_text_name_bank_account.setMinimumSize(
            SIZE_WIDTH_TYPICAL_BUTTON, SIZE_HEIGHT_BUTTON)

        self.new_bank_account_bth_cancel.clicked.connect(
            self.showClientAccount)
        self.new_bank_account_bth_create.clicked.connect(
            self.createNewBankAccount)

        self.main_grid_layout.addWidget(
            self.new_bank_account_widget, 1, 1, 1, 1)
        self.all_items.new_bank_account = [self.new_bank_account_widget,
                                           self.new_bank_account_bank_list]

    def onClickCreateBank(self):
        """Обработка нажатия кнопки "Создать банк" """
        if self.push_btn_create_bank.text() == CREATE_BANK:
            self.createBank()
        elif self.push_btn_create_bank.text() == SIGN_IN:
            self.authorizationBank()

    def onClickSignUp(self):
        """Обработка нажатия кнопки "Зарегистрироваться" """
        if self.radio_btn_Bank.isChecked():
            self.showBankSignUp()
        if self.radio_btn_Client.isChecked():
            self.showClientSignUp()

    def onClickSignIn(self):
        """Обработка нажатия кнопки "Войти" """
        if self.radio_btn_Bank.isChecked():
            self.showBankSignIn()
        if self.radio_btn_Client.isChecked():
            self.showClientSignIn()

    def onClickCreateClient(self):
        """Обработка нажатия кнопки "Создать/Войти/Сохранить" """
        if self.push_btn_create_client.text() == SIGN_IN:
            self.authorizationClient()
            return
        if self.push_btn_create_client.text() == SAVE:
            self.saveClientData()
            return

        first_name = self.line_edit_first_name.text()
        second_name = self.line_edit_second_name.text()
        seria = self.line_edit_seria.text()
        number = self.line_edit_number.text()
        address = self.line_edit_address.text()

        if self.db_reader.isExistClient(first_name, second_name):
            self.showStandardWarning(CLIENT_EXIST)
            return

        if first_name == EMPTY or second_name == EMPTY or address == EMPTY:
            self.showStandardWarning(NOT_ENOUGH_DATA)
            return

        builder = BuilderClient().firstName(first_name).secondName(
            second_name).address(address)
        if seria != EMPTY and number != EMPTY:
            try:
                builder = builder.passport(int(seria), int(number))
            except ValueError:
                self.showStandardWarning(INVALID_PASSPORT)
                return
        self.client = builder.build()

        self.showClientAccount()

    def onClickShowAllTransaction(self):
        """Обработка нажатия кнопки "Создать банк" """
        self.showAllTransaction()

    def onClickOpenBankAccount(self):
        """Обработка нажатия кнопки "Открыть счёт" """
        self.all_banks = self.db_reader.getAllBanks()
        self.hideAll()
        self.showItems(self.all_items.new_bank_account)
        for i in range(len(self.tmp_list_banks)):
            self.new_bank_account_bank_list.removeItem(i)
        self.new_bank_account_bank_list.clear()
        for bank in self.all_banks:
            self.tmp_list_banks.append(bank.name)
            self.new_bank_account_bank_list.addItem(bank.name)

    def showItems(self, items: list):
        """Отображение списка элементов на экране """
        for item in items:
            item.show()

    def showHome(self):
        """Показ стартовой страницы"""
        self.hideAll()
        self.showItems(self.all_items.start_window)

    def showClientSignIn(self):
        """Показ страницы авторизации клиента"""
        self.hideAll()
        self.showItems(self.all_items.create_client_window)
        self.line_edit_seria.hide()
        self.line_edit_number.hide()
        self.label_seria.hide()
        self.label_number.hide()
        self.label_address.hide()
        self.line_edit_address.hide()

        self.push_btn_create_client.setText(SIGN_IN)

    def showBankSignIn(self):
        """Показ страницы авторизации банка"""
        self.hideAll()
        self.showItems(self.all_items.create_bank_window)

        self.push_btn_create_bank.setText(SIGN_IN)

    def showClientSignUp(self):
        """Показ страницы регистрации клиента"""
        self.hideAll()
        self.showItems(self.all_items.create_client_window)

        self.line_edit_first_name.setText(EMPTY)
        self.line_edit_second_name.setText(EMPTY)
        self.line_edit_seria.setText(EMPTY)
        self.line_edit_number.setText(EMPTY)
        self.line_edit_address.setText(EMPTY)
        self.push_btn_create_client.setText(SIGN_UP)

    def showBankSignUp(self):
        """Показ страницы регистрации банка"""
        self.hideAll()
        self.showItems(self.all_items.create_bank_window)

        self.push_btn_create_bank.setText(CREATE_BANK)

    def showClientAccount(self):
        """Показ страницы личного кабинета клиента"""
        self.hideAll()
        self.showItems(self.all_items.client_account)
        self.main_grid_layout.removeItem(self.spacer_left)
        self.main_grid_layout.removeItem(self.spacer_right)
        self.main_grid_layout.removeItem(self.spacer_up)
        self.main_grid_layout.removeItem(self.spacer_down)
        self.change_data_push_btn_back.hide()

        self.label_client_name.setText(
            self.client.first_name + " " + self.client.second_name)
        self.tmp_accounts = self.db_reader.getAllAccounts(self.client.id)[::-1]
        tmp_list = []
        id_list = []
        for acc in self.tmp_accounts:
            bank = str(acc.id_account.bank.name)
            type_acc = str(self.getType(acc))
            balance = str(acc.balance)
            string = BANK + " " + bank + '\n' + TYPE_BANK_ACCOUNTS + " " + \
                     type_acc + "\n" + BALANCE + " " + balance + '\n' + \
                     NAME_ACCOUNT + " " + acc.name_account
            tmp_list.append(string)
            id_list.append(str(acc.id_account.id))
        self.renderListBankAccounts(tmp_list, id_list)

    def showBankManagerAccount(self):
        """Показ страницы кабинета банка"""
        self.hideAll()
        self.showItems(self.all_items.bank_manager_account)

        self.line_edit_change_name_bank.setText(self.bank.name)
        self.line_edit_set_limit_bank.setText(str(self.bank.limit))

    def showStandardWarning(
            self, text: str,
            title: str = WARNING,
            icon: QtWidgets.QMessageBox.Icon = QMessageBox.Warning):
        """Выводит сообщение text пользователю"""
        message = QMessageBox()
        message.setWindowTitle(title)
        message.setText(text)
        message.setIcon(icon)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()

    def showAllTransaction(self):
        """Показ страницы транзакций клиента"""
        self.hideAll()
        self.showItems(self.all_items.client_transaction)
        self.main_grid_layout.removeItem(self.spacer_left)
        self.main_grid_layout.removeItem(self.spacer_right)
        self.main_grid_layout.removeItem(self.spacer_up)
        self.main_grid_layout.removeItem(self.spacer_down)

        transactions = self.db_reader.getAllTransaction(self.client.id)[::-1]
        tmp_list = []
        id_list = []
        is_undo_list = []
        for transaction in transactions:
            tmp_list.append(self.getStringFromTransaction(transaction))
            id_list.append(transaction.id_tr)
            is_undo_list.append(transaction.is_undo)
        self.renderListTransactions(tmp_list, id_list, is_undo_list)

    def showTopUp(self, _id: str):
        """Показ страницы пополнения счёта"""
        self.top_up_amount.setText(EMPTY)
        self.btn_top_up.clicked.disconnect(self.last_connect_top_up)
        self.btn_top_up.clicked.connect(self.topUp)
        self.last_connect_top_up = self.topUp
        self.btn_top_up.setText(TOP_UP)
        self.hideAll()
        self.showItems(self.all_items.top_up)
        self.current_id_acc = _id

    def showWithdraw(self, _id: str):
        """Показ страницы снятия денег со счёта"""
        self.showTopUp(_id)
        self.btn_top_up.clicked.disconnect(self.last_connect_top_up)
        self.btn_top_up.clicked.connect(self.withdraw)
        self.last_connect_top_up = self.withdraw
        self.btn_top_up.setText(WITHDRAW)

    def showTransfer(self, _id: str):
        """Показ страницы перевода денег"""
        self.current_id_acc = _id
        self.hideAll()
        self.showItems(self.all_items.transfer)

    def showChangeClientData(self):
        """Показ страницы изменений данных о пользователе"""
        self.hideAll()
        self.showItems(self.all_items.create_client_window)

        self.line_edit_first_name.setText(self.client.first_name)
        self.line_edit_second_name.setText(self.client.second_name)
        try:
            self.line_edit_seria.setText(str(self.client.passport.series))
            self.line_edit_number.setText(str(self.client.passport.number))
        except Exception:
            pass
        self.line_edit_address.setText(str(self.client.address))
        self.push_btn_create_client.setText(SAVE)
        self.change_data_push_btn_back.show()

    def hideItems(self, items: list):
        """Скрывает с экрана список элементов"""
        for item in items:
            item.hide()

    def hideAll(self):
        """Скрывает с экрана все элементы"""
        self.setStartSpacer()
        for list_items in self.all_items:
            self.hideItems(list_items)

    def setStartSpacer(self):
        """Отображение содержимого окна по центру"""
        if self.main_grid_layout.itemAtPosition(1, 0) is None:
            self.main_grid_layout.addItem(self.spacer_left, 1, 0, 1, 1)
        if self.main_grid_layout.itemAtPosition(1, 2) is None:
            self.main_grid_layout.addItem(self.spacer_right, 1, 2, 1, 1)
        if self.main_grid_layout.itemAtPosition(0, 1) is None:
            self.main_grid_layout.addItem(self.spacer_up, 0, 1, 1, 1)
        if self.main_grid_layout.itemAtPosition(2, 1) is None:
            self.main_grid_layout.addItem(self.spacer_down, 2, 1, 1, 1)

    def createBank(self):
        """Создаёт банк из данных, введённых в соответствующие поля"""
        name = self.line_edit_name_bank.text()
        try:
            self.db_reader.getBankByName(name)
            self.showStandardWarning(CLIENT_EXIST)
            return
        except Exception:
            self.bank = Bank(name, Money(DEFAULT_LIMIT))
            self.showBankManagerAccount()

    def authorizationBank(self):
        """Авторизация банка из данных, введённых в соответствующие поля"""
        try:
            self.bank = self.db_reader.getBankByName(
                self.line_edit_name_bank.text())
        except Exception:
            self.showStandardWarning(BANK_NOT_FOUND)
            return
        self.showBankManagerAccount()

    def authorizationClient(self):
        """Авторизация клиента из данных, введённых в соответствующие поля"""
        first_name = self.line_edit_first_name.text()
        second_name = self.line_edit_second_name.text()

        if not self.db_reader.isExistClient(first_name, second_name):
            self.showStandardWarning(CLIENT_IS_NOT_EXIST)
            return

        self.client = self.db_reader.getClientByName(first_name, second_name)

        self.showClientAccount()

    def renderListBankAccounts(self, bank_accounts: list, id_list: list):
        """Отображение в скролле списка счетов"""
        for widget in self.tmp_list_bank_accounts:
            widget.hide()
            self.vbox_bank_accounts.removeWidget(widget)

        self.tmp_list_bank_accounts.clear()
        for i in range(len(bank_accounts)):
            widget = QtWidgets.QWidget()
            self.tmp_list_bank_accounts.append(widget)
            hbox = QtWidgets.QHBoxLayout(widget)
            button_delete = QtWidgets.QPushButton(DELETE_BANK_ACCOUNT)
            button_delete.clicked.connect(
                lambda checked, tmp=id_list[i]: self.deleteBankAccount(tmp))

            button_top_up = QtWidgets.QPushButton(TOP_UP)
            button_top_up.clicked.connect(
                lambda checked, tmp=id_list[i]: self.showTopUp(tmp))

            button_withdraw = QtWidgets.QPushButton(WITHDRAW)
            button_withdraw.clicked.connect(
                lambda checked, tmp=id_list[i]: self.showWithdraw(tmp))

            button_transfer = QtWidgets.QPushButton(TRANSFER)
            button_transfer.clicked.connect(
                lambda checked, tmp=id_list[i]: self.showTransfer(tmp))

            buttons = [button_delete, button_top_up, button_withdraw,
                       button_transfer]
            for btn in buttons:
                btn.setMaximumSize(INF, INF)
            label = QtWidgets.QLabel(bank_accounts[i])
            label.setMinimumSize(0, 0)
            label.setBackgroundRole(QtGui.QPalette.Midlight)
            label.setAutoFillBackground(True)

            hbox.addWidget(button_delete)
            hbox.addWidget(label)
            hbox.addWidget(button_top_up)
            hbox.addWidget(button_withdraw)
            hbox.addWidget(button_transfer)

            self.vbox_bank_accounts.addWidget(widget)

    def renderListTransactions(self, transactions: list, id_list: list,
                               is_undo_list: list):
        """Отображение в скролле списка транзакций"""
        for widget in self.tmp_list_transactions:
            widget.hide()
            self.vbox_bank_transaction.removeWidget(widget)

        self.tmp_list_transactions.clear()
        for i in range(len(transactions)):
            widget = QtWidgets.QWidget()
            self.tmp_list_transactions.append(widget)
            hbox = QtWidgets.QHBoxLayout(widget)

            button_undo = QtWidgets.QPushButton(
                CANCEL_TRANSACTION if not is_undo_list[
                    i] else BACK_TRANSACTION)
            button_undo.clicked.connect(
                lambda checked, tmp=id_list[i]: self.undoTransaction(tmp))
            button_undo.setMaximumSize(INF, INF)

            label = QtWidgets.QLabel(transactions[i])
            label.setMinimumSize(0, 0)
            label.setBackgroundRole(QtGui.QPalette.Midlight)
            label.setAutoFillBackground(True)

            hbox.addWidget(label)
            hbox.addWidget(button_undo)

            self.vbox_bank_transaction.addWidget(widget)

    def undoTransaction(self, _id: str):
        """Отмена транзакции при нажатии на соответсвующую кнопку"""
        transaction = self.db_reader.getTransactionById(_id)
        try:
            if transaction.is_undo:
                transaction.execute()
            else:
                transaction.undo()
        except Exception:
            self.showStandardWarning(CANNOT_EXEC_OPERATION)
        self.showAllTransaction()

    def getType(self, acc: BankAccount) -> str:
        """Получить строковое представление типа счета"""
        if acc.id_account.type == TypeBankAccount.DEBIT:
            return DEBIT
        if acc.id_account.type == TypeBankAccount.CREDIT:
            return CREDIT
        if acc.id_account.type == TypeBankAccount.DEPOSIT:
            return DEPOSIT

    def writeBankAccountOnComboBox(self):
        """Отобразить список счетов, на которые можно совершить перевод"""
        first_name = self.transfer_le_first_name.text()
        second_name = self.transfer_le_second_name.text()
        try:
            self.acc_other = self.db_reader.getClientByName(first_name,
                                                            second_name)
        except Exception:
            return
        bank_accounts = self.db_reader.getAllAccounts(self.acc_other.id)
        if len(bank_accounts) == 0:
            return
        for i in range(self.cnt_of_combo_box):
            self.transfer_combo_box.removeItem(0)
        self.cnt_of_combo_box = len(bank_accounts)
        self.map_name_account.clear()
        for elem in bank_accounts:
            self.map_name_account[elem.name_account] = elem
            self.transfer_combo_box.addItem(elem.name_account)

    def createNewBankAccount(self):
        """Создаёт счёт из данных, введённых в соответствующие поля"""
        text = self.new_bank_account_kinds_account.currentText()
        name = self.edit_text_name_bank_account.text()
        self.edit_text_name_bank_account.setText(EMPTY)
        bank = self.db_reader.getBankByName(
            self.new_bank_account_bank_list.currentText())
        if text == DEBIT:
            DebitAccount(bank, self.client, name, Money())
        elif text == CREDIT:
            CreditAccount(bank, self.client, name, Money(), bank.limit)
        elif text == DEPOSIT:
            DepositAccount(bank, self.client, name, Money())
        self.showClientAccount()

    def deleteBankAccount(self, _id: str):
        """Удаляет соответствующий счёт"""
        message = QMessageBox()
        message.setWindowTitle(WARNING)
        message.setText(SURE_DEL_ACCOUNT)
        message.setIcon(QMessageBox.Warning)
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        message.buttonClicked.connect(
            lambda checked, _id=_id: self.sureDeleteBankAccount(_id, checked))
        message.exec_()

    def sureDeleteBankAccount(self, _id: str, btn):
        """Проверяет, что пользователь подтвердил удаление"""
        if str(btn.text()) == OK:
            self.db_writer.deleteAccountById(_id)
            self.showClientAccount()

    def topUp(self):
        """Вызвать пополнение баланса"""
        self.changeBalance(1)

    def withdraw(self, _id: str):
        """Вызвать снятие денег"""
        self.changeBalance(-1)

    def changeBalance(self, sign: int):
        """Изменяет баланс на сумму, взятую из соответствующего поля
        1 - пополнить
        -1 - снять"""
        acc = self.db_reader.getBankAccountById(self.current_id_acc)
        amount = self.top_up_amount.text()
        if '.' not in amount:
            amount += '.00'

        try:
            amount = Money(amount)
            if amount.getCents() < 0:
                self.showStandardWarning(INVALID_AMOUNT_MONEY)
            else:
                if sign == 1:
                    command = TopUpTransaction(acc, amount)
                    command.execute()
                if sign == -1:
                    command = WithdrawTransaction(acc, amount)
                    command.execute()
                self.top_up_amount.setText(EMPTY)
                self.showClientAccount()
        except src.Structures.Exceptions.LowBalanceError:
            self.showStandardWarning(LOW_BALANCE)
        except src.Structures.Exceptions.DepositNotFinishedError:
            self.showStandardWarning(DEPOSIT_NOT_FINISHED)
        except src.Structures.Exceptions.DoubtfulClientError:
            self.showStandardWarning(NOT_PASSPORT)
        except Exception:
            self.showStandardWarning(INVALID_AMOUNT_MONEY)

    def getStringFromTransaction(self, transaction: Transaction):
        """Возвращает строку из транзакции с информацией о транзакции"""
        string = EMPTY
        if isinstance(transaction, src.Bank.Transaction.TopUpTransaction):
            string = TYPE_TRANSACTION + ' ' + TYPE_TOP_UP + '\n' + AMOUNT + \
                     ' ' + str(transaction.amount)
        elif isinstance(transaction, src.Bank.Transaction.WithdrawTransaction):
            string = TYPE_TRANSACTION + ' ' + TYPE_WITHDRAW + '\n' + AMOUNT + \
                     ' ' + str(transaction.amount)
        elif isinstance(transaction, src.Bank.Transaction.TransferTransaction):
            string = TYPE_TRANSACTION + ' ' + TYPE_TRANSFER + '\n' + AMOUNT + \
                     ' ' + str(transaction.amount) + '\n' + WHOM + \
                     ' ' + transaction.other.id_account.owner.first_name + \
                     ' ' + transaction.other.id_account.owner.second_name
        string += '\n' + BANK + ' ' + \
                  transaction.account.id_account.bank.name + '\n'
        string += NAME_ACCOUNT + ' ' + transaction.account.name_account + '\n'
        string += TYPE_BANK_ACCOUNTS + ' ' + self.getType(transaction.account)
        return string

    def transfer(self):
        """Переводит деньги в соответствии с введёнными пользователем
        данными"""
        name = self.transfer_combo_box.currentText()
        amount = self.transfer_le_amount.text()
        if '.' not in amount:
            amount += '.00'

        try:
            amount = Money(amount)
            if amount.getCents() < 0:
                self.showStandardWarning(INVALID_AMOUNT_MONEY)
            else:
                transaction = TransferTransaction(
                    self.db_reader.getBankAccountById(self.current_id_acc),
                    self.map_name_account[name], amount)
                transaction.execute()
                self.transfer_le_amount.setText(EMPTY)
                self.showClientAccount()
        except src.Structures.Exceptions.LowBalanceError:
            self.showStandardWarning(LOW_BALANCE)
        except src.Structures.Exceptions.DepositNotFinishedError:
            self.showStandardWarning(DEPOSIT_NOT_FINISHED)
        except src.Structures.Exceptions.DoubtfulClientError:
            self.showStandardWarning(NOT_PASSPORT)
        except Exception:
            self.showStandardWarning(INVALID_AMOUNT_MONEY)

    def saveClientData(self):
        """Сохраняет изменение персональных данных клиента из соответствующих
        полей ui"""
        self.client.first_name = self.line_edit_first_name.text()
        self.client.second_name = self.line_edit_second_name.text()
        seria = self.line_edit_seria.text()
        number = self.line_edit_number.text()
        self.client.updateAddress(self.line_edit_address.text())
        if seria != EMPTY and number != EMPTY:
            try:
                self.client.updatePassport(Passport(int(seria), int(number)))
            except Exception:
                self.showStandardWarning(INVALID_PASSPORT)
        self.showClientAccount()
        self.line_edit_seria.setText(EMPTY)
        self.line_edit_number.setText(EMPTY)
        self.change_data_push_btn_back.hide()

    def changeNameBank(self):
        """Изменяет имя банка из соответствующего поля ui"""
        name = self.line_edit_change_name_bank.text()
        try:
            self.db_reader.getBankByName(name)
            self.showStandardWarning(NAME_EXIST)
        except Exception:
            self.bank.updateName(name)

            self.showBankManagerAccount()
            self.showStandardWarning(DONE, DONE, QMessageBox.Information)

    def changeLimitBank(self):
        """Изменяет макс. сумму снятия денег сомнительным клиентом
        из соответствующего поля ui"""
        amount = self.line_edit_set_limit_bank.text()
        try:
            amount = self.getCorrectMoney(amount)
        except Exception:
            return

        self.bank.updateLimit(amount)
        self.showBankManagerAccount()
        self.showStandardWarning(DONE, DONE, QMessageBox.Information)

    def getCorrectMoney(self, amount: str) -> Money:
        """Возвращает корректную сумму денег Money из строки, если
        возможно, иначе - бросает исключение и оповещает пользователя"""
        if '.' not in amount:
            amount += '.00'

        try:
            amount = Money(amount)
            if amount.getCents() < 0:
                raise src.Structures.Exceptions.InvalidArgMoneyError
        except src.Structures.Exceptions.LowBalanceError:
            self.showStandardWarning(LOW_BALANCE)
            raise
        except src.Structures.Exceptions.DepositNotFinishedError:
            self.showStandardWarning(DEPOSIT_NOT_FINISHED)
            raise
        except src.Structures.Exceptions.DoubtfulClientError:
            self.showStandardWarning(NOT_PASSPORT)
            raise
        except Exception:
            self.showStandardWarning(INVALID_AMOUNT_MONEY)
            raise
        return amount
