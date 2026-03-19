# -*- coding: utf-8 -*-
import argparse
import torch
import torchvision.models
import torchvision.transforms as transforms
from PIL import Image

class imagePrediction():

    def __init__(self, path):
        self.path = path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.value = None
        image = Image.open(path)
        model = torchvision.models.resnet50()
        # model.avgpool = nn.AdaptiveAvgPool2d(1) # for any size of the input
        model.fc = torch.nn.Linear(in_features=2048, out_features=1)
        model.load_state_dict(torch.load('model/model-resnet50.pth', map_location=self.device)) 
        model.eval().to(self.device)
        self.predict(image, model)

    def prepare_image(self, image):
        if image.mode != 'RGB':
            image = image.convert("RGB")
        Transform = transforms.Compose([
                transforms.Resize([224,224]),      
                transforms.ToTensor(),
                ])
        image = Transform(image)   
        image = image.unsqueeze(0)
        return image.to(self.device)

    def predict(self, image, model):
        image = self.prepare_image(image)
        with torch.no_grad():
            preds = model(image)
        self.value = preds.item()
        #print(f'Item: {self.path} | Popularity Score: {preds.item():.2f}')

    def getValue(self):
        return self.value