import tempfile
import datetime
import os
import time
import csv
import socket
import urllib.request
import re
from datetime import timedelta

from peewee import PostgresqlDatabase, Model, CharField, ForeignKeyField, DateTimeField, TextField, DecimalField, IntegerField, DataError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException


DB_CONF = {
    'host': os.environ['db_host'],
    'name': os.environ['db_name'],
    'user': os.environ['db_username'],
    'password': os.environ['db_password'],
    'port': os.environ['db_port']
}

pg_database = PostgresqlDatabase(
    DB_CONF["name"],
    user=DB_CONF["user"],
    password=DB_CONF["password"],
    host=DB_CONF["host"],
    port=DB_CONF["port"],
)

# HEALTHCHECKS_END_URL = os.environ['healthchecks_url']
# HEALTHCHECKS_START_URL = HEALTHCHECKS_END_URL + "/start"


class BaseModel(Model):
    class Meta:
        database = pg_database


# Defined table schema
class ReturnPrimeBrand(BaseModel):
    brand_name = CharField(null=False)
    url = CharField()
    user_name = CharField()
    password = CharField()


class tempData(BaseModel):
    serial_number = CharField()
    brand = ForeignKeyField(ReturnPrimeBrand)
    type = CharField()
    status = CharField()
    customer_name = CharField()
    customer_address = CharField()
    customer_email = CharField(null=True)
    customer_phone = CharField()
    order_number = CharField()
    exchange_with = CharField(null=True)
    exchange_with_sku = CharField(null=True)
    exchange_with_amount = DecimalField(null=True)
    difference_amount = DecimalField(null=True)
    exchange_order_name = CharField(null=True)
    additional_amount_captured = DecimalField(null=True)
    payment_gateway_name = CharField(null=True)
    payment_gateway_transaction_id = CharField(null=True)
    order_payment_gateway = CharField(null=True)
    item_name = CharField()
    item_quantity = IntegerField()
    item_price = DecimalField(null=True)
    sku = CharField(null=True)
    reason = CharField(null=True)
    requested_at = DateTimeField(null=True)
    requested_at_str = CharField(null=True)
    order_created_at = DateTimeField(null=True)
    order_created_at_str = CharField(null=True)
    approved_at = DateTimeField(null=True)
    approved_at_str = CharField(null=True)
    received_at = CharField(null=True)
    customer_comment = TextField(null=True)
    pickup_awb = CharField(null=True)
    pickup_logistics = CharField(null=True)
    warehouse_location = CharField()
    exchange_order_status = CharField(null=True)
    refund_status = CharField(null=True)
    requested_refund_mode = CharField(null=True)
    actual_refund_mode = CharField(null=True)
    return_fee = DecimalField(null=True)
    eligible_refund_amount = DecimalField(null=True)
    refunded_amount = DecimalField(null=True)
    gift_card_number = CharField(null=True)
    account_number = CharField(null=True)
    ifsc_code = CharField(null=True)
    account_holder_name = CharField(null=True)
    refund_link = CharField(null=True)
    shipment_tracking_status = CharField()
    original_return_method = CharField(null=True)
    actual_return_method = CharField(null=True)
    custom_attributes = CharField(null=True)
    inspected_at = CharField(null=True)
    archived_at = DateTimeField(null=True)
    archived_at_str = CharField(null=True)
    payment_transaction_date = CharField(null=True)
    inspection_due_by = CharField(null=True)
    exchanged_at = DateTimeField(null=True)
    exchanged_at_str = CharField(null=True)
    refunded_at = DateTimeField(null=True)
    refunded_at_str = CharField(null=True)





