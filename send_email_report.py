import pandas
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from date_time import date_time


def send_email_report(report_list:list[dict]):
    """
    send email report of app registration status
    :param report_list:
    :return:
    """
    # print(report_list)
    df = pandas.DataFrame(report_list)
    # Convert DataFrame to HTML
    html_table = df.to_html(index=False)
    # html_table = df.to_html(index=False, classes='data', escape=False, formatters={
    #     'Azure app name': lambda x: f'<strong>{x}</strong>',
    #     'Expiry status': lambda x: f'<strong>{x}</strong>',
    #     'Secret id': lambda x: f'<strong>{x}</strong>',
    #     'App created on': lambda x: f'<strong>{x}</strong>',
    #     'App Expiry date': lambda x: f'<strong>{x}</strong>',
    #     'App owners': lambda x: f'<strong>{x}</strong>'
    # })
    # print(html_table)
    # Load HTML template
    with open('email_report_template.html', 'r') as file:
        html_template = file.read()
    # Replace placeholder with the actual HTML table
    html_content = html_template.replace('{table}', html_table)
    # Add the auto-generated email message
    auto_generated_message = '<p><strong>⛔ This is an auto-generated email. Please do not reply. ⛔</strong></p>'
    html_content += auto_generated_message
    # Email details
    sender_email = "krishnadhas@devwithkrishna.in"
    receiver_email = "krishnadhas@devwithkrishna.in"
    subject = "Azure App Expiry Alert Report"

    # Create the email content
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=subject,
        html_content=html_content
    )
    try:
        load_dotenv()
        sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)
        print(f'Status code: {response.status_code}')
        print(f'Communication was send to {receiver_email} for {date_time} IST')
    except Exception as err:
        print(f'Unable to send email at the moment, Something is wrong {err}')

def main():
    """ test code here """
    load_dotenv()
    # send_email_report(report_list=report_list)




if __name__ == "__main__":
    main()
