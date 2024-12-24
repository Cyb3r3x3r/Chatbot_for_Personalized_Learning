# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# import sqlite3
from transformers import TFAutoModelForCausalLM, AutoTokenizer
import yaml
from bs4 import BeautifulSoup
import requests
import googleapiclient.discovery
from typing import Any,Text,Dict,List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction



class ActionRequestBook(Action):
    def name(self)->Text:
        return "action_fetch_books"
    
    def fetch_books(self,query):
        query = query.replace(" ","+")
        url = f"https://www.google.com/search?udm=36&q={query}"
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            books = []
            for link in soup.find_all('a', href=True):
                title_div = link.find('div', class_='BNeawe vvjwJb AP7Wnd')
                if title_div:
                    title = title_div.text.strip()
                    href = link['href']
                    books.append((title, href))
            return books
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
        
    def run(self,dispatcher:CollectingDispatcher,tracker:Tracker,domain:Dict[Text,Any])->List[Dict[Text,Any]]:
        query = tracker.get_slot("topic")
        
        if not query:
            dispatcher.utter_message(text="Please provide me topic so i can search some books for you")
            return []
        books  = self.fetch_books(query)

        if books:
            response = f"Here are some recommended Books on {query} with their links: \n"
            for book in books[:5]:
                response += f"-{book[0]} [View Book]({book[1]})\n"
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_mesaage(text=f"I am sorry. I could not find any relevant books for {query}.")
        return []

class ActionOpenLearn(Action):
    def name(self)->Text:
        return "action_fetch_openlearn"
    
    def fetch_openlearn_courses(self,query):
        query = query.replace(" ","%20")
        base_url = f"https://www.open.edu/openlearn/local/ocwglobalsearch/search.php?q={query}&filter=all/freecourse,article/all/all/all/all/all&sort=relevant"

        try:
            response = requests.get(base_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text,"html.parser")
            courses = []
            for div in soup.find_all("div",class_="view-detail"):
                link_element = div.find("a",class_="view-detail-link")
                if link_element:
                    link = link_element['href']
                    title_span = link_element.find("span",class_="sr-only")
                    title = title_span.text.strip() if title_span else "No title available"
                    title = " ".join(title.replace("\n", " ").split())  # Normalize whitespace
                    courses.append({"title": title, "link": link})
            return courses
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching courses: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
        
    def run(self,dispatcher:CollectingDispatcher,tracker:Tracker,domain:Dict[Text,Any])->List[Dict[Text,Any]]:
        query = tracker.get_slot("topic")
        if not query:
            dispatcher.utter_message(text="Please provide me topic so i can search some lessons for you")
            return []
        courses  = self.fetch_openlearn_courses(query)

        if courses:
            response = f"Here are some Open Learn courses on {query} with their links: \n"
            for course in courses[:5]:
                response += f"-{course['title']} [View Course]({course['link']})\n"
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_mesaage(text=f"I am sorry. I could not find any relevant courses on OpenLearn for {query}.")
        return []

class ActionYoutubeVideos(Action):
    def name(self) -> Text:
        return "action_get_youtube_videos"
    
    def get_video_links(self,query:Text)->List[Text]:
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey="AIzaSyBp6sFXnTfhKQlU3Cy4flB4BY4viyBALSM")
        request = youtube.search().list(q=query, part="snippet", type="video",maxResults=5)
        response = request.execute()
        video_links = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_links.append(f"https://www.youtube.com/watch?v={video_id}")

        return video_links
    
    def run(self,dispatcher:CollectingDispatcher,tracker:Tracker,domain:Dict[Text,Any])->List[Dict[Text,Any]]:
        user_query = tracker.get_slot("topic")
        if not user_query:
            user_query = tracker.get_slot("user_pref")
            if not user_query:
                dispatcher.utter_message(text="Please provide me topic so i can search some lessons for you")
                return []
        video_links = self.get_video_links(user_query)

        if video_links:
            dispatcher.utter_message(text=f"Here are some videos for {user_query} : ")
            for link in video_links:
                dispatcher.utter_message(text=link)

        else:
            dispatcher.utter_mesaage(text=f"I am sorry. I could not find any videos for {user_query}.")
        return []


