# Code à mettre sur la boîte Python

# Importation des librairies
import cv2
import os
import numpy as np
import tensorflow as tf

# Détection de visages avec le modèle Caffe Model Zoo
prototxt_path = os.path.join('resources/deploy.prototxt')
caffemodel_path = os.path.join('resources/weights.caffemodel')
model = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)

#Chargement du modèle permettant de détecter le port du masque
modelMasque = tf.keras.models.load_model("resources/QSTOMIT-MASQUE.model")


class MyClass(GeneratedClass):
    def __init__(self):
        try: # disable autoBind
          GeneratedClass.__init__(self, False)
        except TypeError: # if NAOqi < 1.14
          GeneratedClass.__init__( self )
        self.camera = ALProxy("ALVideoDevice")

    # Fonction exécutée lorsque le programme est initialisé
    def onLoad(self):
        # subscribeCamera(surnom, cameraIndex, resolution, colorSpace, fps)
        # 0 -> camera haute
        # 2 -> résolution 480x640
        # 11 -> RGB
        self.camera_top = self.camera.subscribeCamera("camera_top", 0, 2, 11, 15)

        # Note: On ne connaît pas la raison pour laquelle l'image se trouve dans l'espace
        # BGR, même lorsque l'espace choisie est le RGB

    # Fonction exécutée lorsque le programme est terminé
    def onUnload(self):
        # Déconnexion de la camera
        self.camera.unsubscribe(self.camera_top)

    # Fonction exécutée lorsque l'entrance "onStart" est stimulée
    def onInput_onStart(self):
        while True:
            # Récuperation de l'image
            image = self.camera.getImageRemote(self.camera_top)
            # Fonction avec le traitement de l'image
            self.image_processing(image)
            # Code en attente de mettre fin au programme
            k = cv2.waitKey(30) & 0xff
            if k==27:
                break

    # Fonction exécutée lorsque l'entrance "onStop" est stimulée
    def onInput_onStop(self):
        self.onUnload()
        self.onStopped()

    # Fonction pour le traitement de l'image
    def image_processing(self, image):
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

                #Appel du modèle appris pour la detection de masque
                capture = cv2.resize(frame, (224, 224))
                capture = capture.reshape((1, capture.shape[0], capture.shape[1], capture.shape[2]))
                predict = modelMasque.predict(capture)
                pasDeMasque = predict[0][0]
                avecMasque = predict[0][1]

                if (pasDeMasque > avecMasque):
                    pM_counter += 1
                else:
                    aM_counter += 1


        if pM_counter > 1: # Il y plus d'une personne sans masque dans un groupe
            self.useMasque("Il y a "+str(pM_counter)+" personnes sans masque, mettre votre masque s'il vous plaît")
        elif pM_counter == 1 and aM_counter > 0: # Il y a juste une personne sans masque dans un groupe
            self.useMasque("Il y a une personne sans masque, mettre votre masque s'il vous plaît")
        elif pM_counter == 1 and aM_counter == 0: # Il y a une personne seule que n'utilise pas son masque
            self.useMasque("Vous ne portez pas votre masque, mettre votre masque s'il vous plaît")
        elif pM_counter == 0 and aM_counter > 0: # Tous les personnes utilisent ses masques
            self.useMasque("Merci d'avoir utilisé votre masque")
        return
