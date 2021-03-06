# Wrapper for Azure RBAC Deployment in Alert Logic (Threat Manager and Cloud Defender)
# Contributor: mmohamed@alertlogic.com
#
# Sample usage:
# Get the help menu:
#	python al_cd_azure_rbac_setup.py --help
#
# Deploy and create new RBAC link with name "TestEnv" with data center residency "Ashburn":
#	python al_cd_azure_rbac_setup.py ADD --user first.last@company.com --pswd MyCloudInsightPassword --cid 10000 --sub_id b69ed5af-5843-4b90-bf1f-7b8f81731bbd --ad_name companyname.onmicrosoft.com --ad_user user@companyname.onmicrosoft.com --ad_pswd P@s$w0rd --cred TestArgCred --env TestEnv --dc defender-us-ashburn
#
# Destroy the RBAC link with environment ID specificed:
#   python al_cd_azure_rbac_setup.py DEL --user first.last@company.com --pswd MyCloudInsightPassword --cid 10000 --envid 833CE538-04B4-441F-8318-DBFCB9C9B39C

from __future__ import print_function
import json, requests, datetime, sys, argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

#suppres warning for certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#API Endpoint
YARP_URL="api.cloudinsight.alertlogic.com"
ALERT_LOGIC_CI_SOURCE = "https://api.cloudinsight.alertlogic.com/sources/v1/"

#exit code standard:
#0 = OK
#1 = argument parser issue
#2 = environment issue such as invalid environment id, invalid password, or invalid scope
#3 = timeout
EXIT_CODE = 0

def authenticate(user, paswd, yarp):
	#Authenticate with CI yarp to get token
	url = yarp
	user = user
	password = paswd
	r = requests.post('https://{0}/aims/v1/authenticate'.format(url), auth=(user, password), verify=False)
	if r.status_code != 200:
		sys.exit("Unable to authenticate %s" % (r.status_code))
	account_id = json.loads(r.text)['authentication']['user']['account_id']
	token = r.json()['authentication']['token']
	return token

def prep_credentials(cred_name, ad_name, ad_user, ad_pswd):
	#Setup dictionary for credentials payload
	RESULT = {}
	RESULT['credential']  = {}
	RESULT['credential']['name'] = str(cred_name)
	RESULT['credential']['type'] = "azure_ad_user"
	RESULT['credential']['azure_ad_user'] = {}
	RESULT['credential']['azure_ad_user']['active_directory_id'] = str(ad_name)
	RESULT['credential']['azure_ad_user']['username'] = str(ad_user)
	RESULT['credential']['azure_ad_user']['password'] = str(ad_pswd)
	return RESULT

def post_credentials(token, payload, target_cid):
	#Call API with method POST to create new credentials, return the credential ID
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/credentials/"
	REQUEST = requests.post(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False, data=payload)
	print ("Create Credentials Status : " + str(REQUEST.status_code), str(REQUEST.reason))
	if REQUEST.status_code == 201:
		RESULT = json.loads(REQUEST.text)
	else:
		RESULT = {}
		RESULT['credential']  = {}
		RESULT['credential']['id'] = "n/a"
	return RESULT


def prep_source_environment(sub_id, cred_id, environment_name, defender_location):
	#Setup dictionary for environment payload
	RESULT = {}
	RESULT['source']  = {}
	RESULT['source']['config'] = {}
	RESULT['source']['config']['azure'] = {}
	RESULT['source']['config']['azure']['subscription_id'] = str(sub_id)
	RESULT['source']['config']['azure']['credential'] = {}
	RESULT['source']['config']['azure']['credential']['id'] = str(cred_id)
	RESULT['source']['config']['azure']['defender_location_id'] = str(defender_location)
	RESULT['source']['config']['azure']['defender_support'] = True
	RESULT['source']['config']['azure']['discover'] = True
	RESULT['source']['config']['azure']['scan'] = False
	RESULT['source']['config']['collection_method'] = "api"
	RESULT['source']['config']['collection_type'] = "azure"
	RESULT['source']['config']['deployment_mode'] = "automatic"
	RESULT['source']['enabled'] = True
	RESULT['source']['name'] = str(environment_name)
	RESULT['source']['product_type'] = "outcomes"
	RESULT['source']['tags'] = []
	RESULT['source']['type'] = "environment"
	return RESULT

