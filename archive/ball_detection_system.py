import cv2
import numpy as np
from sklearn.cluster import KMeans
import warnings
import time
import ast


# Suppress specific KMeans warning (UserWarning related to MKL memory leak)
warnings.filterwarnings("ignore", category=UserWarning, message=".*KMeans is known to have a memory leak.*")


'''
This code detects the field and balls from the main camera.
To use setup, go to settings.txt and set: Setup: 1.
When booted in this mode then you can use trackbars to set the parameters for the: white balls, orange balls, field, ball size.
When satisfied with the parameters, click 's' to go to the next state.
When everythin has been setup you will enter final state where both ball detection and field detection are running. In this state you can also press 'p'
to print out the current balls detected.

Whenever you quit using 'q' the program will save your used parameters for next time in the settings.txt
'''

###########################################################################
# Functions
###########################################################################

# Function to do nothing (for trackbars)
def nothing(x):
    pass

# Ball detection function
def detect_ball(image, hsv, lower_white, upper_white, lower_orange, upper_orange, 
                param1, param2, min_radius, max_radius, min_x, max_x, min_y, max_y, num_cells):
    """Detects both white and orange balls and maps them to grid coordinates."""
    
    # Detect white ball
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    blurred_white = cv2.GaussianBlur(mask_white, (9, 9), 2)
    circles_white = cv2.HoughCircles(blurred_white, cv2.HOUGH_GRADIENT, 1, 20, param1=param1, param2=param2, minRadius=min_radius, maxRadius=max_radius)

    # Detect orange ball
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    blurred_orange = cv2.GaussianBlur(mask_orange, (9, 9), 2)
    circles_orange = cv2.HoughCircles(blurred_orange, cv2.HOUGH_GRADIENT, 1, 20, param1=param1, param2=param2, minRadius=min_radius, maxRadius=max_radius)

    detected_balls = []
    
    if circles_white is not None:
        circles_white = np.uint16(np.around(circles_white))
        for (x, y, r) in circles_white[0, :]:
            cv2.circle(image, (x, y), r, (255, 255, 255), 2)  # White circle
            
            # Map ball to grid
            grid_col = int(((x - min_x) / (max_x - min_x)) * num_cells)
            grid_row = int(((y - min_y) / (max_y - min_y)) * num_cells)
            

            ball_position = (grid_col, grid_row)
            cv2.putText(image, f"w({grid_col}, {grid_row})", (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            detected_balls.append(('white', ball_position))

    if circles_orange is not None:
        circles_orange = np.uint16(np.around(circles_orange))
        for (x, y, r) in circles_orange[0, :]:
            cv2.circle(image, (x, y), r, (0, 165, 255), 2)  # Orange circle
            
            # Map ball to grid
            grid_col = int(((x - min_x) / (max_x - min_x)) * num_cells)
            grid_row = int(((y - min_y) / (max_y - min_y)) * num_cells)

            ball_position = (grid_col, grid_row)
            cv2.putText(image, f"o({grid_col}, {grid_row})", (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            detected_balls.append(('orange', ball_position))

    return image, detected_balls

def detect_field(image, hsv, lower_orange_field, upper_orange_field, show_mask):
    """Detects the field using orange boundary markers, finds corners, and updates the grid."""
    
    # Detect field boundaries (orange color)
    mask = cv2.inRange(hsv, lower_orange_field, upper_orange_field)
    
    if show_mask == True:
        cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
        cv2.imshow("Mask", mask)

    # Edge detection
    edges = cv2.Canny(mask, 50, 150)
    dilated_edges = cv2.dilate(edges, None, iterations=1)
    lines = cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=10)

    # Find intersections
    intersection_points = []
    detected_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            detected_lines.append(((x1, y1), (x2, y2)))

        # Compute intersections between every pair of detected lines
        for i in range(len(detected_lines)):
            for j in range(i + 1, len(detected_lines)):
                x1, y1 = detected_lines[i][0]
                x2, y2 = detected_lines[i][1]
                x3, y3 = detected_lines[j][0]
                x4, y4 = detected_lines[j][1]

                # Compute intersection using the line intersection formula
                denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if denominator != 0:
                    intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
                    intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
                    intersection_points.append((int(intersect_x), int(intersect_y)))

    # Update field boundaries immediately if valid intersections are found
    if intersection_points:
        points = np.array(intersection_points)
        valid_points = points[
            (points[:, 0] > 0) & (points[:, 0] < image.shape[1]) &
            (points[:, 1] > 0) & (points[:, 1] < image.shape[0])
        ]
        if len(valid_points) > 3:
            kmeans = KMeans(n_clusters=4, n_init=10, random_state=42)
            kmeans.fit(valid_points)
            cluster_centers = kmeans.cluster_centers_

            # Sort corners into Top-left, Top-right, Bottom-left, Bottom-right
            sorted_corners = sorted(cluster_centers, key=lambda c: (c[1], c[0]))
            top_two = sorted(sorted_corners[:2], key=lambda c: c[0])
            bottom_two = sorted(sorted_corners[2:], key=lambda c: c[0])
            corners = {
                "Top Left": top_two[0],
                "Top Right": top_two[1],
                "Bottom Left": bottom_two[0],
                "Bottom Right": bottom_two[1],
            }

            # Define field boundaries
            min_x = min(c[0] for c in cluster_centers)
            max_x = max(c[0] for c in cluster_centers)
            min_y = min(c[1] for c in cluster_centers)
            max_y = max(c[1] for c in cluster_centers)

            cell_width = (max_x - min_x) / num_cells
            cell_height = (max_y - min_y) / num_cells

            return corners, min_x, max_x, min_y, max_y, cell_width, cell_height

    return None  # No update to field boundaries if conditions are not met

def save_settings(filename="settings.txt"):
    with open(filename, "w") as f:

        # Write comments at the top of the file
        f.write("# This file is used for the settings in the program\n")
        f.write("# It stores the last used values whenever you quit the program with 'q'\n")
        f.write("# You can also change these upon startup if needed\n\n")
        
        f.write("# If you want to use these values and not use the setup, Then set: Setup: 0\n")
        f.write("# If you want to use the setup and pick these values with the trackbars: Setup: 1\n\n")

        f.write(f"Setup: {setup}\n")
        f.write(f"Lower White HSV: {lower_white.tolist()}\n")
        f.write(f"Upper White HSV: {upper_white.tolist()}\n")
        f.write(f"Lower Orange HSV: {lower_orange.tolist()}\n")
        f.write(f"Upper Orange HSV: {upper_orange.tolist()}\n")
        f.write(f"Field Lower Orange HSV: {lower_orange_field.tolist()}\n")
        f.write(f"Field Upper Orange HSV: {upper_orange_field.tolist()}\n")
        f.write(f"Num Cells: {num_cells}\n")
        f.write(f"Param1: {param1}\n")
        f.write(f"Param2: {param2}\n")
        f.write(f"Min Radius: {min_radius}\n")
        f.write(f"Max Radius: {max_radius}\n")

def load_settings_from_file(filename="settings.txt"):
    settings = {}
    try:
        with open(filename, "r") as file:
            lines = file.readlines()

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Split key-value pairs
                key, value = line.split(":")
                key = key.strip()
                value = value.strip()

                # Convert list values using ast.literal_eval for safety
                if value.startswith("[") and value.endswith("]"):
                    settings[key] = ast.literal_eval(value)  # safely evaluate the list
                else:
                    # Convert to integer if possible
                    try:
                        settings[key] = int(value)
                    except ValueError:
                        settings[key] = value  # Otherwise, it's a string (this is unlikely for your settings)
    except Exception as e:
        print(f"Error reading settings from file: {e}")

    return settings

###########################################################################
# Global variables (imported from settings.txt)
###########################################################################
settings = load_settings_from_file()

setup = settings.get("Setup", "Not found")
lower_white = np.array(settings.get("Lower White HSV", [0, 0, 0]))
upper_white = np.array(settings.get("Upper White HSV", [0, 0, 0]))
lower_orange = np.array(settings.get("Lower Orange HSV", [0, 0, 0]))
upper_orange = np.array(settings.get("Upper Orange HSV", [0, 0, 0]))
lower_orange_field = np.array(settings.get("Field Lower Orange HSV", [0, 0, 0]))
upper_orange_field = np.array(settings.get("Field Upper Orange HSV", [0, 0, 0]))

state = "white" if settings.get("Setup", 0) == 1 else "final"

num_cells = settings.get("Num Cells", "Not found")

param1 = settings.get("Param1", "Not found")
param2 = settings.get("Param2", "Not found")
min_radius = settings.get("Min Radius", "Not found")
max_radius = settings.get("Max Radius", "Not found")

last_update_time = 0
field_detection_result = None

first_time_white = True
first_time_orange = True
first_time_ball = True
first_time_field = True

###########################################################################
# Start of main program
###########################################################################


# Camera init
print("Opening connection to camera")
cap = cv2.VideoCapture(0)  # Use 0 for default camera
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Camera loop
print("Starting camera loop")
stop = False
while not stop:
    ret, new_frame = cap.read()
    if not ret:
        print("Can't receive frame. Exiting ...")
        break

    # Quit the program when 'q' is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        save_settings()  # Save settings to file
        stop = True

    # State machine:
    if state == "white":
        # White ball setup state    
        if first_time_white:
            # Create windows for white ball parameter setup
            cv2.namedWindow("White Ball Binary Mask", cv2.WINDOW_NORMAL)

            # Move windows
            cv2.moveWindow("White Ball Binary Mask", 0, 0)
            
            # Create trackbars in the same window as the binary mask
            cv2.createTrackbar("Hue min", "White Ball Binary Mask", lower_white[0], 180, nothing)
            cv2.createTrackbar("Hue max", "White Ball Binary Mask", upper_white[0], 180, nothing)
            cv2.createTrackbar("Sat min", "White Ball Binary Mask", lower_white[1], 255, nothing)
            cv2.createTrackbar("Sat max", "White Ball Binary Mask", upper_white[1], 255, nothing)
            cv2.createTrackbar("Bright min", "White Ball Binary Mask", lower_white[2], 255, nothing)
            cv2.createTrackbar("Bright max", "White Ball Binary Mask", upper_white[2], 255, nothing)

            # Mark first-time setup
            first_time_white = False
        
        # Get HSV trackbar positions for white ball
        lower_h = cv2.getTrackbarPos("Hue min", "White Ball Binary Mask")
        upper_h = cv2.getTrackbarPos("Hue max", "White Ball Binary Mask")
        lower_s = cv2.getTrackbarPos("Sat min", "White Ball Binary Mask")
        upper_s = cv2.getTrackbarPos("Sat max", "White Ball Binary Mask")
        lower_v = cv2.getTrackbarPos("Bright min", "White Ball Binary Mask")
        upper_v = cv2.getTrackbarPos("Bright max", "White Ball Binary Mask")
        
        lower_white = np.array([lower_h, lower_s, lower_v])
        upper_white = np.array([upper_h, upper_s, upper_v])

        # Convert frame to HSV
        hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)

        # Show the binary mask for white ball
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        cv2.imshow("White Ball Binary Mask", mask_white)

        if key == ord('s'):
            # Destroy windows and go to next state
            cv2.destroyWindow("White Ball Binary Mask")
            state = "orange"

    elif state == "orange":
        # Orange ball setup
        if first_time_orange:
            # Create windows for orange ball parameter setup
            cv2.namedWindow("Orange Ball Binary Mask", cv2.WINDOW_NORMAL)

            # Move windows
            cv2.moveWindow("Orange Ball Binary Mask", 0, 0)

            # Create trackbars in the same window as the binary mask
            cv2.createTrackbar("Hue min", "Orange Ball Binary Mask", lower_orange[0], 180, nothing)
            cv2.createTrackbar("Hue max", "Orange Ball Binary Mask", upper_orange[0], 180, nothing)
            cv2.createTrackbar("Sat min", "Orange Ball Binary Mask", lower_orange[1], 255, nothing)
            cv2.createTrackbar("Sat max", "Orange Ball Binary Mask", upper_orange[1], 255, nothing)
            cv2.createTrackbar("Bright min", "Orange Ball Binary Mask", lower_orange[2], 255, nothing)
            cv2.createTrackbar("Bright max", "Orange Ball Binary Mask", upper_orange[2], 255, nothing)

            # Mark first-time setup
            first_time_orange = False

        # Get HSV trackbar positions for orange ball
        lower_h = cv2.getTrackbarPos("Hue min", "Orange Ball Binary Mask")
        upper_h = cv2.getTrackbarPos("Hue max", "Orange Ball Binary Mask")
        lower_s = cv2.getTrackbarPos("Sat min", "Orange Ball Binary Mask")
        upper_s = cv2.getTrackbarPos("Sat max", "Orange Ball Binary Mask")
        lower_v = cv2.getTrackbarPos("Bright min", "Orange Ball Binary Mask")
        upper_v = cv2.getTrackbarPos("Bright max", "Orange Ball Binary Mask")
        
        lower_orange = np.array([lower_h, lower_s, lower_v])
        upper_orange = np.array([upper_h, upper_s, upper_v])

        # Convert frame to HSV
        hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)

        # Show the binary mask for orange ball
        mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
        cv2.imshow("Orange Ball Binary Mask", mask_orange)

        if key == ord('s'):
            # Save HSV parameters and go to ball detection state
            cv2.destroyWindow("Orange Ball Binary Mask")
            state = "field"

    elif state == "field":
        # Field detection state (Not working. You only get here if you change the state to something different manually)
        if first_time_field:
            cv2.namedWindow("Field Detection", cv2.WINDOW_NORMAL)

            # Trackbars for field color detection
            cv2.createTrackbar("Hue min", "Field Detection", lower_orange_field[0], 180, nothing)
            cv2.createTrackbar("Hue max", "Field Detection", upper_orange_field[0], 180, nothing)
            cv2.createTrackbar("Sat min", "Field Detection", lower_orange_field[1], 255, nothing)
            cv2.createTrackbar("Sat max", "Field Detection", upper_orange_field[1], 255, nothing)
            cv2.createTrackbar("Bright min", "Field Detection", lower_orange_field[2], 255, nothing)
            cv2.createTrackbar("Bright max", "Field Detection", upper_orange_field[2], 255, nothing)

            first_time_field = False

        # Get trackbar positions
        lower_h = cv2.getTrackbarPos("Hue min", "Field Detection")
        upper_h = cv2.getTrackbarPos("Hue max", "Field Detection")
        lower_s = cv2.getTrackbarPos("Sat min", "Field Detection")
        upper_s = cv2.getTrackbarPos("Sat max", "Field Detection")
        lower_v = cv2.getTrackbarPos("Bright min", "Field Detection")
        upper_v = cv2.getTrackbarPos("Bright max", "Field Detection")

        lower_orange_field = np.array([lower_h, lower_s, lower_v])
        upper_orange_field = np.array([upper_h, upper_s, upper_v])

        current_time = time.time()

        # Only update detection every 2 seconds (this is changed to 0.5 when setup is done)
        if current_time - last_update_time >= 0.5:
            hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)
            field_detection_result = detect_field(new_frame, hsv, lower_orange_field, upper_orange_field, show_mask=True)

            if field_detection_result is not None:
                corners, min_x, max_x, min_y, max_y, cell_width, cell_height = field_detection_result
                last_update_time = current_time  # Reset timer

        # If we have a valid field_detection_result (even if it's not updated), use it
        if field_detection_result is not None:
            corners, min_x, max_x, min_y, max_y, cell_width, cell_height = field_detection_result

            # Draw red dots at the corners
            for corner_name, corner_coords in corners.items():
                cv2.circle(new_frame, (int(corner_coords[0]), int(corner_coords[1])), 7, (0, 255, 255), -1)  # Red filled circle

            # Draw grid
            for i in range(1, num_cells):
                x = min_x + i * cell_width
                y = min_y + i * cell_height
                cv2.line(new_frame, (int(x), int(min_y)), (int(x), int(max_y)), (255, 255, 255), 1)
                cv2.line(new_frame, (int(min_x), int(y)), (int(max_x), int(y)), (255, 255, 255), 1)

            # Draw rectangle around the field
            cv2.rectangle(new_frame, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 0, 0), 2)

        # Show the updated frame
        cv2.imshow('Field Detection', new_frame)

        if key == ord('s'):
            # Save HSV parameters and go to ball detection state
            cv2.destroyWindow("Field Detection")
            cv2.destroyWindow("Mask")
            state = "ball"

    elif state == "ball":
        # Ball detection state
        if first_time_ball:
            # Create window and move window for ball detection
            cv2.namedWindow("Ball Detection", cv2.WINDOW_GUI_NORMAL)
            cv2.moveWindow("Ball Detection", 0, 0)

            # Trackbars for HoughCircles parameters
            cv2.createTrackbar("p1", "Ball Detection", param1, 50, nothing)
            cv2.createTrackbar("p2", "Ball Detection", param2, 50, nothing)
            cv2.createTrackbar("Ball min", "Ball Detection", min_radius, 50, nothing)
            cv2.createTrackbar("Ball max", "Ball Detection", max_radius, 50, nothing)

            first_time_ball = False
        
        param1 = max(1, cv2.getTrackbarPos("p1", "Ball Detection"))
        param2 = max(1, cv2.getTrackbarPos("p2", "Ball Detection"))
        min_radius = cv2.getTrackbarPos("Ball min", "Ball Detection")
        max_radius = cv2.getTrackbarPos("Ball max", "Ball Detection")

        hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)

        # Detect both white and orange balls
        new_frame, detected_balls = detect_ball(new_frame, hsv, lower_white, upper_white, lower_orange, upper_orange, param1, param2, min_radius, max_radius, min_x, max_x, min_y, max_y, num_cells)

        # Show the final detection window
        cv2.imshow("Ball Detection", new_frame)

        if key == ord('s'):
            # Save HSV parameters and go to ball detection state
            cv2.destroyWindow("Ball Detection")
            state = "final"

    elif state == "final":

        current_time = time.time()

        # Only update detection every 0.5 second
        if current_time - last_update_time >= 0.5:
            hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)
            field_detection_result = detect_field(new_frame, hsv, lower_orange_field, upper_orange_field, show_mask=False)

            if field_detection_result is not None:
                corners, min_x, max_x, min_y, max_y, cell_width, cell_height = field_detection_result   # Field
                last_update_time = current_time  # Reset timer

        # If we have a valid field_detection_result (even if it's not updated), use it
        if field_detection_result is not None:
            corners, min_x, max_x, min_y, max_y, cell_width, cell_height = field_detection_result   # Field

            # Draw red dots at the corners
            for corner_name, corner_coords in corners.items():
                cv2.circle(new_frame, (int(corner_coords[0]), int(corner_coords[1])), 7, (0, 255, 255), -1)  # Red filled circle

            # Draw grid
            for i in range(1, num_cells):
                x = min_x + i * cell_width
                y = min_y + i * cell_height
                cv2.line(new_frame, (int(x), int(min_y)), (int(x), int(max_y)), (255, 255, 255), 1)
                cv2.line(new_frame, (int(min_x), int(y)), (int(max_x), int(y)), (255, 255, 255), 1)

            # Draw rectangle around the field
            cv2.rectangle(new_frame, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 0, 0), 2)
        
        # Detect balls
        new_frame, detected_balls = detect_ball(new_frame, hsv, lower_white, upper_white, lower_orange, upper_orange, param1, param2, min_radius, max_radius, min_x, max_x, min_y, max_y, num_cells)
        
        if key == ord('p'):
            # Print the detected balls
            print("Detected Balls:", detected_balls)
        

        cv2.imshow("Final Detection", new_frame)


        

cv2.destroyAllWindows()
cap.release()
