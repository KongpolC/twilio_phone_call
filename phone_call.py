from twilio.rest import Client
import time
import threading

class TwilioPhoneCall():
    def __init__(self, account_sid, auth_token, twilio_phone_number):
        self.client = Client(account_sid, auth_token)
        self.twilio_phone_number = twilio_phone_number
        self.is_phone_call_timeout = False

    def make_phone_call(self, to_phone_number):
        # Create a Twilio client
        call = self.client.calls.create(to=to_phone_number,
                                        from_=self.twilio_phone_number,
                                        url='http://demo.twilio.com/docs/voice.xml'  # This URL provides a Twilio XML response to handle the call
        )
        print(f"Call initiated with SID: {call.sid}")
        self.call_sid = call.sid
        self.to_phone_number = to_phone_number

        return call.sid

    def poll_call_status(self, max_retries=1, retry_delay=5):
        retries = 0
        while retries <= max_retries:
            call = self.client.calls(self.call_sid).fetch()

            if retries == max_retries:
                while True:
                    call = self.client.calls(self.call_sid).fetch()
                    if call.status in ['ringing','queued']:
                        print(f"call.status: {call.status}")
                        time.sleep(retry_delay)
                    else:
                        break
                break

            if call.status == 'completed':
                print("Call was answered.")
                break
            # elif call.status == 'no-answer':
            elif call.status in ['busy','no-answer']:
                print("Call was not answered. Retrying...")
                retries += 1
                print(f"retries: {retries}")
                self.call_sid = self.make_phone_call(self.to_phone_number)  # Retry the call
            elif call.status in ['busy', 'failed']:
                print(f"Call failed with status: {call.status}")
                break
            else:
                print(f"Call is in progress or other status: {call.status}")
                time.sleep(retry_delay)  # Wait and poll again
        
        return call.status
    
    def set_phone_call_timeout(self, timeout):
        # global is_phone_call_timeout
        self.is_phone_call_timeout = True
        threading.Thread(target=self.start_timeout, args=(timeout,)).start()
        print(f'++ is_phone_call_timeout: {self.is_phone_call_timeout}')
        print(f'Phone call timeout {timeout} s. started')

    # Function to set the variable back to False after a delay
    def start_timeout(self, timeout):
        # global is_phone_call_timeout
        time.sleep(timeout)
        self.is_phone_call_timeout = False
        print("Timeout has been reset")
    
    def make_repeated_phone_call_with_timeout(self, to_phone_number, timeout=21600, status_for_repeat=['busy']):
        if not self.is_phone_call_timeout:
            self.make_phone_call(to_phone_number)
            call_status = self.poll_call_status()
            print(f"call_status: {call_status}")
            if call_status in status_for_repeat:
                self.set_phone_call_timeout(timeout)


if __name__ == "__main__":
    # Twilio credentials (replace with your own)
    account_sid = 'YOUR_ACCOUNT_SID'
    auth_token = 'YOUR_AUTH_TOKEN'
    twilio_phone_number = 'YOUR_TWILIO_PHONE_NUMBER'
    to_phone_number = 'YOUR_PHONE_NUMBER'

    twilio_phone_call = TwilioPhoneCall(account_sid, auth_token, twilio_phone_number)
    while True:
        twilio_phone_call.make_repeated_phone_call_with_timeout(to_phone_number=to_phone_number, 
                                                                timeout=15)