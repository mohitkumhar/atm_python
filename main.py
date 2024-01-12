import pymongo, re, maskpass, os, smtplib, random
from dotenv import load_dotenv

load_dotenv()


myClient = pymongo.MongoClient("mongodb://localhost:27017")
mydb = myClient['mydatabase']
mycol = mydb['user']


def clearscreen():
    return os.system('cls' if os.name == 'nt' else 'clear')


def validEmail(email):
    pattern = r'^[a-zA-z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)


def view_amount(userEmail):
    money_dict = mycol.find_one({'email': userEmail}, {'_id': 0, 'money': 1})
    return int(money_dict.get('money'))


def deposite_money(userEmail, depositedMoney):
    user_amount = view_amount(userEmail)
    total_new_amount = depositedMoney + user_amount
    mycol.update_one({'email': userEmail}, {
                     "$set": {'money':  total_new_amount}})
    print("Money Deposited Successfully")


def smtp_email_verification(userEmail):
    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    otp = ''
    for i in random.sample(numbers, 4):
        otp += str(i)

    HOST = 'smtp.gmail.com'
    PORT = 465
    FROM_EMAIL = os.environ['from_email']
    TO_EMAIL = userEmail
    PASSWORD = os.environ['password']
    MESSAGE = f'''Subject: no@reply

    Please Do Not Share This OTP
    One Time OTP is: {otp}

    If ou Not Request For This OTP,
    Please Let Us Know at {os.environ['my_number']}

    Thank You
    Mohit Kumhar'''

    smtp = smtplib.SMTP_SSL(HOST, PORT)

    smtp.login(FROM_EMAIL, PASSWORD)
    smtp.sendmail(FROM_EMAIL, TO_EMAIL, MESSAGE)
    print("OTP Send Successfully on Your Mail")
    user_otp = input("Enter The OTP Here: ")
    if (user_otp == otp):
        return True

    else:
        return False


print("_______ATM_______")


user = True

while user:
    user_choice = input("New User (y/n)").lower()
    if (user_choice == 'y'):

        print("########## Hello User ##########")
        print("Enter Your Details")
        user_name = input("Name: ").lower()

        while True:
            user_email = input("Email: ").lower()
            if validEmail(user_email):
                check_new_user_email = {"email": user_email}
                if mycol.find_one(check_new_user_email):
                    print("Email Already Exists")
                    print("Enter Email Again")
                    continue
                else:
                    if smtp_email_verification(user_email):
                        print("OTP Successfully Verified")
                        break
                    else:
                        print("Otp is Wrong, Please Try Again")
                        continue

            else:
                print("Invalid email. Please enter a Valid email address.")

        while True:
            user_pin = maskpass.askpass(prompt="PIN: ", mask='*')

            if not user_pin.isnumeric():
                print("PIN Should be in Numberic")
                continue
            if len(user_pin) != 4:
                print("PIN Should be of 4 Digit")
                print("ReEnter PIN !!")
                continue
            user_pin2 = maskpass.askpass(prompt="Again PIN: ", mask='*')

            if user_pin != user_pin2:
                print("PIN Does Not Match")
                print("Please ReEnter PIN")
                continue
            break

        while True:
            user_bankDetails = input("Account Number: ")
            if user_bankDetails.isnumeric() and 9 <= len(user_bankDetails) <= 18:
                if mycol.find_one({'bank number': user_bankDetails}):
                    print("Bank Number is Already Register")
                    continue
                else:
                    break

            else:
                print("Invalid Account Number")
        while True:
            user_money = input("Enter Your Money: ")
            if user_money.isnumeric() and int(user_money) > 0:
                break
            else:
                print("Please Enter Valid Amount")

        user_details = {

            "name": user_name,
            "email": user_email,
            "pin": user_pin,
            "money": user_money,
            "bank number": user_bankDetails,

        }

        new_user_confirmation = {

            "email": user_email,
            "bank number": user_bankDetails,

        }

        existing_user = mycol.find_one(new_user_confirmation)
        if existing_user is None:
            mycol.insert_one(user_details)
            print("Account Created Successfully")
            input("Press Any Key to ReLogin")
            clearscreen()
            continue

        else:
            print("User is Already Exists")
            input("Enter Enter Key For Relogin")
            continue

    elif (user_choice == 'n'):
        print("########## Please Login ##########")
        login_user_email = input("Email: ").lower()
        login_user_pin = maskpass.askpass(prompt="PIN: ", mask='*')

        user_data = {"email": login_user_email, "pin": login_user_pin}

        if mycol.find_one(user_data):
            clearscreen()
            print("Welcome! You are Logged in")
            break
        else:
            print("Email or PIN is Wrong")

    else:
        print("Wrong Input")
        user = True
        clearscreen()
        print("Wrong Input!! Please Enter Correct Choice")


