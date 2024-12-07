import boto3
import os
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = os.getenv("AWS_SERVICE_NAME")
REGION_NAME = os.getenv("AWS_REGION_NAME")
ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
ACCESS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")


import boto3
from botocore.exceptions import ClientError

client = boto3.client(service_name=SERVICE_NAME, region_name=REGION_NAME,
                      aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=ACCESS_SECRET_KEY)

# Set the model ID, e.g., Claude 3 Haiku.
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Start a conversation with the user message.
user_message = """Use the following pieces of content to answer the question at the end. Strictly follow these rules:
1. If the answer is not within the context knowledge, kindly state that you do not know in a very brief resposne in a sentence.
2. If you find the answer, craft a detailed and concise response to the question at the end. Aim for a summary, ensuring that your explanation is thorough.

Context:
Frog pose: 6 benefits and how to do mandukasana | HealthShots Frog pose: 6 benefits and how to do Mandukasana Frog pose: 6 benefits and how to do Mandukasana Frog pose helps to improve posture and enhance overall sleep. Here are all the benefits of the mandukasana, and how to perform it. Frog Pose targets the inner thigh muscles. Image courtesy: Adobe Stock Published: 4 Aug 2024, 08:59 am IST 231 Medically Reviewed by Does your job require prolonged sitting, leading to bad posture and back pain? Including a yoga pose like the frog pose can be helpful. Also known as mandukasana, it is a powerful yoga pose that helps to alleviate back pain and increase mobility. While it may appear simple, this asana is a good way to enhance overall mobility. Regular practice of this pose may also help with digestion, and muscle strength, and offer several other benefits. The frog pose is also considered a preparatory pose for more advanced hip-opening asanas. Here’s how to do it properly and all the benefits it has to offer. What is frog pose or mandukasana? The name mandukasana comes from Sanskrit: “manduka” meaning frog and “asana” meaning pose. The final position resembles the position of a frog. “It is a deep hip opener and a powerful pose for enhancing flexibility and strength. Frog pose is an excellent exercise to incorporate into your yoga practice after a warm-up,” says yoga expert . Frog pose has many health benefits. Image courtesy: Adobe Stock Benefits of frog pose or mandukasana Here are some of the notable benefits of the frog pose: 1. Opens up your hips and improves mobility Regular practice of yoga helps to and aids in balancing your body, as found in a study published in the . Similarly, frog poses can help to relieve chronic muscle tension caused by spending long hours at a desk or in your vehicle. Regular practice of this pose can improve hip mobility and flexibility, allowing you to sit cross-legged on the floor more easily. Take a Poll What is your favourite way to stay active during a working day? Desk exercises Walking breaks Chair squats Climbing stairs 2. Reduces lower back pain A study published in the found that doing yoga daily can help . So, if you are looking for ways to ease back pain, practising the frog pose can help. This pose lengthens the spine and releases tension in the hips. It helps to alleviate lower back pain and stiffness. You may also like 3. Keeps stress at bay Regular yoga increases focus, reduces , and boosts overall mental health, according to a study published in the International Journal of Yoga. The frog pose has a soothing effect on the mind. It can relieve tension by providing a sense of calm and help relax you. 4. Improves digestion The frog pose improves digestion and by applying gentle pressure on the abdomen. “It stimulates the digestive organs and encourages regular bowel movements,” explains Dr Hansaji. 5. Enhances blood circulation Frog pose can enhance blood flow to the pelvis, improving general circulation and possibly alleviating menstruation discomfort. “This can be especially beneficial for people who sit or stand for long periods, as it minimises swelling and the risk of developing blood clots,” says the expert. 6. Improves sleep Doing frog pose will help you sleep better and get you relief from everyday stress. According to a study published in the discovered that yoga can minimise sleep onset delay, enhance sleeping period, and improve sleep quality. Frog pose promotes relaxation and reduces stress, making it easier to fall asleep and improving overall sleep quality. How to do frog pose or mandukasana? Here is a complete guide on how to do frog pose or mandukasana, as explained by yoga expert . Keep an idea of your risk of weight-related issues. Step 1: Start with keeping your hands and knees in a tabletop position. Step 2: Slowly widen your knees apart, moving them toward the edges of your mat. Step 3: Turn your toes outward and flex your feet so the inner edges of your feet are on the floor. Step 4: Lower down onto your forearms, keeping them parallel to each other. Step 5: Slide your hips back slightly, keeping your ankles in line with your knees. Step 6: Keep your spine neutral, neither arched or rounded. Step 7: Hold the pose for 30 seconds to 5 minutes, depending on your comfort level. Note: Practice for 1-2 minutes (as per individual comfort), breathing normally. Breathing pattern to perform frog pose In this pose, focus on deep, slow breaths: Inhale deeply through your nose, letting your belly expand. Exhale gently through your nose, feeling your belly constrict. Aim for a 1:2 inhale-to-exhale ratio (for example, 4 counts in, 8 counts out). Continue to breathe in this pattern throughout the position, allowing it to deepen your relaxation. Side effects of frog pose or mandukasana Mandukasana is a beneficial asana but may not be suitable for everyone due to certain limitations and contraindications which are as follows, as explained by yoga expert Himalayan Siddha Akshar. Digestive problems: It can cause discomfort if you have eaten recently. Headaches: Some people might experience increased head pressure. Back pain: If you have back issues, this pose might worsen it. Knee and hip pain: Overdoing the pose can strain these joints. Not suitable for everyone: Pregnant women, people with high blood pressure, or recent abdominal surgery should avoid it. It might not be safe for pregnant women to perform the frog pose. Image courtesy: Freepik Practising mandukasana under these conditions may exacerbate existing issues or lead to discomfort, so it is important to consult a healthcare provider or a qualified yoga teacher if any of these concerns apply. Things to keep in mind! While yoga asanas are generally considered safe, it is essential to avoid overexertion during practice. Mindful execution with proper alignment is key for ensuring safety in most individuals. However, it is imperative to attune to your body’s signals, adapt postures when necessary, and consult a qualified teacher, especially if you have specific health concerns or conditions. Get Latest Updates on , , , 231 About the Author Shruti Bhattacharya is a content writer and editor for over 2 years. She specialises in writing on a variety of topics such as wellness, lifestyle, beauty, technology and fashion. Her current focus is on creating factually correct and informative stories for readers. ... Related Stories Photo Gallery Next Story TRENDING TOPICS SUBSCRIBE TO OUR WELLNESS NEWSLETTER Get your Daily Dose of Wellness in your Inbox ! DOWNLOAD APP FOLLOW US ON LATEST STORIES DISEASES

Question: Tell me all teh benefits of using this??
Helpful Answer:
"""
conversation = [
    {
        "role": "user",
        "content": [{"text": user_message}],
    }
]

try:
    # Send the message to the model, using a basic inference configuration.
    streaming_response = client.converse_stream(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 4096, "temperature": 0.5, "topP": 0.9},
    )

    # Extract and print the streamed response text in real-time.
    for chunk in streaming_response["stream"]:
        if "contentBlockDelta" in chunk:
            text = chunk["contentBlockDelta"]["delta"]["text"]
            print(text, end="")

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)


