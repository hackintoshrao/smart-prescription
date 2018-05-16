# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

import apiai
from flask import Flask
from flask import request
from flask import make_response
from flask_cors import CORS, cross_origin

import sys


CLIENT_ACCESS_TOKEN = 'c99e92912fa746bd8a7dc3cfd7593d8c'
"""
1. Webhook for dialog flow interactions.
2. The request is parsed.
3. Decisions are made.
4. Response will be send back to the bot's interface.

"""


class IntentEntitiesMatch:
	"""
	Here we maintain the constant strings which are used for identifying the intents and the entities.
	Everytime a new intent or an entity is created in dialogflow please add them here, the knowledge of list of
	entities and intents are necessary to handle the business logic. Also the synonyms which are added as part
	of dialogflow entity UI are also mentioned in the Entities section.

	Intents:
		1. "Platform exploration help" : Used for any navigation based help in the platform.
		2. "FAQ"                       : All the FAQ based services.



	Entities:
		features: Corresponds to all the features in the platform.
		    1. sign out :   "sign out", "signout", "signing out", "logout", "moveout", log out"
		    2. goals :      "goal", "goals", "target", "targets"
		    3. project :    "project", "projects"
		    4. objective :  "objective", "objectives", "dashboard"
		    5. leaderboard: "Leaderboard", "leaderboard", "leader board", "leadershipboard", "winner board", "champion board",
		                    "championshipboard", "leading", "leader", "winner", "winning"
	            6. progress:    "progress", "progres", "achievement", "achievements"
		    7. profile:     "profile","user profile","userprofile","profiles","profile details"
		    8. performance: "performance", "perform", "achieve", "achievement", "accomplishment", "accomplish", "perf", "performing"
		    9. feedback   : "assessment", "evaluation", "reply", "feedback", "feadback","comment", "evaluate", "respond"

		action type: Corresponds to whether the user wants to view, update, delete any feature
		    1. update : "updates", "change", "revise", "edit", "update", "correct", "better", "udpate"
		    2. create : "create", "make", "construct", "build", "crate", "add"
		    3. send   : "give", "send", "make", "push", "write", "make"

	        emotions : Corresponds to variosu emotions the user would express in the platform.
		    1. unhappy: "unhappy", "frustrated", "dissapointed", "sad", "miserable", "sorrowful", "sorrow"
		                "dejected", "let down", "despondent", "heart-broken","unsatisfied", "pissed", "angry"
		    2. happy  : "happy", "content", "contented", "cheerful", "joy", "joyful","delight","delightful",
		                "satisfied","blessed","ecstatic", "excited"

	"""

	"""
	Class containing string names of features and entities
	These names are used in conditional statements to execute business logic based on the intents and entities in the user query.
	Since constants cannot be defined in python they are stored here inside the class for safer access.

	Unintended change of these strings will cause the business logic to fail. Its very important that
	string values of these intents and entities created in dialogflow and the ones declared here match.

	The matching of these intents and the entities too will be done here.
	"""
        # Response for various intent-entity pairs are maintained in this section.

	# All responses for navigation based help are saved here.

	"""
        # Response when user queries for navigation help with updating goals.
	PLATFORM_GOALS_RESPONSE  = Here are the steps to update the goals: First, select the project (from the carousel) > click on an objective > update goals.
			    Here you can drag the seeker to update the progress and then pick the date to assign the progress to that specific date.
			    Then hit save to record your progress.
        """

	def PLATFORM_GOALS_GENERIC_RESPONSE(self):
		"""
		Goals related responses.
		"""
		return  """Redirecting to the Objectives page, Click on any objectives to view, add or update its goals"""


	def PLATFORM_PROJECT_VIEW_PROJECT(self):
		"""
		 Project related responses.
 		 Response when user seeks help in adding project.
		"""
		return  """Here are the list of your projects"""


	def PLATFORM_OBJECTIVE_VIEW_RESPONSE(self):
		"""
		Objective related responses.
		Response when user seeks help in viewing objectives.
		"""
		return """Here are your objectives (Redirecting to the radar chart page).
		          Click on any objective to update them."""


	def PLATFORM_PROGRESS_RESPONSE(self):
		"""
		Response when user asks to view his progress. The objective radar chart will be served.
		"""
		return """(Redirecting to the Radar chart of objectives) Click on the any objectives to view or update the progress."""


	def PLATFORM_PROFILE_VIEW_RESPONSE(self):
		"""
	 	Profile related response.
		Response when user asks to view his profile. The user will be directed to their profile page.
		"""
		return "Redirecting to your profile."


	def PLATFORM_SIGNOUT_RESPONSE(self):
		"""
	 	Response when user asks for navigation help with signing out.
		"""
		return """Here are the steps to signout: Go to top right icon > profile
		 			> sign out and then click on it."""


	def PLATFORM_LEADERBOARD_RESPONSE(self):
		"""
		Response when user seeks navigational help in visiting the leaderboard.
		"""
		return  """Click here to visit the leaderboard"""

	def PLATFORM_DEFAULT_RESPONSE(self):
		"""
		default response when none of the keys match
		"""
		return """Here are the list of things I can help you with curently, I could do more as I evolve."""


	def PLATFORM_INSUFFICIENT_ACTION_TYPE_RESPONSE():
		"""
		for queries like "I want to update" we don't have sufficient information.
		"""
		return "Sorry, You need to mention what you want to update"

	def PLATFORM_PERFORMANCE_VIEW(self):
		 """
		 Response when the user requests to view their performance.
		 """
		 return "Here is how you can view your performance...."



	def FAQ_UNHAPPY_FEEDBACK(self):
	 	"""
			Responses for FAQ.
			Response when the user is frustrated with the feedback.
 		"""

		return """Hey, I'm sorry that you didn't get a great feedback.
				The feedback given is based on your colleagues or managers opinions"""

	def FAQ_HAPPY_FEEDBACK(self):
		"""
		Response when user is happy with his feedback.
		"""
		return "Yaaay!!! Its time to party..."

	def PLATFORM_FEEDBACK_VIEW(self):
		"""
		Response when the user wants to view his feedback.
		"""
	 	return "Here are the feedbacks you've recieved...",

	def PLATFORM_CREATE_OBJECTIVE(self):
		"""
		Entity_type(create) = action_type , Entity_type(objective) = features.
		Response when user requests to create a new objective.
		"""
		return "Here is how to create a new objective"


	def PLATFORM_UPDATE_OBJECTIVE(self):
		"""
		Entity_type(update) = action_type , Entity_type(objective) = features.
		Response when user requests to update an existing objective.
		"""
		return """Redirecting to the objectives page. Click on respective
					objectives to update them"""



	def  PLATFORM_CREATE_GOAL(self):
		"""
		Entity_type(create) = action_type , Entity_type(goals) = features.
		Response when user requests to create a new goal.
		"""
		return """Here is how to create a new goal.
				Go to objectives, click on them and create goals"""

	def PLATFORM_UPDATE_GOALS(self):
		"""
		Entity_type(update) = action_type, Entity_type(goals) = features.
		Response when user requests to update goals.
		"""
		return """"Click on objectives and find the goal you want to update
		 		and edit it"""

	def PLATFORM_CREATE_PROJECT(self):
		"""
		Entity_type(create) = action_type , Entity_type(project) = features.
		Response when user requests to create a new project.
		"""
		return """This is how to create project"""

	def PLATFORM_UPDATE_PROJECT(self):
		"""
		Entity_type(update) = action_type , Entity_type(project) = features.
		"""
		return "Here is where you can update an existing project"

	def PLATFORM_UPDATE_PROGRESS(self):
		"""
		Entity_type(update) = action_type , Entity_type(progress) = features.
		Response when user requests to update their progress.
		"""
		return """Here is where you can update your progress. """

	def PLATFORM_UPDATE_PROFILE(self):
		"""
		Entity_type(update) = action_type , Entity_type(profile) = features.
		Response when user requests to update their profile.
		"""
		return """Here is how to update profile"""

	def PLATFORM_CREATE_PROFILE(self):
		"""
		Entity_type(update) = action_type , Entity_type(profile) = features.
		Response when user requests to update their profile.
		"""
		return """There are three aspects to your profile and their view status is as follows:
			Goals / KPIs - This can be viewed only by you or your reporting line
			Managers and cannot be privatised from them. This also cannot be shared
	    	with your peers or others in the company.
			Profile - This consists of generic information about you such as name,
		 	official contact details, department, etc. This is available for
		 	everyone to view across the organisation and cannot be privatized.
			Leaderboard - This displays your awards, accolades and achievements
		 	and can be privatized if you wish to do so. However, this cannot be
		 	privatised from your reporting line managers.""",



	def PLATFORM_UPDATE_PERFORMANCE(self):
		"""
	    Entity_type(update) = action_type , Entity_type(performance) = features.
	    Response when user requests to update their performance. Its an invalid request.
		"""
		return "Here is where you can.... "


	def PLATFORM_CREATE_PERFORMANCE(self):
		"""
		Entity_type(create) = action_type , Entity_type(performance) = features.
		Response when user requests to create their performance. Its an invalid request.
		"""
		return "You build your performance by performing well!"

	def PLATFORM_SEND_FEEDBACK(self):
		"""
	 	Entity_type(send) = action_type , Entity_type(feedback) = features.
		Response when user requests to send a feedback.
		"""
		return "Here is how you could send a feedback ......"

	def PLATFORM_UPDATE_FEEDBACK(self):
		"""
		Entity_type(update) = action_type , Entity_type(feedback) = features.
		Response when user requests to send a feedback.
		"""
		return "I'm sorry, you cannot update the feedback which you've already sent"

	def PLATFORM_CREATE_FEEDBACK(self):
		"""

		"""
		return "Here is how you could send a feedback...."

	# Maintain the names of intents created in dialogflow here as keys of the dictionary.
	# The values are the response to be sent to the user if there is a match for an entity.
	# This layer has to be replaced by a database instead of a dictionary based query.
	INTENT_RESPONSE_DICT = {
	# Response for all FAQ's
		"FAQ" : {
			 # Entity_type(unhappy) = emotions, Entity_type(feedback) = features.
			 # Response when user is unhappy with their feedback.
			 "unhappyfeedback": FAQ_UNHAPPY_FEEDBACK,

			 "happyfeedback" : FAQ_HAPPY_FEEDBACK
			},
			# Response table for all navigation help related queries
			"Platform exploration help": {
				                        # View queries for features.
							"goals" :      PLATFORM_GOALS_GENERIC_RESPONSE,

							"sign out":    PLATFORM_SIGNOUT_RESPONSE,

							"project":     PLATFORM_PROJECT_VIEW_PROJECT,

							"objective":   PLATFORM_OBJECTIVE_VIEW_RESPONSE,

							"leaderboard": PLATFORM_LEADERBOARD_RESPONSE,

							"progress":    PLATFORM_PROGRESS_RESPONSE,

							"profile":     PLATFORM_PROFILE_VIEW_RESPONSE,

							"performance": PLATFORM_PERFORMANCE_VIEW,

							"default":     PLATFORM_DEFAULT_RESPONSE,
							# Plain action type responses.
							"update":      PLATFORM_INSUFFICIENT_ACTION_TYPE_RESPONSE,
							# Entity_type(feedback) = features.
							# Response when user requests to update their performance
							"feedback":	   PLATFORM_FEEDBACK_VIEW,
							# Responses for query containing both features and action_type entity.
							"createobjective": PLATFORM_CREATE_OBJECTIVE,

							"updateobjective": PLATFORM_UPDATE_OBJECTIVE,

							"creategoals": PLATFORM_CREATE_GOAL,

							"updategoals": PLATFORM_UPDATE_GOALS,

							"createproject": PLATFORM_CREATE_PROJECT,

							"updateproject": PLATFORM_UPDATE_PROJECT,

							"updateprogress": PLATFORM_UPDATE_PROGRESS,

							"updateprofile": PLATFORM_UPDATE_PROFILE,

							"createprofile": PLATFORM_CREATE_PROFILE,

							"updateperformance": PLATFORM_UPDATE_PERFORMANCE,

							"createperformance": PLATFORM_CREATE_PERFORMANCE,

							"sendfeedback": PLATFORM_SEND_FEEDBACK,

							"updatefeedback": PLATFORM_UPDATE_FEEDBACK,

							"createfeedback": PLATFORM_CREATE_FEEDBACK,

						     }
		     }


	# Maintain the names of entities key's and values as dictionary here.
	# the entity  values are maintained as data structure type set.
	ENTITY_MAIN_TYPES = ["dosage", "med_type","duration", "any"]

	def return_main_entities(self):
		"""
		returns the sorted main entity types
		"""
		return sorted(self.ENTITY_MAIN_TYPES)

	def is_intent_exists(self, intent):
		"""

		Check from the INTENT_RESPONSE_DICT whether entry for given intent exists.

		"""
		if intent in self.INTENT_RESPONSE_DICT:
			return True
		else:
			return False

	def fetch_response(self, intent, entity):
		"""
		Fetch response for given intent entity combination from INTENT_RESPONSE_DICT.
		This has to be replaced with the database layer.
		"""
		if self.is_intent_exists(intent):
			if entity in self.INTENT_RESPONSE_DICT[intent]:
				result_func = self.INTENT_RESPONSE_DICT[intent][entity]
				return result_func(self)
			else:
				return self.INTENT_RESPONSE_DICT[intent]["default"](self)

		return None

	def return_default_response(self):
		"""
		Method to return the default answer
		"""
		return PLATFORM_DEFAULT_RESPONSE


