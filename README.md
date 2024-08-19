# Image-analysis-
Python GUI application for Image analysis using Google Gemini API


Image Analysis Application
Overview
This project is a Python-based GUI application that allows users to analyze images using the Google Gemini API. The application provides features such as image selection, live image capture via webcam, text analysis, saving results, and history management. It is designed with a modern, user-friendly interface using PyQt5.

Features
Image Selection: Select images from your local file system for analysis.
Live Image Capture: Capture images directly from your webcam for real-time analysis.
Text Analysis: Analyze the content of the images using the Google Gemini API.
Save Image with Analysis: Save the analyzed image with a text overlay of the results.
History Management: Keep track of all analyzed images and their results.
Export Results: Export the analysis results to a text file.
Dark/Light Mode: Toggle between dark and light themes for the application.
Font Size Adjustment: Customize the font size of the output text for better readability.
Installation
Prerequisites
Python 3.7 or higher
pip (Python package manager)
A Google Gemini API key
Step-by-Step Installation
Clone the Repository

git clone https://github.com/Sherin-SEF-AI/Image-analysis-.git
cd Image-analysis-
Install Required Python Packages

Install the necessary packages using the following command:

bash
Copy code
pip install -r requirements.txt
Set Up the API Key

Replace the placeholder YOUR_API_KEY in the main.py file with your actual Google Gemini API key:


API_KEY = "YOUR_API_KEY"
Run the Application

Run the application using the following command:

Usage
Select or Capture an Image:

Click on "Select Image" to choose an image from your local system.
Click on "Capture Image" to use your webcam to capture an image.
Analyze the Image:

Enter a custom prompt if desired, then click "Identify Image" to analyze the image content.
View and Manage Results:

The analysis result will be displayed in the text area. You can save the image with the analysis text overlay, export the results to a text file, or manage the history of analyzed images.
Toggle Dark/Light Mode:

Use the "Dark Mode" checkbox to switch between themes.
Adjust Font Size:

Use the font size dropdown to adjust the text output size in the results area.
Future Enhancements
Visual Analysis: Implement visual analysis features alongside text analysis.
Multi-language Support: Add support for analyzing images in different languages.
Customizable Themes: Allow users to fully customize the UI themes.
