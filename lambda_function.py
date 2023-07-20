import tempfile
import datetime
import os
import time
import csv


from peewee import  PostgresqlDatabase, Model, CharField, ForeignKeyField, DateTimeField,TextField, DecimalField, IntegerField , DataError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions 



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

class BaseModel(Model):
    class Meta:
        database=pg_database
    

class ReturnPrimeBrand(BaseModel):
    brand_name = CharField(null=False)
    url = CharField()
    user_name = CharField()
    password = CharField()



class ReturnPrimeData(BaseModel):
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
    requested_at= DateTimeField(null=True)
    requested_at_str= CharField(null=True)
    order_created_at = DateTimeField(null=True)
    order_created_at_str = CharField(null=True)
    approved_at= DateTimeField(null=True)
    approved_at_str= CharField(null=True)
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
    inspected_at= CharField(null=True)
    archived_at= DateTimeField(null=True)
    archived_at_str= CharField(null=True)
    payment_transaction_date = CharField(null=True)
    inspection_due_by = CharField(null=True)
    exchanged_at = DateTimeField(null=True)
    exchanged_at_str = CharField(null=True)
    refunded_at = DateTimeField(null=True)
    refunded_at_str = CharField(null=True)



def lambda_handler(event, context):
    print("Started at:", datetime.datetime.now())
    download_path = tempfile.gettempdir()

    print("Temp path:", download_path)
    all_brands= ReturnPrimeBrand.select()
    for brand in all_brands:
        url = brand.url
        user_name = brand.user_name
        password = brand.password
        chrome_options = Options()
        chrome_options.binary_location = '/opt/chrome/chrome'
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280x1696")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")

        chrome_preferences = {"download.default_directory": download_path}
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("prefs", chrome_preferences)

        chrome_service = Service(executable_path="/opt/chromedriver")
                
        # Configure the Selenium driver (replace with the appropriate driver for your browser)
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
        driver.get(url=url)
        WebDriverWait(driver=driver, timeout=3)

        print("Driver is running")

        username_button = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//input[@name="email"]'))
        )
        email = user_name
        for ch in email:
            username_button.send_keys(ch)

        password_button = driver.find_element(By.XPATH, '//input[@name="password"]')
        _password = password
        for ch in _password:
            password_button.send_keys(ch)

        login_button = driver.find_element(By.XPATH, '//button[@class="login-btn"]')

        login_button.click()
        print("Logged in. Waiting for export button")

        export_button = WebDriverWait(driver=driver, timeout=60).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '(//span[@class="sidebar__nav-link-text"])[5]')
            )
        )
        export_button.click()
        print("Export Button clicked. Waiting for the form")


        today = datetime.date.today()
        # today = datetime.date(2023, 7, 1)


        from_date = today - datetime.timedelta(days=1)


        from_date_input = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//div[@class="ant-picker-input"]'))
        )
        from_date_input.click()
        end_date = WebDriverWait(driver=driver, timeout=10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, "(//td[@title='" + from_date.strftime("%Y-%m-%d") + "'])[1]")
            )
        )
        end_date.click()
        if today.strftime("%d") == "01":
            driver.find_element(By.XPATH, '//*[@class="ant-picker-header-prev-btn"]').click()


        driver.find_element(
            By.XPATH, "(//td[@title='" + from_date.strftime("%Y-%m-%d") + "'])[1]"
        ).click()


        request_type = Select(driver.find_element(By.ID, "PolarisSelect1"))
        request_type.select_by_visible_text("Any")


        request_status = Select(driver.find_element(By.ID, "PolarisSelect2"))
        request_status.select_by_visible_text("Any")


        activity_timestamp = Select(driver.find_element(By.ID, "PolarisSelect3"))
        activity_timestamp.select_by_visible_text("Requested at")


        download_button = WebDriverWait(driver=driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button[@class="Polaris-Button Polaris-Button--primary"]')
            )
        )
        download_button.click()
        print("Download button clicked. Waiting for the file to be downloaded")
        seconds = 1
        comeout = True
        while comeout:
            if os.path.isdir(os.path.join(download_path, "report.csv")):
                print("file is checked downloaded")
                break
            else:
                time.sleep(1)
                seconds = seconds + 1
                if seconds > 120:
                    comeout = False
        print("File is download")
        
        driver.quit()
        print("driver is closed")

        csv_file = os.path.join(download_path, "report.csv")
        with open(csv_file, "r", encoding="utf-8-sig") as file:
            csv_reader = csv.DictReader(file)
            print("Reading the data")
            return_data=[]
            for row in csv_reader:
                requested_at = row["requested_at"]
                try:
                    if requested_at:
                        requested_at=datetime.datetime.strptime(requested_at, "%B %d, %Y %I:%M %p (GMT%z) Asia/Calcutta")
                        requested_datetime=requested_at.replace(tzinfo=None)
                        row["requested_at"]=requested_datetime
                    else:
                        row["requested_at"]=None
                except (ValueError,DataError) as e:
                    row["requested_at_str"]=requested_at     

                order_created_at = row["order_created_at"]
                try:
                    if(order_created_at!=""):
                        order_created_at=datetime.datetime.strptime(order_created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                        order_created_at_datetime=order_created_at.replace(tzinfo=None)
                        row["order_created_at"]=order_created_at_datetime
                    else:
                        row["order_created_at"]=None
                except (ValueError,DataError) as e:
                    row["order_created_at_str"]=order_created_at

                approved_at = row["approved_at"]
                try:
                    if(approved_at!=""):
                        approved_at=datetime.datetime.strptime(approved_at, "%B %d, %Y %I:%M %p (GMT%z) Asia/Calcutta")
                        approved_at_datetime=approved_at.replace(tzinfo=None)
                        row["approved_at"]=approved_at_datetime
                    else:
                        row["approved_at"]=None
                except (ValueError,DataError) as e:
                    row["approved_at_str"]=approved_at        

                archived_at=row["archived_at"]
                try:
                    if archived_at!="":
                        archived_at=datetime.datetime.strptime(archived_at, "%B %d, %Y %I:%M %p (GMT%z) Asia/Calcutta")
                        archived_at_datetime=archived_at.replace(tzinfo=None)
                        row["archived_at"]=archived_at_datetime
                    else:
                        row["archived_at"]=None 
                except (ValueError,DataError) as e:
                    row["archived_at_str"]=archived_at

                exchanged_at = row["exchanged_at"] 
                try:
                    if(exchanged_at!="") :
                        exchanged_at=datetime.datetime.strptime(exchanged_at, "%B %d, %Y %I:%M %p (GMT%z) Asia/Calcutta")
                        exchanged_at_datetime=exchanged_at.replace(tzinfo=None)
                        row["exchanged_at"]=exchanged_at_datetime
                    else:
                        row["exchanged_at"] =None    
                except (ValueError,DataError) as e:
                    row["exchanged_at_str"]=exchanged_at

                refunded_at = row["refunded_at"]
                try:
                    if(refunded_at!=""):
                        refunded_at=datetime.datetime.strptime(refunded_at, "%B %d, %Y %I:%M %p (GMT%z) Asia/Calcutta")
                        refunded_at_datetime=refunded_at.replace(tzinfo=None)
                        row["refunded_at"]=refunded_at_datetime
                    else:
                        row["refunded_at"]=None    
                except (ValueError,DataError) as e:
                    row["refunded_at_str"]=refunded_at

                row["brand"]=brand.id
                return_data.append(row)
                
               
            ReturnPrimeData.insert_many(return_data).execute()
        print("program is completed and Data has been pushed to database")
        print("Ended at:", datetime.datetime.now())
           





