#!/usr/bin/python
# -*- coding: utf-8 -*-

# Importation des librairies
import cv2
import os
import numpy as np
import tensorflow as tf
import qi
import sys

# Détection de visages avec le modèle Caffe Model Zoo
prototxt_path = os.path.join('model_data/deploy.prototxt')
caffemodel_path = os.path.join('model_data/weights.caffemodel')
model = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)

#Chargement du modèle permettant de détecter le port du masque
modelMasque = tf.keras.models.load_model("QSTOMIT-MASQUE.model")

# Connexion avec le robot
session = qi.Session()
session.connect("tcp://ilisa.local:9559") # session.connect("tcp://ip:port")

# Connexion aux services du robot
camera = session.service("ALVideoDevice") # Cameras du robot
tts = session.service("ALTextToSpeech") # Permet au robot de parler

# Connexion à la camera haute
camera_top = camera.subscribeCamera("camera_top", 0, 2, 11, 30)
# subscribeCamera(surnom, id_camera, résolution (640x480), colour (RGB), fps)

# Note: On ne connaît pas la raison pour laquelle l'image se trouve dans l'espace
# BGR, même lorsque l'espace choisie est le RGB


while True:
    # Récuperation de l'image
    image = camera.getImageRemote(camera_top)

    # Traitement de l'image
    image = np.array(image[6])
    image = np.reshape(image, (480, 640, 3)) # Redimensionnement
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Change d'espace de couleur
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    model.setInput(blob)
    detections = model.forward() # Reconnaissance des visages
    h = image.shape[0]
    w = image.shape[1]

    # Comptoirs pour le dialogue du robot
    pM_counter = 0
    aM_counter = 0

    # Pour chaque détection de visage fait:
    for i in range(0, detections.shape[2]):
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        confidence = detections[0, 0, i, 2]

        # Si le code a plus d'un 50 pour cent de certitude:
        if (confidence > 0.5):
            frame = image[startY:endY, startX:endX]

            # Appel du modèle appris pour la detection de masque
            capture = cv2.resize(frame, (224, 224))
            capture = capture.reshape((1, capture.shape[0], capture.shape[1], capture.shape[2]))
            predict = modelMasque.predict(capture)

            # Le classificateur retrouve 1 pour le cas positif et 0 pour le négatif
            pasDeMasque = predict[0][0]
            avecMasque = predict[0][1]

            if (pasDeMasque > avecMasque): # Si la personne porte son masque
                pM_counter += 1

                # Décommenter pour afficher l'image et la débouguer
                # cv2.rectangle(image, (startX, startY), (endX, endY),(0, 0, 255), 2)
                # cv2.putText(image, "PAS DE MASQUE", (startX, startY-10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            else:
                aM_counter += 1

                # Décommenter pour afficher l'image et la débouguer
                # cv2.rectangle(image, (startX, startY), (endX, endY),(0, 255, 0), 2)
                # cv2.putText(image, "OK", (startX, startY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)


    # Affichage de l'image (décommenter pour débugger)
    # cv2.imshow('img', image)

    if pM_counter > 1: # Il y plus d'une personne sans masque dans un groupe
        tts.say("Il y a "+str(pM_counter)+" personnes sans masque, mettre votre masque s'il vous plaît")
    elif pM_counter == 1 and aM_counter > 0: # Il y a juste une personne sans masque dans un groupe
        tts.say("Il y a une personne sans masque, mettre votre masque s'il vous plaît")
    elif pM_counter == 1 and aM_counter == 0: # Il y a une personne seule que n'utilise pas son masque
        tts.say("Vous ne portez pas votre masque, mettre votre masque s'il vous plaît")
    elif pM_counter == 0 and aM_counter > 0: # Tous les personnes utilisent ses masques
        tts.say("Merci d'avoir utilisé votre masque")

    # Code en attente de mettre fin au programme
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break

# Déconnexion de la camera et du robot
camera.unsubscribe(camera_top)
session.close()
