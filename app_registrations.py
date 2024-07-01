import os
import requests
from dotenv import load_dotenv
from confidential_client_secret import msal_credential_token
from date_time import date_time,compare_dates
from send_email import send_email_with_sendgrid
from send_email_report import send_email_report


def graph_api_http(access_token: str):
    """
    This fucntion uses graph api and queries app registation in azure to gather details
    https://learn.microsoft.com/en-us/graph/api/application-list?view=graph-rest-1.0&tabs=http#request
    """
    print(f'Process initiated at {date_time()}')

    endpoint = f'https://graph.microsoft.com/v1.0/applications'
    print(f"Graph API call on {endpoint} ")

    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    graph_data = requests.get(url=endpoint, headers=headers)
    graph_data_json = graph_data.json()
    # print(json.dumps(graph_data, indent=2))
    applications = graph_data_json['value']
    applications_list = []
    for item in applications:
        print(f'Getting details of application - {item["displayName"]}')
        application_dict = {}
        application_dict['app_id'] = item['appId']
        application_dict['created_date_time'] = item['createdDateTime']
        application_dict['description'] = item['description']
        application_dict['object_id'] = item['id']
        application_dict['app_display_name'] = item['displayName']
        application_dict['app_expiry_datetime'] = app_expiry_datetime(item=item)
        application_dict['secret_id'] = get_secret_id(item=item)
        applications_list.append(application_dict)

    print(f'App registation details retrieved from azure at {date_time()}')
    return applications_list


def app_expiry_datetime(item:dict):
    """
    returns the application secret expiry.
    if no secret, then returns NA
    :return:
    """
    if 'passwordCredentials' in item:
        if len(item['passwordCredentials']) > 0 :
            app_expiry_datetime = item['passwordCredentials'][0]['endDateTime']
        else:
            app_expiry_datetime = 'NA'
    else:
        app_expiry_datetime =  'NA'

    return app_expiry_datetime

def get_secret_id(item:dict):
    """
    returns the secret id of app secret.
    if no secret, then returns NA
    :return:
    """
    if 'passwordCredentials' in item:
        if len(item['passwordCredentials']) > 0 :
            secret_id = item['passwordCredentials'][0]['keyId']
        else:
            secret_id = 'NA'
    else:
        secret_id =  'NA'

    return secret_id



def get_owners(applications_list: list[dict], access_token:str):
    """
    :param applications_list:
    :return:
    https://learn.microsoft.com/en-us/graph/api/application-list-owners?view=graph-rest-1.0&tabs=http#request
    """
    print(f'Retrieving owners of app registrations started at {date_time()}')
    for application in applications_list:
        print(f'App registration name {application["app_display_name"]}')
        # app_id = application['app_id']
        object_id = application['object_id']
        endpoint = f'https://graph.microsoft.com/v1.0/applications/{object_id}/owners'
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        owners_data = requests.get(url=endpoint, headers=headers)
        owners_data_json = owners_data.json()
        owners = owners_data_json['value']
        # print(owners_data_json)
        owner_list = []
        for owner in owners:
            owner_dict = {}
            owner_dict['display_name'] = owner['displayName']
            owner_dict['email'] = owner['mail']
            owner_list.append(owner_dict)
        application['owners'] = owner_list
    print(f'Owners retrieved for applications in azure at {date_time()}')
    return applications_list

def calculate_time_for_expiry(applications_list_final: list[dict]):
    """ find app registration expiry """
    for app in applications_list_final:
        if app['app_expiry_datetime'] == 'NA':
            expiry = 'NA'
            app['dates_till_expiry'] = expiry
            continue
        else:
            expiry = app['app_expiry_datetime']
            ret_expiry = compare_dates(expiry_date_str=expiry)
            app['dates_till_expiry'] = ret_expiry

    return applications_list_final

def get_owner_email_ids(applications_list_final_with_expiry_dates: list[dict]):
    """
    Get the owner email ids alone from dict
    :param owners:
    :return:
    """
    for application in applications_list_final_with_expiry_dates:
        app_owners = application['owners']
        email_ids = [owner['email'] for owner in app_owners if 'email' in owner]
        # for mail in email_ids:
        #     print(mail)
        application['owner_email_ids'] = email_ids

    return applications_list_final_with_expiry_dates



def expiry_status_based_on_time_difference(applications_list_final_with_expiry_dates: list[dict]):
    """
    define expiry status
    expired, critical and need attention

    if time difference < 0 expired
    if time difference bw 0-14 critical
    if time differnece bw 14-30 need attention
    :return:
    """
    for application in applications_list_final_with_expiry_dates:
        dates_till_expiry = application["dates_till_expiry"]

        if dates_till_expiry == 'NA':
            application["expiry_status"] = "No secret created for the App"
        elif dates_till_expiry < 0:
            application["expiry_status"] = "Expired"
        elif 0 <= dates_till_expiry < 14:
            application["expiry_status"] = "Critical"
        elif 14 <= dates_till_expiry <= 30:
            application["expiry_status"] = "Needs Attention"
        else:
            application["expiry_status"] = "No immediate action needed"
    return applications_list_final_with_expiry_dates


def main():
    """to test the code"""
    load_dotenv()
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    scopes = ['https://graph.microsoft.com/.default']
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    access_token = msal_credential_token(client_id=client_id, client_credential=client_secret,authority=authority, scope=scopes)
    applications_list =graph_api_http(access_token=access_token)
    applications_list_final = get_owners(applications_list=applications_list, access_token=access_token)
    applications_list_final_with_expiry_dates = calculate_time_for_expiry(applications_list_final=applications_list_final)
    applications_list_final_with_expiry_dates = get_owner_email_ids(applications_list_final_with_expiry_dates=applications_list_final_with_expiry_dates)
    applications_list_final_with_expiry_dates_to_sg = expiry_status_based_on_time_difference(applications_list_final_with_expiry_dates=applications_list_final_with_expiry_dates)
    success_list = send_email_with_sendgrid(applications_list_final_with_expiry_dates_to_sg)
    send_email_report(success_list)

if __name__ == "__main__":
    main()