import os
from date_time import date_time
from sendgrid.helpers.mail import Mail,Content
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

# def formatted_datetime():
#     # Get current date and time
#     now = datetime.now()
#
#     # Format date and time as dd:mm:yyyy hh:minur
#     formatted_date_time = now.strftime("%d-%m-%Y %H:%M")
#     return formatted_date_time


def send_email_with_sendgrid(applications_list_final_with_expiry_dates: list[dict]):
    """
    send email using sendgrid.
    json_files --> list of all json files generated
    :return:
    """
    success_list = []
    for application in applications_list_final_with_expiry_dates:
        # Variables for template
        email_ids = application["owner_email_ids"]
        print(f'Owners of {application["app_display_name"]} are {email_ids}')
        manager = "Krishnadhas N K"
        manager_mail = "krishnadhas@devwithkrishna.in"
        app_name = application["app_display_name"]
        expiry_status = application["expiry_status"]
        secret_id = application["secret_id"]
        created_date = application["created_date_time"]
        expiry_date = application["app_expiry_datetime"]
        app_id = application["app_id"]
        date = date_time()
        # send the alert if the expiry date is close to 30 days else ignore till next run
        if (expiry_status == "No immediate action needed") or (expiry_status == 'No secret created for the App'):
            continue
        # Load the template file
        file_loader = FileSystemLoader('.')
        env = Environment(loader=file_loader, autoescape=select_autoescape(['html', 'xml']))
        template = env.get_template('email_template.html')

        # Render the template with dynamic data
        html_content = template.render(app_name=app_name, expiry_status=expiry_status, secret_id=secret_id, date=date,
                                       manager_mail=manager_mail,app_id=app_id,manager=manager, created_date=created_date, expiry_date=expiry_date)
        message = Mail(
            from_email='krishnadhas@devwithkrishna.in',
            to_emails=email_ids,
            subject=f'Azure App credential expiry alert for {app_name} - {expiry_status}',
            html_content= Content("text/html", html_content)
        )
        success_list.append({
            'app_name': app_name,
            'expiry_status': expiry_status,
            'secret_id': secret_id,
            'app_id': app_id,
            'created_date': created_date,
            'expiry_date': expiry_date,
            'app_owners': email_ids,
        })
        try:
            load_dotenv()
            sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sendgrid_client.send(message)
            print(f'Status code: {response.status_code}')
            print(f'Communication was send to {email_ids} for {app_name} at {date}')

        except Exception as e:
            print(e)

    return success_list