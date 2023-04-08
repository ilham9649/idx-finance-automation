import os
import boto3
import zipfile

def create_lambda_zip(folder_name):
    zip_name = f"{folder_name}.zip"
    with zipfile.ZipFile(zip_name, 'w') as zf:
        for root, _, files in os.walk(folder_name):
            for file in files:
                zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_name))
    return zip_name

def lambda_exists(client, function_name):
    try:
        response = client.get_function(FunctionName=function_name)
        return True
    except Exception as e:
        return False

def update_lambda_code(client, function_name, zip_name):
    try:
        response = client.update_function_code(
            FunctionName=function_name,
            ZipFile=open(zip_name, 'rb').read(),
            Publish=True,
        )
    except Exception as e:
        print(f"Error updating Lambda function code: {e}")

def get_role_arn_from_file(folder_name, filename='.gitaction_properties'):
    role_arn = None
    file_path = os.path.join(folder_name, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                if key == 'ROLE_ARN':
                    role_arn = value
                    break
    return role_arn

def deploy_lambda(folder_name, zip_name, role_arn, runtime='python3.8', region='us-east-1'):
    client = boto3.client('lambda', region_name=region)

    if lambda_exists(client, folder_name):
        print(f"Updating existing Lambda function: {folder_name}")
        update_lambda_code(client, folder_name, zip_name)
    else:
        print(f"Creating new Lambda function: {folder_name}")
        try:
            response = client.create_function(
                FunctionName=folder_name,
                Runtime=runtime,
                Role=role_arn,
                Handler=f"{folder_name}.lambda_handler",
                Code={'ZipFile': open(zip_name, 'rb').read()},
                Publish=True,
            )
        except Exception as e:
            print(f"Error creating Lambda function: {e}")

if __name__ == "__main__":
    repo_name = os.environ['REPO_NAME']
    for folder_name in os.listdir():
        if os.path.isdir(folder_name) and not folder_name.startswith('.'):
            role_arn = get_role_arn_from_file(folder_name)
            if role_arn:
                lambda_name = f"{repo_name}_{folder_name}"
                zip_name = create_lambda_zip(folder_name)
                deploy_lambda(lambda_name, zip_name, role_arn)
                os.remove(zip_name)
            else:
                print(f"Skipping {folder_name}: No role ARN found in .gitaction_properties file.")