class ParseDialogflowResponse:
	"""
	Class with methods for parsing the POST response body from Dialogflow
	"""

	def __init__(self, request):
		"""
		Initialize the dictionary with the POST body data from dialog flow.
		"""
		self.req_dict = self.get_dict_from_request(request)

	def get_dict_from_request(self, request):
		"""
		Return the POST request body as a dictionary.
		"""
		return json.loads(request.data)

	def get_intent(self):
		"""
	        Return the intent from the POST body dictionary of request from Dialogflow.
		This parsing is specific to request from dialog flow
		"""

		# returns None of the key is not found.
		if self.req_dict["result"].get("metadata"):
			self.intent = self.req_dict["result"]["metadata"].get("intentName")
			return self.intent

		self.intent = None
		return self.intent

	def get_entities(self):
		"""
		Retrun the key value pairs of entity types and values found in the user query.
		"""

		self.entity_key_values = self.req_dict["result"].get("parameters")
		return self.entity_key_values

	def did_small_talk_respond(self):
		"""
		Verify if small talk has responded to the query.
		Queries like "How old you?", "Who is your boss?" are answere by small talk.

		 if "smalltalk" in req_dict["result"]["action"] , this is hte key conditional check
		 to see if small talk has responsded to the query.
		"""
		if  self.req_dict["result"].get("action"):
			if "smalltalk" in self.req_dict["result"]["action"]:
				return True

		return False

	def fetch_small_talk_response(self):
		"""
		In case the user query matches the small talk question, the small talk response doesn't
		directly reach the user, it reaches the custom backend with the answer, it just has to be
		relayed back ot the user
		"""
		if self.did_small_talk_respond():
			fulfillment =  self.req_dict["result"].get("fulfillment")
			if fulfillment:
				return fulfillment.get("speech")

		return None