while True:
    print('''
        Choose Your Actions: (as per serial number)
            [1]. Check Balance
            [2]. Withdrawal Amount
            [3]. Deposit Amount
            [4]. Update Pin
            [5]. Exit
            [6]. Delete Account
    ''')
    login_user = input("Enter Your Choice: ")

    if login_user == '1':
        print(f"Your Total Balance is: ₹{view_amount(login_user_email)}")
        continue

    elif login_user == '2':
        print("~ ~ ~ ~ Enter Amount To Withdrawal ~ ~ ~ ~")
        login_user_withdrawal = int(input("Amount: "))

        login_user_amount = view_amount(login_user_email)

        if login_user_amount > login_user_withdrawal > 0:
            login_user_remaining_amount = int(
                login_user_amount) - int(login_user_withdrawal)

            mycol.update_one({'email': login_user_email}, {
                             "$set": {'money': login_user_remaining_amount}})
            print("Money Successfully Withdraw")

            # bad me uska remainig balance bhi dikane ka logic add krna h, {check}
            continue

        else:
            print("Invalid Amount")
            continue

    elif login_user == '3':
        while True:
            login_user_deposit_amount = int(
                input("Enter Amount to Be Deposited: "))
            login_user_amount = view_amount(login_user_email)
            if not str(login_user_deposit_amount).isnumeric() or login_user_amount < login_user_deposit_amount < 0:
                print("Invalid Amount")
                print("ReEnter")
                continue
            deposite_money(login_user_email, login_user_deposit_amount)
            break

    elif login_user == '4':
        while True:
            if smtp_email_verification(login_user_email):
                print("OTP Successfully Verified")
                print("You Can Proceed Now\n")
            else:
                print("OTP is Wrong, Try Again")
                continue

            print("~ ~ ~ Change PIN ~ ~ ~")
            login_user_set_new_pin_old = maskpass.askpass(
                prompt="Enter Old PIN: ", mask='*')
            login_user_pin = mycol.find_one(
                {"email": login_user_email}, {'_id': 0, 'pin': 1})
            login_user_oldpin = login_user_pin.get('pin')

            if login_user_oldpin != login_user_set_new_pin_old:
                print("Old PIN is Incorrect")
                continue

            while True:
                login_user_set_new_pin = maskpass.askpass(
                    prompt="Enter New PIN: ", mask='*')
                if not login_user_set_new_pin.isnumeric():
                    print("PIN Should be Numeric")
                    continue
                break
            login_user_set_new_pin1 = maskpass.askpass(
                prompt="Enter New PIN: ", mask='*')

            if login_user_set_new_pin != login_user_set_new_pin1:
                print("PIN Does Not Match")
                continue
            mycol.update_one({'email': login_user_email}, {
                             "$set": {'pin': login_user_set_new_pin}})
            print("PIN Changed SuccessFully")
            break

    elif login_user == '5':
        print("Logging Out...")
        break

    elif login_user == '6':
        print("Please Verify That is You")
        if smtp_email_verification(login_user_email):
            print("OTP Verified Successfully")
            login_user_deleting_account = input(
                "Do You really want to Delete Account: (y/n)").lower()

            if login_user_deleting_account == 'y':
                mycol.delete_one({'email': login_user_email})
                print("Account Delete Successfully")
                break

            elif login_user_deleting_account == 'n':
                print("Redirecting to Home Page...")
                continue

            else:
                print("Please Enter Correct Option and Try Again")
                continue
        else:
            print("OTP Verification is Fail, Try Again")

    else:
        print("Please Enter Correct Choice")
        continue

print('Thank You For Using Our ATM')
