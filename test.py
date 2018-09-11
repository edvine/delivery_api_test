import requests
import unittest
import json
from pprint import pprint
import warnings

API_BASE = 'https://mi.mhpost.ru:8444/MobileService.svc/Delivery/'
API_Login = 'login'
API_Trips = 'trips'
CLOSED = '/closed'
ORDERS = '/orders'
CHECK_SHIFT = '/check_cash_shift'
headers = {'Content-type': 'application/json'}
logindata = {'Password': '51304', 'Username': '51304'}
wronglogindata = {'Password': '55655', 'Username': '555055'}


def trips_fields_verify(verify_key, dataresponse):
    for key in dataresponse:
        if key.get(verify_key) is None:
             warnings.warn(UserWarning(verify_key, 'missed'))
        elif key.get(verify_key) == ['null']:
            warnings.warn(UserWarning(verify_key, 'missed - filed is null'))
        else:
            print_all_data = print_data()
            if print_all_data == 1:
                print(verify_key, 'is ok')


def get_token():
    response = requests.post(url=API_BASE + API_Login, json=logindata, headers=headers, verify = False)
    data = json.loads(response.text)
    token = data['ResponseBody']['Token']
    return token

def get_tripid():
    token = get_token()
    autheader = {'Content-type': 'application/json', 'UserToken': token}
    response = requests.get(url=API_BASE + API_Trips, headers=autheader, verify = False)
    data = json.loads(response.text)
    return data

def get_closedtripid():
    token = get_token()
    autheader = {'Content-type': 'application/json', 'UserToken': token}
    response = requests.get(url=API_BASE + API_Trips + CLOSED, headers=autheader, verify = False)
    data = json.loads(response.text)
    return data

def print_data():
    print_all_data = 1
    return print_all_data