def send_apiapi_request(message):

	ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

	request = ai.text_request()

	request.session_id = "test"

	request.query = message

	response = json.loads(request.getresponse().read())


	print(response)
	return response

# Flask app should start in global layout
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
CORS(app)

@app.route('/')
def hello():
		return "Flask inside Docker!!"

@app.route('/healthz')
def healthz():
		return "Health check endpoint"

@app.route('/messages', methods=['POST'])
def messages():
	req_dict = json.loads(request.data)
	print(req_dict)
	resp = send_apiapi_request(req_dict["message"]["message"])

	bot_response = resp['result']['fulfillment']['speech']
	print(bot_response)
	if bot_response == "":
		bot_response = "Error response"

	res = makeWebhookResult("from server")
	res = json.dumps(res, indent=4)

	r = make_response(res)

	r.headers['Content-Type'] = 'application/json'
	return r

@app.route('/webhook', methods=['POST'])
def webhook():
	"""
	This is the webhook which will be invoked by dialogflow when an user interacts.
	The request contains POST data which will be similar to its format which can witnessed in https://goo.gl/BUZaVz
	Use it as a reference to parse any of its other fields in future.
	"""
	# Uncomment to get the JSON dump of the POST body from dialogflow.
	print("Request:")
	print(json.dumps(request.get_json(silent=True, force=True), indent=4))
	res = processRequest(request)
	res = json.dumps(res, indent=4)
    # Uncommnet the lines below to get the dump of the response.
    #print(res)

	# Send the repsonse back to the user.
	print("\nfinal response: " , res)
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r

