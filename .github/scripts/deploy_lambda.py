import os
import boto3
import zipfile
import shutil
import tempfile
import subprocess
import sys

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

def create_layer_zip(folder_name):
    layer_zip = f"{folder_name}_layer.zip"
    requirements_file = os.path.join(folder_name, "requirements.txt")

    if os.path.isfile(requirements_file):
        with tempfile.TemporaryDirectory() as temp_dir:
            python_dir = os.path.join(temp_dir, 'python')
            os.makedirs(python_dir)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file, "-t", python_dir])

            with zipfile.ZipFile(layer_zip, 'w') as zf:
                for root, _, files in os.walk(python_dir):
                    for file in files:
                        zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), python_dir))
        return layer_zip
    return None

def create_or_update_layer(client, layer_name, layer_zip, runtime='python3.8'):
    layer_arn = None
    try:
        response = client.publish_layer_version(
            LayerName=layer_name,
            Description=f"Lambda layer for {layer_name}",
            Content={'ZipFile': open(layer_zip, 'rb').read()},
            CompatibleRuntimes=[runtime],
        )
        layer_arn = response['LayerVersionArn']
    except Exception as e:
        print(f"Error creating Lambda layer: {e}")

    return layer_arn

def deploy_lambda(client, folder_name, zip_name, role_arn, runtime='python3.8', region='us-east-1'):
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
                Handler="index.lambda_handler",
                Code={'ZipFile': open(zip_name, 'rb').read()},
                Publish=True,
            )
        except Exception as e:
            print(f"Error creating Lambda function: {e}")

if __name__ == "__main__":
    repo_name = os.environ['REPO_NAME']
    client = boto3.client('lambda', region_name='ap-southeast-3')
    for folder_name in os.listdir():
        if os.path.isdir(folder_name) and not folder_name.startswith('.'):
            print(f"Processing folder {folder_name}")
            role_arn = get_role_arn_from_file(folder_name)
            if role_arn:
                print(f"Found role ARN for {folder_name}: {role_arn}")
                lambda_name = f"{repo_name}_{folder_name}"
                layer_name = f"{lambda_name}_layer"

                layer_zip = create_layer_zip(folder_name)
                if layer_zip:
                    print(f"Created layer zip for {folder_name}: {layer_zip}")
                    layer_arn = create_or_update_layer(client, layer_name, layer_zip, runtime='python3.8')
                    os.remove(layer_zip)
                else:
                    print(f"No requirements.txt found for {folder_name}, skipping layer creation.")
                    layer_arn = None

                zip_name = create_lambda_zip(folder_name)
                print(f"Created Lambda zip for {folder_name}: {zip_name}")
                deploy_lambda(client, lambda_name, zip_name, role_arn, layer_arn=layer_arn)
                os.remove(zip_name)
            else:
                print(f"Skipping {folder_name}: No role ARN found in .gitaction_properties file.")