class deliveryTest(unittest.TestCase):


    def test_login(self):
        pprint('Login test')
        response = requests.post(url=API_BASE+API_Login, json=logindata, headers=headers, verify = False)
        print('Response time:', response.elapsed.total_seconds())
        print('Login response code:', response)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        token = data['ResponseBody']['Token']
        print('User Token:', token)

    def test_wronglogin(self):
        pprint('Wrong Login test')
        response = requests.post(url=API_BASE + API_Login, json=wronglogindata, headers=headers, verify = False)
        self.assertEqual(response.status_code, 200)
        print('Response time:', response.elapsed.total_seconds())
        data = json.loads(response.text)
        self.assertEqual(data['ResponseCode'], 400)
        print('Wrong login response code:', data['ResponseCode'])

    def test_trips(self):
        pprint('Trips test')
        token = get_token()
        autheader = {'Content-type': 'application/json', 'UserToken': token}
        response = requests.get(url=API_BASE+API_Trips, headers=autheader, verify = False)
        print('Response time:', response.elapsed.total_seconds())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        print_all_data = print_data()
        if print_all_data == 1:
            pprint(data)

    def test_trips_closed(self):
        pprint('Delivery list test')
        token = get_token()
        autheader = {'Content-type': 'application/json', 'UserToken': token}
        response = requests.get(url=API_BASE + API_Trips + CLOSED, headers=autheader, verify = False)
        print('Response time:', response.elapsed.total_seconds())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        print_all_data = print_data()
        if print_all_data == 1:
            pprint(data)
        # Добавить првоверку всех полей принятых рейсов тут

    def test_orders_iteration(self):
        print('Orders iteration')
        token = get_token()
        data = get_tripid()
        for order in data['ResponseBody']:
            trip_id = order['TripId']
            print(trip_id)
            autheader = {'Content-type': 'application/json', 'UserToken': token}
            response = requests.get(url=API_BASE + API_Trips + '/' + trip_id + '/' + ORDERS, headers=autheader, verify = False)
            print('Response time:', response.elapsed.total_seconds())
            self.assertEqual(response.status_code, 200)
            dataresponse = json.loads(response.text)
            print_all_data = print_data()
            if print_all_data == 1:
                pprint(dataresponse)
            trips_fields_verify('CustomerAddress', dataresponse['ResponseBody'])
            trips_fields_verify('CustomerPhone', dataresponse['ResponseBody'])
            trips_fields_verify('CustomerName', dataresponse['ResponseBody'])
            trips_fields_verify('DocNumber', dataresponse['ResponseBody'])
            trips_fields_verify('Payment', dataresponse['ResponseBody'])
            trips_fields_verify('PaymentLabel', dataresponse['ResponseBody'])
            trips_fields_verify('Status', dataresponse['ResponseBody'])
            trips_fields_verify('StatusLabel', dataresponse['ResponseBody'])
            trips_fields_verify('Waybill', dataresponse['ResponseBody'])
            for key in dataresponse['ResponseBody']:
                if key.get('AutoAcceptance') != None:
                    print('Auto Accept activated')
                if key.get('IsTaken') == True:
                    warnings.warn(UserWarning('Order is taken'))
                if key.get('StatusLabel') == 'Отправлен':
                    warnings.warn(UserWarning('Order  sent'))
            for orderid in dataresponse['ResponseBody']:
                order_id = orderid['OrderId']
                print(order_id)
                responseorder = requests.get(url=API_BASE + API_Trips + '/' + trip_id + '/' + ORDERS + '/' +
                                                 order_id + '/products', headers=autheader, verify = False)
                print('Response time:', responseorder.elapsed.total_seconds())
                responseorder = json.loads(responseorder.text)
                if print_all_data == 1:
                    pprint(responseorder)

                # for i in range(len(responseorder['ResponseBody'])):
                #     responseorder['ResponseBody'][i]["ConcreateProduct"]

                    for product in responseorder['ResponseBody']:
                        trips_fields_verify('Brand', product['ConcreateProduct'])
                        trips_fields_verify('Id', product['ConcreateProduct']['Color'])
                        trips_fields_verify('Name', product['ConcreateProduct']['Color'])
                        trips_fields_verify('Id', product['ConcreateProduct'])
                        trips_fields_verify('Name', product['ConcreateProduct'])
                        trips_fields_verify('Price', product['ConcreateProduct'])
                        trips_fields_verify('ProductId', product['ConcreateProduct'])
                        trips_fields_verify('Id', product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('Name', product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('Site', product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('StorageType',
                                        product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('Id', product['ConcreateProduct']['Quantity']['Size'])
                        trips_fields_verify('Name', product['ConcreateProduct']['Quantity']['Size'])
                        trips_fields_verify('FinalPrice', product)
                        trips_fields_verify('ItemType', product)
                        trips_fields_verify('LineNum', product)
                        trips_fields_verify('Price', product)
                        trips_fields_verify('Quantity', product)
                        trips_fields_verify('Tax', product)


    def test_closed_orders_iteration(self):
        print('Closed Orders iteration')
        token = get_token()
        data = get_closedtripid()
        for order in data['ResponseBody']:
            trip_id = order['TripId']
            print(trip_id)
            autheader = {'Content-type': 'application/json', 'UserToken': token}
            response = requests.get(url=API_BASE + API_Trips + '/' + trip_id + '/' + ORDERS, headers=autheader, verify = False)
            print('Response time:', response.elapsed.total_seconds())
            self.assertEqual(response.status_code, 200)
            dataresponse = json.loads(response.text)
            print_all_data = print_data()
            if print_all_data == 1:
                pprint(dataresponse)
            trips_fields_verify('CustomerAddress', dataresponse['ResponseBody'])
            trips_fields_verify('CustomerPhone', dataresponse['ResponseBody'])
            trips_fields_verify('CustomerName', dataresponse['ResponseBody'])
            trips_fields_verify('DocNumber', dataresponse['ResponseBody'])
            trips_fields_verify('Payment', dataresponse['ResponseBody'])
            trips_fields_verify('PaymentLabel', dataresponse['ResponseBody'])
            trips_fields_verify('Status', dataresponse['ResponseBody'])
            trips_fields_verify('StatusLabel', dataresponse['ResponseBody'])
            trips_fields_verify('Waybill', dataresponse['ResponseBody'])
            for key in dataresponse['ResponseBody']:
                if key.get('AutoAcceptance') != None:
                    print('Auto Accept activated')
                if key.get('IsTaken') != True:
                    warnings.warn(UserWarning('Order not taken'))
                if key.get('StatusLabel') != 'Отправлен':
                    warnings.warn(UserWarning('Order dont sent'))

            for orderid in dataresponse['ResponseBody']:
                order_id = orderid['OrderId']
                print(order_id)
                responseorder = requests.get(url=API_BASE + API_Trips + '/' + trip_id + '/' + ORDERS + '/' +
                                                 order_id + '/products', headers=autheader, verify = False)
                print('Response time:', responseorder.elapsed.total_seconds())
                responseorder = json.loads(responseorder.text)
                if print_all_data == 1:
                    pprint(responseorder)
                    for product in responseorder['ResponseBody']:
                        trips_fields_verify('Brand', product['ConcreateProduct'])
                        trips_fields_verify('Id', product['ConcreateProduct']['Color'])
                        trips_fields_verify('Name', product['ConcreateProduct']['Color'])
                        trips_fields_verify('Id', product['ConcreateProduct'])
                        trips_fields_verify('Name', product['ConcreateProduct'])
                        trips_fields_verify('Price', product['ConcreateProduct'])
                        trips_fields_verify('ProductId', product['ConcreateProduct'])
                        trips_fields_verify('Id', product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('Name', product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('Site', product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('StorageType',
                                                product['ConcreateProduct']['Quantity']['Storage'])
                        trips_fields_verify('Id', product['ConcreateProduct']['Quantity']['Size'])
                        trips_fields_verify('Name', product['ConcreateProduct']['Quantity']['Size'])
                        trips_fields_verify('FinalPrice', product)
                        trips_fields_verify('ItemType', product)
                        trips_fields_verify('LineNum', product)
                        trips_fields_verify('Price', product)
                        trips_fields_verify('Quantity', product)
                        trips_fields_verify('Tax', product)

if __name__ == "__main__":
    unittest.main()