def post_source_environment(token, payload, target_cid):
	#Call API with method POST to create new environment
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/sources/"
	REQUEST = requests.post(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False, data=payload)
	print ("Create Environment Status : " + str(REQUEST.status_code), str(REQUEST.reason))
	if REQUEST.status_code == 201:
		RESULT = json.loads(REQUEST.text)
	else:
		RESULT = {}
		RESULT['source'] = {}
		RESULT['source']['id'] = "n/a"
	return RESULT

def list_source_environments(token, target_cid):
	#Get the source environment detail
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/sources/"
	REQUEST = requests.get(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False)

	print ("Retrieving Environment info status : " + str(REQUEST.status_code), str(REQUEST.reason), file=sys.stderr)
	if REQUEST.status_code == 200:
		RESULT = json.loads(REQUEST.text)
	else:
		RESULT = {}
		RESULT['source'] = {}
		RESULT['source']['id'] = "n/a"
	return RESULT

def del_source_environment(token, target_env, target_cid):
	#Delete the specified environment by environment ID and CID
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/sources/" + target_env
	REQUEST = requests.delete(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False)
	print ("Delete Environment Status : " + str(REQUEST.status_code), str(REQUEST.reason))

def del_source_credentials(token, target_cred, target_cid):
	#Delete the specified credentials by credentials ID and CID
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/credentials/" + target_cred
	REQUEST = requests.delete(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False)
	print ("Delete Credentials Status : " + str(REQUEST.status_code), str(REQUEST.reason))

def get_source_environment(token, target_env, target_cid):
	#Get the source environment detail
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/sources/" + target_env
	REQUEST = requests.get(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False)

	print ("Retrieving Environment info status : " + str(REQUEST.status_code), str(REQUEST.reason))
	if REQUEST.status_code == 200:
		RESULT = json.loads(REQUEST.text)
	else:
		RESULT = {}
		RESULT['source'] = {}
		RESULT['source']['id'] = "n/a"
	return RESULT

def failback(token, cred_id, target_cid):
	#Failback, delete credentials if create environment failed
	API_ENDPOINT = ALERT_LOGIC_CI_SOURCE + target_cid + "/credentials/" + cred_id
	REQUEST = requests.delete(API_ENDPOINT, headers={'x-aims-auth-token': token}, verify=False)
	print ("Delete Credentials Status : " + str(REQUEST.status_code), str(REQUEST.reason))
	print ("Failback completed")

