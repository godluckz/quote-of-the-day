import random, datetime as dt, emoji, requests, json
from class_email_notification import EmailNotification
from class_discord_notification import DiscordNotification
from os import environ, path, makedirs, remove
from dotenv import load_dotenv

load_dotenv()

# Get the current directory of the script
W_CURR_DIR = path.dirname(path.abspath(__file__))
# Construct the path to the "data" directory one level up
W_DATA_DIR = path.join(W_CURR_DIR, 'data')
W_ARCHIVE_DIR = path.join(W_CURR_DIR, 'archive')

W_QUOTE_FILE_EXT : str = 'json'

W_QUOTE_FILE = path.join(W_DATA_DIR, f'quotes.{W_QUOTE_FILE_EXT}')
W_ARCHIVE_QUOTE_FILE = path.join(W_ARCHIVE_DIR, f'quotes.{W_QUOTE_FILE_EXT}')


W_DISCORD_CHANNEL_ID : int = environ.get("DISCORD_QOD_CHANNEL_ID")


def setup_required_dirs():
    print("==>> Check if need to setup program Directories.")
    w_dirs : list = [W_DATA_DIR,W_ARCHIVE_DIR]
    for r_dir in w_dirs:
        if not path.exists(r_dir):
            makedirs(r_dir)
            print(f"Directory '{r_dir}' created.")



def get_quotes_from_file(p_file_name : str) -> list:
    w_all_quotes : list = []

    if path.exists(p_file_name):
        with open(file=p_file_name, mode="r") as qf:  #they came from https://www.positivityblog.com/monday-motivation-quotes/

            w_all_quotes = json.load(fp=qf)
    return w_all_quotes



def write_quotes_to_file(p_file_name : str,
                         p_quotes    : list) -> None:
    with open(file=p_file_name,mode='w') as qf:
        json.dump(obj=p_quotes, fp=qf, indent=4)



def archive_quote_to_file(p_quote : list) -> None:
    w_all_quotes : list = []

    if path.exists(W_ARCHIVE_QUOTE_FILE):
        w_all_quotes : list = get_quotes_from_file(W_ARCHIVE_QUOTE_FILE)

    w_all_quotes.append(p_quote)


    write_quotes_to_file(p_file_name = W_ARCHIVE_QUOTE_FILE,
                         p_quotes    = w_all_quotes)



def send_quote_of_the_day(p_quote: str, p_week_day: str) -> None:

    discord_message_sent : bool = False

    try:
        print("==>> Sending Discord message.")
        discord_notificaton = DiscordNotification(p_channel_id=W_DISCORD_CHANNEL_ID)
        discord_notificaton.send_message(p_quote)
        discord_message_sent = True
    except Exception as e:
        print(f"Fail to send discord message - {e}")


    if not discord_message_sent:

        try:
            print("==>> Sending email.")
            notification : EmailNotification = EmailNotification()

            W_MAIL_TO:  str = environ.get("EMAIL_TO")
            W_MAIL_CC:  str = environ.get("EMAIL_CC")
            W_MAIL_BCC: str = environ.get("EMAIL_BCC")
            W_SUBJECT:  str = "Hello - Quote of the day - with love."
            if not W_MAIL_TO:
                print("Atleast email to is required.")
                return

            w_emoji_name = ":face blowing a kiss:"   #https://carpedm20.github.io/emoji/
            w_emoji_name = w_emoji_name.replace(" ","_")
            w_emoji1 = emoji.emojize(w_emoji_name)

            # w_emoji_name = ":smiling face with heart-eyes:"
            w_emoji_name = ":heart_hands_medium-dark_skin_tone:"
            w_emoji_name = w_emoji_name.replace(" ","_")
            w_emoji2 = emoji.emojize(w_emoji_name)
            # print(w_emoji1)

            w_msg = f"Good morning {w_emoji1}\n\n It is a beautiful {p_week_day}, the year of our Lord \n\n{p_quote}\n\nHave a great {p_week_day} {w_emoji2}"

            notification.send_email(p_email_to = W_MAIL_TO,
                                    p_subject  = W_SUBJECT,
                                    p_message  = w_msg,
                                    p_email_cc = W_MAIL_CC,
                                    p_email_bcc = W_MAIL_BCC)

            print("Email sent.")
        except Exception as e:
            print(f"Fail to send email - msg : {e}")



