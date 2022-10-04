#Developer : SURENDRA 
#date : 2-Oct-2022
import os

from tempfile import NamedTemporaryFile
from InvoiceGenerator.pdf import SimpleInvoice, ProformaInvoice

from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from datetime import datetime, timezone
# choose english as language
os.environ["INVOICE_LANG"] = "en"

client = Client('Client company')
provider = Provider('My company',
                    bank_account='2600420569',
                    bank_code='2010',
                    logo_filename='images/Logo.png')
creator = Creator('John Doe')


invoice = Invoice(client, provider, creator)
invoice.currency_locale = 'en_IN.UTF-8'
invoice.currency = '₹'
invoice.number = "0085"
invoice.use_tax = True
invoice.payback = datetime.now(timezone.utc)
invoice.add_item(Item(32, 600, description="Item 1"))
invoice.add_item(Item(60, 50, description="Item 2", tax=21))
invoice.add_item(Item(50, 60, description="Item 3", tax=0))
invoice.add_item(Item(5, 600, description="Item 4", tax=15))

def letscreate():
    pdf = SimpleInvoice(invoice)
    pdf.gen("invoice3.pdf", generate_qr_code=True)