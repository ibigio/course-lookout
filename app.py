from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os, sys, threading, time
import course_lookout

# Your Account SID from twilio.com/console
account_sid = os.environ.get('ACCOUNT_SID', '')
# Your Auth Token from twilio.com/console
auth_token  = os.environ.get('AUTH_TOKEN', '')

client = Client(account_sid, auth_token)

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    global number
    body = request.values.get('Body', None)
    number = request.values.get('From', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    print(body)
    course_code = body.upper()
    if course_lookout.find_course(course_code):
        lookout_thread = threading.Thread(target=notify_when_open, args=(course_code,))
        lookout_thread.start()
        resp.message("Course " + course_code + " is now being monitored!")
    else:
        resp.message("Course " + course_code + " not found.")
    return str(resp)

def message(body):
    message = client.messages.create(
        to=number, 
        from_=os.environ.get('TWILIO_PHONE', ''),
        body=body)
    print(message.sid)

def notify_when_open(course_code):
    if course_lookout.wait_for_open(course_code) is "course_open":
        message("Course " + course_code + " has become open. Go register now! https://cab.brown.edu")
    else:
        message("Time limit reached for course " + course_code + ". Monitoring deactivated.")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
