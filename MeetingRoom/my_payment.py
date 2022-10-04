#Developer : SURENDRA 
#date : 2-Oct-2022
import razorpay, requests
from .razorpay_credentails import USERNAME, PASSWORD

client = razorpay.Client(auth=(USERNAME, PASSWORD))


def get_customer(customer_id):
    razorpay_client = client.customer.fetch(customer_id=customer_id)
    print(razorpay_client)


def create_invoice(company_id, minutes):
    hours = minutes / 60
    razorpay_client = client.customer.fetch(customer_id=company_id)
    mydata = {
        "type": "invoice",
        "invoice_number": "0086",
        "customer_id": str(razorpay_client["id"]),
        "line_items": [
            {
                "name": "Meeting Room",
                "description": "Booked for " + str(hours),
                "amount": 399,
                "currency": "INR",
                "quantity": 1
            }
        ],
        "sms_notify": 1,
        "email_notify": 1
    }

    razorpay_invoice = client.invoice.create(data=mydata)
    print(razorpay_invoice)


def make_curl_request():
    url = 'https://www.googleapis.com/search?key=56585885'
    payload = open("request.json")
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload, headers=headers)

def do_payment(company_name, email, total_amount):



    payload = {
        "customer": {
            "name": company_name,
            "email": email,

        },
        "type": "link",

        "amount": int(total_amount) * 100,
        "currency": "INR",
        "description": "Meeting Room",
        "sms_notify": 0,
        # "email_notify": 1
    }

    obj = client.invoice.create(payload)
    print("OBJ = " + str(obj))

def do_payment2(request):
    payload = {
        "customer": {
            "name": "surendra",
            "email": "surendra@gmail.com",
            "contact": "874512555"
        },
        "type": "link",
        "amount": "8000.00",
        "currency": "INR",
        "description": "Meeting Room",
        "sms_notify": 1,
        "email_notify": 1
    }
    r = client.payment.create(payload)
    print("RESPONSE = " + str(r))


def do_payment3(request):
    payload = {
        "amount": "400",
        "currency": "INR",
        "payment_capture": 1
    }

    retu = client.order.create(data=payload)

    print(str(retu))
