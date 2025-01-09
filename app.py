import streamlit as st
from groq import Groq
from PIL import Image
import json
import pandas as pd
from datetime import datetime
import io
import base64

from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Initialize Groq client and add to session state
if 'groq_client' not in st.session_state:
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        st.session_state.groq_client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.error(f"Error initializing Groq API: {str(e)}")
        st.session_state.groq_client = None


# Add nutritional preferences and restrictions to session state
if 'dietary_preferences' not in st.session_state:
    st.session_state.dietary_preferences = []
if 'food_allergies' not in st.session_state:
    st.session_state.food_allergies = []

def get_nutrition_response(prompt, pregnancy_month, preferences=None, allergies=None):
    """Get AI response specifically for nutrition queries"""
    try:
        if st.session_state.groq_client is None:
            return "Error: Groq API client not initialized"

        context = f"""You are a maternal nutrition expert. The user is {pregnancy_month} months pregnant.
        Dietary preferences: {preferences if preferences else 'None'}
        Food allergies: {allergies if allergies else 'None'}

        Provide nutritional advice that:
        1. Is safe for pregnancy
        2. Meets increased nutritional needs for the specific pregnancy month
        3. Avoids any listed allergens
        4. Respects dietary preferences
        5. Includes specific food suggestions and portions
        """

        completion = st.session_state.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return completion.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def get_symptom_assessment_response(prompt, pregnancy_month):
    """Get AI response specifically for symptom assessment queries"""
    try:
        if st.session_state.groq_client is None:
            return "Error: Groq API client not initialized"

        context = f"""You are a virtual doctor. The patient is {pregnancy_month} months pregnant.
        Provide a detailed assessment including:
        1. Possible causes
        2. Whether this is normal for their stage of pregnancy
        3. Recommended actions
        4. When to seek immediate medical attention
        """

        completion = st.session_state.groq_client.chat.completions.create(
            model="llama3-8b-8192",  # or your preferred Groq model
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return completion.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def nutritionist_menu():
    st.title("Nutritionist - Your Maternal Nutrition Expert")
    st.header("Maternal Nutrition Guide")

    # Sidebar for preferences and restrictions
    with st.sidebar:
        st.subheader("Dietary Preferences")
        st.session_state.dietary_preferences = st.multiselect(
            "Select your dietary preferences:",
            ["Vegetarian", "Vegan", "Halal", "Kosher", "Gluten-Free", "Dairy-Free"]
        )

        st.session_state.food_allergies = st.multiselect(
            "Select food allergies:",
            ["Nuts", "Dairy", "Eggs", "Soy", "Shellfish", "Wheat", "Fish"]
        )

    # Main nutrition interface
    tabs = st.tabs(["Meal Planner", "Nutrition Chat", "General Guidelines"])

    # Meal Planner Tab
    with tabs[0]:
        st.subheader("Personalized Meal Plan Generator")

        col1, col2 = st.columns(2)
        with col1:
            pregnancy_month = st.slider("Months of Pregnancy:", 1, 9)
        with col2:
            meal_type = st.selectbox(
                "Meal Type:",
                ["Full Day Plan", "Breakfast", "Lunch", "Dinner", "Snacks"]
            )

        if st.button("Generate Meal Plan"):
            prompt = f"Create a {meal_type.lower()} meal plan for someone {pregnancy_month} months pregnant."
            response = get_nutrition_response(
                prompt,
                pregnancy_month,
                st.session_state.dietary_preferences,
                st.session_state.food_allergies
            )
            st.write(response)

    # Nutrition Chat Tab
    with tabs[1]:
        st.subheader("Chat with Nutrition Assistant")

        # Display chat history
        for message in st.session_state.get('nutrition_chat_history', []):
            if message["role"] == "user":
                st.write("You:", message["content"])
            else:
                st.write("Nutritionist:", message["content"])

        # Chat input
        user_question = st.text_input("Ask about nutrition during pregnancy:")
        pregnancy_month = st.slider("Current month of pregnancy:", 1, 9, key="chat_pregnancy_month")

        if st.button("Ask"):
            if user_question:
                if 'nutrition_chat_history' not in st.session_state:
                    st.session_state.nutrition_chat_history = []

                # Add user message to history
                st.session_state.nutrition_chat_history.append(
                    {"role": "user", "content": user_question}
                )

                # Get AI response
                response = get_nutrition_response(
                    user_question,
                    pregnancy_month,
                    st.session_state.dietary_preferences,
                    st.session_state.food_allergies
                )

                # Add AI response to history
                st.session_state.nutrition_chat_history.append(
                    {"role": "assistant", "content": response}
                )

                st.experimental_rerun()

    # General Guidelines Tab
    with tabs[2]:
        st.subheader("Nutrition Guidelines by Trimester")

        trimester = st.selectbox(
            "Select Trimester:",
            ["First Trimester (Months 1-3)",
             "Second Trimester (Months 4-6)",
             "Third Trimester (Months 7-9)"]
        )

        # Show trimester-specific guidelines
        if trimester == "First Trimester (Months 1-3)":
            st.write("""
            ### First Trimester Nutrition Guidelines
            - Focus on folate-rich foods
            - Small, frequent meals to manage nausea
            - Stay hydrated
            - Key nutrients: Folic acid, Iron, Vitamin B6

            **Recommended Foods:**
            - Leafy greens
            - Whole grains
            - Lean proteins
            - Citrus fruits
            """)

        elif trimester == "Second Trimester (Months 4-6)":
            st.write("""
            ### Second Trimester Nutrition Guidelines
            - Increased caloric needs
            - Focus on calcium and vitamin D
            - Protein-rich foods
            - Omega-3 fatty acids

            **Recommended Foods:**
            - Dairy products
            - Fatty fish (low-mercury)
            - Lean meats
            - Nuts and seeds
            """)

        else:
            st.write("""
            ### Third Trimester Nutrition Guidelines
            - Higher protein needs
            - Iron-rich foods
            - Smaller, more frequent meals
            - Foods to aid digestion

            **Recommended Foods:**
            - High-protein foods
            - Iron-fortified foods
            - Fiber-rich fruits and vegetables
            - Healthy fats
            """)

        # Important note
        st.info("""
        **Note:** These are general guidelines. Always consult your healthcare provider
        for personalized nutrition advice during pregnancy.
        """)

# Function for the Educational Library Tab
def educational_library():
    st.title("Educational Library - Pregnancy Resources")
    
    # Welcome message
    st.write("""
    Welcome to our Educational Library! Here, you'll find comprehensive resources to guide you through every aspect of pregnancy, from early stages to postpartum care.
    """)

    # Sidebar to choose a topic
    topic = st.sidebar.selectbox(
        "Choose a section:",
        ["Pregnancy Stages & Development", "Nutrition and Diet Guides", "Exercise & Fitness", 
         "Mental Health & Emotional Well-being", "Common Pregnancy Symptoms", "Prenatal Care & Medical Tests", 
         "Childbirth Preparation", "Postpartum Care", "Baby Care Basics", "Expert Articles & Research", 
         "Pregnancy & Parenting Blogs", "Interactive Quizzes", "Pregnancy Glossary", "FAQ", "Interactive Journals"]
    )

    # Pregnancy Stages & Development
    if topic == "Pregnancy Stages & Development":
        st.subheader("Pregnancy Stages & Development")
        st.write("""
        Learn what to expect each month during pregnancy, from fetal development to physical changes in the body.
        """)
        st.image("https://example.com/pregnancy_stages_image.jpg", caption="Pregnancy Development Stages")
        
        st.write("""
        **First Trimester** (0-12 Weeks):
        - Key Development: The embryo forms organs and structures.
        - Symptoms: Morning sickness, fatigue, and nausea.

        **Second Trimester** (13-26 Weeks):
        - Key Development: Fetal movement, developing organs.
        - Symptoms: Reduced nausea, increased energy.

        **Third Trimester** (27-40 Weeks):
        - Key Development: Baby grows rapidly, prepares for birth.
        - Symptoms: Physical discomfort, back pain, frequent urination.

        For more details on each month, check out these guides:
        - [First Trimester Guide](https://example.com/first_trimester)
        - [Second Trimester Guide](https://example.com/second_trimester)
        - [Third Trimester Guide](https://example.com/third_trimester)
        """)

    # Nutrition and Diet Guides
    elif topic == "Nutrition and Diet Guides":
        st.subheader("Nutrition and Diet Guides")
        st.write("""
        Proper nutrition during pregnancy is essential for both you and your baby. Here's a breakdown of what to eat during each trimester.
        """)
        
        st.write("""
        **First Trimester**:
        - Focus on folic acid, vitamin D, and iron-rich foods like leafy greens, eggs, and fortified cereals.

        **Second Trimester**:
        - Add more protein-rich foods like beans, lentils, and lean meats. Focus on calcium and vitamin D for strong bones.

        **Third Trimester**:
        - Focus on healthy fats, whole grains, and continue to include calcium and protein-rich foods.
        """)

        # Interactive Meal Planner (This will be a simple input and suggestion tool)
        st.write("**Dietary Preferences**")
        dietary_preference = st.selectbox(
            "Select your dietary preference:",
            ["Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free", "No preference"]
        )

        if dietary_preference:
            st.write(f"Suggested meal plan for {dietary_preference} diet:")
            # You can enhance this by providing actual meal recommendations based on input
            st.write("Breakfast: Oatmeal with nuts and fruits")
            st.write("Lunch: Grilled chicken with quinoa and salad")
            st.write("Dinner: Stir-fried vegetables with tofu")

    # Exercise & Fitness for Pregnant Women
    elif topic == "Exercise & Fitness":
        st.subheader("Exercise & Fitness for Pregnant Women")
        st.write("""
        Staying active during pregnancy can help you feel better and prepare for childbirth. Here are some safe exercises.
        """)
        st.video("https://www.youtube.com/watch?v=exercise_video_id", caption="Pregnancy Fitness Video")
        
        st.write("""
        **Recommended Exercises:**
        - **Walking:** Low-impact and safe for all trimesters.
        - **Yoga:** Helps with flexibility and reduces stress.
        - **Pelvic Floor Exercises:** Strengthen muscles for labor.
        """)

    # Mental Health & Emotional Well-being
    elif topic == "Mental Health & Emotional Well-being":
        st.subheader("Mental Health & Emotional Well-being")
        st.write("""
        Pregnancy is an emotional rollercoaster. It's important to manage your mental well-being during this time.
        """)

        st.write("""
        **Tips:**
        - Take time for yourself with relaxation and mindfulness exercises.
        - Practice breathing techniques to manage anxiety.
        - Talk to a professional if you feel overwhelmed.
        """)

        st.audio("https://example.com/guided_meditation.mp3", caption="Guided Meditation for Pregnancy")

    # Common Pregnancy Symptoms
    elif topic == "Common Pregnancy Symptoms":
        st.subheader("Common Pregnancy Symptoms")
        st.write("""
        Here's a guide on common symptoms and how to manage them during pregnancy.
        """)

        st.write("""
        - **Nausea & Vomiting:** Eat small meals, drink fluids, and rest.
        - **Back Pain:** Practice good posture, use a pregnancy pillow.
        - **Fatigue:** Rest when needed and maintain a balanced diet.
        """)

        # Symptom Tracker
        st.write("**Track Your Symptoms**")
        symptom = st.selectbox("Select your current symptom:", ["Nausea", "Back Pain", "Fatigue", "Headache"])
        if symptom:
            st.write(f"You are experiencing: {symptom}")
            st.write("Based on your symptom, here are some remedies: ...")

    # Prenatal Care & Medical Tests
    elif topic == "Prenatal Care & Medical Tests":
        st.subheader("Prenatal Care & Medical Tests")
        st.write("""
        Prenatal care is crucial during pregnancy. Here are some key tests and what to expect.
        """)

        st.write("""
        **Key Tests**:
        - **Blood Tests:** Check for iron levels, infections, and blood type.
        - **Ultrasound:** Track fetal development.
        - **Glucose Test:** Screen for gestational diabetes.
        """)

        # Interactive Test Checklist
        st.write("**Prenatal Visit Checklist**")
        visit_checklist = ["Discuss any concerns", "Review ultrasound results", "Ask about recommended exercises"]
        checklist_completed = st.multiselect("Select completed items:", visit_checklist)
        st.write(f"Completed checklist: {', '.join(checklist_completed)}")

    # Continue with more sections similarly...

    # **Optional**: You can implement a blog section, expert articles, quizzes, and journaling features in a similar fashion.


def home_page():
    st.title("Welcome to Mother Health Care 👶")

    # Hero section with a background image
    st.markdown(
        """
        <style>
        .hero {
            background-image: url('https://example.com/your-background-image.jpg'); /* Replace with your image URL */
            background-size: cover;
            background-position: center;
            padding: 50px;
            color: white;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.header("Your Trusted Pregnancy Companion")
    st.write("""
    We're here to support you through every step of your pregnancy journey with:
    - 🏥 **Virtual Health Monitoring**
    - 🍎 **Personalized Nutrition Guidance**
    - 📚 **Educational Resources**
    - 🤒 **AI-Powered Symptom Checking**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Attractive sections for navigation without images
    st.subheader("Explore Our Services")

    st.markdown("### Nutritionist")
    st.write("Get personalized meal plans and nutrition advice tailored to your pregnancy stage.")

    st.markdown("### Virtual Doctor")
    st.write("Receive expert advice and assessments for your pregnancy symptoms.")

    # Optional: Add more information or features below the sections if needed
    st.write("Select an option to get started with personalized advice and support.")

def symptom_checker():
    st.title("Virtual Doctor - Your Pregnancy Symptom Checker 👩‍⚕️")

    # Patient Information
    st.subheader("Basic Information")
    col1, col2 = st.columns(2)

    with col1:
        pregnancy_week = st.slider("Current Week of Pregnancy:", 1, 42)
        previous_complications = st.multiselect(
            "Any previous pregnancy complications?",
            ["None", "Gestational Diabetes", "Preeclampsia", "Morning Sickness", "Other"]
        )

    with col2:
        current_symptoms = st.multiselect(
            "Current Symptoms:",
            ["Nausea", "Headache", "Fatigue", "Cramping", "Bleeding",
             "Swelling", "Back Pain", "Fever", "Other"]
        )
        symptom_severity = st.select_slider(
            "Symptom Severity:",
            options=["Mild", "Moderate", "Severe"]
        )

    # Additional Details
    st.subheader("Symptom Details")
    symptom_description = st.text_area(
        "Please describe your symptoms in detail:",
        height=100
    )

    # Emergency Warning
    if any(symptom in ["Bleeding", "Fever"] for symptom in current_symptoms) or symptom_severity == "Severe":
        st.error("""
        ⚠️ IMPORTANT: If you're experiencing severe symptoms, heavy bleeding, or high fever,
        please seek immediate medical attention or contact your healthcare provider.
        This tool is not a replacement for professional medical care.
        """)

    if st.button("Get Assessment"):
        if current_symptoms:
            prompt = f"""
            Patient is {pregnancy_week} weeks pregnant with the following symptoms:
            - Current Symptoms: {', '.join(current_symptoms)}
            - Severity: {symptom_severity}
            - Previous Complications: {', '.join(previous_complications)}
            - Additional Details: {symptom_description}
            """

            # Get response from the virtual doctor
            response = get_symptom_assessment_response(
                prompt,
                pregnancy_week // 4  # Convert weeks to months
            )

            # Add AI response to history with the correct role
            if 'symptom_chat_history' not in st.session_state:
                st.session_state.symptom_chat_history = []

            # Add user message to history
            st.session_state.symptom_chat_history.append(
                {"role": "user", "content": prompt}
            )

            # Add AI response to history
            st.session_state.symptom_chat_history.append(
                {"role": "doctor", "content": response}  # Change role to "doctor"
            )

            st.write("### Assessment")
            st.write(response)
        else:
            st.warning("Please select at least one symptom for assessment.")

def main():
    st.set_page_config(
        page_title="Mother Health Care",
        page_icon="👶",
        layout="wide"
    )

    # Initialize navigation in session state if not exists
    if 'navigation' not in st.session_state:
        st.session_state.navigation = "Home"

    # Main navigation
    st.sidebar.title("Mother Health Care")
    st.session_state.navigation = st.sidebar.radio(
        "Navigation",
        ["Home", "Symptom Checker", "Nutritionist", "Educational Library", "Resources"]
    )

    # Page routing
    if st.session_state.navigation == "Home":
        home_page()
    elif st.session_state.navigation == "Symptom Checker":
        symptom_checker()
    elif st.session_state.navigation == "Nutritionist":
        nutritionist_menu()
    elif st.session_state.navigation == "Educational Library":
        educational_library()

if __name__ == "__main__":
    main()