def processRequest(req):
	"""
	Parse the request.
	Process the solution.
	Fetch the response string and return.
	"""
	# Parsing the POST request body into a dictionary for easy access.
	process_req = ParseDialogflowResponse(req)
	# Fetch intent.
	intent = process_req.get_intent()
	print("intent is: ", intent)
	# Fetch entity key values.

	request_dict = json.loads(request.data)

	request_str = request_dict["result"]["resolvedQuery"]
	params = request_dict["result"]["parameters"]
	print("The request query: ", request_str)
	entity_key_val = process_req.get_entities()
	prescription = {}
	parsed_prescription = []
	# Currently we can expect the queries to either one or two entity types.
	# This would be more when we have complex user interactions in the future.
	found = 0

	query_answer = IntentEntitiesMatch()

    # Iterate through all possible main entities.
	for main_entity in query_answer.return_main_entities():
		# If there's a match in list of entities and the entities from request
		# Parse the values and add them to the final result dictionary.
		if main_entity in entity_key_val:
			entity_value = entity_key_val[main_entity]
			if main_entity == "any":
				prescription["Medicine Name"] = entity_value

			elif main_entity == "duration":
				prescription["Duration of medicine intake"] = str(entity_value["amount"]) + " days"

			elif main_entity == "dosage":
				prescription["Medicine Dosage"] = entity_value
			elif main_entity == "med_type":
				prescription["Medicine Type"] = entity_value

	print("precription")
	print(prescription)

	# See if the given entity and intent have a match in our response dictionary.

	"""
	speech = query_answer.fetch_response(intent, entity_value)
	if speech is None:
	    speech = process_req.fetch_small_talk_response()
	if speech is None:
	    speech = query_answer.return_default_response()
	"""

	res = makeWebhookResult(json.dumps(prescription))

	print("response: ", res)
	return res


def makeWebhookResult(speech):
    """
    Construct the response for Dialogflow bot in a consumable way
    """

    return {
        "speech": speech,
        "displayText": speech,
        "source": "TIA TEST 1"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
