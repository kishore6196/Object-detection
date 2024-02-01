# Object-detection
Object detection in gaming (Minecraft)
[poster.pptx](https://github.com/kishore6196/Object-detection/files/14077665/poster.pptx)
Tutorial
Copy and paste the Yolov4 Tiny Folder
Run dataset generator.py To take in game screenshots and paste it in Images folder
Run label dataset.ipynb to shuffle the images and annotate the data using Makesense.ai online platform Line 7 creates the Annotated image folder and zip the the file for training
Upload the all these files in the drive and start the yolo-training.ipynb process using google collab change runtime to GPU
after training get the training weights and run Yolo model.py file 
output you get two windows one object detection and other the game
This project works in real time
Absctract
This project concerns itself with the development and implementation of an object detection model tailored for the unique environment of the video game Minecraft. In this game, players interact with a variety of entities, including animals and hostile mobs, all depicted in a distinct, block-style graphical interface. The primary challenge lies in accurately identifying and classifying these entities in real-time, a task that traditional object detection models often struggle with due to the game's unconventional visual presentation.
Data collection from Minecraft gameplay sessions was done for this study. An extensive collection of in-game photos was acquired, covering a range of settings, illumination styles, and creature kinds. This dataset's careful annotation of many entities made it a strong training ground for the detection model. To improve the model's accuracy and versatility, extra care was taken to guarantee a broad representation of entities in varied states and interactions.
The results are encouraging, as the model shows a notable capacity to identify and distinguish between different types of creatures and animals in the world of Minecraft. Although the model works well in typical scenarios, in more complicated scenarios, including crowded environments or unique lighting conditions, its accuracy varies. The precision and recall metrics, crucial indicators of the model's performance, suggest that while the model is reliable, there's room for improvement in specific contexts.
Future work will concentrate on improving the model's accuracy, particularly in difficult settings. This includes increasing the diversity of the training dataset and maybe including advanced machine learning techniques such as transfer learning or data augmentation. Real-time implementations and optimization for in-game performance will also be important areas of work. The goal is to create a model that not only enhances the gaming experience through intelligent entity detection but also contributes to the broader field of object detection in stylized, virtual environments. Also, by object detection guiding players to their objectives and understanding the player behaviours.  
