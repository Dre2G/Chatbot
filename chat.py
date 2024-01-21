from tkinter import *
import subprocess
import customtkinter 
import os 
import openai
import asyncio
import threading
import uuid 
import time
from datetime import datetime, timezone 
import pytz

# Generate a sesseion ID when the application starts 
def generate_session_id():
	return str(uuid.uuid4())

session_id = generate_session_id()

def schedule_cleanup():
	remove_expired_sessions()
	root.after(3600000, schedule_cleanup)

client = None


# initiate app
root = customtkinter.CTk()
root.title("Speak with me Bot") 
root.geometry('600x750')
root.iconbitmap('ai_lt.ico')

 


# Generate a sesseion ID when the application starts


# Set Color Scheme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

conversions = {}



async def query_openai(prompt, client):	
	completion = client.completions.create(
			model="gpt-3.5-turbo-instruct",			
			prompt=prompt,
			temperature=0,
			max_tokens=100,
			top_p=1.0,
			frequency_penalty=0.0,
			presence_penalty=0.0,
		)

	return completion.choices[0].text





# Helper function to update the conversation
def update_conversation(session_id, user_message, bot_response):
    if session_id not in conversations:
        conversations[session_id] = []
 
 # Setting up the time   
    eastern = pytz.timezone('US/Eastern')    
    current_time_utc = datetime.now(timezone.utc)
    eastern_time = current_time_utc.astimezone(eastern)
    
    conversations[session_id].append({"user": user_message, "bot": bot_response})


# Submit To ChatGPT
def speak():
	global client, session_id
	if chat_entry.get():
		user_input = chat_entry.get()

		# Define our filename
		filename = "api_key.txt"	
			
		try:

			if os.path.isfile(filename):
				#open the file
				with open(filename, 'r') as input_file:

				# Load the data frm the file into a variable
					api_key = input_file.read().strip()
				# Query ChatGPT
				# Define our API Key To ChatGPT
				openai.api_key = api_key

				if client is None:
					client = openai.Client(api_key=api_key)

				prompt = chat_entry.get()

				
				threading.Thread(target=lambda: asyncio.run(query_openai_and_update(prompt, client)), daemon=True).start()

				# Create an instance
		
			
				
			else: 
				# Error message - you need an api key 
				my_text.insert(END, "\n\nYou Need An API Key To Talk With The Bot.")

		
		except Exception as e:
			my_text.insert(END, f"\n\n There was an error\n\n{e}")
	else:
		my_text.insert(END, "\n\nHey! You Forgot To Type Anything!")


def query_openai_and_update(prompt, client):
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(query_openai_and_update_coroutine(prompt, client))
	loop.close()



    
async def query_openai_and_update_coroutine(prompt, client):
    try:
        response = await query_openai(prompt, client)
        # Update the Tkinter widget in the main thread
        root.after(0, lambda: update_text_widget(response))
    except Exception as e:
        root.after(0, lambda: update_text_widget(f"Error: {e}"))

        update_conversation(session_id, user_input, bot_response)

def update_text_widget(text):
    my_text.insert(END, text)
    my_text.insert(END, "\n\n")


# Clear The Screens 
def clear():
	# Clear The main Text Box
	my_text.delete(1.0, END)
	# Clear the query entry widget
	chat_entry.delete(0, END)

# Do API Stuff
def key():
	
	# Define our filename
	filename = "api_key.txt"
	try:

		if os.path.isfile(filename):
			#open the file
				with open(filename, 'r') as input_file:

					# Load the data frm the file into a variable
					api_key = input_file.read().strip()

					# Output stuff to our entry box
					api_entry.insert(END, api_key)

		else: 
			# Create the file
			input_file = open(filename, 'wb')
			# Close the file
			input_file.close()
	
	except Exception as e:
		my_text.insert(END, f"\n\n There was an error\n\n{e}")

# Resize App
	root.geometry('600x750')
	# Reshow API frame
	api_frame.pack(pady=30)

# Save The API Key
def save_key():
	# Define Our filename
	filename = "api_key.txt"

	try:
		# Open file
		with open(filename, 'w') as output_file:

			# Actually add the data to the file
			output_file.write(api_entry.get())

		
		# Delete Entry Box
		api_entry.delete(0, END)

		# Hide API Frame
		api_frame.pack_forget()
		# Resize App Smaller
		root.geometry('600x600')

	except Exception as e:
		my_text.insert(END, f"\n\n There was an error\n\n{e}")

# Create Text Frame
text_frame = customtkinter.CTkFrame(root)
text_frame.pack(pady=20)

# Add Text Widget To Get ChatGPT Responses
my_text = Text(text_frame,
	bg="#343638",
	width=65,
	bd=1,
	fg="#d6d6d6",
	relief="flat",
	wrap=WORD,
	selectbackground="#1f538d")
my_text.grid(row=0, column=0)

# Creat Scrollbar for text widget
text_scroll = customtkinter.CTkScrollbar(text_frame, 
	command=my_text.yview)
text_scroll.grid(row=0, column=1, sticky='ns')

# Add the scrollbar to the textbox
my_text.configure(yscrollcommand=text_scroll.set)

# Entry Widget To Type Stuff to ChatGPT
chat_entry = customtkinter.CTkEntry(root, 
	placeholder_text="Type something To The Bot...",
	width=535,
	height=50,
	border_width=1)
chat_entry.pack(pady=10)

# Create Button Frame
button_frame = customtkinter.CTkFrame(root, fg_color="#242424")
button_frame.pack(pady=10)

# Create Submit Button 
submit_button = customtkinter.CTkButton(button_frame,
	text="Speak To ChatGPT",
	command=speak)
submit_button.grid(row=0, column=0, padx=25)

# Create Clear Button
clear_button = customtkinter.CTkButton(button_frame,
	text="Clear Response",
	command=clear)
clear_button.grid(row=0, column=1, padx=25)

# Create API Button
api_button = customtkinter.CTkButton(button_frame,
	text="Update API Key",
	command=key)
api_button.grid(row=0, column=2, padx=25)

#Add API Key Frame
api_frame = customtkinter.CTkFrame(root, border_width=1)
api_frame.pack(pady=30)

# Add API Entry Widget
api_entry = customtkinter.CTkEntry(api_frame,
	placeholder_text="Enter Your API Key",
	width=350, height=50, border_width=1)
api_entry.grid(row=0, column=0, padx=20, pady=20)

# Add API Button 
api_save_button = customtkinter.CTkButton(api_frame,
	text="Save Key",
	command=save_key)
api_save_button.grid(row=0, column=1, padx=10)

root.mainloop()