def convert_quote_txt_to_json() -> None:

    w_quote_txt_file : str = "data/quotes.txt"
    if path.exists(w_quote_txt_file):
        with open(w_quote_txt_file, "r") as qf:
            w_all_quotes: list = qf.readlines()
        w_quote_list : list = []

        for r_quote in w_all_quotes:
            w_quote_split = r_quote.split("-")
            w_q : str = w_quote_split[0]
            w_a : str = w_quote_split[1]
            w_new_quote : json = {
                                    "q": w_q.strip().strip('"'),
                                    "a": w_a.strip()
                            }
            w_quote_list.append(w_new_quote)

        w_quote_json = json.dumps(obj=w_quote_list, indent=4)

        if len(w_quote_list) > 0:
            write_quotes_to_file(p_file_name = W_QUOTE_FILE,
                                 p_quotes    = w_quote_list)


        remove(w_quote_txt_file)



def reload_quotes_file(p_today : dt.datetime) -> None:
    try:
        print("==>> Reload new quotes into file")
        w_month_quotes_response = requests.get(url="https://zenquotes.io/api/quotes")
        # print(w_quotes_response.status_code)

        w_quotes_json = w_month_quotes_response.json()
        w_number_of_quotes = len(w_quotes_json)
        # print(f"Number of quotes: {w_number_of_quotes}")

        if w_number_of_quotes > 0:
            # w_today_date = p_today.strftime("%Y%m%d")
            # w_new_path = f"{W_ARCHIVE_DIR}/quotes_{w_today_date}.{W_QUOTE_FILE_EXT}"
            # if path.exists(w_new_path):
            #     remove(w_new_path)

            # if path.exists(W_QUOTE_FILE):
            #     move(W_QUOTE_FILE, w_new_path)

            with open(W_QUOTE_FILE, "w") as qf:
                json.dump(obj=w_quotes_json, fp=qf, indent=4)

    except Exception as e:
        print(f"Fail to get quote from API - msg: {e}")



def get_random_quote(p_today : dt.datetime ) -> str:
    w_quote_of_the_day : str = None

    try:
        convert_quote_txt_to_json()
    except Exception:
        pass


    w_all_quotes = get_quotes_from_file(p_file_name = W_QUOTE_FILE)
    w_total_quotes_found = len(w_all_quotes)

    if w_total_quotes_found > 0:
        print("==>> Use quote from file.")

        w_quote_choice = random.choice(w_all_quotes)
        w_all_quotes.remove(w_quote_choice) #Remove the quote that was picked

        w_quote_of_the_day = f'"{w_quote_choice["q"]}" - {w_quote_choice["a"]}'

        archive_quote_to_file(p_quote = w_quote_choice)

        # w_total_quotes_left = len(w_all_quotes)
        # print(f"before: {w_total_quotes_left}")

        write_quotes_to_file(p_file_name = W_QUOTE_FILE,
                            p_quotes    = w_all_quotes) #write a new list with the item removed.

    else:
        reload_quotes_file(p_today)
        try:
            print("==>> Get quote from qapi.")
            w_quotes_response = requests.get(url="https://qapi.vercel.app/api/random")
            # print(w_quotes_response.status_code)

            # print(json.dumps(w_quotes_response.json(), indent=4))

            w_quote_json = w_quotes_response.json()
            w_quote_of_the_day = f'"{w_quote_json["quote"]}" - {w_quote_json["author"]}'
        except Exception as e:
            print(f"Fail to get quote from API - msg: {e}")


        if not w_quote_of_the_day:
            try:
                print("==>> Get quote from zenquotes.")
                w_quotes_response = requests.get(url="https://zenquotes.io/api/random")
                # print(w_quotes_response.status_code)

                w_quote_json = w_quotes_response.json()
                # print(json.dumps(w_quote_json, indent=4))

                w_quote_of_the_day = f'"{w_quote_json[0]["q"]}" - {w_quote_json[0]["a"]}'
            except Exception as e:
                print(f"Fail to get quote from API - msg: {e}")

    return w_quote_of_the_day



def main() -> None:
    w_now: dt.datetime = dt.datetime.now()

    w_quote_of_the_day: str = get_random_quote(w_now)
    # print(w_quote_of_the_day)

    if w_quote_of_the_day:
        w_weekday = w_now.strftime('%A') # read more here: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        send_quote_of_the_day(w_quote_of_the_day, w_weekday)
    else:
        print("Could not find quotes to email out.")




if __name__ == "__main__":
    setup_required_dirs()
    print("====================================")
    print("=======Processing Started!!=======")
    print("====================================")
    print("============++++++++++++============")
    main()
    print("====================================")
    print("=======Processing Completed!!=======")
    print("====================================")
    print("============++++++++++++============")
