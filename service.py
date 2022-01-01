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


def handler(event, context):
    try:
        imgfilepath = '/tmp/inputimage.jpg'

        print(os.path.isfile('/tmp/yolov3.weights'))
        strWeightFile = '/tmp/yolov3.weights'
        strKey = 'darknet/yolov3.weights'
        strBucket = 'myqueuecounter'
        if not os.path.isfile('/tmp/yolov3.weights'):
            downloadFromS3(strBucket, strKey, strWeightFile)
        print(strWeightFile)

        if ('imagelink' in event):
            urllib.request.urlretrieve(event['imagelink'], imgfilepath)
            print(imgfilepath)
        else:
            strBucket = 'myqueuecounter'
            strKey = 'darknet/street.jpg'
            downloadFromS3(strBucket, strKey, imgfilepath)
        print(imgfilepath)

        command = './darknet detect cfg/yolov3.cfg {} {} > /tmp/results.txt'.format(
            # command='./darknet classifier predict cfg/coco.data cfg/yolov3.cfg {} {} > /tmp/results.txt'.format(
            strWeightFile,
            imgfilepath
        )

        print(command)
        output = None

        try:
            print('Start')
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            print('Finish')
            # print(output)
        except subprocess.CalledProcessError as e:
            print('Error')
            print((e.output))
    except Exception as e:
        print('Error e')
        print(e)
        raise e
    results_file = open("/tmp/results.txt", "r")
    results = results_file.readlines()
    results_file.close()
    print(results)
    return results
