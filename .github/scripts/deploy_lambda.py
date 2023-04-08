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

def deploy_lambda(function_name, zip_name, runtime='python3.8', region='us-east-1'):
    client = boto3.client('lambda', region_name=region)

    try:
        response = client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Handler=f"{function_name}.lambda_handler",
            Code={'ZipFile': open(zip_name, 'rb').read()},
            Publish=True,
        )
    except Exception as e:
        print(f"Error creating Lambda function: {e}")

if __name__ == "__main__":
    for folder_name in os.listdir():
        if os.path.isdir(folder_name) and folder_name != '.github':
            zip_name = create_lambda_zip(folder_name)
            deploy_lambda(folder_name, zip_name)
            os.remove(zip_name)
