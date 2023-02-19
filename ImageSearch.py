from io import BytesIO
import os
from PIL import Image, ImageDraw
import requests

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import urllib.request

'''
RESOURCES: References: 
Computer Vision SDK: https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-computervision/?view=azure-python
Computer Vision documentation: https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/
Computer Vision API: https://westus.dev.cognitive.microsoft.com/docs/services/5cd27ec07268f6c679a3e641/operations/56f91f2e778daf14a499f21b
'''
'''

Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = '92fa44dc-01c2-4bdd-80d8-cb76b6454824'
endpoint = 'https://imagesearchhackathon.cognitiveservices.azure.com/'

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


lst = []
#lst.append("https://moderatorsampleimages.blob.core.windows.net/samples/sample16.png")
taggedImgs = []
#This is the one that generates tags for images 
def generateTags(remote_image_url):

    #image_features = ['objects','tags']
    tags = []
    remote_image_features = ['categories','brands','color','objects','tags']
    if 'www' not in remote_image_url:
        local_image_objects = open(remote_image_url, "rb")
        results_remote = computervision_client.analyze_image(local_image_objects , remote_image_features)
    else:
        results_remote = computervision_client.analyze_image(remote_image_url , remote_image_features)

    
    #print("===== Analyze an image - remote =====")
    # Select the visual feature(s) you want.
    #results_remote = computervision_client.analyze_image(remote_image_url, image_features)
    
    #remote_image_details = [Details.celebrities,Details.landmarks]

    # Call API with URL and features. Only One API Call per new image here. to save it 
    #results_remote = computervision_client.analyze_image(remote_image_url , remote_image_features)

    # Print results with confidence score
    #print("Categories from remote image: ")
    if (len(results_remote.categories) == 0):
        print("No categories detected.")
    else:
        for category in results_remote.categories:
            if category.score * 100 > 85:
                tags.append(category.name)

    # Detect colors
    # Print results of color scheme
    if results_remote.color.is_bw_img > 0.5:
        tags.append("black and white")
    tags.append(results_remote.color.accent_color)
    tags.append(results_remote.color.dominant_colors)

    # Detect image type
    # Prints type results with degree of accuracy
    if results_remote.image_type.clip_art_type >= 2:
        tags.append("clip art")

    if results_remote.image_type.line_drawing_type > 0:
        tags.append("line art")

    # Detect brands
    #print("Detecting brands in remote image: ")
    if len(results_remote.brands) > 0:
        for brand in results_remote.brands:
            if brand.confidence * 100 > 85:
                tags.append(brand.name)

    # Detect objects
    # Print detected objects results with bounding boxes
    #print("Detecting objects in remote image:")
    if (len(results_remote.tags) > 0):
        for tag in results_remote.tags:
            if tag.confidence * 85 > 100:
                tags.append(tag.name)


    #Add this along with url
    return tags

    



#image search func
def imageSearch(tagTotal):
    tags = tagTotal.split(",")
    images = []
    for tag in tags:
        for img in taggedImgs:
            url = img[0]
            tagsLst = img[1]
            if tag in tagsLst:
                filename = url.split('/')[-1]
                images.append(urllib.request.urlretrieve(remote_image_url, filename))

    return images


    



'''MAIN FUNCTION'''
option = input("Enter A for adding an image, S for Searching an image, and any other key to exit: ")
while option[0].upper == 'A' or option[0].upper == 'S':
    if option[0].upper == 'A':
        remote_image_url = input("Enter image url or name of an in the local repository:")
        if remote_image_url not in list:
            list.append(remote_image_url)
            #filename = link.split('/')[-1]
            #urllib.request.urlretrieve(remote_image_url, filename)
            tags = generateTags(remote_image_url) #This function generates the tags only once.
            taggedImgs.append([remote_image_url, tags])
        else:
            print("Sorry, It's already there!")
    elif option[1] == 'S':
        tagTotal = input("Enter tags separated by commas: ")
        withoutSpaces = tagTotal.replace(",", "")
        withoutSpaces = tagTotal.replace(" ", "")
        if withoutSpaces.isalpha():
            print(imageSearch(tagTotal)) #returns all images that fit the tags.  
        else:
            print("Please only add spaces, commas and letters!")
    option = input("Enter A for adding an image, S for Searching an image, and any other key to exit: ")

