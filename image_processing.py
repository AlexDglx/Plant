import cv2
import numpy as np


def blur_and_sharpen_background(image_path, output_path, low_threshold=0, high_threshold=215, blur_strength=(7, 7), alpha=0.5):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not read image.")
        return
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use Canny edge detection to find edges
    edges = cv2.Canny(gray, low_threshold, high_threshold)
    
    # Dilate edges to make the mask more inclusive of the subject
    kernel = np.ones((5,5), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Create a mask where edges are white and everything else is black
    mask = np.zeros_like(image)
    mask[dilated_edges != 0] = [255, 255, 255]
    
    # Invert mask to get the background mask
    mask_inv = cv2.bitwise_not(mask)
    
    # Blur the entire image
    blurred = cv2.GaussianBlur(image, blur_strength, 0)
    
    # Sharpen the subject with a softened kernel
    kernel_sharpening = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
    sharpened = cv2.filter2D(image, -1, kernel_sharpening)
    
    # Blend the original image with the sharpened image
    softened_sharpened = cv2.addWeighted(image, alpha, sharpened, 1 - alpha, 0)
    
    # Combine the sharpened subject and the blurred background using the masks
    foreground = cv2.bitwise_and(softened_sharpened, mask)
    background = cv2.bitwise_and(blurred, mask_inv)
    final = cv2.add(foreground, background)
    
    # Save the output image
    cv2.imwrite(output_path, final)
    
    # Display the images for debugging (optional)
    cv2.imshow('Original Image', image)
    cv2.imshow('Edges', edges)
    cv2.imshow('Dilated Edges', dilated_edges)
    cv2.imshow('Mask', mask)
    cv2.imshow('Mask Inverse', mask_inv)
    cv2.imshow('Blurred Image', blurred)
    cv2.imshow('Sharpened Image', sharpened)
    cv2.imshow('Softened Sharpened Image', softened_sharpened)
    cv2.imshow('Final Image', final)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage:
if __name__ == "__main__":
    image_path = '/Users/adegallaix/Downloads/abi photo.jpg'  # Replace with your image path
    output_path = '/Users/adegallaix/Downloads/abi photo-cg.jpg'  # Replace with your desired output path
    blur_and_sharpen_background(image_path, output_path)