import urllib.request
import os
import subprocess
import boto3
import os.path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')


def downloadFromS3(strBucket, strKey, strFile):
    s3_client = boto3.client('s3')
    s3_client.download_file(strBucket, strKey, strFile)

def uploadToS3(strBucket, strLocalPath, strRemotePath):
    s3_client = boto3.client('s3')
    s3_client.upload_file(strLocalPath, strBucket, strRemotePath)


def handler(event, context):
    try:
        mediafilepath = '/tmp/inputmedia.jpg'
        resultFilePath = '/tmp/results.json'
        predictionFilePath = '/tmp/predictions.png'

        # commandStr = './darknet detect cfg/yolov3.cfg {} {} > /tmp/results.txt'
        commandStr = './darknet detector test ./cfg/coco.data ./cfg/yolov4.cfg {} {} -out {} -i 0 -thresh 0.25'

        if ('mediatype' in event):
            if (event['mediatype'].lower() == 'videonote'):
                mediafilepath = '/tmp/inputmedia.mp4'
                commandStr = './darknet detector demo cfg/coco.data cfg/yolov4.cfg {} {} -i 0 -thresh 0.25 > {}'

        strWeightFile = '/tmp/yolov.weights'
        print(os.path.isfile(strWeightFile))
        # strKey = 'darknet/yolov3.weights'
        # strBucket = 'myqueuecounter'
        strKey = 'LunaYOLO/yolov4.weights'
        strBucket = 'lunappmbucket'
        if not os.path.isfile(strWeightFile):
            downloadFromS3(strBucket, strKey, strWeightFile)
        print(strWeightFile)

        if ('imagelink' in event):
            urllib.request.urlretrieve(event['imagelink'], mediafilepath)
        else:
            strBucket = 'myqueuecounter'
            strKey = 'darknet/street.jpg'
            downloadFromS3(strBucket, strKey, mediafilepath)
        print(mediafilepath)

        command = commandStr.format(
            # command='./darknet classifier predict cfg/coco.data cfg/yolov3.cfg {} {} > /tmp/results.txt'.format(
            strWeightFile,
            mediafilepath,
            resultFilePath
        )

        print(command)
        output = None

        try:
            print('Start')
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            print('Finish')
            print(output)

            print('Is predictions file is created: ')
            print(os.path.isfile(predictionFilePath))

            print('Upload File to S3')
            strBucketPrediction = 'lunappmbucket'
            uploadToS3(strBucketPrediction,predictionFilePath,"predictions.png")
            print('Upload Done')
        except subprocess.CalledProcessError as e:
            print('Error')
            print((e.output))
    except Exception as e:
        print('Error e')
        print(e)
        raise e
    results_file = open(resultFilePath, "r")
    # results = results_file.readlines()
    results = results_file.read()
    results_file.close()


    print(results)
    return results
