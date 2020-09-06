#  Setup AWS cloud resources

## Prerequisite

- Python 3.6 or above

## Setup cloud resources for autonomous surveillance demo

Install AWS CDK and deploy the stack.

```bash
npm install -g aws-cdk
cd path/to/your/autonomous-surveillance-demo/cloud
pip3 install -r requirements.txt
cdk deploy
```

The result will be like below, please note the `S3Bucket` and `CollectionID`.

```bash
Outputs:
AutonomousSurveillanceDemoStack.S3Bucket = autonomoussurveillancede-collectionbucket12345689-0123456789
AutonomousSurveillanceDemoStack.CollectionID = autonomous-surveillance-demo-collection
AutonomousSurveillanceDemoStack.GreengrassSystemdLambda = AutonomousSurveillanceDem-GreengrassResourceSystem-ABCDFEGHIJK
```

## Register faces in the collection

Create `faces` directory on your laptop and add face pictures with the file names like `alice.jpg` or `bob.png`.

Set `BUCKET_NAME` and `COLLECTION_ID` environmental variables with the values noted in the previous step.

```bash
export BUCKET_NAME=REPLACE_WITH_YOUR_BUCKET_NAME  # (e.g. autonomoussurveillancede-collectionbucket12345689-0123456789)
export COLLECTION_ID=autonomous-surveillance-demo-collection
```

Copy the face pictures and register them into the collection.

```bash
cd faces

aws s3 cp ./* s3://$BUCKET_NAME/

for key in $(aws s3 ls s3://$BUCKET_NAME/ | awk '{print $4}'); do
  name=$(echo $key | sed 's/\.[^\.]*$//')
  echo "index: $key"
  aws rekognition index-faces --collection-id $COLLECTION_ID \
  --image "S3Object={Bucket=$BUCKET_NAME,Name=$key}" \
  --external-image-id $name \
  --max-faces=1
done
```

## Setup AWS IoT Greengrass

- Create Greengrass group named `autonomous-surveillance-NN` (NN is number) on AWS IoT Greengrass console and download `hash-setup.tar.gz`.
- `hash-setup.tar.gz` will be used in the [robot setup process](../robot/README.md)
- Add `AutonomousSurveillanceDemoStack.GreengrassSystemdLambda` function created by CDK to the Greengrass group.
- Create a subscription from AWS Cloud to the lambda function above with the topic name `autonomous-surveillance/cmd/gg`.
