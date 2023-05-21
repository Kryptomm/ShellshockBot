import cv2

video_path = 'D://Programmieren//Python//ShellshockBot//sonstiges//gravity_vid.mp4'
output_folder = 'D://Programmieren//Python//ShellshockBot//sonstiges//frames//'

# Open the video file
video = cv2.VideoCapture(video_path)

# Initialize variables
frame_count = 0
success = True

# Iterate through the frames of the video
while success:
    # Read the next frame
    success, frame = video.read()

    if success:
        # Save the frame as an image
        image_path = output_folder + f"frame_{frame_count}.jpg"
        cv2.imwrite(image_path, frame)
        
    frame_count += 1

# Release the video file
video.release()