#MAIN MODULE
if __name__ == '__main__':
	EXIT_CODE=0

	parent_parser = argparse.ArgumentParser()
	subparsers = parent_parser.add_subparsers(help="Select mode", dest="mode")
	#Add parser for both ADD and DELETE mode
	add_parser = subparsers.add_parser("ADD", help="Create new environment")
	del_parser = subparsers.add_parser("DEL", help="Delete environment")
	list_parser = subparsers.add_parser("LIST", help="List environments")

	#Parser argumetn for ADD
	add_parser.add_argument("--user", required=True, help="User name / email address for API Authentication")
	add_parser.add_argument("--pswd", required=True, help="Password for API Authentication")
	add_parser.add_argument("--cid", required=True, help="Alert Logic Customer CID as target for this deployment")
	add_parser.add_argument("--sub_id", required=True, help="Azure subscription ID where the RBAC is created")
	add_parser.add_argument("--ad_name", required=True, help="Active Directory default name")
	add_parser.add_argument("--ad_user", required=True, help="Username of a user that represents Alert Logic in Active Directory Tenant")
	add_parser.add_argument("--ad_pswd", required=True, help="Password of a user that represents Alert Logic in Active Directory Tenant")
	add_parser.add_argument("--cred", required=True, help="Credential name, free form label, not visible in Alert Logic UI")
	add_parser.add_argument("--env", required=True, help="Environment name, will be displayed in Alert Logic UI under Deployment")
	add_parser.add_argument("--dc", required=True, help="Alert Logic Data center assignment, i.e. defender-us-denver, defender-us-ashburn or defender-uk-newport")

	#Parser argumetn for DEL
	del_parser.add_argument("--user", required=True, help="User name / email address for API Authentication")
	del_parser.add_argument("--pswd", required=True, help="Password for API Authentication")
	del_parser.add_argument("--cid", required=True, help="Alert Logic Customer CID where the environment belongs")
	del_parser.add_argument("--envid", required=True, help="Environment ID that you wish to remove")

	#Parser argumetn for LIST
	list_parser.add_argument("--user", required=True, help="User name / email address for API Authentication")
	list_parser.add_argument("--pswd", required=True, help="Password for API Authentication")
	list_parser.add_argument("--cid", required=True, help="Alert Logic Customer CID where the environment belongs")

	try:
		args = parent_parser.parse_args()
	except:
		EXIT_CODE = 1
		sys.exit(EXIT_CODE)

	#Set argument to variables
	if args.mode == "ADD":

		EMAIL_ADDRESS = args.user
		PASSWORD = args.pswd
		TARGET_CID = args.cid
		TARGET_AZURE_SUBSCRIPTION = args.sub_id
		TARGET_AD_NAME = args.ad_name
		TARGET_AD_USER = args.ad_user
		TARGET_AD_PASS = args.ad_pswd
		TARGET_CRED_NAME = args.cred
		TARGET_ENV_NAME = args.env
		TARGET_DEFENDER = args.dc

	elif args.mode == "DEL":

		EMAIL_ADDRESS = args.user
		PASSWORD = args.pswd
		TARGET_CID = args.cid
		TARGET_ENV_ID = args.envid

	elif args.mode == "LIST":

		EMAIL_ADDRESS = args.user
		PASSWORD = args.pswd
		TARGET_CID = args.cid

	print ("### Starting script - " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + " - Deployment Mode = " + str(args.mode) + " ###\n", file=sys.stderr)

	#Authenticate with Cloud Insight and retrieve token
	try:
		TOKEN = str(authenticate(EMAIL_ADDRESS, PASSWORD, YARP_URL))
	except:
		print ("### Cannot Authenticate - check user name or password ###\n")
		print ("\n### Script stopped - " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + "###\n")
		EXIT_CODE = 2
		sys.exit(EXIT_CODE)

	if args.mode == "ADD":

		#Create credentials using the IAM role ARN and external ID
		CRED_PAYLOAD = prep_credentials(TARGET_CRED_NAME, TARGET_AD_NAME, TARGET_AD_USER, TARGET_AD_PASS)
		CRED_RESULT = post_credentials(TOKEN, str(json.dumps(CRED_PAYLOAD, indent=4)), TARGET_CID)
		CRED_ID = str(CRED_RESULT['credential']['id'])

		if CRED_ID != "n/a":
			print ("Cred ID : " + CRED_ID)
			ENV_PAYLOAD = prep_source_environment(TARGET_AZURE_SUBSCRIPTION, CRED_ID, TARGET_ENV_NAME, TARGET_DEFENDER)
			ENV_RESULT = post_source_environment(TOKEN, str(json.dumps(ENV_PAYLOAD, indent=4)), TARGET_CID)
			ENV_ID = str(ENV_RESULT['source']['id'])

			if ENV_ID != "n/a":
				print ("Env ID : " + ENV_ID)
				print ("\nCloud Defender Azure RBAC created successfully")
			else:
				EXIT_CODE=2
				print ("Failed to create environment source, see response code + reason above, starting fallback ..")
				failback(TOKEN, CRED_ID, TARGET_CID)

		else:
			EXIT_CODE=2
			print ("Failed to create credentials, see response code + reason above, stopping ..")

	elif args.mode == "LIST":
		SOURCE_RESULT = list_source_environments(TOKEN, TARGET_CID)
		print(json.dumps(SOURCE_RESULT))

	elif args.mode == "DEL":

		#Check if the provided Environment ID exist and valid
		SOURCE_RESULT = get_source_environment(TOKEN, TARGET_ENV_ID, TARGET_CID)

		if SOURCE_RESULT["source"]["id"] != "n/a":
			TARGET_CRED_ID = SOURCE_RESULT["source"]["config"]["azure"]["credential"]["id"]
			print ("Env ID : " + TARGET_ENV_ID)
			print ("Credential ID : " + TARGET_CRED_ID)

			#Delete the environment and credentials associated with that environment
			del_source_environment(TOKEN, TARGET_ENV_ID, TARGET_CID)
			del_source_credentials(TOKEN, TARGET_CRED_ID, TARGET_CID)

		else:
			EXIT_CODE=2
			print ("Failed to find the environment ID, see response code + reason above, stopping ..")

	print ("\n### Script stopped - " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + "###\n", file=sys.stderr)
	sys.exit(EXIT_CODE)
