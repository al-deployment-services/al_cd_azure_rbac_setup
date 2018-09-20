Wrapper for Azure RBAC Deployment in Alert Logic (Threat Manager)
=================
This script will create the Azure Role-based access control (RBAC) link setup for Threat Manager and Cloud Defender deployments. Two components that will be created:

- Creates a new credential object in Sources service according to Azure AD user credential schema
- Creates a new Azure environment object in Sources service according to Azure environment source schema with reference to credential created by the script

Requirements
------------
* Alert Logic Account ID (CID)
* Credentials to Alert Logic Cloud Insight (this call is made from Cloud Insight API endpoint)
* Custom RBAC role and user created in Azure (https://docs.alertlogic.com/gsg/Azure-environ-in-Cloud-Defender.htm)
* Assign created RBAC role to the created user in the scope of the subscription

Deployment Mode
---------------
* ADD = will create the Threat Manager/Cloud Defender RBAC role link via deployments
* DEL = will delete the existing Threat Manager/Cloud Defender deployment in the UI
* LIST = will list all deployments associated with an Account ID

Sample ADD Usage
----------------
Replace the parameters to match your environment and run this command ::

	python al_cd_azure_rbac_setup.py ADD --user first.last@company.com --pswd MyCloudInsightPassword --cid 10000 --sub_id b69ed5af-5843-4b90-bf1f-7b8f81731bbd --ad_name companyname.onmicrosoft.com --ad_user user@companyname.onmicrosoft.com --ad_pswd P@s$w0rd --cred TestArgCred --env TestEnv --dc defender-us-ashburn

Arguments
----------
	-h, --help       	 show this help message and exit
	--user USER      	 User name / email address for API Authentication
	--pswd PSWD      	 Password for API Authentication
	--cid CID        	 Alert Logic Customer CID as target for this deployment
	--sub_id AZURE   	 Azure subscription ID where the RBAC is created
	--ad_name AD_NAME 	 Active Directory default name
	--ad_user AD_USER 	 Username of a user that represents Alert Logic in Active Directory Tenant
	--ad_pswd AD_PSWD 	 Password of a user that represents Alert Logic in Active Directory Tenant
	--cred CRED      	 Credential name, free form label, not visible in Alert Logic UI
	--env ENV        	 Environment name, will be displayed in Alert Logic UI under Deployment
	--dc DC          	 Alert Logic Data center assignment, i.e. defender-us-denver, defender-us-ashburn or defender-uk-newport

Take note of the output from the script, you will need to record the Environment ID if you wish to delete it later using this script (see below)

Sample DEL Usage
----------------
Replace the parameters to match your environment and run this command ::

	python al_cd_azure_rbac_setup.py DEL --user first.last@company.com --pswd MyCloudInsightPassword --cid 10000 --envid 833CE538-04B4-441F-8318-DBFCB9C9B39C

Arguments
----------
	-h, --help   	show this help message and exit
	--user USER  	User name / email address for API Authentication
	--pswd PSWD  	Password for API Authentication
	--cid CID       Alert Logic Customer CID as target for this deployment
	--envid ENVUD   Environment ID that you wish to delete

Exit Code
----------
If you going to integrate this script to another orchestration tool, you can use the exit code to detect the status:

* 0 = script run successfully
* 1 = missing or invalid argument
* 2 = environment issue such as invalid environment id or invalid credentials
* 3 = timeout

WARNING: This script will not revert back any changes due to timeout, any commands / API calls that it executed prior to timeout will run until completed, even if the script exit due to timeout.
