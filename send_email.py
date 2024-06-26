import os
from date_time import datetime
from sendgrid.helpers.mail import Mail,Content
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv
from jinja2 import Environment,FileSystemLoader

def formatted_datetime():
    # Get current date and time
    now = datetime.now()

    # Format date and time as dd:mm:yyyy hh:minur
    formatted_date_time = now.strftime("%d-%m-%Y %H:%M")
    return formatted_date_time


def send_email_with_sendgrid(applications_list_final_with_expiry_dates: list[dict]):
    """
    send email using sendgrid.
    json_files --> list of all json files generated
    :return:
    """
    for application in applications_list_final_with_expiry_dates:
        email_ids = application["owner_email_ids"]
        print(f'Owners of {application["app_display_name"]} are {email_ids}')
        # Variables for template
        manager = "Krishnadhas N K"
        manager_mail = "krishnadhas@devwithkrishna.in"
        app_name = application["app_display_name"]
        expiry_status = application["expiry_status"]
        secret_id = application["secret_id"]
        created_date = application["created_date_time"]
        expiry_date = application["app_expiry_datetime"]
        app_id = application["app_id"]
        # repo_name = "github-automation-to-fetch-remaining-github-runner-time"
        # org_name = 'devwithkrishna'
        # username = 'githubofkrishnadhas'
        date = formatted_datetime()
        # send the alert if the expiry date is close to 30 days else ignore till next run
        if expiry_status == "No immediate action needed":
            continue
        # Load the template file
        file_loader = FileSystemLoader('.')
        env = Environment(loader=file_loader)
        template = env.get_template('email_template.html')

        # Render the template with dynamic data
        html_content = template.render(app_name=app_name, expiry_status=expiry_status, secret_id=secret_id, date=date,
                                       manager_mail=manager_mail,app_id=app_id,manager=manager, created_date=created_date, expiry_date=expiry_date)
        message = Mail(
            from_email='krishnadhas@devwithkrishna.in',
            to_emails='krishnadhasnk1997@gmail.com',
            # to_emails=email_ids,
            subject=f'Azure App credential expiry alert for {app_name} - {expiry_status}',
            html_content= Content("text/html", html_content)
        )
        # if attachments:
        #     for attachment in attachments:
        #         message.add_attachment(attachment)

        try:
            load_dotenv()
            sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sendgrid_client.send(message)
            print(f'Status code: {response.status_code}')
            print(f'Communication was send to {email_ids} for {app_name} at {date}')
            # print(response.body)
            # print(response.headers)
        except Exception as e:
            print(e)