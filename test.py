import cv2

# Load the pre-trained Haar Cascade model for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the image from the file
# img = cv2.imread(r'C:\Users\roman\Downloads\selected-image (1).jpg')
img = cv2.imread(r'C:\Users\roman\Downloads\face.jpg')

# Convert the image to grayscale for better accuracy in face detection
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Use the detectMultiScale method to detect faces
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

# Check if faces are detected
if len(faces) > 0:
    print("Faces detected!")
    # Draw rectangles around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Display the image with detected faces
    cv2.imshow("Faces", img)
    cv2.waitKey(0)  # Wait for any key to close the window
    cv2.destroyAllWindows()
else:
    print("No faces detected.")
