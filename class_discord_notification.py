import discord
from os import environ
from dotenv import load_dotenv

load_dotenv()


class DiscordNotification():
    

    def __init__(self, p_channel_id : int):
        self.token            = environ.get("DISCORD_TOKEN")        
        self.channel_id : int = p_channel_id
        self.message    : str = None

        intents         = discord.Intents.all()
        intents.members = True
        intents.message_content = True

        # Create a client instance with intents
        self.client = discord.Client(intents=intents)


    async def on_ready(self):
        try:
            w_channel = await self.client.fetch_channel(self.channel_id)
            # print(f"Got channel: {w_channel}")

            if w_channel:
                w_chunk_size = 2000
                for i in range(0, len(self.message), w_chunk_size):
                    await w_channel.send(self.message[i:i+w_chunk_size]) 
                                   
                # await w_channel.send(self.message)
                print("--> Discord Message sent.")
        except  Exception as e:
            print(f"Discord communication error - msg: {e}")
        finally:
            await self.client.close()    
            


    def send_message(self, p_message : str):
        self.message = p_message
        self.client.event(self.on_ready)
        self.client.run(self.token)



if __name__ == "__main__":
    print("===Run main.py===") 
    # W_DISCORD_CHANNEL_ID : int = environ.get("DISCORD_CHANNEL_ID")
    # w_notificaton = DiscordNotifiacation(p_channel_id=W_DISCORD_CHANNEL_ID)
    # w_notificaton.send_message("Utility test.")