class ActionFetchFromGPT(Action):
    def name(self) -> Text:
        return "action_fetch_from_gpt"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        model_name = "gpt2"
        try:

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = TFAutoModelForCausalLM.from_pretrained(model_name)
            input_text = tracker.latest_message.get('text')
            inputs = tokenizer.encode(input_text, return_tensors="tf")
            outputs = model.generate(inputs, max_length=75)

            # Decode the generated text
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)

            dispatcher.utter_message(response)
        except Exception as e:
            dispatcher.utter_message(f"Sorry I wasn't able to get more information for you. {e}")

# class ActionSaveUserDetails(Action):
#     def name(self) -> Text:
#         return "action_save_user_details"

#     def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain:Dict[Text,Any]) -> List[Dict[Text, Any]]:
#         user_name = tracker.get_slot("user_name")
#         user_pref = tracker.get_slot("topic")
#         #for debugging
#         print(user_name)
#         print(user_pref)

#         if user_name and user_pref:
#             connection = sqlite3.connect('user_data.db')
#             cursor = connection.cursor()
#             cursor.execute(
#                 "INSERT INTO users (name, pref) VALUES (?, ?)",
#                 (user_name, user_pref),
#             )
#             connection.commit()
#             connection.close()
#             dispatcher.utter_message(text=f"Got it, {user_name}! I've saved your preference for {user_pref}.")
#         else:
#             dispatcher.utter_message(text="I need both your name and preferences to save your details.")

#         return []

# class ActionRetrieveUserDetails(Action):
#     def name(self) -> Text:
#         return "action_retrieve_user_details"

#     def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain:Dict[Text,Any]) -> List[Dict[Text, Any]]:
#         user_name = tracker.get_slot("user_name")
#         print(user_name)
#         if user_name:
#             connection = sqlite3.connect('user_data.db')
#             cursor = connection.cursor()
#             cursor.execute("SELECT pref FROM users WHERE LOWER(name) = ?", (user_name.lower(),))
#             result = cursor.fetchone()
#             connection.close()

#             if result:
#                 user_pref = result[0]
#                 dispatcher.utter_message(text=f"Hi {user_name}, I remember you like {result[0]}!. Is this correct?")
#                 return [SlotSet("topic", user_pref)]
#             else:
#                 dispatcher.utter_message(text=f"Hi {user_name}, I don't have your preferences saved yet.")
#                 # ask the user preference if his name is not in the database
#                 dispatcher.utter_message(response="utter_ask_preferences")
#         else:
#             dispatcher.utter_message(text="I need your name to retrieve your preferences.")

#         return []

# class ActionSaveNewPreferences(Action):
#     def name(self) -> Text:
#         return "action_save_new_preferences"

#     def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain:Dict[Text,Any]) -> List[Dict[Text, Any]]:
#         user_name = tracker.get_slot("user_name")
#         new_preferences = tracker.get_slot("user_pref")

#         if user_name and new_preferences:
#             # Open the database connection
#             connection = sqlite3.connect('user_data.db')
#             cursor = connection.cursor()

#             # Update the user's preferences in the database
#             cursor.execute(
#                 "UPDATE users SET preferences = ? WHERE name = ?",
#                 (new_preferences, user_name),
#             )
#             connection.commit()
#             connection.close()

#             dispatcher.utter_message(text=f"Your preferences have been updated to {new_preferences}. Thank you for updating!")
#         else:
#             dispatcher.utter_message(text="I could not update your preferences. Please ensure your name and preferences are provided correctly.")

#         return [SlotSet("user_pref", new_preferences)]
    
# class ValidateLearningResourceForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_request_learning_resource_form"

#     def validate_topic(
#         self,
#         value: Text,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#         # Check if topic was provided
#         if not value:
#             user_pref = tracker.get_slot("user_pref")
#             if user_pref:
#                 # Use user_pref value as topic if topic is missing
#                 dispatcher.utter_message(text=f"I'll use your preference '{user_pref}' as the topic.")
#                 return {"topic": user_pref}
#             else:
#                 dispatcher.utter_message(text="I didn't catch the topic. Could you please clarify?")
#                 return {"topic": None}
#         return {"topic": value}