def lambda_handler(event, context):
    print("Started at:", datetime.datetime.now())
    # try:
    #     urllib.request.urlopen(HEALTHCHECKS_START_URL, timeout=10)
    # except socket.error as e:
    #     # Log ping failure here...
    #     print("Healthcheck ping failed: %s" % e)

    download_path = tempfile.gettempdir()
    print("Temp path:", download_path)

    all_brands = ReturnPrimeBrand.select()

    for brand in all_brands:
        url = brand.url
        user_name = brand.user_name
        password = brand.password
        chrome_options = Options()
        chrome_options.binary_location = '/opt/chrome/chrome'
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_preferences = {"download.default_directory": download_path}
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("prefs", chrome_preferences)

        # provided path for chromedriver.exe
        chrome_service = Service(executable_path="/opt/chromedriver")

        # Configure the Selenium driver (replace with the appropriate driver for your browser)
        driver = webdriver.Chrome(
            options=chrome_options, service=chrome_service)
        driver.get(url="https://apps.returnprime.com/user/login")
        WebDriverWait(driver=driver, timeout=3)

        print("Driver is running")
        
        store_url_button=WebDriverWait(driver=driver,timeout=30).until(
            expected_conditions.element_to_be_clickable(
            (By.XPATH,'//input[@name="store"]'))
        )
        store_url=url
        for ch in store_url:
            store_url_button.send_keys(ch)

        username_button = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//input[@name="email"]'))
        )
        # sending username and password to log-in to dashboard
        email = user_name
        for ch in email:
            username_button.send_keys(ch)

        password_button = driver.find_element(
            By.XPATH, '//input[@name="password"]')
        for ch in password:
            password_button.send_keys(ch)

        login_button = driver.find_element(
            By.XPATH, '//button[@class="login-btn"]')

        login_button.click()
        print("Logged in.")

        time.sleep(20)
        print("Waiting for export button")
        try:
            export_button = WebDriverWait(driver=driver, timeout=60).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '(//span[@class="sidebar__nav-link-text"])[5]')
                )
            )
            export_button.click()
            print("Export Button clicked. Waiting for the form")
        except (ElementClickInterceptedException, TimeoutException):
            print("Not able to click export button. Clicking on modal")
            close_button = WebDriverWait(driver=driver, timeout=20).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '//button[@class="Polaris-Modal-CloseButton"]')
                )
            )
            close_button.click()
            print("Close button clicked.")

            export_button = WebDriverWait(driver=driver, timeout=60).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '(//span[@class="sidebar__nav-link-text"])[5]')
                )
            )
            export_button.click()
            print("Export Button clicked. Waiting for the form")

        # selecting form elements to send data to the form input fields
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=1)
        end_date = from_date

        if event.get('from_date'):
            from_date_str = event.get('from_date')
            from_date = datetime.datetime.strptime(from_date_str, "%Y-%m-%d")

        if event.get('end_date'):
            end_date_str = event.get('end_date')
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

        from_date_input = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//div[@class="ant-picker-input"]'))
        )
        from_date_input.click()
        end_date_input = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH,
                    "(//td[@title='" + end_date.strftime("%Y-%m-%d") + "'])[1]")
            )
        )
        end_date_input.click()
        if today.strftime("%d") == "01":
            driver.find_element(
                By.XPATH, '//*[@class="ant-picker-header-prev-btn"]').click()

        driver.find_element(
            By.XPATH, "(//td[@title='" +
            from_date.strftime("%Y-%m-%d") + "'])[1]"
        ).click()

        request_type = Select(driver.find_element(By.ID, "PolarisSelect1"))
        request_type.select_by_visible_text("Any")

        request_status = Select(driver.find_element(By.ID, "PolarisSelect2"))
        request_status.select_by_visible_text("Any")
        try:
            activity_timestamp = Select(
                driver.find_element(By.ID, "PolarisSelect3"))
            activity_timestamp.select_by_visible_text("Requested at")
        except NoSuchElementException:
            print("Activity timestamp elemnt not found") 

        download_button = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH,
                    '//button[@class="Polaris-Button Polaris-Button--primary"]')
            )
        )
        download_button.click()
        print("Download button clicked. Waiting for the file to be downloaded")

        seconds = 1
        comeout = True
        while comeout:
            if os.path.isfile(os.path.join(download_path, "report.csv")):
                break
            else:
                time.sleep(1)
                seconds = seconds + 1
                if seconds > 120:
                    comeout = False
        print("File is downloaded")

        driver.quit()
        print("Driver is closed")

        # assigning temp path to csv_file where file is located and readind the csv_file as dict reader
        csv_file = os.path.join(download_path, "report.csv")
        with open(csv_file, "r", encoding="utf-8-sig") as file:
            csv_reader = csv.DictReader(file)
            print("Reading the data")
            return_data = []
            for row in csv_reader:
                # taking datetime field value(string format) and converting them into datetime object format to store it into database
                datetime_fields = ["requested_at", "approved_at",
                                   "archived_at", "exchanged_at", "refunded_at"]
                for field in datetime_fields:
                    field_str = row[field]
                    try:
                        if field_str:
                            # date = "June 1, 2023 4:08 AM (GMT+05:30) Asia/Calcutta"
                            #input_timestamp_str = "Tue August 8th 2023, 9:50:35 (GMT+05:30) Asia/Calcutta"
                            format_str = "%B %d %Y, %H:%M:%S"

                            # Define a regular expression pattern to match the timestamp components
                            pattern = r"(\w+) (\w+) (\d+)(?:st|nd|rd|th)? (\d{4}), (\d{1,2}):(\d{2}):(\d{2}) \(GMT([+-]\d{2}):(\d{2})\) (.+)"

                            match = re.match(pattern, field_str)
                            if match:
                                groups = match.groups()
                                
                                day_name, month_name, day, year, hour, minute, second, tz_hours, tz_minutes, _ = groups
                                
                                month_num = datetime.datetime.strptime(month_name, "%B").month  
                                tz_offset = timedelta(hours=int(tz_hours), minutes=int(tz_minutes))
                                
                                parsed_datetime = datetime.datetime(
                                    year=int(year),
                                    month=int(month_num),
                                    day=int(day),
                                    hour=int(hour),
                                    minute=int(minute),
                                    second=int(second),
                                ) 
                            field_datetime = parsed_datetime.strftime(format_str)
                            row[field] = field_datetime
                        else:
                            row[field] = None
                    except (ValueError,DataError) as e:
                        row[field + "_str"] = field_str

                # datetype for order_created_at = "2023-05-27T09:08:45.000Z"
                order_created_at_str = row["order_created_at"]
                try:
                    if order_created_at_str:
                        order_created_at_datetime_obj = datetime.datetime.strptime(
                            order_created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        order_created_at_datetime = order_created_at_datetime_obj.replace(
                            tzinfo=None)
                        row["order_created_at"] = order_created_at_datetime
                    else:
                        row["order_created_at"] = None
                except (ValueError,DataError) as e:
                    row["order_created_at_str"] = order_created_at_str

                row["brand"] = brand.id
                return_data.append(row)

            tempData.insert_many(return_data).execute()
        print("Data has been pushed to database")
        print("Ended at:", datetime.datetime.now())

        # try:
        #     urllib.request.urlopen(HEALTHCHECKS_END_URL, timeout=10)
        # except socket.error as e:
        #     # Log ping failure here...
        #     print("Healthcheck ping failed: %s" % e)
lambda_handler({},{})